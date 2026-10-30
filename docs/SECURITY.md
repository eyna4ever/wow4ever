# Sécurité et protection des données

Cette revue porte sur la branche locale, pas sur l’infrastructure de production. Elle ne vaut ni audit d’intrusion externe ni certification RGPD ou WCAG.

## Modèle de menace

Actifs : comptes Discord associés, contributions, préférences, signalements, sessions, privilèges et disponibilité du wiki. Frontières : navigateur non fiable, endpoints Discord fixes, proxy TLS, processus applicatif non privilégié et base locale privée. Menaces principales : usurpation de session, CSRF/OAuth, XSS stockée, lecture ou modification d’un objet tiers, élévation de privilèges, abus de publication, exposition de fichiers et réapparition de données effacées après restauration.

## Contrôles implémentés

| Domaine | Contrôle et limite |
| --- | --- |
| OAuth | Code + PKCE S256, `state` lié à la session, délai 10 minutes, consommation atomique unique, émetteur vérifié s’il est fourni, scope exact `identify` |
| Identité | Profil Discord validé, handle local aléatoire distinct du Discord ID ; aucun rôle attribué par le client |
| Sessions | Jeton aléatoire de 256 bits ; empreinte SHA-256 en base ; rotation après connexion ; expiration 1 h inactive / 24 h absolues ; révocation serveur |
| Cookies | HttpOnly, SameSite=Lax, cookie hôte sans Domain ; Secure et préfixe `__Host-` en HTTPS ; cookie local distinct en HTTP localhost |
| CSRF | POST authentifiés protégés par un secret lié à la session ; première connexion protégée par un double-submit signé de 10 minutes sans session SQLite au GET ; comparaison constante et rejet d’un Origin fourni différent de l’origine configurée |
| XSS | Jinja autoéchappé, texte brut pour les messages et citations, aucun `safe`, aucun HTML/Markdown utilisateur interprété ; CSP sans script/style inline, sans CDN |
| Injections | Paramètres SQLite pour toutes les valeurs ; identifiants et fragments SQL limités à des constantes serveur |
| Permissions | Relecture du rôle et de la suspension en base à chaque requête ; auteur ou modérateur pour édition ; administrateur pour salons/rôles ; membres suspendus privés de publication mais conservant leurs droits RGPD |
| Contenu masqué | Exclu des recherches, profils, notifications, permaliens et citations publics ; inspection réservée à la modération |
| Actions sensibles | Réauthentification de moins de 10 minutes pour rôles, suspension et effacement ; dernier administrateur protégé ; journal d’audit sans texte de message ni IP brute |
| Anti-abus | Compteurs SQLite communs aux workers ; 5 sujets/10 min/compte, 10 réponses/min/compte, 20 éditions/10 min/compte, 30 réactions/min/compte, 5 signalements/10 min/compte ; budgets par IP du client ou du pair si aucun proxy n’est autorisé ; limites OAuth/exports/avatars |
| Requêtes | Corps limité à 32 Kio, titre 150 caractères, message 10 000, signalement 1 000 ; listes paginées par 20 |
| Réseau | Host exact, HTTPS hors localhost, endpoints OAuth/CDN constants, délais réseau, redirections externes non suivies, TLS vérifié |
| Navigateur | CSP, nosniff, frame-ancestors none/X-Frame-Options DENY, Referrer-Policy same-origin (no-referrer sur callback OAuth), Permissions-Policy restrictive, HSTS HTTPS, no-store sur pages de compte et communauté |
| Fichiers | Liste autorisée pour le wiki, rejet de traversée ; jamais d’exposition de `.env`, `.git`, SQLite, code serveur ou script d’installation |
| Stockage | FK activées, transactions et rollback sur erreur, SQLite secure_delete, sauvegarde via API cohérente et contrôle d’intégrité ; permissions système et chiffrement des sauvegardes restent des responsabilités opérateur |

Les plafonds sont des valeurs initiales, pas une protection DDoS. Une protection de bord et une supervision restent nécessaires. La base utilise une pseudonymisation des clés anti-abus par HMAC, pas une anonymisation garantie. `TRUSTED_PROXY_IPS` est vide par défaut. L’en-tête X-Forwarded-For n’est utilisé que depuis un pair immédiat expressément autorisé par son adresse exacte, pour un seul saut ; tous les autres en-têtes de proxy sont ignorés. Le proxy doit remplacer l’en-tête et le backend rester inaccessible directement depuis Internet. L’omission de cette configuration regroupe les budgets d’écriture derrière le proxy. Les lectures anonymes ne consomment plus de budget de création de session. L’activité d’une session est écrite au plus une fois par minute, ce qui peut anticiper d’au plus une minute son expiration inactive.

Les cibles d’audit sont typées (`user:12`, `post:12`, etc.) et migrées par `init-db` (schéma 2). Lors d’un effacement, seule la cible utilisateur est anonymisée ; la FK retire séparément l’identité de cet utilisateur comme acteur. Les cibles de messages/sujets/catégories portant le même numéro et l’identité d’un autre modérateur sont préservées.

La CSP autorise uniquement sur le compte et le départ OAuth la destination de formulaire Discord fixe `https://discord.com/oauth2/authorize`, nécessaire pour la redirection navigateur après le POST. Les autres pages gardent `form-action 'self'`. Scripts, styles et connexions restent sur l’origine locale. Un test navigateur intercepte cette navigation externe sans contacter Discord.

## Matrice de permissions

| Action | Visiteur | Membre actif | Modérateur | Administrateur |
| --- | --- | --- | --- | --- |
| Lire wiki/forums publics | Oui | Oui | Oui | Oui |
| Créer/répondre/réagir/suivre/favoris | Non | Oui | Oui | Oui |
| Modifier ses messages | Non | Oui, hors verrouillage/masquage | Oui | Oui |
| Modifier/masquer le message d’autrui | Non | Non | Oui, journalisé | Oui, journalisé |
| Signaler | Non | Oui | Oui | Oui |
| Examiner/clore les signalements | Non | Non | Oui | Oui |
| Gérer catégories et sous-catégories | Non | Non | Non | Oui |
| Suspendre un membre | Non | Non | Oui, connexion récente | Oui, connexion récente |
| Attribuer un rôle | Non | Non | Non | Oui, connexion récente |
| Modifier un administrateur existant | Non | Non | Non | Opérateur CLI uniquement |
| Exporter/supprimer le compte d’autrui | Non | Non | Non | Non |

Un compte suspendu conserve paramètres, export, effacement et déconnexion. Le dernier administrateur ne peut pas effacer son compte avant transfert du rôle. Une suppression efface le texte et masque le sujet créé par le compte ; les réponses d’autres personnes restent en base pour leur propre gestion, dans la discussion masquée.

## Analyse statique et dépendances

Bandit détecte sept constructions SQL dynamiques (B608, sévérité moyenne). Revue manuelle : choix `follows`/`favorites` après validation d’une action ou d’un filtre ; fragments de recherche assemblés à partir de constantes ; noms de tables d’export issus d’une liste littérale interne ; colonne de modération issue du dictionnaire `lock/unlock/hide/restore`. Les valeurs utilisateur restent des paramètres `?`. Ces alertes ne sont pas supprimées du rapport. Les tests d’injection et de permissions complètent cet examen.

L’audit initial de dépendances a détecté des avis sur Flask 3.1.2 et Requests 2.32.5. Versions corrigées retenues : Flask 3.1.3 et Requests 2.34.2. L’audit final doit être conservé avec la révision et renouvelé régulièrement. Une absence d’avis connu ne prouve pas l’absence de faille.

## Données et rétention

La politique publique est à `/privacy/`. Bases proposées à valider : exécution du service demandé pour compte/interactions ; intérêt légitime pour sécurité et modération. Collecte minimale Discord `identify`, aucun e-mail, aucune liste de guildes et aucun jeton Discord persistant. Avatar servi par proxy pour éviter un appel CDN depuis le navigateur. Aucun traceur non essentiel.

| Données | Conservation prévue | Application |
| --- | --- | --- |
| Session | 1 h inactive, 24 h absolues | Vérifiée à chaque requête, purge quotidienne |
| Tentative OAuth / PKCE | 10 min / usage unique | Vérifiée et consommée atomiquement, purge quotidienne |
| Compteur anti-abus HMAC | Fin de la fenêtre 1–10 min | Purge quotidienne |
| Notification | 90 jours | Purge quotidienne |
| Signalement clos | 180 jours après clôture | Purge quotidienne |
| Journal d’audit | 180 jours | Purge quotidienne |
| Signalement ouvert | Jusqu’à examen | Revue mensuelle humaine obligatoire |
| Profil/contributions | Jusqu’à demande de suppression | Effacement en libre-service, revue annuelle des comptes inactifs à organiser |
| Sauvegardes | 30 jours | Commande et timer de rotation locale fournis ; installation, chiffrement et copie hors serveur à configurer |

L’effacement révoque toutes les sessions, retire les données liées de compte, remplace les textes des contributions et titres, supprime les signalements/réactions/notifications associés et retire l’association du journal au compte. Les citations sont des références à la contribution source, elles ne recopient pas le texte dans chaque réponse. Les données éventuellement présentes dans les messages d’un tiers nécessitent examen sur demande. SQLite WAL et sauvegardes doivent suivre la procédure de rétention ; `secure_delete` ne garantit pas l’effacement physique des supports, snapshots ou WAL historiques.

**Deux blocages avant le public restent ouverts suite à la revue** : un membre suspendu peut actuellement effacer son compte puis recréer un compte Discord non suspendu ; l’effacement retire aussi les signalements visant ses contributions. La politique d’empreintes de bannissement et de conservation restreinte des preuves, ses durées, sa base et son accès doivent être décidés puis implémentés/testés. Aucun stockage supplémentaire de ces données n’est activé arbitrairement dans ce lot. La préproduction doit rester privée et limitée aux comptes de test ; cette livraison n’est pas prête pour le public.

Avant ouverture publique, le responsable doit renseigner son identité et son contact, valider les finalités/bases/durées, recenser hébergeur et sous-traitants, transferts et garanties, organiser traitement des demandes et incidents, et appliquer une politique propre aux journaux d’infrastructure. Référence de principe : [CNIL — durées de conservation](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees).

Référence technique utilisée : [OWASP — Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).

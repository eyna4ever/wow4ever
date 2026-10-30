# Rapport de livraison — WoW Forever

30 octobre 2026 · branche locale `codex/community-redesign` · dépôt `eyna4ever/wow4ever`.

Voir aussi [la réponse à la revue](REVIEW-FOLLOWUP.md). La livraison reste réservée à la préproduction privée ; les politiques de bannissement et de preuves signalées restent bloquantes avant le public.

## Résultat

Le wiki existant est conservé et reçoit un thème commun bleu nuit, noir et or. Un serveur communautaire Flask/SQLite complète son architecture statique ; aucune reconstruction du wiki ni migration de ses contenus. Les 100 pages bilingues, leurs URL, scripts et sources sont préservés. Les nouveaux forums sont en français.

| Fonctionnalités | État de livraison |
| --- | --- |
| Thème, navigation communautaire, responsive | Implémentés et vérifiés dans Chromium de 320 à 1440 px |
| Discord Code + PKCE S256 + état CSRF | Implémenté et testé avec réponses simulées ; application Discord réelle à configurer |
| Sessions, déconnexion, révocation des autres sessions | Implémentées et testées |
| Catégories et sous-catégories | Initialisation de salons vides, création/édition administrateur, hiérarchie à deux niveaux avec prévention de cycles |
| Sujets et réponses | Création/édition, citations par référence, pagination et permaliens |
| Recherche et filtres | Titre/corps publics, catégorie et descendants, discussions suivies et favoris |
| Réactions et mentions | Votes utile/merci, pas d’auto-vote, mentions par handle local, notifications internes |
| Profils | Identité/rapport d’avatar Discord, historique public réglable, réputation et badges calculés à partir des contributions réelles |
| Modération | Signalements, clôture, masquage/restauration, verrouillage, suspension, rôles côté serveur et journal des actions |
| Données personnelles | Paramètres, export JSON, effacement libre-service, politique de rétention et commande de purge |
| Préproduction | Serveur local opérationnel, base vide réelle, unités systemd et procédure privée préparées ; aucun serveur distant modifié |

Aucun faux membre, faux sujet, faux compteur ni authentification de démonstration n’est visible dans l’application. Les données QA existent exclusivement dans des bases temporaires supprimées après les tests. Le Talent Builder et la gestion de guilde ne sont pas développés. Aucun autre projet n’a été modifié.

## Vérifications exécutées

- **29 tests serveur réussis** : OAuth PKCE/CSRF/rejeu/émetteur/échecs fournisseur, rotation et expiration des sessions, droits auteur/modérateur/admin, compte suspendu, prévention XSS/injection, visibilité des contenus masqués, citations, export/effacement, conservation, sauvegarde/restauration, transactions, catégories et pagination.
- **100 pages bilingues comparées** à la base Git : aucun changement de contenu après retrait des seuls liens/stylesheet ajoutés. Chaque page est aussi servie avec succès par le nouveau serveur.
- **41 contrôles navigateur réussis** : 24 vérifications de largeur, lien clavier vers le contenu, parcours fonctionnel complet, redirection Discord interceptée et 14 audits axe-core WCAG A/AA sur écrans publics et authentifiés. Aucun débordement détecté dans l’échantillon final à 320, 390, 768 et 1440 px. Aucun échec JavaScript/CSP détecté dans le parcours fonctionnel.
- **14 dépendances runtime auditées : aucun avis de vulnérabilité connu dans le résultat final**. Mise à jour de Flask 3.1.2 vers 3.1.3 et Requests 2.32.5 vers 2.34.2 après les alertes initiales. Résultat ponctuel, à renouveler.
- Bandit : sept alertes B608 de sévérité moyenne sur des identifiants SQL construits à partir de constantes, examinées dans [SECURITY.md](SECURITY.md). Aucune donnée utilisateur interpolée dans ces identifiants. Pas d’alerte de sévérité élevée.
- `pip check` et `git diff --check` exécutés sans erreur.

Corrections issues de la QA : débordements à 320 px dans les liens et filtres du wiki ; contraste des badges ; contrôle CSRF tolérant correctement une valeur malformée sans exception serveur ; politique de référent compatible avec les formulaires natifs tout en protégeant la callback OAuth ; séparation des actions de suspension et d’attribution de rôle dans le formulaire administrateur.

Le test de préservation utilise désormais un manifeste SHA-256 vérifié contre le Git initial dans un clone complet et exploitable dans une archive sans `.git`. Le test de service des pages/fichiers privés est distinct.

Les résultats navigateur sont reproductibles avec `tests/browser_checks.py`. Les instantanés de validation sont dans [evidence/](evidence/). Les commandes et dépendances QA sont dans [tests/README.md](../tests/README.md).

## Risques et limites restants

1. **Discord réel non recetté** : aucun identifiant d’application n’était fourni. Les mocks valident le protocole émis et les protections locales, pas l’acceptation effective par une application Discord configurée. Une recette avec de vrais comptes de test est indispensable.
2. **Infrastructure distante non auditée** : le domaine public n’était pas consultable avec l’outil web ; la révision réellement déployée, TLS, proxy, droits disque, journaux et sauvegardes restent à contrôler sur la préproduction cible. Aucun accès production n’a eu lieu.
3. **Maquettes absentes** : la direction artistique a été appliquée selon le brief. Une fidélité exacte aux maquettes ne peut pas être attestée.
4. **WCAG** : les audits automatiques ne constituent pas une certification WCAG 2.2 AA. Restent la recette lecteur d’écran, le zoom, les parcours clavier complets et les pages hors échantillon.
5. **RGPD** : le responsable doit renseigner et valider identité, contact, bases légales, sous-traitants, transferts éventuels, durées, journalisation d’infrastructure et traitement des demandes. Le timer et les sauvegardes ne sont pas installés à distance.
6. **Montée en charge** : stockage SQLite sur un serveur unique, recherche LIKE et budgets initiaux anti-abus. Aucun test de charge représentatif d’une communauté réelle ni test d’intrusion indépendant n’a été mené. La confiance dans le proxy doit être configurée explicitement et vérifiée sur la cible ; un pair non autorisé ne peut pas imposer son en-tête IP. Les GET anonymes ne créent plus de session.
7. **Exploitation/modération** : désigner les personnes habilitées et les procédures d’incident ; revoir mensuellement les signalements ouverts et annuellement les comptes inactifs ; la pertinence des messages pour Forever repose aussi sur la modération humaine.

8. **Suspension après effacement et preuves de modération** : le contournement par recréation de compte et la perte des signalements visant un compte effacé restent ouverts. Décider les politiques/durées, puis développer et tester ces traitements avant le public.

## Intervention humaine requise

| Intervention | Document associé |
| --- | --- |
| Fournir les maquettes et confirmer le rendu attendu | Aperçus locaux et `docs/AUDIT.md` |
| Créer/configurer l’application Discord, fournir les secrets hors Git, exécuter la recette réelle | [DISCORD.md](DISCORD.md) |
| Désigner responsable RGPD, contact et équipe de modération ; valider la politique et les prestataires | [SECURITY.md](SECURITY.md), page `/privacy/` |
| Choisir la machine de préproduction et installer service/timer, sauvegardes chiffrées et supervision | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Attribuer le premier rôle administrateur après connexion réelle | Commande `set-role`, `docs/DISCORD.md` |
| Effectuer recette manuelle d’accessibilité et revue de sécurité indépendante | `tests/README.md` |
| Autoriser explicitement toute publication, fusion ou modification de production | [DEPLOYMENT.md](DEPLOYMENT.md) |

La livraison reste dans l’espace de travail et sa branche dédiée. Aucun push, aucune fusion, aucun déploiement public, aucun reload Caddy et aucune installation distante n’ont été effectués.

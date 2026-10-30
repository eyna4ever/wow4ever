# Configuration Discord OAuth

Le flux implémenté est Authorization Code avec PKCE S256, état CSRF aléatoire et session serveur. Il n’utilise ni bot, ni accès aux guildes, ni e-mail.

## Paramétrage par l’opérateur

1. Créer une application dédiée dans le [Discord Developer Portal](https://discord.com/developers/applications). Utiliser une application distincte pour la préproduction.
2. Sous OAuth2, enregistrer exactement la callback correspondant à l’origine de l’environnement : `http://localhost:8000/auth/discord/callback` pour le local, ou `https://HOTE-PRIVE/auth/discord/callback` pour une préproduction TLS. La callback de production sera `https://wow4ever.raveforge.eu/auth/discord/callback`, uniquement après autorisation de mise en production.
3. Configurer `PUBLIC_URL` sans slash final ni chemin, `DISCORD_CLIENT_ID` et `DISCORD_CLIENT_SECRET`. Stocker le secret côté serveur dans le gestionnaire de secrets ou le fichier d’environnement 0600, jamais dans Git, le HTML ou le JavaScript. Fixer `SECRET_KEY` à une valeur aléatoire forte et stable pour cet environnement.
4. Autoriser les connexions sortantes HTTPS vers `discord.com` et `cdn.discordapp.com`. Conserver la vérification TLS et la confiance CA du système.
5. Redémarrer le service et effectuer la recette ci-dessous. Ne pas activer de bot, d’installation de guilde ou de permission supplémentaire.

## Garanties du code

- Permission unique `identify`. L’application vérifie le type Bearer et l’ensemble exact des scopes retournés.
- `state` et vérificateur PKCE propres à chaque tentative ; état conservé sous empreinte SHA-256, lié à la session, valable 10 minutes, consommé une seule fois avant l’échange réseau.
- `code_challenge_method=S256`, vérificateur transmis uniquement au token endpoint par le serveur. Métadonnées Discord indiquant S256 : [discovery OAuth](https://discord.com/.well-known/oauth-authorization-server).
- Vérification de l’émetteur `iss` lorsqu’il est présent ; endpoints et callback fixés côté serveur, aucune URL de retour fournie par le navigateur.
- Rotation du jeton de session et du CSRF après identification, suppression de l’ancienne session.
- Aucun état de session en base pour la consultation anonyme : cookie CSRF signé sur le formulaire (10 minutes), puis session allouée au POST valide. La CSP du compte permet la seule destination de redirection Discord attendue ; un contrôle Chromium intercepte cette navigation sans appel réel au fournisseur.
- Jetons Discord en mémoire uniquement. Après identification, une révocation est demandée ; un échec réseau produit un avertissement sans secret. L’opérateur doit surveiller ce message. Aucun refresh token n’est stocké ni réutilisé.
- Aucun rôle Discord ou pseudonyme ne donne automatiquement de privilèges locaux.
- L’avatar est récupéré via le serveur à une URL CDN construite à partir d’identifiants validés ; il ne provoque aucun appel direct du navigateur au CDN.

## Recette humaine indispensable

Les tests automatisés simulent Discord. Aucune connexion réelle n’a été effectuée : aucun identifiant d’application n’était fourni.

Vérifier sur l’application de préproduction : première connexion, reconnexion avec mise à jour du pseudonyme/avatar, consentement limité à l’identité, refus de consentement, expiration, fermeture du navigateur, onglets concurrents, callback rejouée, changement de compte Discord, perte de session, déconnexion et révocation des autres sessions. Confirmer dans les outils réseau que `code_verifier` ne quitte pas le serveur et que les cookies HTTPS portent `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`, sans `Domain`.

Ne pas capturer les codes OAuth, cookies ou jetons dans les rapports. Les journaux du proxy doivent exclure les query strings de callback ; les access logs Gunicorn sont désactivés dans l’unité fournie.

Pour le premier administrateur, se connecter normalement, puis exécuter localement, avec l’environnement du service :

```bash
.venv/bin/flask --app community.app:create_app set-role IDENTIFIANT_DISCORD admin
```

Le compte doit exister. L’action est inscrite dans le journal d’audit. Garder deux administrateurs autorisés pour la continuité de service, sans partage de compte.

Référence : [documentation OAuth Discord](https://docs.discord.com/developers/topics/oauth2).

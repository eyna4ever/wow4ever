# Déploiement statique (préparé, non exécuté)

Aucun déploiement n’a été effectué par la V2.2. Ce document décrit la procédure ; elle ne doit être lancée qu’avec l’accord du propriétaire.

## Ce qui est servi

Uniquement le contenu de `dist/`, emballé par `npm run package:web` dans `artifacts/deliveries/wow4ever-web.tar.gz` :
`index.html`, `fr/index.html`, `en/index.html`, `site.css`, `app.js`, `ui-core.mjs`, `assets/*.webp|svg`.
Le script refuse tout fichier hors liste blanche et tout identifiant de brouillon. Catalogue public : 0 fiche (36 brouillons non servis).

Jamais servis : `runtime/`, `artifacts/content-package/` (relecture, SQLite, JSON), `data/`, `docs/`, `design/`, `scripts/`, `node_modules/`.

## Procédure (Caddy)

```sh
npm test && npm run package:web          # depuis source/
sha256sum -c artifacts/deliveries/wow4ever-web.tar.gz.sha256
# sur le serveur, après sauvegarde de l’existant :
sudo mkdir -p /srv/wow4ever && sudo tar -xzf wow4ever-web.tar.gz -C /srv/wow4ever
# ajouter le bloc deploy/Caddyfile.example, puis :
caddy validate --config /etc/caddy/Caddyfile && sudo systemctl reload caddy
```

Retour arrière : restaurer la sauvegarde de `/srv/wow4ever` (ou l’ancien bloc Caddy) puis `systemctl reload caddy`.

## CSP

`default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; …` — aucun `unsafe-inline` ni `data:` : le build ne contient ni script exécutable inline (le bloc `application/json` n’est pas exécuté), ni attribut `style`, ni image `data:`. Testé le 24 octobre 2026 avec Caddy 2.11.7 en local (loopback) et Chrome headless : 0 violation CSP, 0 erreur console.
Le fichier autonome `wow-forever-integre.html` (scripts et images inline) n’est pas destiné à ce serveur.

# WoW Forever Wiki V2.2 « koa » — lire d’abord

Corrections locales du 24 octobre 2026 sur l’archive V2.1. Aucun site, DNS ou serveur n’a été contacté ni modifié. Les 36 notices restent des **brouillons** ; 0 fiche publique.

- `RAPPORT-CORRECTIONS.md` : constats P0/P1/P2, changements, tests réellement exécutés.
- `verification-koa/` : journaux de chaque commande (`logs/`, `commands.tsv` = commande + code de sortie), captures PNG (ordinateur 1440×900, mobile 390×844), scripts de contrôle navigateur, liens/traductions et serveur CSP local.
- `apercu-site.html` : fichier autonome reconstruit avec les corrections (ouvrir dans un navigateur).
- `documentation/` : dossier privé de relecture d’origine (import du 19 octobre), conservé tel quel pour garder l’historique. Ne pas le servir.
- `verification/`, `ETAT-VERIFIE.json`, `LIRE-MOI-SUPERGROK.md`, `PROMPT-SUPERGROK.md` : documents V2.1 d’origine (historiques). État à jour : `ETAT-VERIFIE-KOA.json`.

## Reconstruire (Node.js 24, Python 3)

```sh
cd source
npm test                       # 114 tests
npm run content:prepare        # import local + relecture + SQLite dans artifacts/ (rien hors du projet)
npm run package:web            # artifacts/deliveries/wow4ever-web.tar.gz = SEUL dossier à servir
npm install && npm run typecheck && npm run build   # optionnel : adaptateur Next.js
```

Dossier web à servir : `source/dist/` (ou l’archive `wow4ever-web.tar.gz`). Bloc Caddy : `source/deploy/Caddyfile.example`. Procédure et retour arrière : `source/docs/DEPLOY-STATIC.md`.

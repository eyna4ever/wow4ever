# Rapport de corrections — WoW Forever Wiki V2.1 → V2.2 « koa »

Date : 24 octobre 2026 (heure de Paris). Travail fait **uniquement en local** sur une copie. Aucun site, DNS, serveur ou hébergement n’a été contacté, modifié ou déployé. Aucun achat. Aucun statut ni attestation modifié : **les 36 notices restent des brouillons, 0 fiche publique**. Aucune relecture humaine signée.

Méthode : les angles « architecture », « documentation/sources », « UX/accessibilité/i18n » et « sécurité/DevOps/QA » ont été examinés **l’un après l’autre par un seul agent** (pas d’équipe réelle).

## 1. Environnement

| Élément | Valeur |
|---|---|
| Node.js système | v20.19.2 → **incompatible** avec `npm test` (voir P1-4) |
| Node.js utilisé | **v24.22.1**, archive officielle nodejs.org (somme SHA-256 vérifiée), installée dans `/workspace/tools` |
| Python | 3.13.5 |
| Navigateur | Google Chrome 156 headless, piloté par `playwright-core` 1.64.1 (installé hors projet) |
| Caddy | 2.11.7 (binaire officiel, somme vérifiée), utilisé seulement en local sur 127.0.0.1 |
| Réseau | registre npm accessible (installation Next gratuite) |
| sqlite3 CLI | absent → contrôles PRAGMA faits avec le module `sqlite3` de Python |

## 2. Constats P0 / P1 / P2

Aucun **P0** reproduit : pas de secret dans l’archive (seulement `.env.example` avec `CHANGE_ME`), aucun brouillon dans `dist/` ni dans le HTML autonome (vérifié par recherche des 36 identifiants), circuit de revue non contournable (tests 57/58 : approbation et publication d’un brouillon refusées).

| # | Prio | Fichier:ligne (V2.1) | Preuve | Conséquence | Correction | Statut |
|---|---|---|---|---|---|---|
| 1 | P1 | `scripts/prepare-content.mjs:9` | log 03 : a créé `/workspace/shared/downloads/` hors du projet | écrit hors du projet, non portable | dossier configurable (`--output-dir`, `WOW_FOREVER_OUTPUT_DIR`), défaut `artifacts/deliveries/` | corrigé |
| 2 | P1 | `scripts/package-local.py:5` et `:12` | log 07 : `FileNotFoundError …/preview/index.html`, code 1 | `npm run package:local` cassé sur une copie neuve, chemin fixe | même dossier configurable + création de `preview/` | corrigé (log 94) |
| 3 | P1 | `scripts/export-preview.py:9` | chemin fixe `/workspace/shared/downloads` | non portable | dossier configurable | corrigé (log 56) |
| 4 | P1 | `package.json:13` | log 00 : `node: bad option: --test-isolation=none`, code 9 sous Node 20 | tests impossibles hors Node ≥ 22, aucun avertissement | `engines: node >=24`, `.nvmrc`, README | corrigé |
| 5 | P1 | `lib/site.mjs:5` | log 23 : `next build` échoue (`import.meta.dirname` indéfini dans le bundle) | adaptateur Next.js impossible à compiler | racine calculée avec repli (`WOW_FOREVER_ROOT`, URL du module, dossier courant) | corrigé (logs 25, 82) |
| 6 | P1 | `tsconfig.json` / `next-env.d.ts` | log 22 : 4 erreurs TS dans les types de Next ; `next-env.d.ts` casse `tsc` si `.next/` absent | typecheck en échec | `skipLibCheck` (ajouté par Next), `next-env.d.ts` exclu du dépôt (.gitignore) | corrigé (log 81) |
| 7 | P1 | `public/wiki/template.html:44` | mention « Site indépendant et non officiel de Blizzard Entertainment. » absente | exigence du propriétaire non respectée | mention ajoutée en pied de page (FR) + équivalent EN, contrôlée par `check-release` et un nouveau test | corrigé |
| 8 | P1 | `public/wiki/template.html:23` | bandeau « construite avec des sources vérifiées » alors que 0 fiche est vérifiée | affirmation trompeuse | « en construction : rien n’est publié sans sources vérifiées » (FR/EN) | corrigé |
| 9 | P1 | (absent) | aucun paquet contenant **seulement** le dossier web | risque de servir sources/brouillons | `scripts/package-web.mjs` + `npm run package:web` : liste blanche, refus de tout ID de brouillon, archive tar.gz prête pour `/srv/wow4ever` | corrigé |
| 10 | P2 | `scripts/check-preview.cjs:8` | chemin `/opt/codex/...` propre à l’ancien environnement | contrôle navigateur non portable | recherche `WIKI_PLAYWRIGHT_MODULE` / `playwright` / `playwright-core`, Chrome accepté | corrigé (log 98) |
| 11 | P2 | `scripts/build-static.mjs:17` | `<meta description>` en français sur `/en/` | SEO/i18n | description par langue | corrigé |
| 12 | P2 | `scripts/build-static.mjs:17` | log 70 : erreur console 404 (`/favicon.ico`) | console non propre | `assets/favicon.svg` (blason existant) + lien | corrigé (logs 96–97) |
| 13 | P2 | `app/layout.tsx:3` | `<html lang="fr">` aussi pour `/en` (Next) | i18n Next imparfaite (atténué : `lang` sur `#wiki-app`) | à restructurer en `app/[lang]/layout.tsx` | restant |
| 14 | P2 | `next.config.ts:2` | CSP Next avec `'unsafe-inline'` | CSP moins stricte côté Next | nonces Next à mettre en place si Next est retenu | restant |
| 15 | P2 | `docs/ASSETS.md:17-19`, `design/README.md:7` | chemins `/workspace/generated_images/...` | provenance non vérifiable ailleurs | historique, sans effet sur le code | restant |
| 16 | P2 | `artifacts/wow-forever-integre.html` | fichier autonome ≈ 9,5 Mo (images en base64) | lent sur mobile en 4G | non servi par Caddy ; optimisation d’images à prévoir | restant |
| 17 | P2 | `ETAT-VERIFIE.json`, `LIRE-MOI-SUPERGROK.md` | indiquent « Next non exécuté », 112 tests | obsolètes après V2.2 | conservés comme historiques ; état à jour dans `ETAT-VERIFIE-KOA.json` | corrigé (ajout) |

Fonctionnalités **honnêtement annoncées absentes** (pas des régressions) : comptes/rôles, PostgreSQL connecté, modération, réputation, cartes vérifiées, comparateurs, PWA (le manifeste n’est pas lié au site statique), test Android réel.

Effet de bord à signaler : la reproduction du défaut n°1 (log 03) et de l’ancien `package-local` (log 07) a créé `/workspace/shared/downloads/` sur la machine de travail (2 HTML + 1 ZIP + 1 HTML de relecture locaux, rien en ligne). Sa suppression automatique a été bloquée par le contrôle de sécurité ; dossier laissé en place.

## 3. Changements (copie `work/`, détail dans `DIFF.patch`)

- `scripts/prepare-content.mjs`, `scripts/package-local.py`, `scripts/export-preview.py` : sortie portable dans le projet, option `--output-dir`, variable `WOW_FOREVER_OUTPUT_DIR`.
- `scripts/package-web.mjs` (nouveau) + script `package:web` : archive du seul dossier web.
- `lib/site.mjs` : racine robuste (Next, bundlers).
- `public/wiki/template.html` : mention « non officiel » FR/EN, bandeau corrigé.
- `scripts/build-static.mjs` : description par langue, favicon.
- `scripts/check-release.mjs` : refuse un template sans la mention ; `tests/legal-notice.test.mjs` (2 tests).
- `scripts/check-preview.cjs` : chemins portables.
- `package.json` (`engines`, `package:web`), `.nvmrc`, `package-lock.json` (nouveau, Next 16.4.3 / React 19.3.1 / TypeScript 5.9.3), `tsconfig.json` (ajouts de Next), `.gitignore`/`.dockerignore`.
- `deploy/Caddyfile.example`, `docs/DEPLOY-STATIC.md` (nouveaux) ; README, `docs/PREVIEW.md`, `docs/VALIDATION.md` mis à jour.
- Racine : `apercu-site.html` reconstruit ; `LIRE-MOI-V2.2-KOA.md`, `ETAT-VERIFIE-KOA.json`, `verification-koa/` ajoutés. `documentation/` (import du 19 octobre) **non modifié** pour conserver l’historique.

## 4. Tests (journaux : `verification-koa/logs/`, liste : `commands.tsv`)

Tous exécutés réellement le 24 octobre 2026, Node 24.22.1 sauf mention.

| Commande | Code | Résultat | Exécuté |
|---|---|---|---|
| `npm test` (Node 20, état initial) | 9 | option `--test-isolation` inconnue | oui |
| `npm test` (Node 24, état initial) | 0 | 112/112 | oui |
| `python3 scripts/package-local.py` (initial) | 1 | crash `preview/` | oui |
| `npm run typecheck` / `next build` (initial) | 2 / 1 | erreurs TS / `import.meta.dirname` | oui |
| **`npm test` (final)** | 0 | **114 réussis, 0 échec** | oui |
| `npm install` + `npm audit --omit=dev` | 0 / 0 | lockfile généré, 0 vulnérabilité | oui |
| **`npm run typecheck` (final)** | 0 | OK | oui |
| **`npm run build` = `next build` (final)** | 0 | 4 routes compilées | oui |
| `npm run content:import -- --dry-run` | 0 | 36 lues, aucune écriture | oui |
| `npm run content:prepare` | 0 | import + rapports + relecture + SQLite, tout dans `artifacts/` | oui |
| relance de l’import (reprise/doublons) | 0 | 0 insertion, 36 doublons reconnus | oui |
| `node scripts/check-data.mjs` (graine et runtime) | 0 | 0 erreur | oui |
| `npm run content:review`, `content:report`, `content:db` | 0 | OK | oui |
| SQLite `PRAGMA integrity_check` / `foreign_key_check` | 0 | `ok` / 0 erreur ; 36 fiches `draft`, 62 sources, 24 relations, 72 révisions | oui |
| `npm run build:static` | 0 | 12 rubriques, 0 fiche publiée | oui |
| `check-release.mjs` (HTML autonome, runtime) | 0 | catalogue = sélection stricte (0) | oui |
| `check-release.mjs` + ZIP `package:local` | 0 | 105 fichiers, CRC OK | oui |
| `package-web.mjs` | 0 | 12 fichiers, 0 publié, aucun brouillon | oui |
| `review.mjs approve/publish` sur brouillon | 1 / 1 | **refus attendu** | oui |
| `restore.mjs` à blanc + aller-retour réel (runtime isolé) | 0 | état restauré identique (36 = 36) | oui |
| liens/traductions (`qa-links-i18n.mjs`) | 0 | 49 liens, 144 paires FR/EN, 0 problème | oui |
| `caddy validate` (bloc fourni) | 0 | Valid configuration | oui |
| navigateur via **Caddy local** (CSP stricte) | 0 | 20/20 : 0 violation CSP, 0 erreur console, focus clavier, recherche, filtres, favoris, FR/EN, menu mobile, pas de débordement à 390 px | oui |
| navigateur via serveur Python CSP | 0 | 20/20 | oui |
| `node scripts/check-preview.cjs` (contrôle du projet) | 0 | PASS | oui |
| `next start` / rendu Next en navigateur | — | — | **non** (hors périmètre statique) |
| essai sur téléphone Android réel | — | — | **non** (pas d’appareil) |
| audit WCAG / lecteur d’écran / Lighthouse | — | — | **non** |
| déploiement Caddy réel sur le serveur | — | — | **non** (interdit sans accord) |

Le test « mobile » est une émulation Chrome 390×844, pas un téléphone réel.

## 5. Notices par catégorie × statut

Source : `runtime/entries.json` après import local (identique à l’export SQLite).

| Catégorie | draft | review | verified | published |
|---|---:|---:|---:|---:|
| Classes et spécialisations | 9 | 0 | 0 | 0 |
| Races et factions | 1 | 0 | 0 | 0 |
| Zones et exploration | 4 | 0 | 0 | 0 |
| Donjons et raids | 3 | 0 | 0 | 0 |
| Métiers et artisanat | 2 | 0 | 0 | 0 |
| Objets et équipements | 2 | 0 | 0 | 0 |
| Quêtes et progression | 3 | 0 | 0 | 0 |
| PvP et activités | 3 | 0 | 0 | 0 |
| Créatures et boss | 2 | 0 | 0 | 0 |
| Guides | 2 | 0 | 0 | 0 |
| Actualités et annonces | 3 | 0 | 0 | 0 |
| Glossaire et références | 2 | 0 | 0 | 0 |
| **Total** | **36** | 0 | 0 | 0 |

Aucune couverture complète n’est revendiquée (pas d’inventaire de référence).

## 6. Lacunes restantes et coûts

- Contenu : périmètre du jeu non confirmé ; faits, droits et traductions non relus par un humain ; sources consultées le 19 octobre à revalider (la bêta annoncée jusqu’au 21 octobre ne doit pas être présentée comme ouverte) ; contradiction Flèches multiples/Visée toujours ouverte dans `data/research/forever-classes-sources.json`.
- Fonctions : comptes, PostgreSQL, modération, cartes, comparateurs, PWA, sauvegardes planifiées côté serveur.
- Qualité : Android réel, audit WCAG, poids des images (≈ 7 Mo d’illustrations).
- Coût de cette intervention : **0 €** (outils gratuits). Déploiement statique sur le Caddy existant : pas de coût supplémentaire prévu.

## 7. Préparation réelle au déploiement

- **Dossier à servir : `source/dist/`**, livré tout prêt dans `out/deploy/wow4ever-web.tar.gz` (index.html à la racine ; `tar -xzf wow4ever-web.tar.gz -C /srv/wow4ever`). Il ne contient ni brouillon, ni SQLite, ni relecture, ni sources, ni PNG de conception.
- Bloc Caddy : `out/deploy/Caddyfile-block.txt` (= `source/deploy/Caddyfile.example`), validé par `caddy validate` et testé en local avec Chrome : CSP stricte sans `unsafe-inline` ni `data:`, aucune violation.
- La page servie contient bien « Site indépendant et non officiel de Blizzard Entertainment. »
- Le site public affichera **0 fiche** : c’est voulu tant que la revue humaine n’est pas faite.
- Ne jamais servir `documentation/`, `source/artifacts/content-package/`, `runtime/`, `data/`.
- Procédure + retour arrière : `source/docs/DEPLOY-STATIC.md`. Rien n’a été déployé.

## 8. Une seule action du propriétaire

**Confirmer par écrit que le wiki vise bien « World of Warcraft: Forever » de Blizzard (annonces/bêta d’octobre 2026).** Cela débloque `--confirm-identity` et donc le circuit de relecture humaine puis de publication des 36 brouillons (`docs/PIPELINE.md`) ; sans cette confirmation, le site restera à 0 fiche publique.

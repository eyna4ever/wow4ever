# WoW Forever Wiki V2.2 (corrections « koa », 24 octobre 2026)

> **Dossier à servir sur le web : `dist/` uniquement** (ou l’archive `artifacts/deliveries/wow4ever-web.tar.gz` produite par `npm run package:web`, à extraire dans la racine du serveur). Ne jamais servir `runtime/`, `artifacts/content-package/`, `data/`, `docs/`, `design/`, `scripts/` ni la base SQLite. Le site affiche « Site indépendant et non officiel de Blizzard Entertainment. »

La conception fantasy est intégrée en **HTML/CSS/JavaScript utilisable**, avec les mêmes éléments pour l’export statique, le fichier autonome et l’adaptateur Next.js. La démo privée est publiée sur **https://wow4ever.raveforge.eu**, avec domaine et HTTPS confirmés actifs par Sites. La base documentaire locale contient **36 brouillons FR/EN, 24 URL sources et 14 articles primaires distincts**, couvrant les douze rubriques. **0 fiche est publiée** : identité ciblée du wiki et revue humaine des faits, droits et traductions restent à confirmer. Comptes applicatifs et backend documentaire ne sont pas connectés.

## Préparer le contenu

```sh
npm run content:prepare
```

Cette commande importe les trois lots versionnés sans doublons, puis produit un dossier HTML privé de relecture, un rapport de couverture, un export JSON et une base relationnelle SQLite locale dans une archive de livraison. Elle ne change ni le DNS ni le site déployé, et ne publie aucune fiche. Voir [CONTENT-LIBRARY.md](docs/CONTENT-LIBRARY.md) pour les sources, lacunes et validations restantes. SQLite est un export local ; ce n’est pas une base de production hébergée.

## Ouvrir le résultat

Ouvrir `wow-forever-integre.html` depuis l’archive de livraison dans un navigateur. Ce fichier contient ses images, ses styles et son JavaScript et fonctionne sans installation ni connexion. Il conserve les paramètres personnels en stockage local lorsque le navigateur l’autorise. Une page ouverte comme fichier ne constitue pas une PWA installée.

## Construire sans dépendances

Node.js 24 requis (`engines` et `.nvmrc`) : `npm test` utilise `--test-isolation=none`, option absente de Node 20 (erreur « bad option »). Aucun appel réseau ni clé nécessaire.

```sh
npm run build:static
```

Le dossier `dist/` contient le site statique pour serveur HTTP, avec `/fr/` et `/en/`. Le fichier autonome est écrit dans `artifacts/wow-forever-integre.html`.

`npm run preview` construit puis sert la version HTTP sur `http://127.0.0.1:3000/fr/` avec Python 3. Le serveur écoute seulement en boucle locale ; cette adresse n’est pas accessible depuis un téléphone distant. Son démarrage dépend des permissions réseau locales de l’environnement. Ctrl+C l’arrête.

`npm run package:local` construit et produit l’archive complète dans `artifacts/deliveries/` (dans le projet). Autre dossier : `python3 scripts/package-local.py --output-dir /chemin` ou variable `WOW_FOREVER_OUTPUT_DIR`. Même règle pour `scripts/prepare-content.mjs` et `scripts/export-preview.py`. Aucun script n’écrit plus en dehors du projet par défaut.

`npm run package:web` construit puis produit `artifacts/deliveries/wow4ever-web.tar.gz` : uniquement le dossier web public (index.html à la racine, `fr/`, `en/`, CSS/JS, `assets/`), contrôlé par liste blanche et sans brouillon. Extraction : `tar -xzf wow4ever-web.tar.gz -C /srv/wow4ever`. Exemple Caddy avec CSP stricte testée : `deploy/Caddyfile.example`.

## Interface intégrée

- Illustration panoramique originale, cadres médiévaux dorés, textures, recherche centrale et cartes illustrées.
- Douze rubriques, six cartes principales et six rubriques supplémentaires.
- Mise en page responsive et menu mobile, FR/EN, libellés clavier, focus et mouvement réduit.
- Recherche sans accents, suggestions et filtres combinables ; aucun résultat fictif ajouté pour remplir le catalogue.
- Fiches à sources/historique/relations, favoris et étapes de guides par révision, raccordés pour l’arrivée des contenus approuvés. Le catalogue vide ne permet pas d’en démontrer l’usage réel.
- Comptes, contributions, atelier documentaire et cartes affichent leur état réel. Aucun formulaire d’authentification ni marqueur inventé.

Les illustrations sont conceptuelles : elles ne documentent pas les lieux, classes ou objets du jeu. Voir `docs/ASSETS.md`.

## Architecture et sécurité documentaire

`public/wiki/template.html`, `site.css`, `app.js` et `lib/ui-core.mjs` forment l’interface partagée. `lib/site.mjs` charge le magasin local, `lib/public-catalog.mjs` sélectionne uniquement les fiches publiées avec revue actuelle, identité, droits et traductions attestés. Les brouillons, attestations internes et acteurs privés sont exclus de l’export ; les relations vers des fiches privées sont masquées.

Le magasin source est `runtime/entries.json` s’il existe, sinon `data/entries.json`. Une corruption de `runtime` bloque le build, elle ne provoque pas de repli silencieux. `runtime` n’est jamais copié dans la livraison publique.

Le dossier `site/` de l’archive peut être servi comme site statique. **Ne pas exposer `sources/` sur le web.** Les politiques de sécurité du serveur local sont dans `scripts/serve.py`. La version Next utilise `next.config.ts`.

## Pipeline local

```sh
npm run import -- /chemin/lot-autorise.json --dry-run
npm run check:data
```

Les imports restent en brouillon. Validation humaine, publication éditoriale, corrections et restauration sont effectuées par les CLI `scripts/review.mjs` et `scripts/restore.mjs`, avec attestations explicites et sauvegardes à checksum. Les étapes et arguments exacts sont dans `docs/PIPELINE.md`. Ne pas modifier à la main un statut ou une attestation pour contourner le circuit.

Quotas locaux : aucun accès réseau ni service payant dans le pipeline, plafond de dépenses 0 EUR. Recherche des sources, autorisations d’extraction et traduction humaine restent en amont.

## Adaptateur Next.js / TypeScript

Les routes `/fr` et `/en` utilisent le même template et contrôleur. `/admin` renvoie à l’atelier en lecture seule. L’installation du framework nécessite l’accès au registre npm :

```sh
npm install
npm run typecheck
npm run build
npm start
```

Le 24 octobre 2026 (V2.2), `npm install` a généré `package-lock.json` (Next 16.4.3, React 19.3.1, TypeScript 5.9.3), `npm audit --omit=dev` a signalé 0 vulnérabilité, puis `npm run typecheck` et `next build` ont réussi après correction de `lib/site.mjs` (`import.meta.dirname` absent dans le bundle Next). `next start` et le rendu Next en navigateur n’ont pas été validés. Le site statique reste la voie de déploiement recommandée. L’export statique utilise uniquement Node et reste indépendant de cette installation.

## Vérifier et livrer

```sh
npm test
npm run check:data
npm run build:static
node scripts/check-release.mjs artifacts/wow-forever-integre.html data/entries.json
npm run package:local
```

Le contrôle d’archive accepte ensuite le ZIP en troisième argument de `check-release.mjs`. S’il existe un magasin `runtime`, passer ce fichier en second argument au lieu de la graine.

Le contrôle navigateur optionnel est `node scripts/check-preview.cjs` avec Playwright (ou `playwright-core`, chemin via `WIKI_PLAYWRIGHT_MODULE`) et Chromium/Chrome. Il a été exécuté avec succès le 24 octobre 2026 avec Chrome headless. Les vérifications de structure, de syntaxe et de logique ne remplacent pas une validation visuelle, un test Android réel ou un audit d’accessibilité.

## Mise en ligne et suite

La démo utilise l’hébergement géré Sites ; son domaine et HTTPS ont été confirmés actifs. Aucun accès OVH ni serveur n’a été connecté à cette session : les modifications DNS ont été réalisées par le propriétaire. `Dockerfile` et `deploy/compose.static.yaml` préparent une autre possibilité d’hébergement statique isolé et n’ont pas été exécutés. Voir `docs/CUSTOM-DOMAIN.md`, `docs/DEPLOYMENT.md` et `docs/VALIDATION.md`.

À réaliser : contenu sourcé et validé, vérification de l’identité ciblée, tests visuels et Android, backend PostgreSQL connecté, authentification/permissions, modération et réputation, cartes vérifiées, comparateurs, PWA et synchronisation, sauvegardes planifiées/restauration serveur. Aucun achat ni service payant ajouté. La mise en production exigera l’audit de l’hébergement puis la validation unique demandée dans le cahier des charges.

## Démo privée Sites

`npm run prepare:demo` exécute les contrôles, construit et archive un instantané public vérifié. `npm run archive:demo` produit ensuite le paquet de publication Sites. L’identité du site est conservée dans `.openai/hosting.json`, sans jeton. La publication distante est effectuée par les outils Sites connectés après synchronisation du commit ; son résultat doit être vérifié avant de fournir une URL comme active. Voir `docs/DEMO-AUTOMATION.md`. La publication automatique sur simple push n’a pas été activée par le service pour ce compte.

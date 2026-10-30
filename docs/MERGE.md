# Build fusionné : communauté (lot 2 Codex) et wiki en ligne actuel

Préparé le 30/10/2026 (heure de Paris), **en local sur la box uniquement**. Rien n'a été déployé ni poussé, aucun serveur n'a été touché et aucun secret n'a été lu.

## Sources
- **Application communauté** : `/workspace/wow4ever-community/src2`, lot 2 de la branche `codex/community-redesign` après la contre-revue.
- **Wiki** : le build statique **en ligne depuis le 28/10**, `wow4ever-web.tar.gz`, SHA-256 `944750bbd3432a668cdbca7f9f5d34422f33048f2e7de362c401a5e7c62fba55`. Il est construit depuis `wow-forever-supergrok/source/` et son `dist/` est identique octet pour octet à l'archive (vérifié). Il contient :
  - 125 pages HTML et 203 fichiers ;
  - 49 contenus publiés (34 fiches et 15 articles AR01–AR15) ;
  - **AC2 (`forever-news-beta`) et CL3 (`forever-class-priest`), restés brouillons et absents du build** (vérifié par un test).

## Ce qui a changé par rapport à `src2`
1. **L'ancien wiki embarqué est retiré** : les 100 pages `fr/` et `en/` du commit `9b51f38`, `assets/`, `index.html`, `sitemap.xml` et `robots.txt`. Le build actuel n'a ni `robots.txt` ni sitemap ; il porte `noindex` dans ses pages.
2. **Nouveau répertoire `wiki/`**, produit par `tools/integrate_wiki.py <tarball>`. Le script :
   - vérifie le SHA-256 de l'archive ;
   - refuse tout fichier hors liste blanche ;
   - vérifie la mention Blizzard dans chaque page ;
   - n'applique **que des modifications de navigation**, enregistrées dans `tests/wiki-baseline.json` :
     - pages d'accueil (`/`, `/fr/`, `/en/`) : l'entrée « Communauté » ouvrait un panneau factice, elle pointe maintenant vers `/community/`. Le bouton « Connexion », qui ouvrait une boîte de dialogue locale « comptes non connectés », devient un lien `/account/` ;
     - 122 fiches et rubriques : lien « Communauté » ou « Community » ajouté à la fin de `nav.page-nav`.
   - Le texte, les statuts, les images, `site.css`, `app.js` et `ui-core.mjs` restent **identiques octet pour octet**.
   - L'option `--no-community-links` copie le wiki sans aucun lien, pour une phase où la communauté resterait cachée.
3. **Ressources de la communauté déplacées** vers `community/static/` et servies sous `/community/static/` : `style.css`, `community.css`, la police Cinzel et `default.svg`. Elles ne se mélangent plus avec `assets/` du wiki et restent sous un préfixe protégeable.
4. **`community/app.py`** :
   - `WIKI_ROOT` (par défaut `wiki/`) ;
   - liste blanche limitée aux fichiers du build : `index.html`, `site.css`, `app.js`, `ui-core.mjs`, `assets/*.webp|jpg|svg` et `fr|en/<slug>/…/index.html` ;
   - redirection 308 `/fr/zones` → `/fr/zones/` ;
   - cache d'une semaine sur `assets/`, `no-cache` sur les pages ;
   - nouvelle route `/community/static/…` avec sa propre liste blanche ;
   - avatar par défaut à son nouvel emplacement.
   Le blocage des traversées (`..`) et des fichiers sensibles est conservé et testé.
5. **Gabarits de la communauté** : nouveaux chemins CSS et favicon du wiki. La navigation devient « Wiki » → `/fr/`, « Actualités » → `/fr/actualites/`, « Retour au wiki » et « Wiki (English) » en pied de page, « Explorer le wiki » → `/fr/guides/`. Les liens vers des pages qui n'existent plus (`/fr/news/`, `/fr/sources/`, `/fr/credits/`, `/fr/guide/`) ont été retirés. La mention exacte « Site indépendant et non officiel de Blizzard Entertainment. » est toujours présente.
6. **Tests** :
   - `test_wiki_preservation` est réécrit : l'ancienne référence Git ne s'applique plus. La nouvelle référence est l'empreinte de chaque fichier de l'archive en ligne ; le test annule les modifications enregistrées et compare les empreintes.
   - Nouveau test `test_drafts_not_published`.
   - `test_source_allowlist_and_pages` sert les 203 fichiers et vérifie les types MIME `.jpg`/`.mjs`, la redirection et 22 chemins interdits.
   - `tests/browser_checks.py` :
     - pages du wiki remplacées (`/fr/actualites/calendrier-forever/`, `/en/zones/mount-hyjal/`) ;
     - **correctif d'une ligne** (`errors.clear()` après la simulation Discord) ;
     - les audits axe des pages du wiki deviennent **informatifs** (`axe-wiki`), puisqu'ils relèvent du build statique et pas de l'application ; ceux de la communauté restent bloquants.
7. **Déploiement** : `deploy/production/` contient les unités systemd `wow4ever-community*` et la proposition de fragment Caddy. Rien n'est appliqué. Voir `docs/INSTALL-HETZNER.md`.

## Compatibilité CSP
- **Si l'application sert le wiki** (tunnel ou préproduction) : la CSP de l'application (`default-src 'self'`, `img-src 'self' data:`) est plus permissive que celle du wiki et couvre tous ses besoins : module ES `'self'`, CSS `'self'`, images `'self'`. Le bloc `<script type="application/json">` n'est pas exécuté. Les contrôles navigateur, avec la CSP réellement appliquée, ne relèvent **aucune violation CSP et aucune erreur JS** sur les pages du wiki, à 4 largeurs.
- **Si Caddy sert le wiki** (production proposée) : la CSP stricte actuelle du wiki doit être limitée au `handle` statique. Appliquée aussi aux chemins proxifiés, elle se cumulerait avec celle de l'application et casserait la redirection vers Discord (`form-action 'self'`).

## Préfixes à protéger par mot de passe (Caddy, plus tard)
`/community`, `/community/*` (y compris `/community/static/*`), `/auth/*`, `/account`, `/account/*`, `/notifications`, `/notifications/*`, `/moderation`, `/moderation/*`, `/privacy`, `/privacy/*`.
- `/healthz` n'est pas publié.
- Le wiki (`/`, `/fr/*`, `/en/*`, `/assets/*`, `/site.css`, `/app.js`, `/ui-core.mjs`) reste public.
- Pendant une phase protégée, les liens « Communauté » et « Connexion » du wiki mènent à une demande de mot de passe. Pour l'éviter, reconstruire avec `--no-community-links`.

## Mise à jour v6 (30/10/2026)
- Le wiki est reconstruit par le pipeline `wow-forever-supergrok/source/` après l'import du lot `data/batches/forever-news-2026-10-30.json` et le circuit `review.mjs` (submit → approve → publish, acteur « Mathieu », approbation donnée par Mathieu le 30/10/2026) pour 6 actualités : `forever-news-golive-nov4`, `forever-news-return-guide`, `forever-news-starter-guide`, `forever-news-podcast-tech`, `forever-news-story-unbowed`, `forever-news-portal-room`.
- Nouvelle archive : `wow4ever-web.tar.gz`, SHA-256 `2ed60db2b192585b7963d1561afe49246a41df672f044a4b6aedba8c7bcca885` : 137 pages HTML, 215 fichiers, 55 contenus publiés.
- AC2 (`forever-news-beta`) et CL3 (`forever-class-priest`) restent des brouillons absents du build.
- Communauté en lecture publique : la basic auth Caddy ne protège plus que `/auth/*`, `/account*`, `/notifications*` et `/moderation*` (voir `update-v6.sh`).

# Rapport étape 03 — Validateur + Lot 1 (environnement de test isolé)

Date : 9 novembre 2026, ~20 h 25 (heure de Paris, CET). **Production : rien n'a été déployé.** wowkipedia.com, le VPS, Caddy, Raveforge et ForgeCraft n'ont pas été touchés. Pas de push, pas de branche, pas de PR, pas de cloud agent, aucun secret lu.

## 1. Décision GO / NO-GO
**Mise en production future : NO-GO pour l'instant.** Raisons, par ordre :
1. La sauvegarde du VPS `/root/wow4ever-v31-backup-20261109T100544` n'est toujours pas vérifiée.
2. Les 7 fiches ne sont « publiées » que dans l'arbre de test, avec une approbation de **test** (acteur « TEST-ISOLE … PAS une validation humaine de Mathieu »). Ta vraie relecture est nécessaire (`review.mjs approve` à ton nom).
3. Le déploiement demandera de mettre à jour les garde-fous de la communauté. Avec le nouveau wiki, 5 tests sur 47 échouent, comme prévu :
   - nombre de pages figé à 227 ;
   - hash du tarball v31 ;
   - empreinte v8 (« 86 nouvelles pages ») ;
   - en-tête du forum `site/community/templates/_v2_header.html`, dont les compteurs sont écrits en dur (Quêtes 6 au lieu de 11, Métiers 3 au lieu de 5).

   Ces mises à jour relèvent de l'étape de déploiement, pas de ce lot.

## 2. Validateur corrigé (bloquant) — fait et prouvé
Détail complet dans `VALIDATOR_FIX.md`.
- Une source uniquement Eternadex, client-extraite ou communautaire donne **toujours « à confirmer »**. C'est visible en FR (« À confirmer ») et en EN (« Unconfirmed — to be confirmed »), et jamais affiché comme « officiel confirmé » ni « vérifié en jeu ».
- warcraft.wiki.gg (et tout `*.wiki.gg`) est **refusé** : quarantaine à l'import, invalide en édition directe.
- Wowhead est classé client-extrait. Rien n'est récupéré ni importé depuis Wowhead, et aucune URL Wowhead n'est utilisée dans le lot.
- Les sources Blizzard restent de première classe : les 97 fiches existantes se rendent à l'identique.
- Une fiche mixte officielle + Eternadex ne promeut **pas** ce qui ne repose que sur Eternadex. Le contrôle est fait bloc par bloc et fait par fait.
- L'ancien cas d'échec `q-eternadex-quest-count-test` est maintenant rétrogradé en « à confirmer » et signalé (`downgraded`). Avant, il était inséré en silence.
- 5 tests de régression sur 5 passent.

## 3. Lot 1 — fiches réellement créées (mesurées)
**7 fiches × 2 langues = 14 pages.** Toutes sont sourcées uniquement par Blizzard (articles du 13/09, 23/09 et 21/10/2026, plus le message officiel du forum US du 08/10/2026). Toutes ont le statut « officiel confirmé » et aucune ne porte la mention « à confirmer ». Liste : `LISTE_FICHES.csv`.

| Bloc | Fiche (id) | Contenu |
|---|---|---|
| D Héritage | forever-legacy-challenges | 65 défis = 27 + 18 + 12 + 2 + 3 + 3, condition par catégorie, règle 29 / 16 points, mode Extrême (12 défis prévus) |
| D Héritage | forever-legacy-perks | 3 arbres × 7 = 21 avantages, noms FR/EN officiels + effet décrit |
| D Héritage | forever-legacy-rewards | 4 récompenses du lancement (jouet, mascotte, tabard, monture) |
| C Campements | forever-camp-features | 11 objets (1 par métier) : compétence, effet, buff de classe incompatible ; obtention ; restrictions ; risque JcJ ; avantages d'héritage liés |
| B Métiers | forever-professions-overview | 2 principaux parmi 9, 3 secondaires, rangs Apprenti → Artisan, maîtres de métier, onglet K, paliers 150/225/300 |
| A Quêtes | forever-quest-rewards-expanded | Mor’Ladim (bois de la Pénombre, lien vers l'anneau d’héritage de Ladimore) et Hemet Nesingwary (sorcépée de maître-chasseur) |
| A Quêtes | forever-questline-gelkis-magram | Quêtes Gelkis/Magram en Désolace à partir de « Valley of Bones » : niveau min. 35 (au lieu de 30), 16 récompenses réajustées (source : bêta) |

- Architecture réutilisée :
  - entries.json (import via `scripts/import.mjs`, revue via `review.mjs`) ;
  - catégories existantes `quests` et `professions` ;
  - nouvelles sous-catégories : `heritage`, `metiers-et-rangs`, `recompenses-de-quetes` (aucune nouvelle rubrique) ;
  - documentary.mjs et le rendu v2.
- Chaque fiche :
  - a une section « à confirmer » qui dit ce que Blizzard n'a pas publié ;
  - signale les écarts FR/EN (par exemple « Charismatique » contre « Performance bonus », et « un métier » au singulier en FR contre « each » en EN) ;
  - a des relations vers des fiches existantes publiées ;
  - garde la mention © Blizzard (droits réservés).
- Dans le catalogue de test : 97 → **104** fiches publiées, 227 → **241** pages.

## 4. Ce qui n'a pas été fait, et pourquoi
- **Calculateur de matériaux : non fait.** Blizzard n'a publié ni recettes ni quantités de composants pour Forever. Un calculateur fondé sur Eternadex ou Wowhead serait « à confirmer » et pourrait induire en erreur. La fiche Métiers l'explique.
- **Noms individuels des 65 défis : non listés**, car Blizzard ne les publie pas. La liste exacte des donjons par tranche de niveaux et celle des réputations de champ de bataille ne sont pas précisées non plus.
- **11 fiches séparées par objet de campement : non faites.** Chacune n'aurait contenu qu'une ligne, soit des pages quasi vides. Un tableau complet a été fait à la place. Blizzard précise d'ailleurs que c'est « un aperçu », pas la liste complète.
- **Recettes, composants, emplacements des maîtres, niveaux par rang :** non publiés officiellement, donc absents.
- **Quêtes secondaires :** pas d'import des 5 167 quêtes ni des 48 factions. Seules 2 fiches sont documentées officiellement. Valthalak, Dalaran et Onyxia existaient déjà. La quête d'introduction au campement n'a pas de nom publié, donc pas de fiche.
- **Checklist Héritage locale : non faite.** C'était optionnel. Il faudrait un nouveau script client, à valider côté CSP et UX Android. Je la propose pour un lot suivant, avec stockage local uniquement (localStorage) et rien sur le serveur.
- **Aucune donnée Eternadex, Wowhead ou wiki.gg** dans le lot. Aucun dump n'a été téléchargé.

## 5. Tests réellement exécutés (preuves dans `preuves/`)
| Test | Résultat |
|---|---|
| Suite pipeline complète (`npm test`) | **175 tests : 172 OK, 0 échec, 3 ignorés** (les mêmes 3 qu'avant ; avant le lot : 165 → 162 OK / 3 ignorés). Fichier `pipeline_node_tests.txt` |
| Régression validateur (4 cas demandés + ancien cas) | 5/5 OK — `validator_regression_tests.txt` |
| Intégrité référentielle (audit, relations publiées, sources de blocs, pas de collision d'URL) | OK — `v21-lot1.test.mjs`, `check_data_runtime.json` (106 fiches, 104 publiées, 0 erreur) |
| Idempotence | Import 7 insérées ; ré-import 0 insérée / 7 doublons, `unchanged: true`, même hash d'entries.json ; re-test après revue : 7 doublons — `import_lot1_*.json`, `entries_*.sha256` |
| Dry-run import | 7 insérables, 0 invalide, 0 quarantaine — `import_lot1_dry_run.json` |
| Pages existantes | 194 fichiers identiques octet pour octet ; 200 diffèrent **uniquement** par les compteurs du menu ; 28 pages de liste/accueil/A-Z/recherche mises à jour ; 0 supprimé. **Blocs de contenu (sections + sources) des pages existantes : 194 identiques, 0 modifié.** Les pages Discord ne diffèrent que par le compteur du menu — `diff_existing_pages.txt`, `content_blocks_existing_pages.txt` |
| Rendu à l'identique des 97 fiches existantes (hors lot) contre site/wiki | OK (test v16) |
| Android / accessibilité (14 pages + listes) | viewport, `lang`, noindex, 1 seul h1, pas de saut de titre, tableaux avec caption et `th scope`, tableaux dans une zone défilante focusable, ni script ni style en ligne, pas de sitemap. Captures 412 px : `captures-android/` |
| Communauté (47 tests unitaires) | Wiki de production : **47/47 OK**. Wiki du lot 1 : 5 échecs attendus (garde-fous de déploiement, voir §1) |
| Gunicorn de test | Copie temporaire, base neuve, sans variable Discord. `/healthz` → `{"schema":3,"status":"ok"}`, 15 tables. Pages du lot, Discord, `/community/` et `/privacy/` en 200. **Arrêté**, port 8015 libre — `gunicorn_test_health.txt` |
| Permissions | Aucune modification des droits ni des fichiers ops/ et site/ (`git diff` limité à `pipeline/lib`, `pipeline/scripts` et `pipeline/tests`). La SQLite communautaire n'a été ni migrée ni écrasée |

## 6. Aperçu local
- Arbre de test : `/workspace/wowkipedia-v21-elite/etape-03/test-tree` (commits locaux `0959c68` base, `dba183e`, `ac725a1`, `af5d2d0`).
- Pages générées : `test-tree/pipeline/dist-v2/` (par ex. `fr/quetes/defis-heritage/index.html`, `fr/metiers/campement-fonctionnalites/index.html`).
- Démo de la mention « à confirmer » (fiche fictive, jamais publiée) : `preuves/demo_a_confirmer_fr.html` / `_en.html`.

## 7. Patches (aucune PR)
- `patches/00-diff-complet-code-et-tests.diff` : s'applique proprement sur 17e037542b8f (vérifié avec `git apply --check` seulement).
- `patches/01-validateur-politique-sources.diff` et `patches/02-tests-validateur-et-lot1.diff`.
- `patches/03-runtime-entries-lot1-TEST-UNIQUEMENT.diff` : contient les approbations de test, **à ne pas appliquer en production**. Le bon chemin est d'importer `04-lot1.entries.json`, puis de faire ta revue.
- `patches/04-lot1.entries.json` : les 7 brouillons sources, générés par `lot1/build_lot1.py`.

## 8. À décider par Mathieu
1. Relire et valider (ou corriger) les 7 fiches. Seule ton approbation compte pour la production.
2. La fiche Gelkis/Magram repose sur des notes de **bêta** (8 oct.), avec des noms seulement en anglais. Faut-il la garder, ou attendre une source postérieure au lancement ?
3. Les nouvelles sous-catégories `heritage`, `metiers-et-rangs` et `recompenses-de-quetes` te conviennent-elles ?
4. Veux-tu la checklist Héritage locale (navigateur uniquement) dans un prochain lot ?
5. Pour le déploiement : feu vert pour mettre à jour les garde-fous communauté (compteurs de l'en-tête du forum, nombre de pages, hash du tarball), une fois la sauvegarde VPS vérifiée.

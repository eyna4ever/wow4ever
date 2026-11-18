# Import Polestar (forever-db) — audit, licences et importateur

Statut : **brouillon technique, rien n'est publié.** Branche `feat/polestar-import`. `main`, la production et le serveur ne sont pas touchés.
Aucune donnée tierce n'est stockée dans ce dépôt : seuls le code, la configuration épinglée et des tests synthétiques y sont.

## 1. Ce que contient Polestar (commit épinglé `8c3d3476e025dfd4cf199b0a320df354b371454d`, 18/11/2026)

| Partie | Contenu | Format | Volume | Version du jeu |
|---|---|---|---|---|
| `forever-db/data` | quêtes, donneurs, receveurs, objectifs, prérequis (suites), récompenses, PNJ, objets du décor, objets, sources de butin, positions, étapes, mécaniques | JSON Lines + schémas JSON, `datapackage.json` avec sha256 et licence par fichier | 5 287 quêtes, 3 811 liens de prérequis, 6 200 récompenses, 13 239 PNJ, 10 437 objets du décor, 23 344 objets, 38 105 sources, 88 761 positions, 2 409 étapes, 3 401 mécaniques | Forever, client **1.60.1.70532** (le nôtre : 70862) |
| `addon/Polestar_QuestDB` | base de quêtes de l'add-on | Lua | **absente du dépôt** (construite en local) | Forever |
| `addon/Polestar_ItemDB` | `Items.lua` : caractéristiques d'objets ; `Forever.lua` : objets de montée en niveau et leur provenance | Lua | 9 483 objets ; listes de montée en niveau | `Items.lua` = **Classic Era 1.15.9** ; `Forever.lua` = Forever |
| `guides/forever` | 265 guides (montée 1-60 par faction et race, classes, métiers, réputations, montures, mascottes) | texte `.guide` généré | 265 fichiers | Forever |

## 2. Verdict des licences

| Source | Licence (citation) | Verdict |
|---|---|---|
| `forever-db` tables `quest*`, `npc`, `object`, `spawn`, `item`, `item_source` | « GPL-3.0 (`LICENSE`): the database » | **Réutilisable sous GPL-3.0** : licence jointe, crédits, données modifiées fournies sous la même licence. Réserve ci-dessous (QuestieDB). |
| `forever-db` `step`, `mechanic` | « CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`): our own layer » | **Réutilisable avec attribution** et mention des modifications (traduction). |
| `forever-db` `ui_map` | GPL-3.0 | Pas utilisé : le cadre des cartes est lu dans **nos** fichiers du client 70862 (identique). |
| `Polestar_QuestDB` | contient QuestieDB : « the maintainers ask that it be treated as all rights reserved » | **Exclu.** |
| `Polestar_ItemDB/Items.lua` | tables Classic Era 1.15.9 (Blizzard) | **Exclu** (pas Forever). |
| `Polestar_ItemDB/Forever.lua` | faits tirés de ForeverLevelingBiS, MIT, dans un add-on GPL-3.0-only | **Non importé** pour l'instant ; à réévaluer depuis la source MIT. |
| `guides/` | GPL-3.0 ; l'exception « does not cover guide text copied from Polestar's own guides » ; trajets faits avec des cartes prêtées « with Leffe's permission given to Polestar's author » | **Exclu** (texte d'auteur, non recopié). |

Réserve importante : le tri de Polestar compte QuestieDB comme source indépendante (`tier.rs` : `"questie"` dans `ALWAYS`). Une valeur peut donc
n'être appuyée que par QuestieDB, dont les mainteneurs demandent de traiter les données comme « tous droits réservés ». Le fichier de provenance
par valeur est privé (`provenance.sqlite`, « Never committed »). Les faits bruts (noms, niveaux, identifiants) sont rarement protégés par le droit
d'auteur, mais **le droit européen des bases de données** peut protéger une extraction substantielle. Décision à prendre par Mathieu.

## 3. Importateur (`tools/polestar/`)

- `UPSTREAM.json` : commit, version et liste fermée des fichiers autorisés avec leur licence ; liste des exclusions avec la raison.
- `polestar_import.py verify` : refuse si le build n'est pas Forever (1.60.1.*), si la version ou le commit diffèrent, si un sha256 ou une licence change.
- `stage` : sélection d'une zone (et de ses sous-zones, d'après `AreaTable` du client), positions converties en % de carte avec `UiMapAssignment`
  du client 70862. Chaque enregistrement porte `provenance` (source, commit, table, licence, sha256), `status: a-confirmer`, `origin: third-party`
  et `dedupe` (`nouveau`, `doublon-identique`, `doublon-conflit` avec le détail). Rien n'écrase nos données : fichier de staging séparé.
  Noms d'objets français tirés du client (provenance « client »), séparés des données Polestar.
- `diff` : rapport ajoutés / retirés / modifiés entre deux versions. Mise à jour contrôlée : on change le commit dans `UPSTREAM.json`,
  on joint le rapport à la pull request, Mathieu valide. Aucune publication automatique.
- `render_sample.py` + `frontend/wk-map.js|css` : rendu d'essai dans une **copie** de l'arbre du wiki (carte interactive + tableau des suites de quêtes
  + page « Sources et licences »). Compatible avec la CSP (`script-src 'self'`, `style-src 'self'`), sans dépendance.

## 4. Attribution et règle « pas de nom de site tiers dans le texte »

Le texte des pages ne nomme aucun site tiers. L'attribution exigée par les licences passe par :
1. une entrée dans la liste « Sources » de chaque page concernée, qui renvoie vers
2. une page « Sources et licences » (noindex) qui nomme Polestar, ses sources amont, les licences, le commit, et donne le fichier de données modifié.
C'est une proposition : Mathieu choisit.

## 5. Carte interactive

Images : tuiles de la carte du monde du client Forever 1.60.1.70862 (`UiMapArtTile`), téléchargées sur le CDN officiel de Blizzard,
converties en WebP sans perte, non retouchées, créditées « © Blizzard Entertainment ». Aucune image ne vient de Polestar.
Repères : positions Polestar (à confirmer). Les tuiles ne sont pas dans ce dépôt.

## 6. Armurerie Battle.net (faisabilité seulement)

Une armurerie officielle Forever existe (worldofwarcraft.blizzard.com, « World of Warcraft: Forever », personnages à partir du niveau 10).
Le format exact des adresses de personnage reste à vérifier ; rien n'est construit.

## 7. Futur assistant de progression (notes de conception)

Entrées possibles : niveau, faction, race, classe, quêtes faites (saisies par le joueur, stockées seulement sur son téléphone).
Le graphe `prereq` / `next` donne les quêtes disponibles ; `level`/`min_level` filtrent ; les zones viennent de `zone_area`.
Aucun compte, aucune donnée envoyée au serveur. À construire seulement après décision sur la licence.

## 8. Objets Classic (Items.lua, Classic Era 1.15.9) — `tools/polestar/classic_items.py`

- Fichier `Items.lua` du dépôt (GPL-3.0, faits de jeu Blizzard). Refus si le build n'est pas `1.15.*` ou si l'export Forever n'est pas `1.60.1.*`.
- Seuls les ID présents dans le client Forever 70862 sont admissibles ; les valeurs Forever (notre extraction client) l'emportent toujours.
- Résultat : 9 483 objets dans Items.lua → 4 691 présents dans Forever (4 159 identiques sur les champs communs, 532 différents) ; 4 783 sont chiffrés/absents côté client Forever (comptés, non utilisés) ; 9 ignorés (non équipables).
- Les nombres propres à Classic (dégâts, armure, montants de stats — colonnes absentes du client Forever) ne sont conservés que si tous les champs communs sont identiques (4 269 objets), sous `classic_1_15_9` avec statut « à confirmer » et provenance (commit, sha256).

## 9. Toutes les zones (test uniquement) — `render_zone.py` / `render_all.py`

- 50 zones Forever, pages FR et EN (100 pages). Le tableau des quêtes fusionne notre index et forever-db sans doublon (ancres existantes conservées par titre ; nouvelles lignes `r-q<id>` ; nom/niveau alternatif affiché en `wk-alt`).
- Totaux : 3 349 lignes (2 999 communes, 268 index seul, 82 forever-db seul), 1 120 lignes avec écart signalé, 40 438 repères, 4 679 PNJ, 1 530 objets interactifs, 3 819 objets. 0 ancre perdue.
- Zones sans données : Mont Hyjal (aucune quête dans les deux sources → message explicite, pas de tableau vide) ; Rives claires (1 quête, aucun repère).
- Carte : images officielles du client (UiMapArt), converties en WebP q85 (format seulement, non retouchées), créditées. Fiche mobile compacte : ≤ 8 repères proches, un seul ouvert, hauteur max 42vh.
- Crédits : entrée « Sources » sur chaque page + pages noindex `fr/sources-et-licences/` et `en/sources-and-licences/` avec les données sous forme modifiable (`.json.gz`).

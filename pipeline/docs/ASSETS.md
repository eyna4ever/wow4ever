# Illustrations de l’intégration V2.1

Les trois images ci-dessous ont été générées le 18 octobre 2026 avec l’outil de génération d’images, en prenant `design/projection-accueil.png` comme référence visuelle fournie par le projet. Elles reprennent sa composition, sa lumière dorée et ses ombres bleu nuit, sans incorporer ses textes ou son interface.

Ces illustrations de conception représentent un univers fantasy imaginaire. Elles ne constituent ni des cartes vérifiées, ni des personnages officiels, ni des références documentaires sur WoW Forever ou World of Warcraft. Aucun lieu, race, classe, emblème ou équipement représenté ne doit être présenté comme une donnée de jeu confirmée. Aucun contenu d’un wiki tiers n’a été recopié pour les produire. La validation juridique des noms, marques et éventuelles ressemblances reste distincte de cette documentation de provenance.

| Asset intégré | Dimensions PNG | Utilisation |
| --- | --- | --- |
| `public/wiki/assets/hero.png` | 1942 × 809 | Panorama d’accueil : aventuriers sur un promontoire, vallée alpine, citadelle et cascades. |
| `public/wiki/assets/categories.png` | 1536 × 1024 | Atlas de six illustrations en grille exacte de trois colonnes et deux lignes. |
| `public/wiki/assets/features.png` | 2172 × 724 | Atlas de deux illustrations en deux colonnes : grimoire à gauche, carte et boussole à droite. |

## Origines préservées

Les fichiers de génération originaux sont conservés sans modification dans l’espace de travail :

- `/workspace/generated_images/exec-0095dc55-018b-4f7b-943b-8af412049cf1.png` → copie `hero.png`.
- `/workspace/generated_images/exec-eb0384ab-9eb6-4afb-8a05-177a28646925.png` → copie `categories.png`.
- `/workspace/generated_images/exec-2b74527e-535c-4e35-8775-a21cb626b9e4.png` → copie `features.png`.

Les copies intégrées ont exactement le même contenu binaire que leurs originaux. Aucun recadrage, retouche, ajout de texte ou conversion n’a été appliqué.

## Grille des catégories

L’atlas mesure 1536 × 1024 pixels : chaque cellule mesure 512 × 512 pixels. Cette dimension réelle a été retenue par le générateur ; les cartes web utilisent un masque paysage. La sélection d’une cellule peut être réalisée en CSS avec `background-size: 300% 200%`, puis les positions suivantes :

| Illustration | Colonne / ligne | `background-position` |
| --- | --- | --- |
| Guerrier et cercles de magie | 1 / 1 | `0% 0%` |
| Aventuriers et bannières originales | 2 / 1 | `50% 0%` |
| Vallée, montagnes et citadelle | 3 / 1 | `100% 0%` |
| Crypte éclairée aux flambeaux | 1 / 2 | `0% 100%` |
| Enclume, marteau et forge | 2 / 2 | `50% 100%` |
| Parchemin, boussole et lanterne | 3 / 2 | `100% 100%` |

## Panneaux des guides et cartes

`features.png` a un ratio global de 3:1 et deux cellules de 1086 × 724 pixels. Avec `background-size: 200% 100%`, utiliser `background-position: 0% 0%` pour le grimoire, et `100% 0%` pour la carte et la boussole. Le grimoire est placé à gauche de son panneau ; la carte et la boussole à droite du leur. Des zones sombres permettent de superposer des titres HTML réels et accessibles.

## Contrôles exécutés

- Inspection visuelle des trois fichiers : absence de texte et d’interface ; six catégories et deux panneaux présents dans le bon ordre.
- Dimensions lues avec `file`.
- Empreintes SHA-256 :
  - `hero.png` : `f68b16f2836cf86c63e54f4d56f18762f7df4971daa8f3fac2deebbff6236ee0`.
  - `categories.png` : `7a0c5fa955922c334d4b8fdc8901f6890324b96202e4cb6232a673f9bc7a4687`.
  - `features.png` : `eb23ffd35335d8f4436a121bca27f91bec30cbad183b49bfad6c768abc3694a0`.

Les illustrations seules pèsent environ 9,3 Mio en PNG. Une future optimisation de livraison peut produire des variantes AVIF/WebP tout en conservant ces originaux.

## Encodage de livraison sans perte

Les trois originaux PNG sont conservés. Des variantes WebP **sans perte** ont été encodées localement avec FFmpeg/libwebp pour la livraison web, sans recadrage, changement de dimensions ni retouche. Les empreintes des pixels RGBA décodés de chaque PNG et WebP ont été comparées et sont identiques.

| Asset | PNG original | WebP servi |
| --- | ---: | ---: |
| hero | 3 367 556 octets | 2 616 560 octets |
| categories | 3 514 360 octets | 2 739 898 octets |
| features | 2 712 394 octets | 1 914 290 octets |

La livraison charge environ 7,27 Mo d’illustrations, au lieu de 9,59 Mo, sans perte de pixels. Les sprites sont recadrés uniquement par CSS avec leurs proportions naturelles. L’export autonome référence chaque illustration une seule fois via une variable CSS, puis l’intègre en base64 ; cela évite les doublons tout en permettant une ouverture hors ligne.

Les PNG de travail restent dans cet espace de travail et les originaux générés sont préservés. L’archive d’intégration contient les variantes WebP utilisées par le code ; elle ne duplique pas les PNG inutilisés.

## Illustrations d’articles (28 octobre 2026)

15 illustrations d’ambiance originales, une par article élite AR01–AR15, générées le 28/10/2026 avec l’outil GenerateImage (aucune référence, capture, logo, personnage reconnaissable ni texte). Sources 1280 × 720 inchangées dans `design/illustrations-src/articles/`, exports `public/wiki/assets/art-arNN-*-640.webp`, `-1280.webp` et `-1280.jpg` (repli) produits par `scripts/build-article-visuals.py`. Prompt, date, méthode, sha256 et textes alternatifs FR/EN : `design/illustrations-src/provenance.json` (clés `article:ARNN`) et `lib/visuals.mjs`. Les fiches courtes réutilisent l’illustration de leur article lié. Légende : « Illustration d’ambiance — ne constitue pas une source ».

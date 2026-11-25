# Lots v39 et v40 — brouillons d’import, non importés

**Aucun import dans un arbre live, aucune publication, aucun déploiement.** L’arbre v38 n’a pas été touché.

## v39 — fiches de zones

- `v39-zones.entries.json` — JSON compact (limite d’import 2 Mo). 52 entrées, toutes valides contre `documentary.validate()` de l’arbre v37 (lecture seule).
- `v39-zones.stats.json` — comptages.
- 1 index (`forever-zones-directory`, slugs `liste-des-zones` / `zone-list`) + 4 révisions des fiches officielles déjà en ligne (version 9, `identityConfirmed: true`) + 47 nouvelles fiches monde (version 1, `identityConfirmed: false`). Statut `draft`.
- Zones monde seulement (celles qui apparaissent dans les données Forever, plus mont Hyjal et Rives Claires déjà officielles, 0 PNJ). Les labels d’instance sont dans l’index, sans seconde fiche « zone ».
- Données issues des fichiers du jeu : non marquées « à confirmer ». Champs absents : « non indiqué ». `article.confirmed` ne contient que des faits officiels (le validateur l’exige).

## v40 — insertions de liens (pas un lot d’import)

- `v40-cross-links.json` — liste d’insertions par page, pas des `revise` complets (évite de collisionner avec v38).
- 121 paires monstre–recette (55 recettes, 31 monstres, 9 zones) déjà présentes dans les 96 lignes des tableaux publiés (19 lignes listent plusieurs monstres d’une même zone dans une cellule). Liens à poser sur les noms. 2 vendeurs. 32/37 poissons déjà liés vers la cuisine/alchimie ; liens inverses : 29 cuisine, 3 alchimie. 91 boss étiquetés → donjons. 17 pages, 611 insertions.

Voir aussi `../map-prototype/` (cartographe Zéphras, hors lot d’import).

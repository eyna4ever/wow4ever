# Rapport — recettes à butin par zone (t344u), 12 novembre 2026 (Europe/Paris)

Décisions Mathieu : (1) section « à confirmer » sur le site ; (2) suite des recettes Drop **par zone**.

## Comptages

- Recettes « Drop » dans l’index consulté : **55**. Fiches item ouvertes : **55/55** (HTTP 200).
- **Sources + zone trouvées : 55. Introuvables : 0.**
- Paires monstre–recette : **121**. Coffres / objets-conteneurs : **0** (aucun indiqué). Taux de drop : **0** (aucun indiqué, donc aucun repris).
- Tous les statuts : **à confirmer (données extraites du client)**. Date de consultation : 2026-11-12. URL exacte dans `RECETTES_PNJ.csv`.

### Par zone (une recette peut apparaître dans plusieurs donjons)

| Zone (nom sur la fiche consultée) | Recettes distinctes | Paires monstre–recette |
|---|---:|---:|
| The Deadmines | 23 | 31 |
| Blackfathom Deeps | 21 | 36 |
| Shadowfang Keep | 20 | 20 |
| The Stockade | 13 | 13 |
| Ragefire Chasm | 10 | 12 |
| Razorfen Kraul | 5 | 5 |
| Ruins of Lordaeron (Ruines de Lordaeron, nom officiel Forever) | 2 | 2 |
| Wailing Caverns | 1 | 1 |
| Scarlet Monastery: Graveyard | 1 | 1 |
| **Total unique** | **55** | **121** |

Hors périmètre, non consultées fiche par fiche : 510 « probably trainer », 1 305 sans source, 174 réputation, 80 quêtes (hors échantillon déjà présent). Pas de crawl, pas d’import de masse, pas de wiki.gg, pas de Wowhead, pas de report Classic Era.

## Exemples

- **Blueprint: Fermenter** (Alchimie 140) — Rath’mael, Ruines de Lordaeron.
- **Blueprint: Cookie's Feast** (Cuisine 140) — Cookie, The Deadmines.
- **Blueprint: Repair Bot** (Ingénierie 140) — Sneed, The Deadmines (distinct du Reagent Bot officiel, niveau 20).
- **Blueprint: Anvil** (Forge 140) — Gilnid, The Deadmines.
- **Blueprint: Arcane Salvager** (Enchantement 140) — Rath’mael (Ruines de Lordaeron) et Charlga Razorflank (Razorfen Kraul). Existence officielle ; butin à confirmer.
- **Pattern: Stormrider's Leather Gloves** — Oggleflint (Ragefire Chasm), Mr. Smite (The Deadmines), Deviate Faerie Dragon (Wailing Caverns), Fel Steed / Shadow Charger (Shadowfang Keep).
- **Pattern: Defender's Leather Kilt** — Baron Aquanis et Twilight Lord Kelris (Blackfathom Deeps) ; Bloodmage Thalnos (Scarlet Monastery: Graveyard).
- **Vendeurs déjà trouvés** : Recipe: Smoked Sagefish et Sagefish Delight, Zerril Softbreeze, île de Zéphras (prix d’achat non indiqué).

## Fiches (brouillons, slugs inchangés)

- `forever-professions-blueprints` draft v9 : règles officielles, noms des correctifs, vendeurs à confirmer, **tableaux par zone** (55 recettes). Texte de page : « données extraites du client, à confirmer » — **sans** nommer de base tierce. URLs exactes des 55 fiches dans le CSV (limite pipeline : 20 sources par fiche ; les 7 guides métier sont cités comme index).
- `forever-camp-features` draft v5 : Tanning Rack 125, Journeyman Campfire Kit 90 (officiel).
- `forever-professions-camping` draft v13 : mêmes exceptions officielles.

## Tests

- Dry-run puis `revise` réel dans `test-tree-v34/` : OK, `committed` seulement dans l’arbre isolé. Origine v33 : blueprints published v8, camp-features published v4, camping published v12.
- `check-data` isolé : 110 entrées, 105 publiées, **0 erreur**.
- Aperçu local : 244 pages, bannière « ne pas déployer ».
- npm sur la copie v33 d’origine (non modifiée) : **179 pass / 0 fail / 3 skipped**.
- Captures 412 px : Chrome headless bloqué, non livrées.

## Déploiement

**Aucun.** Pas de tar wiki publié (le pipeline ne construit un site déployable qu’après approbation humaine). Pas de SIM_OK. Pas de litterbox. Voir `../recettes-pnj-deploy/RAPPORT_PRET_DEPLOIEMENT.md`.

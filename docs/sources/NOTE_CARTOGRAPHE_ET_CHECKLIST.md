# Propositions pour plus tard (NON construites)

## 1. Modèle de données compatible avec un futur Cartographe
La fiche `forever-exploration-named-places` contient un tableau dont la 1re colonne est un **identifiant stable** de lieu
(ex. `salle-des-thanes`, `cite-de-dalaran`, `profondeurs-des-saisons`) et une colonne « Coordonnées » à **« Non publiées »**.
Un futur Cartographe pourrait lire un fichier séparé, par ex. `data/places.json` :

```json
{"id": "cite-de-dalaran", "kind": "dungeon|raid|bg|port|subzone", "entryId": "forever-dungeon-city-of-dalaran",
 "zone": {"fr": "Montagnes d’Alterac", "en": "Alterac Mountains"},
 "coords": null, "coordsStatus": "non publiées", "coordsSource": null,
 "sources": ["bz-dungeons"], "verifiedAt": "2026-11-09"}
```
Règles proposées : `coords` reste `null` tant qu'aucune source officielle Blizzard ne publie de coordonnées ; une coordonnée
relevée en jeu exigerait le statut « vérifié en jeu » (date, personnage non nominatif) ; aucune coordonnée extraite du client
(Wowhead/Eternadex) ; aucune API de personnage promise. Rien de cela n'est implémenté.

## 2. Liste de lecture « Bibliothèque » en localStorage
Non construite (pas de nouveau script navigateur : une revue CSP serait nécessaire). Idée : un module ES externe
(`/wk-checklist.mjs`, même origine, aucun inline) stockant `{"wk.checklist.v1": ["id-livre", …]}` dans localStorage, sans
envoi réseau ni compte. Préalable : une source officielle listant des livres à collectionner (inexistante au 2026-11-09).

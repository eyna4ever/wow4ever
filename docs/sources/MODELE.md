# Wowkipedia V2.1 — Modèle de données (étape 02, proposition)

Date : 9 novembre 2026, 19 h 55 (heure de Paris). Statut : **proposition technique, rien n’a été appliqué, importé ni déployé.**

## 1. Ce qui existe déjà (à garder)

| Brique | Où | Rôle | Constat |
|---|---|---|---|
| Fiches `entries.json` | `pipeline/runtime/entries.json` (99 fiches : 97 publiées, 2 brouillons) | Source unique du wiki. `build-v2.mjs` la transforme en HTML statique (227 pages) | Champs : `id` stable (`^[a-z0-9][a-z0-9-]{2,99}$`), `title/description {fr,en}`, `category` (12 valeurs fermées), `subcategory` (libre), `sources[]` (`url, title, license, accessedAt, publishedAt, gameVersion, key, language`), `status`, `identityConfirmed`, `version`, `relations[]` (IDs sans type), `article`, `history[]`, `review`, `importMeta.fingerprint` |
| Validation et import | `lib/documentary.mjs`, `scripts/import.mjs`, `check-data.mjs`, `review.mjs` | Tout import repasse en `draft`, approbations importées supprimées, empreinte SHA-256, conflits ⇒ résolution humaine, quotas (100 fiches/lot, 2 Mo, 20 sources/fiche), verrou, reçus | `check-data` : 99 fiches, 0 erreur. Tests du pipeline : **162/165 OK, 3 ignorés, 0 échec** (copie isolée dans /tmp) |
| Schéma SQL historique | `pipeline/db/001_initial.sql` (PostgreSQL : `wiki_entries`, `wiki_sources`, `wiki_relations`, `wiki_revisions`) et `export-content-sqlite.mjs` | Export miroir des fiches | Pas utilisé en production (le site est statique) |
| Base communautaire | `community.sqlite3`, schéma 3, 15 tables (users, sessions, oauth, topics, posts…) | Forum et Discord | **Ne pas y mettre de données du jeu.** Séparation stricte |
| Fusions | `pipeline/data/merges.json` (2 fusions décidées par Mathieu le 01/11) | Doublons retirés vers une fiche cible | Modèle à réutiliser pour la déduplication |

**Principe** : pas de CMS parallèle. La publication reste `entries.json`, puis la revue humaine (`review.mjs`), puis `build-v2.mjs`, puis la release. Le nouveau modèle ajoute une **couche de staging factuelle** en amont, qui alimente les fiches sans changer le rendu.

## 2. Correspondance des nouveaux types d’entités avec les catégories existantes

Les 12 catégories du site ne changent pas (pas de nouvelle rubrique de menu, pas de reconstruction). Chaque nouveau type s’y rattache par `category` et `subcategory`, déjà libres et validées :

| Type (modèle) | `category` existante | `subcategory` proposée | Exemple déjà en ligne |
|---|---|---|---|
| quest / quest_chain | `quests` | `quete`, `suites-de-quetes` (déjà utilisé) | `forever-questline-lord-valthalak` |
| zone / subzone | `zones` | `region-annoncee`, `zone-de-depart-annoncee` (déjà utilisés), `sous-zone` | `forever-zone-mount-hyjal` |
| npc | `creatures` | `pnj` | — |
| creature | `creatures` | `famille-de-familiers-annoncee` (déjà utilisé), `rencontre` | `forever-creature-onyxia` |
| item | `items` | `legendaire-annonce`, `bijou-annonce`… | `forever-item-ladimore-heirloom-ring` |
| profession / recipe | `professions` | `metier`, `recettes` (déjà utilisé) | `forever-professions-blueprints` |
| camp (campement) | `professions` | `campement` (déjà utilisé) | `forever-professions-camping` |
| legacy_system / challenge / perk | `glossary` ou `quests` | `progression`, `legacy` (déjà utilisés) | `forever-progression-legacy`, `forever-glossary-legacy-points` |
| faction (réputation) | `pvp` (champs de bataille) ou `glossary` | `faction` | — |
| dungeon / raid | `instances` | `donjon-annonce`, `raid-annonce` (déjà utilisés) | `forever-raid-barrow-deeps` |
| book (livre en jeu) | `glossary` | `livre` | — |
| collection (ensembles, montures, jouets) | `items` | `collection` | — |
| event (correctif, événement, date) | `news` | `correctif`, `evenement` | `forever-news-hotfixes-nov5-6` |

Ajouter une **13e catégorie** (par exemple `npcs` ou `factions`) obligerait à modifier `categories` dans `documentary.mjs` et la navigation `build-v2.mjs`, et à ajouter des pages de hub. C’est **hors périmètre** tant que Mathieu ne l’a pas demandé.

## 3. Extensions rétrocompatibles des fiches

`normalizeEntry`/`validate` acceptent les clés inconnues. L’import à blanc d’une fiche pilote contenant `facts` et `sources[].verification` est passé (voir §6). Champs proposés :

```jsonc
{
  "sources": [{ "...champs actuels...": "",
    "verification": "officiel confirmé",        // un des 6 statuts (DATA_QUALITY.md)
    "proofType": "annonce officielle",           // annonce, forum bleu, page du jeu, compte support, constat en jeu, extraction client, base communautaire
    "build": null,                                // ex. "1.60.1.70862" si la source le donne
    "sourceId": "bz-24317865-fr"                  // clé du catalogue SOURCES.csv
  }],
  "facts": [{ "ref": "fact-taldramir-name", "status": "officiel confirmé", "inGameVerified": false }],
  "links": [{ "type": "located_in", "to": "forever-zone-mount-hyjal" }]   // relations typées ; relations[] reste pour la compatibilité
}
```

Règles à ajouter dans `validate()` (étape 03, en test) :
- `verification` ∈ 6 statuts.
- `status` ∈ {`verified`, `published`} ⇒ au moins une source `officiel confirmé` ou `vérifié en jeu`.
- Hôte de la source dans une **liste autorisée** (`news.blizzard.com`, `worldofwarcraft.blizzard.com`, `us|eu.forums.blizzard.com`, `x.com/Blizzard*`, `www.blizzard.com/legal`).
- Tout autre hôte force `verification ∈ {communautaire, extrait client, à confirmer}` et interdit la publication.

## 4. Couche de staging relationnelle

Fichier : `exemples/002_modele_entites.sqlite.sql`. C’est une base SQLite de travail, **distincte** de `community.sqlite3`, jamais déployée.

```
source(id, url, publisher, proof_type, tier, published_at, verified_at, http_status, build, rights, import_allowed, forever_specific)
entity(id, type, name_fr, name_en, wiki_entry_id → entries.json, game_ids, status, created_at, updated_at)
fact(id, entity_id → entity, property, value_json, status, build, valid_from, valid_to, superseded_by → fact, in_game_verified, fingerprint UNIQUE)
fact_source(fact_id → fact, source_id → source, quote ≤ 400 car., locator)        -- provenance, ≥ 1 par fait
relation(from_id, to_id, type ∈ 18 types, fact_id → fact)                          -- graphe typé et sourcé
quarantine(id, payload_json, source_id, reason, decided_by, decided_at, decision)
import_run(id, started_at, batch_sha256, dry_run, inserted, duplicates, conflicts, invalid, quarantined)
VIEW fact_publishable : statut officiel ou en jeu, non périmé, avec au moins une source de tier officiel ou en jeu
```

Types de relations : `located_in`, `part_of_chain`, `next_quest`, `starts_at`, `ends_at`, `drops`, `rewards`, `sold_by`, `taught_by`, `requires`, `crafted_by`, `member_of_faction`, `reputation_with`, `legacy_challenge_for`, `attunement_for`, `part_of_collection`, `mentions`, `event_affects`.

**Test exécuté** (SQLite en mémoire, `preuves/schema_sqlite_test.txt`) :
- Schéma créé : 7 tables et 1 vue.
- 9 sources, 7 faits, 13 liens de provenance et 2 éléments en quarantaine chargés depuis `exemples/faits-pilotes.json`.
- La réinsertion d’un fait identique est **refusée** (empreinte unique, donc import idempotent).
- Un statut hors liste est **refusé**.
- Un fait étiqueté par erreur « officiel confirmé » mais sourcé seulement par Eternadex est **exclu** de `fact_publishable`.

## 5. Identifiants stables

- Une entité qui a déjà une fiche garde **l’`id` de la fiche** (`forever-raid-barrow-deeps`…), pour ne casser ni URL ni lien entrant.
- Nouvelle entité : `forever-<type>-<slug-en-ascii>` (par exemple `forever-item-taldramir-whispering-wood`). Il est figé à la création et n’est jamais recalculé depuis un titre traduit.
- Les identifiants du jeu (questId, npcId, itemId) vont dans `game_ids`, seulement si une source **autorisée** les fournit. **Ils ne servent jamais de clé primaire.**
- Fusion : on reprend le modèle `merges.json` (`retired` vers `into`, avec date et décision de Mathieu). L’ancien ID reste réservé, et l’ancienne URL devient une page de renvoi, comme pour les 2 pages podcast.

## 6. Preuve de compatibilité (import à blanc isolé)

`node scripts/import.mjs <lot> --dry-run --runtime-dir runtime`, lancé dans une **copie** du pipeline sous `/tmp/wk-import-test` (le fichier `entries.json` a la même empreinte avant et après) :

| Fiche testée | Attendu | Obtenu |
|---|---|---|
| `forever-item-taldramir-whispering-wood` (nouvelle, avec `facts` et `verification`) | insérée en brouillon | **inserted** |
| copie exacte de `forever-raid-barrow-deeps` | doublon | **duplicates** |
| `forever-raid-barrow-deeps` modifiée (v9) | conflit et arbitrage humain | **conflicts** (code de sortie 2) |
| fiche test sourcée **uniquement par Eternadex** | doit être bloquée | **inserted** ⇒ **faille actuelle** : `validate()` n’a ni liste d’hôtes ni statut de vérification. La correction est prévue au §3 et doit précéder tout lot 1 |

Rapport complet : `preuves/import_dry_run_report.json`.

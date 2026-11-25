# Wowkipedia V2.1 — Plan d’import (étape 02 : plan seulement, aucun import réel)

Le circuit réutilise `lib/documentary.mjs`, `import.mjs`, `review.mjs` et `check-data.mjs`. Le seul ajout est la base de staging de `MODELE.md` §4. Chaque étape produit un reçu JSON (comme les rapports actuels de `import.mjs`).

```
 sources autorisées ──► 0. COLLECTE ──► 1. STAGING ──► 2. NORMALISATION ──► 3. DÉDUPLICATION ──► 4. VALIDATION ──┬─► 6. REVUE HUMAINE ──► 7. PUBLICATION
 (liste SOURCES.csv)    (manuelle,      (lot JSON      (NFC, slugs,         (empreinte,           (règles bloquantes)  │   (review.mjs, Mathieu)   (build-v2 → release
                         lecture        horodaté,      dates ISO, noms      ID stable, fusion)                         │                             → update-vNN.sh)
                         seule)         sha256)        officiels FR/EN)                                                └─► 5. QUARANTAINE (ne sort que par décision écrite)
```

## 0. Collecte
- Les seules sources autorisées sont celles du catalogue `SOURCES.csv` dont le tier est **officiel**. Les constats en jeu de Mathieu ou de testeurs nommés sont à ajouter plus tard, avec capture et date.
- Méthode : lecture d’une page précise, une à la fois, comme un navigateur.
  - **Pas d’aspiration ni de crawler** sur des sites tiers.
  - Pas de lecture des fichiers client par Wowkipedia : la clause « Data Mining » de l’EULA Blizzard l’interdit.
- Chaque source collectée reçoit un `id`, une `url`, `verified_at`, `http_status` et des `rights`. Les citations de preuve sont limitées à **400 caractères**.

## 1. Staging
- Un lot = un fichier JSON local (`data/batches/<lot>-<date>.json`), avec son SHA-256 et une entrée `import_run`.
- Plafonds existants (`limits`) : 100 fiches par lot, 2 Mo, 20 sources par fiche, 10 000 fiches au total.
- Pilote recommandé : **≤ 20 fiches**.

## 2. Normalisation
- `normalizeEntry` (NFC, trim, URL canonique, dédoublonnage des sources) existe déjà.
- Ajouts prévus :
  - dates ISO 8601 avec fuseau, stockées en UTC et affichées en heure de Paris ;
  - noms FR et EN repris **tels que Blizzard les publie** (ex. « profondeurs des Saisons » = *Barrow Deeps*, « Taldramir, le bois des murmures ») ;
  - slugs ASCII.

## 3. Déduplication
- **Même ID, même contenu** : `duplicates`, ignoré. C’est l’idempotence ; la ré-exécution d’un lot ne change rien.
- **Même ID, contenu différent** : `conflicts`, avec un code de sortie 2 et une **résolution humaine obligatoire**.
- **Faits** : l’empreinte `sha256(entity_id | property | valeur canonique)` est UNIQUE. Une même valeur venue de plusieurs sources donne **un seul fait et plusieurs liens `fact_source`**.
- **Entités** : on rapproche sur le nom officiel FR/EN, le type et la zone. Une proposition de fusion va dans `merges.json` et n’est **jamais automatique**.
- **Valeurs contradictoires** (ex. Eternadex affiche 5 167 puis 5 165 quêtes) : les deux vont en quarantaine, et rien n’est publié.

## 4. Validation (règles bloquantes)
1. Les validations actuelles de `validate()` (bilinguisme, ID, dates, licence, historique, revue).
2. **Nouveau** : `sources[].verification` doit être l’un des 6 statuts.
3. **Nouveau** : une fiche `verified` ou `published` doit avoir au moins une source `officiel confirmé` ou `vérifié en jeu`. La faille constatée au test à blanc (une fiche sourcée par Eternadex a été acceptée) doit être corrigée **avant le lot 1**.
4. **Nouveau** : l’hôte de chaque source doit figurer dans la liste autorisée. Sinon, la source est forcée à `communautaire` ou `extrait client` et la fiche devient non publiable.
5. **Nouveau** : Forever uniquement.
   - Une source de tier `officiel` mais `forever_specific = 0` (les 16 pages de races génériques) ne peut étayer que du **lore**, jamais une mécanique.
   - Le vocabulaire Classic, Retail, SoD ou Hardcore n’est accepté que dans une citation d’une source Forever officielle, ou pour un nom de mode Forever (préréglage Classic, ensemble de règles Hardcore).
6. **Nouveau** : une annonce datée (ex. l’équilibrage du 10/11) porte `expiresReview`. Passé cette date, elle est signalée pour passer à `obsolète` ou être remplacée.
7. Le contrôle de fraîcheur actuel (`staleDays` = 180) est **ramené à 30 jours** pour les faits de type `event`.

## 5. Quarantaine
- On y place automatiquement :
  - toute donnée sans source autorisée ;
  - tout `extrait client` ;
  - tout `communautaire` ;
  - toute contradiction ;
  - tout chiffre global (nombre de quêtes, factions, objets) qui n’est pas publié par Blizzard ;
  - tout contenu signalé « complément communautaire » (refus de Mathieu, t329u).
- On n’en sort que par une **décision écrite**, avec auteur, date et motif : `rejeté`, `à confirmer` (reste non publiable) ou `libéré` (une source officielle ou un constat en jeu a été trouvé).

## 6. Revue humaine et 7. publication (inchangées)
- `review.mjs submit|approve|publish` avec `--confirm-human-review --confirm-identity --confirm-rights --confirm-translations`, puis `--confirm-publish`. L’approbation est liée au `contentDigest`.
- Publication : `build-v2.mjs`, puis un tarball signé SHA-256 en release, puis `update-vNN.sh` avec sauvegarde et rollback automatique (procédure prouvée à l’étape 01).
- Le site reste **noindex, sans sitemap**.

## Ce qui ne doit JAMAIS être importé à l’aveugle
- Les bases Eternadex et Wowhead : données, listes, dumps, tooltips, scripts d’intégration. Il n’y a aucune licence, et Wowhead interdit explicitement robots et data-mining.
- Tout fichier client ou datamining, y compris un fichier « déjà extrait » par un tiers.
- Les fichiers d’addon de joueurs (ex. `EternaDexMeter.lua`) : ils peuvent contenir des données personnelles et n’ont pas de droits établis.
- Les textes Blizzard copiés en entier, ainsi que les images et vidéos Blizzard sans mention © (Legal FAQ).
- Les chiffres « 5167 quêtes » et « 48 factions » (Eternadex, non officiels) ; ils ne doivent pas non plus servir d’objectifs de couverture.
- Les pages warcraft.wiki.gg : leur licence CC BY-SA imposerait la même licence aux pages dérivées, et elles couvrent Retail et Classic. Il faut une décision de Mathieu.
- Toute donnée tirée de la base communautaire du forum (données personnelles).

## Dry-run et tests requis à l’étape 03 (en environnement de test, pas en production)
1. `check-data.mjs` sans erreur.
2. Tests du pipeline au vert, plus les nouveaux tests des règles 2 à 7.
3. `import.mjs --dry-run` sur le lot 1 : 0 `invalid`, 0 `conflicts` non arbitré ; la fiche test Eternadex doit être **rejetée**.
4. Une deuxième exécution du même lot ne produit **que des `duplicates`** (idempotence).
5. Le build en test donne le même nombre de pages qu’avant, plus les seules pages du lot, et la page Discord reste identique.

# VALIDATOR_FIX — politique de sources (étape 03, partie A)

Environnement : arbre de test isolé `etape-03/test-tree` (copie de 17e037542b8f, git local, commits `dba183e`, `af5d2d0`). Rien n'a été poussé ni déployé.

## Le cas qui échouait (étape 02)
`etape-02/preuves/import_dry_run_batch.json`, enregistrement `q-eternadex-quest-count-test` :
- seule source : `https://eternadex.com/en/datenbank/`, licence « Aucune licence publiée » ;
- verification « extrait client ».

L'ancien `merge()` l'**insérait** sans aucune trace. Rien n'empêchait non plus un statut « officiel confirmé », et rien ne s'affichait à l'écran.

## Ce qui change
1. Nouveau module `pipeline/lib/source-policy.mjs` (fonctions pures). `classifySource(url)` range chaque source dans un niveau :
   - `officiel` : news.blizzard.com, worldofwarcraft.blizzard.com, us/eu.forums.blizzard.com, (www.)blizzard.com, support Blizzard, comptes X Blizzard/Warcraft. Il faut du https et un hôte exact (`news.blizzard.com.evil.example` est refusé).
   - `extrait_client` : eternadex.com, wowhead.com, wago.tools, wow.tools, wowdb.com.
   - `communautaire` : toute autre source.
   - `refuse` : tout hôte `*.wiki.gg`, dont warcraft.wiki.gg (décision du 09/11/2026).
2. `validate()` (documentary.mjs) ajoute `policyErrors()`. Une modification directe de entries.json ne peut donc plus contourner la règle. Sont refusés :
   - une source wiki.gg ;
   - « officiel confirmé » ou « vérifié en jeu » posé sur une source non officielle ;
   - une fiche marquée officielle alors qu'aucune de ses sources n'est officielle ;
   - un fait (`facts[]`) ou un bloc d'article qui se dit officiel sans source officielle **propre** ;
   - un élément de la colonne « Confirmé par les sources officielles » qui ne cite aucune source officielle ;
   - « vérifié en jeu » sans proofType, observedBy et build.
3. `merge()` (import) passe par `applySourcePolicy()` :
   - une fiche avec une source wiki.gg va en **quarantaine** (`report.quarantined`, rien n'est inséré, code de sortie 2) ;
   - les sources, faits, blocs et fiches non officiels sont **rétrogradés** en « à confirmer » (`report.downgraded`) ;
   - un élément « confirmé » non officiel passe dans « à confirmer » ;
   - rien n'est jamais promu. Le comportement reste idempotent : l'empreinte est calculée sur l'entrée brute, et une ré-importation donne des doublons.
4. Affichage, avec les classes CSS existantes (`status-pill is-draft`), sans style en ligne et sans modifier v2.css (le hash V30CSS reste intact) :
   - la pastille « À confirmer » (FR) ou « Unconfirmed — to be confirmed » (EN) apparaît :
     - dans le statut de la fiche (infocard et ligne méta) ;
     - à côté de chaque citation dont **toutes** les sources sont non officielles ;
     - dans « En bref » ;
     - sur les cartes des listes de rubrique ;
   - le compteur de sources est honnête, par exemple « 0 source officielle + 1 source non officielle » au lieu de « N sources officielles » ;
   - chaque source non officielle porte « Source non officielle — à confirmer » ;
   - la note de droits n'annonce plus « Sources officielles Blizzard » quand aucune source officielle n'existe ;
   - le DTO public et search-index.json portent `verification: « à confirmer »` et le niveau de chaque source **uniquement** quand ce n'est pas officiel. Les 97 fiches existantes, toutes officielles, se rendent donc octet pour octet comme en production : vérifié par le test v16 et par le build avant import.

## Les nouveaux tests (`pipeline/tests/v21-source-policy.test.mjs`) — 5 sur 5 OK
1. **Fiche sourcée uniquement par Eternadex** :
   - `validate()` refuse « officiel confirmé » ;
   - l'import l'insère en brouillon, rétrogradée en « à confirmer » (source, fiche et fait « vérifié en jeu ») ;
   - une fois publiée, la page FR/EN affiche la pastille, « 0 source officielle + 1 source non officielle » et « Source non officielle — à confirmer », sans jamais afficher « officiel confirmé » ni la note « Sources officielles Blizzard » ;
   - la liste de rubrique et l'index de recherche portent la mention.
2. **URL wiki.gg** : niveau `refuse`. L'import met en quarantaine la fiche, même si elle est mêlée à une source Blizzard. `validate()` la rejette et elle n'est jamais publique.
3. **Fiche sourcée uniquement par Blizzard** : elle reste officielle, sans rétrogradation, sans pastille, avec « 1 source officielle ». Le classement des hôtes est vérifié, y compris le refus de http://, d'un faux domaine, de wowhead et d'un compte X non Blizzard.
4. **Mélange officiel + Eternadex** :
   - la fiche reste « officiel confirmé », mais le fait, le bloc et l'élément « confirmé » qui ne citent qu'Eternadex sont rétrogradés ;
   - à l'écran, seule la phrase Eternadex porte « À confirmer », et la phrase officielle n'en porte pas ;
   - le compteur affiche « 1 source officielle + 1 source non officielle ».
5. **Le cas qui échouait à l'étape 02** (fixture copiée) : il est maintenant rétrogradé en « à confirmer » et signalé dans `downgraded`. Une seconde application ne change rien (idempotent).

Preuves : `preuves/validator_regression_tests.txt`, `preuves/demo_a_confirmer_fr.html` / `_en.html` (rendu de démonstration jamais publié) et les captures Android `preuves/captures-android/*demo*.png`.
Diff : `patches/01-validateur-politique-sources.diff` (code) et `patches/02-tests-validateur-et-lot1.diff` (tests).

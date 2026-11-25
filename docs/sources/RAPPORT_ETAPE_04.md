# Rapport — étape 04, lot 2 « monde » (ENVIRONNEMENT DE TEST ISOLÉ)

Date : 2026-11-09, travail exécuté vers 22 h 00–22 h 20 (heure de Paris). Instruction : « Vas-y » (t340u).
**Décision : NO-GO** pour la production tant que Mathieu n'a pas relu les fiches. Rien n'a été déployé.

## 1. Ce qui a été fait
- Nouvel arbre `etape-04/test-tree` (copie de v32, commit 75e53da), branche locale sans remote (voir TEST_TREE_POINTER.md).
- Pipeline existant réutilisé (import.mjs → review.mjs revise/submit/approve/publish → build-v2.mjs). Aucun nouveau script navigateur, aucune nouvelle rubrique de menu. 4 sous-catégories ajoutées dans les catégories existantes : `quests/reputations`, `zones/lieux-et-acces`, `creatures/notes-officielles`, `items/itemisation`.
- Les fiches existantes ont été vérifiées d'abord. Aucun doublon : les 9 fiches donjon déjà publiées ont été **mises à jour** (review.mjs revise, historique conservé avec une note de correction) au lieu d'être recréées. Gelkis/Magram n'a pas été ajouté, car c'est déjà couvert par le lot 1.
- **Approbations de TEST** : l'acteur est « GrokBot — TEST ISOLÉ étape 04 (CE N'EST PAS une validation humaine de Mathieu) » pour les étapes submit, approve et publish. Les notes de ces 3 étapes précisent « CE N'EST PAS une validation humaine de Mathieu ; aucune mise en production ». Dans le wiki de test, la pastille « Publié · validé » vient de cette approbation de test, **pas** d'une validation de Mathieu.

## 2. Comptes réels
| | Nombre |
|---|---|
| Fiches créées | **4** (8 pages FR/EN) |
| Fiches modifiées | **9** (18 pages FR/EN ; URL inchangées) |
| Parties rejetées / non créées | **1** partie complète (C Bibliothèque) + éléments non publiés dans A, D, E, F (§4) |
| Total wiki de test | 110 fiches, 108 publiées (v32 : 106 / 104) ; 249 pages (v32 : 241) |

Détail : LISTE_FICHES.csv.

| Partie | ID | Slug FR / EN | Source principale | Statut |
|---|---|---|---|---|
| A Réputations | forever-reputations-confirmed | reputations-confirmees / confirmed-reputations | Blizzard, donjons (20/10/2026) + notes de dév. 6 et 9 + héritage | publiée en TEST |
| D Exploration | forever-exploration-named-places | lieux-nommes-acces / named-places-access | Blizzard, donjons + raids (20/10/2026), lancement, « Photos retrouvées » | publiée en TEST |
| E Bestiaire | forever-creatures-official-notes | creatures-notes-officielles / creatures-official-notes | Correctifs des 5–6/11/2026 + notes de dév. 1/5/9 + « Au cœur de » | publiée en TEST |
| F Objets | forever-items-loot-appearances | butin-apparences-itemisation / loot-appearances-itemization | « Au cœur de » (13/09/2026), camp, notes de dév. 1/4/5 | publiée en TEST |
| B Donjons (×9) | forever-dungeon-{hall-of-thanes, ruins-of-lordaeron, excavation-site, city-of-dalaran, drowned-city, kroldok-stronghold, alcaz-prison, blackmaw-hold, shapers-terrace} | slugs v32 inchangés | Blizzard, donjons (20/10/2026) + « L'avenir de » + notes/correctifs | modifiées, publiées en TEST |

## 3. Sources (23 URL, toutes officielles Blizzard)
Toutes viennent de news.blizzard.com (FR et EN) ou des forums officiels us/eu.forums.blizzard.com, avec les messages bleus de Kaivax. Elles ont été consultées le 2026-11-09 et sont citées sous « Droits réservés Blizzard ; synthèse originale, courtes citations, © Blizzard ». Chaque source porte une date, une langue et une licence. Aucun numéro de build n'a été publié, donc aucun n'est indiqué. Les pages brutes (83 news et les sujets de forum) sont dans `sources-brutes/`.
- Aucune URL vers wiki.gg, Eternadex ou Wowhead (vérifié par test).
- Les chiffres « 5167 quêtes » et « 48 factions » ne sont pas utilisés : ils restent en quarantaine.
- Aucun mélange Classic/Retail.
- Deux fiches mentionnent par leur nom des « bases extraites du client (par ex. Eternadex, Wowhead) », uniquement pour préciser qu'elles ne sont pas reprises. Mathieu peut demander de retirer ces noms (question 6).

## 4. Non fait, et pourquoi
- **C Bibliothèque : non créée.** Blizzard n'a publié aucune source sur des livres à collectionner. La seule mention est la quête « Greater Friend of the Library » / l'arc du Truthseeker niveau 40, dans les notes bêta du 8 octobre. C'est insuffisant pour une page indexable non vide. La checklist localStorage est proposée pour plus tard (NOTE_CARTOGRAPHE_ET_CHECKLIST.md) et n'est pas construite.
- **Coordonnées : non publiées par Blizzard.** La colonne affiche « Non publiées » et les identifiants de lieu sont stables. Le Cartographe n'est pas construit et aucune API de personnage n'est promise.
- **Réputations :** la liste des factions, les vendeurs, les récompenses et les gains par action ne sont pas publiés. Les camps des Sombrelances sont cités, mais pas présentés comme des réputations.
- **Bestiaire / Objets :** les listes de boss, les tables de butin, les **taux de drop** et les statistiques objet par objet ne sont pas publiés. Il n'y a aucun taux dans les fiches. Les noms FR des créatures et des quêtes n'ont pas de traduction officielle : les noms anglais sont conservés.
- Hors périmètre (étape 05) : champs de bataille JcJ, calendrier, collections, économie, lore communautaire, favoris et signalements. Exception : une ligne du tableau des réputations parle des réputations de champ de bataille (4 points d'héritage) (question 5).
- update-v33.sh n'a pas été produit (pas demandé avant ce rapport).

## 5. Tests (preuves/)
| Test | Résultat |
|---|---|
| npm test, état v32 tel que commité (00_…) | 175 tests : 171 réussis, **1 échec**, 3 ignorés. **Constat :** la garde v16 était figée sur le wiki v31 et excluait le lot 1. Elle échoue depuis que site/wiki est passé en v32. Aucun impact en production : ces tests ne tournent pas sur le serveur, et les 47 tests communauté v32 passent. |
| npm test après alignement de la garde sur v32, sans lot 2 (01_…) | 175 tests : 172 réussis, 0 échec, 3 ignorés |
| Dry-import (03_…) | 4 insérées, 0 invalide, 0 conflit ; runtime inchangé (sha vérifié) |
| Import réel (04_…) puis réimport (05_…) | 4 insérées ; puis 0 insérée, 4 doublons, `unchanged: true`, sha identique → **idempotent** |
| Révisions en dry-run, puis réelles (06_, 07_) | 9 sur 9 sans erreur |
| check-data, intégrité référentielle (08_) | 110 fiches, 108 publiées, 0 erreur, 0 périmée |
| Build (09_) | 108 fiches, 249 pages, 2 redirections de fusion |
| npm test avec lot 2 (10_) | **181 tests : 178 réussis, 0 échec**, 3 ignorés. Inclut le nouveau tests/v22-lot2.test.mjs (6 tests : sources officielles uniquement, pas de données tierces, slugs stables, approbations de test ≠ Mathieu, historique conservé, a11y, pas de coordonnées, pas de sitemap). |
| Non-régression v32 → lot 2 (11_) | Sur 436 fichiers : 194 identiques à l'octet ; 156 ne diffèrent que par les compteurs du menu ; 52 seulement par le rail « même catégorie / liées » ; 33 ont un contenu modifié, à savoir les 18 pages des donjons révisés + 10 index de catégorie + 2 accueils FR/EN + la racine + 2 index A–Z (ajout des nouvelles fiches et des « mises à jour récentes ») ; 0 supprimé ; 8 pages nouvelles (+ PROPOSITION-V2-LOCALE.txt, exclu du paquet) ; search-index.json passe de 104 à 108 entrées (+4, 9 modifiées) |
| Page Discord (12_) | FR/EN identiques **hors compteurs wk-count** |
| Android / a11y (11_ + v22) | 0 page HTML en défaut sur viewport, lang, noindex, h1 unique, sauts de titres, légendes de tableaux, script ou style en ligne ; aucun sitemap |
| Captures 412 px (captures-412px/) | 2 sur 4 nouvelles pages FR : lieux-nommes-acces et butin-apparences-itemisation. Les 3 autres (réputations, créatures, Dalaran) ont échoué : Chrome headless a dépassé le délai (code 124), deux essais. |
| Communauté sur site/wiki v32 (14_) | **47/47 OK** |
| Communauté avec le wiki lot 2, copie temporaire supprimée ensuite (15_) | 5 gardes figées cassent, comme attendu : test_shared_header et test_v2_stylesheet_and_notice (241 → 249 pages), test_wiki_content_unchanged_since_v8 (100 → 108 nouvelles pages), test_wiki_preservation (liste de fichiers de référence), test_forum_uses_wiki_v2_design (compteur du menu 5 → 6 dans l'en-tête du forum). **Non corrigées** : à mettre à jour seulement lors d'un futur paquet v33, après validation de Mathieu. |

Adaptations de tests faites **uniquement dans l'arbre de test** : v16-format (garde de rendu : lot 2 exclu ; compteurs et rail normalisés une fois le lot 2 publié), articles, v10-drafts (comptes + lot2NewPublished ; pour les 9 donjons, l'approbation est celle de TEST et l'approbation antérieure de Mathieu reste dans l'historique), v15-fusion (lot 2 exclu), v16 check-data (compte).

## 6. Lots d'import (chemin de production proposé, non exécuté)
- `lot2/lot2.entries.json` : 4 brouillons, sans review.
- `lot2/revisions/<id>.json` : 9 révisions.
- `lot2/build_lot2.py` : générateur.

En production, il faudrait importer ces brouillons, appliquer `review.mjs revise`, puis faire approuver **par Mathieu** (son propre acteur). L'état « approuvé en test » de l'arbre de test ne doit **pas** être repris tel quel.

## 7. Questions pour Mathieu
1. Garder les noms anglais (créatures, quêtes, objets) quand aucune traduction FR officielle n'existe ?
2. Inclure les notes datées de la bêta (balisées « bêta », avec leur date) ?
3. Accepter la réécriture en article des 9 fiches donjon publiées (URL inchangées) ?
4. Valider les 4 sous-catégories (reputations, lieux-et-acces, notes-officielles, itemisation) ?
5. Garder dans la fiche Réputations la ligne « réputations de champ de bataille » ou la déplacer à l'étape 05 ?
6. Retirer les noms « Eternadex / Wowhead » des avertissements dans les fiches ?
7. Lancer ensuite un paquet v33 (update-v33.sh, avec mise à jour des 5 gardes communauté) après sa relecture ?

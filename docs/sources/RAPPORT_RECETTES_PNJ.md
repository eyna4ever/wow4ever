# Rapport de recherche : recettes, PNJ vendeurs et sources de butin

**Date :** 12 novembre 2026 (Europe/Paris).  
**Périmètre :** t342u (listes de recettes et PNJ vendeurs, zone) étendu par t343u (toutes les recettes de tous les métiers ; pour les lootables : monstre, coffre/objet, zone, taux seulement s’il est sourcé).  
**Statut :** recherche et brouillons uniquement. **Aucun déploiement**, aucune publication, aucune approbation. Les dry-run de validation ont été faits dans une copie isolée (`recettes-pnj/test-validate/`), acteur clairement indiqué comme **n’étant pas une validation de Mathieu**. Les arbres `etape-03*`, `etape-04*` et `etape-04-deploy*` n’ont pas été modifiés.

---

## 1. Inventaire des fiches déjà en ligne (et lacunes)

D’après le runtime v33 local (`etape-04-deploy/work`, lecture seule, commit de base `266a8a8`) :

| Fiche | URL (inchangées) | Ce qui est déjà dit | Ce qui manque |
|---|---|---|---|
| **forever-professions-blueprints** (v8, principale) | `/fr/metiers/recettes-et-plans-avances/` · `/en/professions/recipes-and-advanced-blueprints/` | « plus de 600 nouvelles recettes » ; premier objet à 20 auprès de PNJ / maîtres ; plans avancés sur des boss de donjon ; onglet Métiers | Liste des recettes ; boss ; taux ; vendeurs ; zones ; prix. Pending actuel : « non publiés ». |
| **forever-camp-features** (v4) | `/fr/…/campement-fonctionnalites/` | Tableau officiel des 11 exemples (21/10) ; obtention 20 / 140+ ; feux améliorés, laboratoire, râteliers | Exceptions officielles postérieures (Tanning Rack 125, Journeyman Campfire Kit 90) **absentes** ; liste complète et coûts toujours non publiés. |
| **forever-professions-camping** | — | Mêmes règles d’apprentissage | Liste complète des objets de camp ; exceptions de novembre. |
| **article-forever-campfire** | — | Article campement + exemples nommés | PNJ, listes, coûts. |
| **forever-professions-overview** | — | 2 métiers sur 9, rangs, formateurs « dans les capitales et le monde » (non nommés) ; refuse une calculette de matériaux sur données client | Recettes, composants, lieux exacts des formateurs, seuils de rang. |
| **guide-debutant-equipement-metiers** | — | Formateurs dans les zones de départ ou les capitales ; demander à un garde ; touche K | Aucun PNJ nommé, aucun prix, aucune liste. |

**Décision de rédaction :** mettre à jour les fiches existantes (pas de fiche doublon). Brouillons livrés pour **blueprints** (principale) et **camp-features** (correctifs). Les autres peuvent recevoir plus tard un simple renvoi ; leur pending est déjà juste sur le fond.

---

## 2. Réponse officielle à « quel PNJ, quelle zone, quel monstre »

**Blizzard n’a publié, dans les sources officielles consultées le 12 novembre 2026, aucun PNJ vendeur de recette nommé, aucun prix d’achat de recette, aucune coordonnée de formateur, aucun boss ou coffre nommé pour un plan précis, et aucun taux de drop.**

Ce qui est **officiellement confirmé**, ce sont des *règles* d’obtention et un ensemble de *noms* (objets / recettes) sans source d’obtention détaillée.

Sources officielles (news.blizzard.com), consultées le 12/11/2026 :

- Article campement 24301516 FR/EN (21/10/2026) : tableau de 11 exemples ; à 20, quêtes des zones de départ ou achat chez un maître de métier ; à 140 ou plus, butin de donjons et de raids ; feux améliorés (5 ou 10) ; laboratoires et râteliers.
- Deep Dive 24303313 FR/EN (13/09/2026) : plus de 600 nouvelles recettes ; « Blueprint recipes that drop from specific dungeon bosses » (boss non nommés) ; trois objets par métier, niveaux différents ; laboratoire d’alchimie ; chevalet / râtelier de tannage.
- Correctifs 24315281 EN, titre « November 11, 2026 », même article pour les 5–11 novembre (URL utilisée : `https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-11-2026`). **Page FR : 404 le 12/11.** D’où : pas de noms FR officiels pour Journeyman Campfire Kit, Arcane Salvager, Fishing Rack, Elixir of Holy Power, Tanning Rack (le nom EN est dans le correctif ; le FR « râtelier / chevalet de tannage » vient des articles antérieurs).
- Héritage 24307383 : ACA et Transports logistiques Durotar = « a major source of new tradeskill activities », **sans liste**.

Correctifs métiers utiles (texte officiel, voir `sources-brutes/bz-24315281-en-PROFESSIONS.txt`) :

- 5/11 : marchands de fournitures de métier sur l’île de Zéphras (non nommés) ; ils ne vendaient pas les sacs d’apprenti. Mild Spices : 1 c de revente (était 2 c).
- 6/11 : Tanning Rack, compétence **125** (était 140) ; gains de compétence baissés de 15.
- 9/11 : Waylaid Crates et Craftsman’s Writs tombent dans les donjons (le texte **ne dit pas** que ce sont des recettes).
- 10/11 : Journeyman Campfire Kit, Cuisine **90** pour le placer (était 140), égal à l’exigence de la recette ; Arcane Salvager : Runed Golden Rod ; Fishing Racks parfois sans leurres ; Recipe: Elixir of Greater Firepower renommé Recipe: Elixir of Holy Power.
- 11/11 : cinq sacs de couture, matériaux et taille.

**Exceptions officielles à la règle « 140 ou plus » :** Tanning Rack 125, Journeyman Campfire Kit 90. La source d’obtention de ces objets n’est **pas** republicée.

---

## 3. Comptages

### 3.1 Dans `RECETTES_PNJ.csv` (65 lignes de données)

| Catégorie | Nombre | Commentaire |
|---|---|---|
| **Officiel confirmé** (existence, règle, prérequis ou nom) | **28** | Dont 11 objets du tableau campement, objets avancés nommés, correctifs, et 4 lignes de contexte (600+, ACA, marchands Zéphras, Waylaid). |
| dont **vendeur officiel nommé** | **0** | — |
| dont **source de butin officielle nommée** (monstre / coffre + zone pour une recette précise) | **0** | — |
| dont **taux de drop officiel** | **0** | — |
| dont **prix d’achat officiel d’une recette** | **0** | Iron Grenades 1 a 25 c et Mild Spices 1 c sont des prix de *vente / revente d’objets fabriqués ou de consommables*, pas de recettes. |
| **À confirmer (données extraites du client), consultation ciblée** | **37** | Voir § 4. Pas un import de masse. |
| **Introuvable dans une source officielle Forever** | la **liste complète** de tous les métiers, tous les PNJ, toutes les zones, tous les boss/coffres, tous les taux, tous les prix, tous les formateurs nommés | Confirmé comme non publié, pas comme « inexistant en jeu ». |

### 3.2 Volume total estimé (données client, **à confirmer**, une seule page d’ensemble consultée)

Sur `https://eternadex.com/en/rezepte/` au 12/11/2026 (extrait client, **pas un chiffre officiel Blizzard**) : **2 126** recettes listées dans les fichiers du jeu, dont 900 avec un nouvel identifiant Forever.

Répartition des sources **telle qu’affichée sur cette page** (à confirmer, ne pas traiter comme fait officiel) :

| Source affichée | Nombre | Conséquence pour cette recherche |
|---|---|---|
| Vendor | 2 | Consultées (les deux, Cuisine, même PNJ). |
| Drop | 55 | 5 fiches item ouvertes (consultation ciblée). **Il en reste ~50.** |
| Quest | 80 | Guide cuisine + 3 pages de quête, pas les 80. |
| Reputation | 174 | **Aucune** fiche ouverte (volume déjà trop large pour une consultation ciblée). |
| « probably from the trainer (not confirmed) » | 510 | Page formateurs : les emplacements Forever « aren’t confirmed yet ». |
| Source non enregistrée | 1 305 | Inutile à « crawler » : pas de source à reporter. |
| **Total** | **2 126** | Un passage fiche par fiche = **collecte de masse, refusée**. |

**Métier (même page, à confirmer) :** Alchemy 179, Blacksmithing 420, Enchanting 223, Engineering 241, Leatherworking 508, Tailoring 401, Cooking 123, First Aid 31. Pas de décompte publié pour les métiers de récolte seuls (Herboristerie, Minage, Dépeçage) sur cette vue « recettes ».

---

## 4. Consultation ciblée « à confirmer » — ce qui a été ouvert, et ce qui ne l’a pas été

Pages ouvertes (URLs exactes et date : `sources-brutes/CONSULTATION.tsv`) : vue d’ensemble des recettes, page formateurs, guide cuisine (build 1.60.1.70862, 7/11/2026), 2 recettes vendeur, 1 PNJ, 5 plans/patrons de butin, 3 quêtes. **Pas de crawl, pas d’import en masse, pas de Wowhead, pas de wiki.gg.**

### Exemples concrets (pour le parent / Mathieu)

**Officiels (pas de PNJ ni de monstre) :**

1. Premier objet de campement, compétence 20 : quêtes des zones de départ **ou** achat chez un maître de métier — PNJ, zone et prix **non publiés**.
2. Règle générale 140+ : butin de donjons et raids ; boss **non nommés** ; taux **non publiés**. Exceptions officielles : **Tanning Rack 125** (6/11), **Journeyman Campfire Kit Cuisine 90** (10/11).
3. « Plus de 600 nouvelles recettes » : volume annoncé, **pas de liste**.
4. Noms officiels EN sans obtention : **Arcane Salvager**, **Fishing Rack**, **Recipe: Elixir of Holy Power**.
5. Marchands de fournitures sur **l’île de Zéphras** (5/11) : existent, **non nommés**, pas une liste de recettes.

**À confirmer uniquement (extrait client) :**

6. **Recipe: Smoked Sagefish** (Cuisine 80) et **Recipe: Sagefish Delight** (Cuisine 175) — vendues par **Zerril Softbreeze**, **île de Zéphras**. Prix d’*achat* non indiqué (la fiche montre un *Sell Price*, revente). Coordonnées 43,8 / 43,8 marquées « per quest data » : dans le CSV seulement, **pas dans le brouillon d’article**, et non officielles.
7. **Blueprint: Cookie’s Feast** (Cuisine 140 selon la fiche) — monstre **Cookie**, **The Deadmines**. Taux : non indiqué.
8. **Blueprint: Repair Bot** (Ingénierie 140) — monstre **Sneed**, **The Deadmines**. Distinct du **Reagent Bot** officiel (niveau 20). Taux : non indiqué.
9. **Blueprint: Arcane Salvager** (Enchantement 140 selon la fiche) — **Rath’mael** (Ruines de Lordaeron) et **Charlga Razorflank** (Razorfen Kraul). L’*existence* d’Arcane Salvager est officielle ; la source de butin **reste à confirmer**. Rath’mael n’apparaît pas dans les articles officiels consultés (la fiche donjon officielle nomme The Baron). Taux : non indiqué.
10. **Pattern: Filigreed Shining Gown** (Couture 75) — Cookie (Deadmines) et Fel Steed / Shadow Charger (Shadowfang Keep). **Pattern: Brawler’s Leather Hood** (Travail du cuir 100) — Lady Sarevess, Blackfathom Deeps. Taux : non indiqués.

Autres lignes à confirmer dans le CSV (même guide cuisine, une seule page) : quêtes (Skywall Souffle / Restocking the Larders ; Beer Basted Boar Ribs / Dun Morogh Alliance ; Soothing Turtle Bisque / Chef Jessen et Christoph Jeffcoat ; et une série de quêtes dont la **zone n’a pas été ouverte** fiche par fiche — volontairement) ; recettes « from the trainer » (le tableau d’ensemble dit pourtant « probably from the trainer, not confirmed »).

**Rien inventé. Rien reporté de Classic Era faute de source Forever.** Zerril a un identifiant élevé (251905) dans les données consultées, présenté comme PNJ Forever — cela n’en fait pas un fait officiel.

---

## 5. Approche proposée pour le volume (plutôt qu’un crawl)

Couvrir **les 2 126** recettes, ou même les **~821** qui ont une source enregistrée (2+55+80+174), exigerait d’ouvrir des **centaines** de fiches. Ce n’est plus une consultation ciblée. Ce n’a **pas** été fait.

Proposition, si Mathieu veut aller plus loin **sans** collecte automatique :

1. **Priorité lootables (demande t343u) :** les **55** recettes classées Drop — par **lots ciblés de 5 à 10 fiches**, mêmes règles (à confirmer, taux seulement s’il est écrit, monstre/coffre + zone, pas de wiki.gg, pas de Wowhead scrapé, pas de report Classic). Estimation : plusieurs sessions, ~55 URLs, pas un crawl.
2. **Puis** les 80 quêtes et, seulement si utile, un échantillon des 174 réputations (les 174 d’un coup restent trop volumineuses pour une consultation ciblée).
3. **Ne pas** importer les 510 « probably trainer » ni les 1 305 sans source comme liste wiki.
4. **Sur le wiki publié :** garder la section « À confirmer » **courte** (c’est déjà le choix du brouillon), ou la retirer et ne laisser que l’officiel — à décider (question 1).
5. Si un export structuré public existait sans manquement aux conditions d’utilisation, ce serait à Mathieu de l’autoriser explicitement ; **rien de tel n’a été téléchargé ici**.

---

## 6. Fiches que les brouillons proposent de modifier

| Fiche | Fichier | Version actuelle → si appliqué | Contenu proposé |
|---|---|---|---|
| forever-professions-blueprints | `brouillons/forever-professions-blueprints.revise.json` | published v8 → draft v9 | Règles officielles d’obtention ; tableau des noms officiels ; **courte** section d’exemples clairement marquée « à confirmer » (données extraites du client, **sans** citer de nom de base tierce dans le texte) ; historique 12/11. Slugs **inchangés**. |
| forever-camp-features | `brouillons/forever-camp-features.revise.json` | published v4 → draft v5 | Conservation du tableau du 21/10 ; **exceptions officielles** 125 / 90 ; section correctifs novembre ; historique. Slugs **inchangés**. Pas de données client. |

**Validation :** `review.mjs revise --dry-run` dans `recettes-pnj/test-validate/` : **SIM_OK** (blueprints contentDigest `5359d577…`, camp-features `7b5a65d8…`), `committed: false`. Runtime d’origine inchangé (blueprints toujours published v8, camp-features published v4).

**Non appliqué, non soumis, non approuvé, non publié.** L’acteur du dry-run est `recherche-recettes-pnj (pas une validation de Mathieu)`.

Fiches non rédigées en brouillon, mais à prévoir si Mathieu le souhaite : `forever-professions-camping` (règle 140+ à annoter des mêmes exceptions) ; éventuellement un renvoi depuis overview et article-campfire. Pas de nouvelle fiche (éviter les doublons).

Captures 412 px : **non faites** (pas de wiki de test construit pour cette recherche, et pas nécessaire pour livrer le CSV / le rapport / les JSON).

---

## 7. Politique de sources — ce qui a été exclu

- **Officiel Blizzard** = seul statut « officiel confirmé ».
- **Extrait client** = « à confirmer », consultation ciblée, URL et date dans le tableau de travail. Dans le **texte destiné à la page**, formulation « données extraites du client, à confirmer » — **sans** nommer la base. Les URL réelles sont dans le CSV, le TSV de consultation, et les objets `sources` du JSON (le pipeline les affichera avec la pastille « à confirmer »).
- **Wowhead :** pas de scraping, pas de consultation ici.
- **warcraft.wiki.gg / \*.wiki.gg :** exclus, non consultés.
- **wowforever.wiki.fextralife.com** et **foreverguide.net :** non autorisés, **non utilisés** (notamment pour une sous-zone ou des coordonnées de Zerril).
- **Forums joueurs** (noms de PNJ non « blue ») : non repris comme faits.
- **Notes de bêta** (t/2360696 : Peace Tea, recettes de forge / cuir en drop de donjon, etc.) : **non reprises** dans les brouillons, conformément à t341u. Mentionnées ici seulement pour mémoire : ce n’est pas une confirmation post-lancement.
- **Retail / Midnight** (Coiled Isle, Recipe: Liquid Luster, etc.) : **exclu**, hors Forever.
- **Classic Era :** aucun vendeur, monstre ou quête Classic n’a été copié « parce que c’était comme ça avant ». Seules des données présentées comme Forever, et encore comme « à confirmer ».
- **Aucun constat en jeu** n’est revendiqué.

---

## 8. Risques

- **Prendre un « à confirmer » pour un fait officiel**, surtout Arcane Salvager (existence officielle, butin seulement à confirmer) et Zerril (absent des news Blizzard).
- **Confondre prix de revente et prix d’achat** (Sagefish, Mild Spices, Iron Grenades).
- **Fusionner Reagent Bot (officiel, 20) et Repair Bot (à confirmer, 140).**
- **Importer les 2 126 lignes** ou crawler les 55+80+174 : hors politique, et trop volumineux pour une consultation ciblée.
- **Inventer des noms FR** (Journeyman Campfire Kit, Elixir of Holy Power, noms de patrons) : volontairement laissés en anglais.
- **Publier des coordonnées** client (« 43,8, 43,8 ») : volontairement absentes de l’article, seulement dans le CSV avec mention « per quest data ».
- Appliquer les brouillons **sans** décision de Mathieu sur la section « à confirmer ».
- Toucher à la production / déployer : **hors mandat**, non fait.

---

## 9. Questions pour Mathieu

1. **Sur le wiki :** garder la courte section « Exemples à confirmer » du brouillon blueprints, ou ne publier que l’officiel (règles + noms sans vendeur ni boss) ?
2. **Suite lootables :** autoriser un prochain passage **ciblé par lots** sur les ~50 recettes Drop restantes (même politique, toujours à confirmer), ou s’arrêter là jusqu’à une publication officielle ?
3. Faut-il aussi un brouillon pour **forever-professions-camping** (mêmes exceptions 125 / 90) dans le même futur paquet ?
4. Y a-t-il des constatations **en jeu** que Mathieu veut apporter lui-même (par ex. Zerril, un plan de boss) ? Elles seules pourraient passer au statut « vérifié en jeu », avec preuve, observateur et build — ce n’est pas le cas ici.
5. Les 174 recettes « Reputation » : on les laisse de côté jusqu’à une source officielle (ACA / DSL n’ont pas de liste), ou un échantillon ciblé plus tard ?

---

## 10. Fichiers livrés

```
recettes-pnj/
  RECETTES_PNJ.csv
  RAPPORT_RECETTES_PNJ.md          (ce fichier)
  SHA256SUMS
  brouillons/
    LIRE-AVANT-APPLICATION.md
    forever-professions-blueprints.revise.json
    forever-camp-features.revise.json
  sources-brutes/
    CONSULTATION.tsv
    bz-24315281-en-PROFESSIONS.txt
    (HTML/RSC déjà présents de la session)
  preuves/                         (journal du dry-run isolé, si écrit)
  test-validate/                   (copie isolée, dry-run uniquement, committed: false)
```

**Rien n’a été déployé. Rien n’a été poussé. Aucun `update-v34.sh` n’a été préparé.**

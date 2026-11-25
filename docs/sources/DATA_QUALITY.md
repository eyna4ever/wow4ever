# Wowkipedia V2.1 — Qualité des données (étape 02)

## 1. Statuts de vérification (définitions)

| Statut | Définition | Preuve minimale | Publiable ? |
|---|---|---|---|
| **officiel confirmé** | Publié par Blizzard : article Blizzard News, message « bleu » d’un forum officiel, page officielle du jeu, compte support officiel | URL officielle, HTTP 200, date de la page, citation ≤ 400 caractères | Oui, avec la mention « annoncé » si ce n’est pas encore livré |
| **vérifié en jeu** | Constaté en jeu sur Forever par une personne identifiée | Capture datée, royaume et région, build client affiché, personne nommée | Oui |
| **extrait client** | Lu dans les fichiers du client par un tiers. **Ne prouve pas que la donnée existe ou est accessible en jeu** (contenu désactivé, futur ou de test) | Build exact, source tierce | **Non** (quarantaine) |
| **communautaire** | Observation de joueurs ou d’un site fan (Eternadex, addon, forum joueur sans réponse bleue) | URL et date | **Non** (catalogue seulement ; t329u) |
| **à confirmer** | Plausible, mais sans source suffisante ou avec des sources contradictoires | Motif écrit | Non |
| **obsolète** | Vrai à une date, puis remplacé (correctif, changement de bêta, annonce dépassée) | Lien vers le fait qui le remplace (`superseded_by`) | Visible seulement dans l’historique, avec sa date |

Règles :
- Une donnée **extraite du client ne passe jamais** directement à « vérifié en jeu ».
- Une **annonce** ne prouve pas la livraison : le libellé reste « annoncé » ou « prévu » jusqu’à une source de déploiement (ex. le correctif du 8/11, « we deployed »).

## 2. Résultats des vérifications du 9 novembre 2026

### Sources déjà citées par le wiki
- **123 URL uniques** au total : 84 sur news.blizzard.com, 17 sur worldofwarcraft.blizzard.com, 15 sur le forum US, 4 sur le forum EU, 3 sur x.com. Ce sont exactement les mêmes dans `entries.json` et dans le HTML.
- **123/123 répondent en HTTP 200.** 24 redirigent vers une URL canonique.
- 107 mentionnent « Forever ». Les **16 pages de races génériques** (worldofwarcraft.blizzard.com/game/races/*) **ne mentionnent pas Forever**. Elles ne sont utilisées que dans les 2 guides d’histoire Alliance et Horde, 8 sources sur 14 dans chacun : c’est acceptable pour du lore, interdit pour une mécanique.
- **Les messages forum sont authentifiés** par leur auteur :
  - Kaivax, CM Blizzard, sur 17 des 19 URL de forum ;
  - les 2 fils joueurs (« Zeppelins broken? », « Why do I see maybe 8 people… ») contiennent bien **une réponse d’Aggrend**, vérifiée sur les pages 1 à 3.
- **Dates** : sur 123 sources, 20 ont un `publishedAt` différent de la date de la page.
  - 11 écarts d’un jour sont dus au fuseau (UTC ou Paris).
  - **9 écarts de 2 jours ou plus**, à corriger dans les fiches :
    - l’article de lancement 24315820 est cité au 29/10 alors que la page indique le 04/11 (mise à jour ou republication) ;
    - la réservation de noms 24303866 : 20/10 cité contre 27/10 ;
    - la séance de dédicaces d’Irvine 24302547 : 26/10 contre 28/10 ;
    - les notes de développement 2360696 et 631316 : la date de la page est celle de la création du fil, alors que la fiche cite la date de mise à jour, ce qui est légitime.
- Les **3 publications X** viennent de comptes support officiels (@BlizzardCS, @BlizzardCSEU_FR). J’ai vérifié le titre, le compte et la date ; le texte n’est rendu que partiellement sans JavaScript.

### Eternadex : vérification d’authenticité et de licence
- **Nature** :
  - site fan indépendant (eternadex.com) ;
  - éditeur identifié par ses mentions légales : « Elemental Gilde », à Munich ;
  - financé par la publicité, **non affilié à Blizzard** (déclaration du site) ;
  - données « lues dans les fichiers du jeu » (client 1.60.1.70862, extraction du 07/11/2026), complétées par un addon de collecte (« EternaDex Meter ») ;
  - traductions hors allemand « partiellement par IA ».
- **Licence** :
  - **aucune licence de réutilisation ni conditions d’utilisation publiées** (/terms, /agb, /nutzungsbedingungen, /en/lizenz et /api renvoient 404) ;
  - les données de jeu sont © Blizzard, et la base est protégée par le droit sui generis européen des bases de données (directive 96/9/CE) ;
  - le kit presse autorise seulement à citer le nom et des textes de présentation ;
  - le robots.txt ne bloque que /entwurf/, ce qui **ne vaut pas licence**.
- **Fiabilité** : les chiffres changent d’une page à l’autre le même jour.

  | Donnée | Accueil EN | Page base | Page presse |
  |---|---|---|---|
  | Objets | 18 999 | 18 965 | 18 881 |
  | Quêtes | 5 167 | 5 167 | 5 165 |
  | Donjons | 26 | 31 | 14 |
  | PNJ | — | 3 284 | 1 820 |
  | Métiers | 8 | 14 | — |

  Le build affiché diffère aussi entre l’accueil (« client build 1.60.1.70862 ») et la page « à propos » (« beta build 1.60.1 »).
- **Conclusion : NO-GO pour l’import et la republication.**
  - Usage permis : citer Eternadex comme **référence communautaire** (lien), avec le statut `communautaire` ou `extrait client`, sans reprendre ses données.
  - Les tooltips intégrables sont **incompatibles avec la CSP** du site (`script-src 'self'`) et ne doivent pas être intégrés.

### Chiffres revendiqués (5167 / 48 / 65)
| Chiffre | Origine identifiée | Source officielle ? | Statut |
|---|---|---|---|
| **5 167 quêtes** | Eternadex : accueil et base (5 165 sur la page presse) | **Aucune** source Blizzard trouvée dans les 123 sources | **extrait client**, quarantaine, ni publiable ni objectif |
| **48 factions** | Eternadex, page base : « Reputation — Factions and rewards 48 » | **Aucune** | **extrait client**, quarantaine. Le périmètre « réputation » n’équivaut pas à « factions » |
| **65 défis** | Eternadex reprend un chiffre **officiel** | **OUI** : Blizzard 24307383 (23/09/2026). FR : « Au total, il existe 65 défis d’héritage, répartis dans six catégories distinctes » ; EN : « sixty-five Legacy Challenges… six different categories ». Total par catégorie : 27 + 18 + 12 + 2 + 3 + 3 = 65 | **officiel confirmé** (annonce d’avant le lancement), **pas vérifié en jeu** |

Correction de l’étape 01 : « 65 défis » n’apparaissait pas sur le wiki, mais le chiffre **existe chez Blizzard**. Il est utilisable, sourcé, avec le statut « officiel confirmé ». Les 2 autres chiffres restent non officiels.

## 3. Vocabulaire Classic / Retail : notes de revue
- L’étape 01 a relevé 46 pages qui contiennent « Classic », « Hardcore » ou « Season of Discovery ».
- **Les usages dans des sources Blizzard Forever sont avérés** :
  - « Classic Era » comme référence d’équilibrage (Kaivax, 06/11 : « effectiveness … relatively the same as in Classic Era ») ;
  - « shocks reverted to Classic Era values » (notes du chaman) ;
  - « tools similar to Season of Discovery » (populations par faction) ;
  - « non-Hardcore characters » (héritage).
  - Il faut aussi compter les noms de modes Forever : préréglage *Classic/Enhanced* et ensemble de règles *Hardcore*.
- Règle : ce vocabulaire est **accepté seulement** en citation ou en paraphrase d’une source Forever officielle, ou comme nom de mode Forever. Il est **interdit** pour décrire une mécanique non-Forever comme si elle s’appliquait.
- Action pour l’étape 03 : une liste blanche de contextes, et un contrôle automatique qui signale tout autre usage.

## 4. Lacunes connues
- Aucun constat « vérifié en jeu » n’existe : tout repose sur des annonces.
- Aucun build n’est indiqué par les sources Blizzard (articles et forums) ; le build n’est connu que côté tiers.
- Les étapes des suites de quêtes (ex. Valthalak) ne sont pas publiées par Blizzard.
- Aucune liste officielle de quêtes, PNJ, objets ou factions : une couverture « complète » est impossible sans source autorisée.
- Il reste 9 dates de fiches à corriger (voir ci-dessus).
- Le caractère **non commercial** de Wowkipedia (condition de la Legal FAQ Blizzard) est à confirmer par Mathieu : pas de publicité, pas de revenus.

## 5. Règles de qualité permanentes
1. Un fait = une valeur, au moins une source autorisée, une date, un build (ou `null`), un statut et des droits.
2. Les noms sont ceux que publie Blizzard en FR et en EN. On ne traduit pas soi-même un nom officiel.
3. Un fait daté qui expire (annonce) est revu à sa date.
4. Aucun chiffre global n’est publié sans source Blizzard.
5. Aucune donnée personnelle (forum, addons) n’entre dans le staging.

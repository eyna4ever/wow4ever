#!/usr/bin/env python3
"""Lot 1 (étape 03) — fiches documentées uniquement à partir de sources officielles Blizzard consultées le 2026-11-09.
Produit lot1.entries.json (brouillons) à importer avec pipeline/scripts/import.mjs. Aucune donnée tierce."""
import json, pathlib
GV = 'World of Warcraft: Forever — annonces, état documentaire 2026-11-09'
LIC = 'Droits réservés Blizzard ; référence et synthèse originale (courtes citations), mention © Blizzard Entertainment conservée ; site non commercial.'
ACC = '2026-11-09'
def src(key, lang, url, title, pub):
    return {'key': key, 'language': lang, 'url': url, 'title': title, 'publishedAt': pub, 'accessedAt': ACC, 'license': LIC, 'gameVersion': GV}
LEG = [src('bz-legacy-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24307383/decouvrez-le-systeme-dheritage-de-world-of-warcraft-forever', 'Découvrez le système d’héritage de World of Warcraft: Forever', '2026-09-23'),
       src('bz-legacy-en', 'en', 'https://news.blizzard.com/en-us/article/24307383/get-to-know-the-world-of-warcraft-forever-legacy-system', 'Get to Know the World of Warcraft: Forever Legacy System', '2026-09-23')]
CAMP = [src('bz-camp-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24301516/retrouvez-vous-autour-dun-feu-de-camp-dans-world-of-warcraft-forever', 'Retrouvez-vous autour d’un feu de camp dans World of Warcraft: Forever', '2026-10-21'),
        src('bz-camp-en', 'en', 'https://news.blizzard.com/en-us/article/24301516/gather-around-the-campfire-in-world-of-warcraft-forever', 'Gather Around the Campfire in World of Warcraft: Forever', '2026-10-21')]
DIVE = [src('bz-dive-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever', 'Récapitulatif de la présentation « Au cœur de World of Warcraft: Forever »', '2026-09-13'),
        src('bz-dive-en', 'en', 'https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap', 'World of Warcraft: Forever Deep Dive Panel Recap', '2026-09-13')]
DEV5 = [src('bz-devnotes5', 'en', 'https://us.forums.blizzard.com/en/wow/t/2360696/5', 'WoW Forever Beta Development Notes — message du 8 octobre 2026 (forum officiel US)', '2026-10-08')]

def C(fr, en): return {'fr': fr, 'en': en}
def P(fr, en, s): return {'type': 'p', 'fr': fr, 'en': en, 'src': s}
def L(items, s): return {'type': 'list', 'items': [{'fr': a, 'en': b, 'src': s} for a, b in items], 'src': s}
def T(cap, head, rows, s): return {'type': 'table', 'caption': C(*cap), 'head': [C(*h) for h in head], 'rows': [[C(*c) for c in r] for r in rows], 'src': s}
def K(fr, en, s): return {'fr': fr, 'en': en, 'src': s}
def entry(id, cat, sub, title, desc, sources, relations, article):
    return {'id': id, 'title': C(*title), 'description': C(*desc), 'category': cat, 'subcategory': sub, 'sources': sources, 'status': 'draft',
            'updatedAt': ACC, 'gameVersion': GV, 'version': 1, 'relations': relations, 'verification': 'officiel confirmé',
            'history': [{'at': ACC, 'actor': 'GrokBot — lot 1 étape 03 (environnement de test isolé)', 'note': 'Fiche rédigée uniquement à partir des sources officielles Blizzard citées (synthèse originale, courtes reprises de noms). Relecture humaine de Mathieu requise avant toute mise en production.', 'version': 1}],
            'article': article}
def art(slug, ill, lead, kps, sections, confirmed, pending, notes=None, dates=None):
    a = {'format': 1, 'slug': C(*slug), 'illustration': ill, 'lead': lead, 'keyPoints': kps, 'sections': sections, 'confirmed': confirmed, 'pending': pending}
    if notes: a['notes'] = notes
    if dates: a['dates'] = dates
    return a
S = lambda id, t, blocks: {'id': id, 'title': C(*t), 'blocks': blocks}
lg, cp, dv, d5 = ['bz-legacy'], ['bz-camp'], ['bz-dive'], ['bz-devnotes5']
E = []

# ---------- D. Héritage ----------
E.append(entry('forever-legacy-challenges', 'quests', 'heritage',
  ('Défis d’héritage : les 65 défis et leurs 6 catégories', 'Legacy Challenges: the 65 challenges and their 6 categories'),
  ('Répartition officielle des 65 défis d’héritage de WoW: Forever en six catégories (27 + 18 + 12 + 2 + 3 + 3 points), avec la condition de chaque groupe de défis et les règles du mode Extrême.',
   'Official breakdown of the 65 WoW: Forever Legacy Challenges into six categories (27 + 18 + 12 + 2 + 3 + 3 points), with the condition behind each group of challenges and the Hardcore rules.'),
  LEG, ['forever-progression-legacy', 'article-forever-legacy', 'forever-glossary-legacy-points', 'forever-questline-lord-valthalak', 'forever-legacy-perks', 'forever-legacy-rewards'],
  art(('defis-heritage', 'legacy-challenges'), 'quests',
    K('Blizzard décrit 65 défis d’héritage répartis en six catégories ; chaque défi accompli rapporte un point d’héritage, partagé par tous les personnages du compte Battle.net hors mode Extrême. Cette fiche reprend la répartition officielle sans inventer de nom de défi individuel.',
      'Blizzard describes 65 Legacy Challenges across six categories; each completed challenge grants one Legacy Point, shared by every character on the Battle.net account except Hardcore ones. This entry restates the official breakdown without inventing any individual challenge name.', lg),
    [K('65 défis au total, 1 point d’héritage par défi.', '65 challenges in total, 1 Legacy Point per challenge.', lg),
     K('Points liés au compte Battle.net, disponibles pour tous les personnages hors mode Extrême.', 'Points are Battle.net account-wide and available to all non-Hardcore characters.', lg),
     K('Accès au système dès le premier point : niveau 25, 150 dans un métier principal non lié à la récolte, ou exploration complète de la carte du monde.', 'Access opens with the first point: level 25, 150 in a non-gathering primary profession, or exploring the entire world map.', lg)],
    [S('categories', ('Les six catégories', 'The six categories'), [
       T(('Défis d’héritage par catégorie (source : Blizzard, 23/09/2026)', 'Legacy Challenges by category (source: Blizzard, 2026-09-23)'),
         [('Catégorie', 'Category'), ('Points', 'Points'), ('Condition', 'Condition')],
         [[('Classes', 'Classes'), ('27', '27'), ('Atteindre les niveaux 25, 45 et 60 avec chaque classe', 'Reach level 25, 45 and 60 with each class')],
          [('Métiers', 'Tradeskills'), ('18', '18'), ('Atteindre 150, 225 et 300 dans chaque métier principal non lié à la récolte', 'Reach 150, 225 and 300 skill in each non-gathering primary profession')],
          [('JcJ', 'Player vs. Player'), ('12', '12'), ('Rangs 3, 7, 10, 13 et 14 (5) ; exalté auprès de chaque réputation de champ de bataille (4) ; quêtes des semaines 4, 7 et 10 du parcours de saison JcJ du champ d’honneur (3)', 'Ranks 3, 7, 10, 13 and 14 (5); Exalted with each battleground reputation (4); week 4, 7 and 10 quests of the Field of Honor PvP Season’s Journey (3)')],
          [('Aventure', 'Adventure'), ('2', '2'), ('Explorer toute la carte du monde avec un même personnage ; terminer la suite de quêtes du donjon du seigneur Valthalak', 'Explore the entire world map on one character; complete the Lord Valthalak dungeon set questline')],
          [('Donjons', 'Dungeons'), ('3', '3'), ('Vaincre le boss final de tous les donjons de niveaux 15 à 25, 26 à 45 et 46 à 60', 'Defeat the final boss of every level 15–25, 26–45 and 46–60 dungeon')],
          [('Raids', 'Raids'), ('3', '3'), ('Vaincre Onyxia ; les 13 boss du sommet d’Hyjal ; les 8 boss des profondeurs des Saisons', 'Defeat Onyxia; all 13 Hyjal Summit bosses; all 8 Barrow Deeps bosses')]], lg),
       P('Total : 27 + 18 + 12 + 2 + 3 + 3 = 65 défis, donc 65 points d’héritage possibles sur l’ensemble du compte au lancement.', 'Total: 27 + 18 + 12 + 2 + 3 + 3 = 65 challenges, hence 65 possible Legacy Points across the account at launch.', lg)]),
     S('un-personnage', ('Un seul personnage suffit-il ?', 'Is one character enough?'), [
       P('Blizzard indique qu’un seul personnage peut gagner jusqu’à 29 points : 3 par la montée en niveau, 6 par les métiers, 12 en JcJ, 2 en aventure et 6 en donjons et raids. Les avantages se dépensent dans la limite de 16 points par personnage au lancement : créer des personnages secondaires n’est donc pas obligatoire.', 'Blizzard states that a single character can earn up to 29 points: 3 from leveling, 6 from tradeskills, 12 from PvP, 2 from Adventure and 6 from dungeons and raids. Perks are bought within a cap of 16 points per character at launch, so alts are not required.', lg)]),
     S('extreme', ('Mode Extrême (Hardcore)', 'Hardcore'), [
       P('Le mode Extrême n’est pas disponible au lancement. Quand il le sera, les défis accomplis ailleurs n’y apparaîtront pas, mais un défi accompli en mode Extrême sera accordé dans les autres ensembles de règles. Les défis JcJ ne pouvant pas y être accomplis, Blizzard prévoit 12 défis propres au mode Extrême.', 'Hardcore is not available at launch. When it is, challenges completed elsewhere will not show up there, but a challenge earned in Hardcore will be granted in the other rulesets. Since PvP challenges cannot be completed there, Blizzard plans 12 Hardcore-specific challenges.', lg)])],
    [K('65 défis en 6 catégories (27 + 18 + 12 + 2 + 3 + 3).', '65 challenges in 6 categories (27 + 18 + 12 + 2 + 3 + 3).', lg),
     K('1 point par défi, partagé par le compte hors mode Extrême.', '1 point per challenge, account-wide except Hardcore.', lg),
     K('Jusqu’à 29 points sur un seul personnage ; 16 points dépensables par personnage au lancement.', 'Up to 29 points on one character; 16 spendable points per character at launch.', lg)],
    [C('Le nom individuel affiché en jeu de chaque défi n’est pas publié par Blizzard : ce wiki ne les liste pas.', 'The in-game name of each individual challenge is not published by Blizzard: this wiki does not list them.'),
     C('Les 12 défis du mode Extrême et les défis des futures mises à jour de contenu ne sont pas encore détaillés.', 'The 12 Hardcore challenges and the challenges of future content updates are not detailed yet.'),
     C('Liste exacte des « réputations de champ de bataille » et des donjons de chaque tranche de niveaux : non précisée dans l’article.', 'Exact list of “battleground reputations” and of the dungeons in each level band: not specified in the article.')],
    notes=[K('Écart FR/EN : la version française parle d’« un métier principal non lié à la récolte » au singulier, la version anglaise de « chaque » métier (each). Le total de 18 points correspond à 6 métiers d’artisanat × 3 paliers, ce qui concorde avec la version anglaise.', 'FR/EN discrepancy: the French text says “a” non-gathering primary profession (singular), the English text says “each”. The 18-point total matches 6 crafting professions × 3 tiers, consistent with the English text.', lg)],
    dates=[{'date': '2026-09-23', 'fr': 'Publication de la présentation officielle du système d’héritage.', 'en': 'Official Legacy System overview published.', 'src': lg}])))

PERKS = {
 'metiers': (('Métiers', 'Professions'), [
   ('Heures supplémentaires', 'Working Overtime', 'Plus de chances de gagner un point de compétence dans tous les métiers, y compris les métiers de classe comme le crochetage', 'Higher chance to gain a skill point in all tradeskills, including class ones such as Lockpicking'),
   ('Récolte généreuse', 'Bountiful Harvest', 'Matériaux rares supplémentaires en minage, herboristerie et dépeçage', 'Additional Scarce resources from mining, herbalism and skinning'),
   ('Marchandage', 'Bartering', 'Prix en or réduit chez les marchands', 'Lower gold price at vendors'),
   ('Charismatique', 'Performance bonus', 'Chance de faveur marchande supplémentaire auprès de l’Administration commerciale d’Azeroth ou des Transports logistiques Durotar', 'Chance of extra Merchant’s Favor from the Azeroth Commerce Authority or Durotar Supply and Logistics'),
   ('Cordon bleu', 'Master Chef', 'Chance qu’une recette de cuisine produise un plat supplémentaire', 'Chance for cooking recipes to produce additional results'),
   ('Maître des appâts', 'Luremaster', 'Chance de pêcher un poisson supplémentaire', 'Chance to fish up extra fish'),
   ('Étude assidue', 'Dedicated Study', 'Effet quotidien pour progresser plus vite dans ses métiers, ou essences élémentaires gratuites une fois 300 atteint partout', 'Daily cooldown to level tradeskills faster, or free Elemental Essences once all reach 300')]),
 'aventure': (('Aventure', 'Adventure'), [
   ('Bien reposé', 'Well Rested', 'Plafond d’expérience de repos plus élevé et accumulation plus rapide', 'Higher rested experience cap and faster accumulation'),
   ('Frisson de l’aventure', 'Thrill of Adventure', 'Un peu de vie et de mana rendus après chaque victime non négligeable', 'A small amount of health and mana after every non-trivial kill'),
   ('Alerte avancée', 'High Alert', 'Meilleure détection du camouflage hors champs de bataille', 'Better stealth detection outside battlegrounds'),
   ('Guide de terrain', 'Field Guide', 'Réduit le temps de recharge d’une heure des fonctionnalités de campement', 'Reduces the 1-hour cooldown on placing camping features'),
   ('Médecine de terrain', 'Field Medicine', 'Affaiblissement « Un bandage a été appliqué récemment » plus court, sauf en donjon, raid et champ de bataille', 'Shorter Recently Bandaged debuff, except in dungeons, raids and battlegrounds'),
   ('Talent', 'Talented', 'Points de talent débloqués jusqu’à 5 niveaux plus tôt', 'Talent points unlocked up to 5 levels earlier'),
   ('Vols fréquents', 'Frequent Flier', 'Vols moins chers et plus rapides', 'Cheaper, faster flights')]),
 'ingeniosite': (('Ingéniosité', 'Resourcefulness'), [
   ('Gourmand', 'Gourmand', 'Améliorations de nourriture plus longues', 'Longer food buffs'),
   ('Mort et vif', 'The Quick and the Dead', 'Retour plus rapide au corps et améliorations de groupe et de raid gratuites après résurrection', 'Faster corpse runs and free party and raid buffs after resurrecting'),
   ('Renforcer', 'Reinforce', 'Moins de perte de durabilité à la mort', 'Less durability damage from death'),
   ('Pour un grand honneur', 'For Great Honor', 'Plus de points d’honneur en JcJ', 'More Honor from PvP'),
   ('Permanence', 'Permanence', 'Améliorations de groupe, de raid et de campement plus longues', 'Longer party, raid and camping buffs'),
   ('Diplomatie', 'Diplomat', 'Gains de réputation augmentés', 'Increased reputation gains'),
   ('Économie des composants', 'Reagent Economy', 'Techniques de classe sans composants achetables ; éléments de campement de niveau 1 fabriqués sans composants', 'Class abilities without purchasable reagents; tier 1 camping features crafted without materials')])}
secs = []
for sid, (t, rows) in PERKS.items():
    secs.append(S(sid, (f'Arbre {t[0]}', f'{t[1]} tree'), [T((f'Avantages de l’arbre {t[0]} (7)', f'{t[1]} tree perks (7)'), [('Avantage (FR)', 'Perk (FR)'), ('Avantage (EN)', 'Perk (EN)'), ('Effet annoncé', 'Announced effect')],
        [[(a, a), (b, b), (c, d)] for a, b, c, d in rows], lg)]))
E.append(entry('forever-legacy-perks', 'quests', 'heritage',
  ('Avantages d’héritage : les 3 arbres et leurs 21 avantages', 'Legacy Perks: the 3 trees and their 21 perks'),
  ('Les avantages d’héritage annoncés par Blizzard, arbre par arbre (Métiers, Aventure, Ingéniosité), avec leurs noms français et anglais officiels et l’effet décrit ; plafond de 16 points par personnage au lancement.',
   'The Legacy Perks announced by Blizzard, tree by tree (Professions, Adventure, Resourcefulness), with their official French and English names and the described effect; 16-point cap per character at launch.'),
  LEG, ['forever-legacy-challenges', 'forever-legacy-rewards', 'forever-progression-legacy', 'article-forever-legacy', 'forever-camp-features'],
  art(('avantages-heritage', 'legacy-perks'), 'quests',
    K('Chaque personnage dépense les points d’héritage du compte pour acheter des avantages qui ne valent que pour lui, dans trois arbres : Métiers, Aventure et Ingéniosité. Blizzard en présente sept par arbre ; les valeurs chiffrées ne sont pas publiées.', 'Each character spends the account’s Legacy Points on perks that apply to that character only, in three trees: Professions, Adventure and Resourcefulness. Blizzard presents seven per tree; numeric values are not published.', lg),
    [K('Trois arbres : Métiers, Aventure, Ingéniosité.', 'Three trees: Professions, Adventure, Resourcefulness.', lg),
     K('Chaque personnage dépense ses points indépendamment des autres.', 'Each character spends points independently of the others.', lg),
     K('Au lancement, 16 points au plus peuvent être dépensés par personnage.', 'At launch, at most 16 points can be spent per character.', lg)],
    secs,
    [K('Noms FR/EN et effets des 21 avantages tels que décrits le 23/09/2026.', 'FR/EN names and effects of the 21 perks as described on 2026-09-23.', lg),
     K('Plafond de 16 points dépensés par personnage au lancement.', 'Cap of 16 spent points per character at launch.', lg)],
    [C('Coût en points de chaque avantage, valeurs chiffrées (pourcentages, durées) et ordre de déblocage : non publiés.', 'Point cost of each perk, numeric values (percentages, durations) and unlock order: not published.'),
     C('Blizzard prévoit de nouveaux avantages, puis de nouveaux arbres, avec les futures mises à jour.', 'Blizzard plans new perks, then new trees, in future updates.')],
    notes=[K('Écart de nom : l’avantage « Charismatique » (FR) est appelé « Performance bonus » dans la version anglaise ; la version anglaise écrit aussi « Bountfiful Harvest » (coquille de la source), retranscrit ici « Bountiful Harvest ».', 'Name discrepancy: the perk “Charismatique” (FR) is called “Performance bonus” in the English text; the English text also spells “Bountfiful Harvest” (typo in the source), written here as “Bountiful Harvest”.', lg)])))

E.append(entry('forever-legacy-rewards', 'quests', 'heritage',
  ('Récompenses d’héritage : les 4 récompenses du lancement', 'Legacy Rewards: the 4 launch rewards'),
  ('Les quatre récompenses d’héritage annoncées pour le lancement (jouet, mascotte, tabard, monture), débloquées par les points d’héritage cumulés sur le compte.',
   'The four Legacy Rewards announced for launch (toy, pet, tabard, mount), unlocked by Legacy Points accumulated on the account.'),
  LEG, ['forever-legacy-challenges', 'forever-legacy-perks', 'forever-progression-legacy', 'article-forever-legacy'],
  art(('recompenses-heritage', 'legacy-rewards'), 'quests',
    K('En plus des avantages par personnage, les points d’héritage s’accumulent sur tout le compte et débloquent des jouets et des objets ornementaux. Quatre récompenses sont annoncées au lancement.', 'Besides per-character perks, Legacy Points accumulate across the account and unlock toys and cosmetic items. Four rewards are announced at launch.', lg),
    [K('Quatre récompenses au lancement.', 'Four rewards at launch.', lg), K('De nouvelles récompenses sont prévues à chaque mise à jour de contenu.', 'New rewards are planned with each content update.', lg)],
    [S('liste', ('Les récompenses', 'The rewards'), [T(('Récompenses d’héritage au lancement', 'Legacy Rewards at launch'), [('Nom (FR)', 'Name (FR)'), ('Nom (EN)', 'Name (EN)'), ('Type et description', 'Type and description')],
       [[('Réplique de carabine à air comprimé de Forgefer', 'Réplique de carabine à air comprimé de Forgefer'), ('Replica Ironforge Air Rifle', 'Replica Ironforge Air Rifle'), ('Jouet : batailles factices entre joueurs ; étourdit et compte les points', 'Toy: mock shootouts between players; stuns and keeps score')],
        [('Ourson spectral', 'Ourson spectral'), ('Spectral Bear Cub', 'Spectral Bear Cub'), ('Mascotte exclusive, inspirée du chasseur nain et de son compagnon de la cinématique', 'Exclusive pet inspired by the Dwarven Hunter and his companion in the cinematic')],
        [('Tabard d’ours spectral', 'Tabard d’ours spectral'), ('Spectral Bear Tabard', 'Spectral Bear Tabard'), ('Tabard exclusif', 'Exclusive tabard')],
        [('Rênes d’ours spectral', 'Rênes d’ours spectral'), ('Reins of the Spectral Bear', 'Reins of the Spectral Bear'), ('Monture spectrale exclusive', 'Exclusive spectral mount')]], lg)])],
    [K('Les quatre noms FR/EN et leur type.', 'The four FR/EN names and their type.', lg)],
    [C('Nombre de points d’héritage nécessaire pour chaque récompense : non publié.', 'Number of Legacy Points needed for each reward: not published.')])))

# ---------- C. Campements ----------
FEAT = [('Cuisine', 'Cooking', 'Feu de camp basique', 'Basic Campfire', '1', 'Permet de cuisiner et d’ajouter jusqu’à 3 fonctionnalités de campement', 'Allows cooking and up to 3 additional camp features', '—', '—'),
 ('Secourisme', 'First Aid', 'Trousse de premiers soins', 'First Aid Kit', '20', '+3 à 56 Endurance (selon le niveau)', '+3–56 Stamina (level dependent)', 'Mot de pouvoir : Robustesse', 'Power Word: Fortitude'),
 ('Pêche', 'Fishing', 'Bocal à poisson', 'Fishing Bowl', '20', '+8 % aux caractéristiques', '+8% stats', 'Bénédiction des rois', 'Blessing of Kings'),
 ('Alchimie', 'Alchemy', 'Puits de mana', 'Mana Well', '20', '10 à 29 points de mana toutes les 5 s (selon le niveau)', '10–29 Mana every 5 sec (level dependent)', 'Bénédiction de sagesse', 'Blessing of Wisdom'),
 ('Forge', 'Blacksmithing', 'Meule à aiguiser', 'Sharpening Wheel', '20', '+6 à 34 Force (selon le niveau)', '+6–34 Strength (level dependent)', 'Totem de Force de la Terre', 'Strength of Earth Totem'),
 ('Enchantement', 'Enchanting', 'Luth enchanté', 'Enchanted Lute', '20', '+28 à 260 Armure, +0 à 13 caractéristiques, +0 à 22 résistances (selon le niveau)', '+28–260 Armor, +0–13 all stats, +0–22 all resistances (level dependent)', 'Marque du fauve', 'Mark of the Wild'),
 ('Ingénierie', 'Engineering', 'Robot vendeur de composants', 'Reagent Bot', '20', 'Achat de composants à proximité', 'Buy reagents nearby', '—', '—'),
 ('Herboristerie', 'Herbalism', 'Bougie d’encens', 'Incense Candle', '20', '+2 à 25 Intelligence (selon le niveau)', '+2–25 Intellect (level dependent)', 'Intelligence des arcanes', 'Arcane Intellect'),
 ('Travail du cuir', 'Leatherworking', 'Tente du camp', 'Camp Tent', '20', 'Expérience de repos +5 % d’un niveau (sans effet au-delà)', 'Rested experience +5% of a level (no effect above that)', '—', '—'),
 ('Dépeçage', 'Skinning', 'Chaise du camp', 'Camp Chair', '20', '+2 % de chances de coup critique', '+2% critical strike chance', 'Aura de sélénien', 'Moonkin Aura'),
 ('Couture', 'Tailoring', 'Bannière de faction', 'Faction Banner', '20', '+14 à 32 Esprit pour sa faction (selon le niveau)', '+14–32 Spirit for your faction (level dependent)', 'Esprit divin', 'Divine Spirit')]
E.append(entry('forever-camp-features', 'professions', 'campement',
  ('Campements : fonctionnalités par métier, effets et restrictions', 'Camping: features by profession, effects and restrictions'),
  ('Tableau officiel des fonctionnalités de campement (un exemple par métier) : objet, niveau de compétence, effet et amélioration de classe incompatible, plus les règles d’installation, d’obtention et de risque en JcJ.',
   'Official table of camp features (one example per profession): item, skill level, effect and the incompatible class buff, plus the placement, acquisition and PvP-risk rules.'),
  CAMP, ['forever-professions-camping', 'article-forever-campfire', 'forever-professions-overview', 'forever-legacy-perks'],
  art(('campement-fonctionnalites', 'camping-features'), 'professions',
    K('Le feu de cuisine devient un feu de camp basique autour duquel les joueurs proches ajoutent des objets de métier. Blizzard publie un exemple de fonctionnalité par métier ; ces effets sont des variantes d’améliorations de classe et ne se cumulent pas avec elles.', 'The Cooking Fire becomes a Basic Campfire around which nearby players add profession items. Blizzard publishes one example feature per profession; these effects are variants of class buffs and do not stack with them.', cp),
    [K('Feu de camp basique : jusqu’à 3 fonctionnalités, une par joueur.', 'Basic Campfire: up to 3 features, one per player.', cp),
     K('S’asseoir ou fabriquer au campement pendant au moins 1 minute donne les bonus des autres fonctionnalités.', 'Sitting or crafting at the campsite for at least 1 minute grants the other features’ benefits.', cp),
     K('Toutes les fonctionnalités exigent un feu de camp et partagent un temps de recharge d’une heure.', 'All features require a campfire and share a 1-hour cooldown.', cp)],
    [S('tableau', ('Fonctionnalités par métier', 'Features by profession'), [
       T(('Exemples officiels de fonctionnalités de campement (Blizzard, 21/10/2026)', 'Official camp feature examples (Blizzard, 2026-10-21)'), [('Métier', 'Profession'), ('Objet', 'Item'), ('Compétence', 'Skill'), ('Effet', 'Effect'), ('Incompatible avec', 'Exclusive with')],
         [[(a, b), (c, d), (e, e), (f, g), (h, i)] for a, b, c, d, e, f, g, h, i in FEAT], cp),
       P('Blizzard précise que ce tableau est un aperçu (un exemple par métier), pas la liste complète des objets de campement.', 'Blizzard specifies that this table is a sample (one example per profession), not the full list of camp items.', cp)]),
     S('obtention', ('Obtention', 'How to obtain'), [
       L([('Une courte quête présente le système au début de l’aventure (son nom n’est pas publié).', 'A short quest introduces the system early on (its name is not published).'),
          ('À 20 en compétence : premiers objets via des quêtes des zones de départ ou chez un maître de métier.', 'At skill 20: first items from starter-zone quests or from a profession trainer.'),
          ('Objets demandant 140 ou plus : butin de donjons et de raids.', 'Items requiring 140 or more: dungeon and raid drops.'),
          ('Les cuisiniers apprennent ensuite des feux de camp améliorés (5 ou 10 objets) ; d’autres métiers débloquent par exemple des laboratoires d’alchimie et des râteliers de tannage.', 'Cooks later learn upgraded campfires (5 or 10 objects); other professions unlock e.g. Alchemy Laboratories and Tanning Racks.')], cp)]),
     S('restrictions', ('Restrictions et risques', 'Restrictions and risks'), [
       L([('Effets incompatibles avec l’amélioration de classe équivalente (voir tableau).', 'Effects are exclusive with the matching class buff (see table).'),
          ('Bannière de faction : seuls les membres de votre faction en profitent.', 'Faction Banner: only members of your faction benefit.'),
          ('Tente du camp : sans effet si l’expérience de repos dépasse déjà 5 % d’un niveau.', 'Camp Tent: no effect if rested experience already exceeds 5% of a level.'),
          ('Sous l’ensemble de règles JcJ, le risque augmente si des adversaires trouvent votre campement.', 'On a PvP ruleset, the risk increases when enemy players find your camp.')], cp),
       P('Avantages d’héritage liés : Guide de terrain réduit le temps de recharge d’une heure, Permanence allonge les améliorations de campement et Économie des composants supprime les composants des éléments de niveau 1.', 'Related Legacy Perks: Field Guide reduces the 1-hour cooldown, Permanence lengthens camping buffs and Reagent Economy removes materials from tier 1 features.', lg)])],
    [K('Les 11 objets du tableau, leur niveau de compétence et leur effet.', 'The 11 items in the table, their skill level and effect.', cp),
     K('Règles : 3 fonctionnalités, 1 par joueur, 1 minute, recharge d’1 heure.', 'Rules: 3 features, 1 per player, 1 minute, 1-hour cooldown.', cp)],
    [C('Liste complète des objets de campement de chaque métier, composants et recettes : non publiés par Blizzard.', 'Full list of each profession’s camp items, their materials and recipes: not published by Blizzard.'),
     C('Durée exacte des bonus : seule la meule à aiguiser est décrite comme durant « une heure ».', 'Exact buff duration: only the Sharpening Wheel is described as lasting “an hour”.')],
    dates=[{'date': '2026-10-21', 'fr': 'Publication de l’article officiel sur le système de campement.', 'en': 'Official Camping article published.', 'src': cp}]),
  ) | {'sources': CAMP + LEG})

# ---------- B. Métiers ----------
E.append(entry('forever-professions-overview', 'professions', 'metiers-et-rangs',
  ('Métiers : principaux, secondaires, rangs et maîtres de métier', 'Professions: primary, secondary, ranks and trainers'),
  ('Ce que Blizzard confirme sur les métiers de WoW: Forever : deux métiers principaux parmi neuf, les trois métiers secondaires, les rangs d’Apprenti à Artisan, l’onglet Métiers (K) et les paliers d’héritage 150/225/300.',
   'What Blizzard confirms about WoW: Forever professions: two primary professions out of nine, the three secondary ones, ranks from Apprentice to Artisan, the Professions tab (K) and the 150/225/300 Legacy tiers.'),
  CAMP + LEG, ['forever-camp-features', 'forever-professions-blueprints', 'forever-professions-camping', 'forever-legacy-challenges', 'forever-legacy-perks'],
  art(('metiers-principaux-secondaires', 'professions-primary-secondary'), 'professions',
    K('Chaque personnage peut apprendre deux métiers principaux et les trois métiers secondaires. Les métiers s’apprennent auprès d’un maître de métier et progressent d’Apprenti à Artisan.', 'Each character can learn two primary professions and all three secondary ones. Professions are learned from a trainer and progress from Apprentice to Artisan.', cp),
    [K('Deux métiers principaux au plus.', 'At most two primary professions.', cp), K('Trois métiers secondaires : cuisine, pêche, secourisme.', 'Three secondary professions: Cooking, Fishing, First Aid.', cp),
     K('Rangs : Apprenti, Compagnon, Expert, Artisan.', 'Ranks: Apprentice, Journeyman, Expert, Artisan.', cp)],
    [S('liste', ('Liste des métiers', 'Profession list'), [
       T(('Métiers de WoW: Forever (Blizzard, 21/10/2026)', 'WoW: Forever professions (Blizzard, 2026-10-21)'), [('Type', 'Type'), ('Métiers', 'Professions')],
         [[('Principal — récolte', 'Primary — gathering'), ('Dépeçage, minage, herboristerie', 'Skinning, Mining, Herbalism')],
          [('Principal — artisanat', 'Primary — crafting'), ('Alchimie, forge, enchantement, ingénierie, travail du cuir, couture', 'Alchemy, Blacksmithing, Enchanting, Engineering, Leatherworking, Tailoring')],
          [('Secondaire', 'Secondary'), ('Cuisine, pêche, secourisme', 'Cooking, Fishing, First Aid')]], cp)]),
     S('maitres', ('Maîtres de métier et onglet Métiers', 'Trainers and the Professions tab'), [
       L([('Apprendre : auprès d’un maître de métier, dans les capitales et ailleurs dans le monde.', 'Learn: from a trainer, in major cities and elsewhere in the world.'),
          ('Oublier : onglet Métiers (K) ou barre de menu, puis le « X » à côté du métier.', 'Unlearn: Professions tab (K) or the menu bar, then the “X” next to the profession.'),
          ('L’onglet Métiers affiche les recettes et plans disponibles, les matériaux nécessaires et si la fabrication fait progresser la compétence.', 'The Professions tab shows available recipes and blueprints, required materials and whether crafting raises your skill.')], cp)]),
     S('paliers', ('Paliers 150 / 225 / 300 et héritage', '150 / 225 / 300 tiers and Legacy'), [
       P('Le système d’héritage récompense 150, 225 et 300 dans chaque métier principal non lié à la récolte (18 défis), et atteindre 150 dans l’un d’eux suffit à ouvrir le système.', 'The Legacy System rewards 150, 225 and 300 in each non-gathering primary profession (18 challenges), and reaching 150 in one of them is enough to open the system.', lg)]),
     S('calculateur', ('Pourquoi pas de calculateur de matériaux ?', 'Why no material calculator?'), [
       P('Blizzard n’a publié ni la liste des recettes ni les quantités de composants de Forever. Un calculateur fondé sur des données extraites du client ou d’une base tierce serait « à confirmer » et pourrait induire en erreur : il n’est donc pas proposé tant qu’aucune source officielle ne détaille les recettes.', 'Blizzard has published neither the recipe list nor the material quantities for Forever. A calculator built on client-extracted or third-party data would be “unconfirmed” and could mislead, so none is offered until an official source details recipes.', cp)])],
    [K('Deux principaux parmi neuf, trois secondaires, quatre rangs.', 'Two primary out of nine, three secondary, four ranks.', cp), K('Paliers d’héritage 150/225/300.', 'Legacy tiers 150/225/300.', lg)],
    [C('Recettes, composants, emplacements précis des maîtres de métier et niveaux requis pour chaque rang : non publiés officiellement.', 'Recipes, materials, exact trainer locations and the skill needed for each rank: not officially published.'),
     C('Activités de métier des nouvelles factions Administration commerciale d’Azeroth / Transports logistiques Durotar : seulement mentionnées.', 'Tradeskill activities of the new Azeroth Commerce Authority / Durotar Supply and Logistics factions: only mentioned.')])))

# ---------- A. Quêtes ----------
E.append(entry('forever-quest-rewards-expanded', 'quests', 'recompenses-de-quetes',
  ('Récompenses de quêtes élargies : Mor’Ladim et Hemet Nesingwary', 'Expanded quest rewards: Mor’ladim and Hemet Nesingwary'),
  ('Deux exemples officiels de récompenses de quêtes revues pour davantage de classes : la quête de Mor’Ladim au bois de la Pénombre et les quêtes de Hemet Nesingwary dans la vallée de Strangleronce.',
   'Two official examples of quest rewards reworked for more classes: Mor’ladim’s quest in Duskwood and Hemet Nesingwary’s quests in Stranglethorn.'),
  DIVE, ['forever-item-ladimore-heirloom-ring', 'article-forever-quests'],
  art(('recompenses-quetes-elargies', 'expanded-quest-rewards'), 'quests',
    K('Blizzard indique que des récompenses de quêtes ont été mises à jour ou élargies pour convenir à plus de classes et de rôles, et cite deux exemples.', 'Blizzard states that quest rewards were updated or expanded to support more classes and roles, and gives two examples.', dv),
    [K('Mor’Ladim (bois de la Pénombre) : l’épée à deux mains reste proposée, l’anneau d’héritage de Ladimore s’ajoute pour les lanceurs de sorts.', 'Mor’ladim (Duskwood): the two-handed sword remains, the Ladimore Heirloom Ring is added for spellcasters.', dv),
     K('Hemet Nesingwary (vallée de Strangleronce) : nouvelles options, dont la sorcépée de maître-chasseur.', 'Hemet Nesingwary (Stranglethorn): new options, including the Master Hunter’s Spellsword.', dv)],
    [S('exemples', ('Exemples officiels', 'Official examples'), [
       T(('Récompenses de quêtes élargies citées par Blizzard', 'Expanded quest rewards cited by Blizzard'), [('PNJ', 'NPC'), ('Zone', 'Zone'), ('Récompenses citées', 'Rewards cited')],
         [[('Mor’Ladim', 'Mor’ladim'), ('Bois de la Pénombre', 'Duskwood'), ('Épée à deux mains (inchangée) + anneau d’héritage de Ladimore (lanceurs de sorts)', 'Two-handed sword (unchanged) + Ladimore Heirloom Ring (spellcasters)')],
          [('Hemet Nesingwary', 'Hemet Nesingwary'), ('Vallée de Strangleronce', 'Stranglethorn'), ('Nouvelles options, dont la sorcépée de maître-chasseur', 'New options, including the Master Hunter’s Spellsword')]], dv)])],
    [K('Les deux exemples ci-dessus.', 'The two examples above.', dv)],
    [C('Noms exacts des quêtes, prérequis, statistiques des objets et liste complète des options de Nesingwary : non publiés dans la source.', 'Exact quest names, prerequisites, item stats and the full list of Nesingwary options: not published in the source.')],
    notes=[K('La zone des quêtes de Hemet Nesingwary (Stranglethorn) n’est indiquée que dans la version anglaise ; la version française ne la nomme pas.', 'The zone of Hemet Nesingwary’s quests (Stranglethorn) is given only in the English text; the French text does not name it.', dv)])))

GELKIS = ['Abandoned Ferocity', 'Blade of the Magram Clan', 'Bludgeon of Betrayed Virtues', 'Centaur Spear', 'Ceremonial Centaur Blanket', 'Desert Crawler’s Claw', 'Desperate Barrier', 'Greatstaff of the Necrokhans', 'Kolkar Hunter’s Belt', 'Kolkar Marauder Chain', 'Scavenged Magram Armament', 'Soulsplatter Mace', 'Staff of Revelations', 'Thrice-Damned Effigy', 'Traitor’s Finger', 'Wanderer’s Broadsword']
E.append(entry('forever-questline-gelkis-magram', 'quests', 'suite-de-quetes',
  ('Quêtes des Gelkis et des Magram (Désolace)', 'Gelkis and Magram quests (Desolace)'),
  ('Nouvelles quêtes des centaures Gelkis et Magram en Désolace, débutant par « Valley of Bones » : niveau minimum relevé à 35 pendant la bêta et 16 récompenses réajustées, selon les notes de développement officielles du 8 octobre 2026.',
   'New Gelkis and Magram centaur quests in Desolace, starting with “Valley of Bones”: minimum level raised to 35 during the beta and 16 rewards retuned, per the official development notes of 2026-10-08.'),
  DEV5, ['article-forever-quests'],
  art(('quetes-gelkis-magram', 'gelkis-magram-quests'), 'quests',
    K('Les notes de développement de la bêta mentionnent de nouvelles quêtes pour les Gelkis et les Magram en Désolace. Les noms de quêtes et d’objets sont donnés en anglais : aucun nom français officiel n’est publié dans cette source.', 'The beta development notes mention new quests for the Gelkis and the Magram in Desolace. Quest and item names are given in English: no official French name is published in this source.', d5),
    [K('Première quête citée : « Valley of Bones ».', 'First quest cited: “Valley of Bones”.', d5), K('Niveau minimum : 35 (au lieu de 30) depuis la build bêta du 8 octobre 2026.', 'Minimum level: 35 (was 30) since the 2026-10-08 beta build.', d5),
     K('16 récompenses réajustées, avec un niveau 35 requis annoncé pour un correctif à venir.', '16 rewards retuned, with a level-35 requirement announced for an upcoming hotfix.', d5)],
    [S('recompenses', ('Récompenses réajustées', 'Retuned rewards'), [
       L([(f'*{n}*', n) for n in GELKIS], d5),
       P('Les développeurs précisent que la plupart de ces objets ont surtout vu leur puissance alignée sur la valeur attendue de la quête, et que certains ont changé de caractéristiques.', 'The developers note that most of these items mainly had their power aligned with the quest’s expected value, while some received stat changes.', d5)])],
    [K('Quêtes Gelkis/Magram débutant par « Valley of Bones », niveau minimum 35 (bêta).', 'Gelkis/Magram quests starting with “Valley of Bones”, minimum level 35 (beta).', d5)],
    [C('Source de bêta : l’état au lancement (4 novembre 2026) et l’application du correctif « niveau 35 pour équiper » ne sont pas confirmés par une source officielle postérieure.', 'Beta source: the state at launch (2026-11-04) and whether the “level 35 to equip” hotfix shipped are not confirmed by a later official source.'),
     C('Noms français officiels, PNJ donneurs, étapes de la suite et prérequis : non publiés.', 'Official French names, quest givers, chain steps and prerequisites: not published.')],
    dates=[{'date': '2026-10-08', 'fr': 'Build bêta : niveau minimum relevé à 35 et récompenses réajustées.', 'en': 'Beta build: minimum level raised to 35 and rewards retuned.', 'src': d5}])))

out = pathlib.Path(__file__).with_name('lot1.entries.json')
out.write_text(json.dumps(E, ensure_ascii=False, indent=1) + '\n')
print(len(E), 'entries ->', out)

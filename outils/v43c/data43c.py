"""v43c (Oui de Mathieu t422u, 23/11/2026, Europe/Paris) : textes des mises à jour, repris des brouillons de veille approuvés
(/workspace/wow4ever-chatgpt/veille/articles/2026-11-18-, 2026-11-20-, 2026-11-21-maj-correctifs-forever-5-et-6-novembre.md et
2026-11-20-maj-le-podcast-officiel-wow-forever.md). Seule la typographie change (’, « », “ ”) ; aucun fait ajouté."""
# Sources numérotées à la suite des 16 existantes : [17] page officielle cumulative (titre du 20 novembre), puis relais Kaivax US/EU.
SRC = [
 ('https://news.blizzard.com/en-us/article/24315281', {'fr': 'WoW: Forever Hotfixes - November 20, 2026', 'en': 'WoW: Forever Hotfixes - November 20, 2026'}, '2026-11-21', '2026-11-21'),
 ('https://us.forums.blizzard.com/en/wow/t/2403040/12', {'fr': 'WoW: Forever Hotfixes - November 17, 2026 (Kaivax, forum officiel US, message 12)', 'en': 'WoW: Forever Hotfixes - November 17, 2026 (Kaivax, official US forum, post 12)'}, '2026-11-18', '2026-11-18'),
 ('https://eu.forums.blizzard.com/en/wow/t/639885/11', {'fr': 'WoW: Forever Hotfixes - November 17, 2026 (Kaivax, forum officiel EU, message 11)', 'en': 'WoW: Forever Hotfixes - November 17, 2026 (Kaivax, official EU forum, post 11)'}, '2026-11-18', '2026-11-18'),
 ('https://us.forums.blizzard.com/en/wow/t/2403040/13', {'fr': 'WoW: Forever Hotfixes - November 19, 2026 (Kaivax, forum officiel US, message 13)', 'en': 'WoW: Forever Hotfixes - November 19, 2026 (Kaivax, official US forum, post 13)'}, '2026-11-20', '2026-11-20'),
 ('https://eu.forums.blizzard.com/en/wow/t/639885/12', {'fr': 'WoW: Forever Hotfixes - November 19, 2026 (Kaivax, forum officiel EU, message 12)', 'en': 'WoW: Forever Hotfixes - November 19, 2026 (Kaivax, official EU forum, post 12)'}, '2026-11-20', '2026-11-20'),
 ('https://us.forums.blizzard.com/en/wow/t/2403040/14', {'fr': 'WoW: Forever Hotfixes - November 20, 2026 (Kaivax, forum officiel US, message 14)', 'en': 'WoW: Forever Hotfixes - November 20, 2026 (Kaivax, official US forum, post 14)'}, '2026-11-21', '2026-11-21'),
 ('https://eu.forums.blizzard.com/en/wow/t/639885/13', {'fr': 'WoW: Forever Hotfixes - November 20, 2026 (Kaivax, forum officiel EU, message 13)', 'en': 'WoW: Forever Hotfixes - November 20, 2026 (Kaivax, official EU forum, post 13)'}, '2026-11-21', '2026-11-21'),
]
# lot -> (numéro de source « page », relais US, relais EU)
CITES = {'nov17': (17, 18, 19), 'nov19': (17, 20, 21), 'nov20': (17, 22, 23)}
SEC = {
 'nov20': {
  'fr': ('20 novembre 2026',
         'Lot publié sur la page officielle, désormais titrée « WoW: Forever Hotfixes - November 20, 2026 », et relayé par Kaivax sur les forums officiels US et EU le 21 novembre à 01:18 heure de Paris. Les noms de sorts, PNJ, objets et quêtes sont repris en anglais.',
         ['Classes : Voleur Combat : Blade Flurry fait bien toucher une cible supplémentaire aux dégâts de Shank.',
          'Classes : Démoniste Démonologie : correction d’un bug qui permettait de conserver les effets du talent Demonic Aegis dans Demon Armor ou Demon Skin après l’avoir désappris ; Demonic Aegis et Demon Skin sont retirés quand les talents sont réinitialisés.',
          'Donjons : chaque joueur peut désormais réinitialiser et entrer dans un donjon au maximum 5 fois par heure (contre 10 auparavant). Blackrock Spire : un pilier de pierre ne piège plus les aventuriers.',
          'Ennemis et PNJ : Orgrimmar, Mayhoa Skyhoof n’a plus les yeux brillants.',
          'Objets : bonus 3 pièces de la Stormshroud Armor ramené à 3 % de chances (contre 4 %) en mêlée de rendre 18 points d’énergie (contre 30).',
          'Métiers : la forge et l’enclume de Toron Rockhoof à Summit of Eternity sont de nouveau utilisables pour la forge et la fonte.',
          'Quêtes : The Hinterlands, Witch Doctor Ti’ik laisse plusieurs exemplaires de sa tête pour un groupe ayant la quête ; Feralas, la Perfect Yeti Hide ne tombe plus pendant que sa quête est en cours ; Tanaris, Gor’marok réapparaît plus vite (« The Dunemaul Compound ») ; Riverglades, Dunston Willis ne s’enfuit plus en cours de « Dunston Checks Out ».',
          'Interface : correction d’un problème qui affichait moins de groupes que prévu dans la recherche de groupe.',
          'Conséquences pour les joueurs : le farm de donjons en boucle est freiné (5 entrées par heure) ; les porteurs de Stormshroud Armor perdent de l’énergie ; l’astuce Demonic Aegis ne fonctionne plus.']),
  'en': ('November 20, 2026',
         'Batch published on the official page, now titled “WoW: Forever Hotfixes - November 20, 2026”, and relayed by Kaivax on the official US and EU forums on November 21 at 01:18 Paris time.',
         ['Classes: Combat Rogue: Blade Flurry now correctly makes Shank’s damage hit an additional target.',
          'Classes: Demonology Warlock: fixed a bug that let Demonic Aegis effects be snapshotted into Demon Armor or Demon Skin and kept after untalenting; Demonic Aegis and Demon Skin are removed when talents are unlearned.',
          'Dungeons: players can now reset and enter each dungeon at most 5 times per hour (was 10). Blackrock Spire: a stone pillar no longer traps adventurers.',
          'Enemies and NPCs: Orgrimmar, Mayhoa Skyhoof no longer has glowing eyes.',
          'Items: Stormshroud Armor 3-piece bonus lowered to a 3% chance (was 4%) on melee attack to restore 18 energy (was 30).',
          'Professions: Toron Rockhoof’s forge and anvil in Summit of Eternity are usable again for blacksmithing and smelting.',
          'Quests: The Hinterlands, Witch Doctor Ti’ik drops multiple copies of his head for a group on the quest; Feralas, Perfect Yeti Hide no longer drops while its quest is active; Tanaris, Gor’marok respawns faster (“The Dunemaul Compound”); Riverglades, Dunston Willis no longer runs off during “Dunston Checks Out”.',
          'User Interface: fixed an issue that showed fewer groups than intended in group finder.',
          'What it means for players: repeated dungeon farming is slowed (5 entries per hour); Stormshroud Armor wearers lose energy; the Demonic Aegis trick no longer works.'])},
 'nov19': {
  'fr': ('19 novembre 2026',
         'Lot publié sur la page officielle, alors titrée « WoW: Forever Hotfixes - November 19, 2026 », et relayé par Kaivax sur les forums officiels US et EU le 20 novembre à 05:00 heure de Paris. Les noms de sorts, PNJ, objets et quêtes sont repris en anglais.',
         ['Camping : le Seed Hybridizer est de nouveau activé ; l’hybridation de graines a des valeurs ajustées et peut désormais échouer ; les Scarce Herb Seeds ne peuvent plus y être utilisées.',
          'Classes : Paladin Vindicte : Two-Handed Weapon Specialization augmente bien tous les dégâts du Sacré infligés avec une arme à deux mains équipée.',
          'Donjons : City of Dalaran : Shade of the Archmage ne disparaît plus dès l’entrée en combat ; The Shaper’s Terrace : le Poison Shock de Vitrix inflige moins de dégâts.',
          'Ennemis : Shimmering Flats, un Silithid Hive Drone coincé sous le monde près de Rustmaul Dig Site est corrigé ; Riverglades, Mosh’gra peut de nouveau donner son butin rare.',
          'Objets : les Motes of Unstable Magic deviennent liées ; la Squall-breaker’s Potion peut être détruite.',
          'Quêtes : corrections à Booty Bay (Rix Xizzix après « Rift Away »), dans les Alterac Mountains (nouvel Ensorcelled Parchment pour « Stormpike’s Deciphering ») et pour « Hunting for Ectoplasm » (bon type de créature).',
          'Races : les Skyborne obtiennent bien la réduction de 10 % au rang Honoré sur les compétences de monte Apprenti et Compagnon vendues par Genn Fairweather sur Zephras Isle ; Tauren : Cultivation réussit plus souvent sur les herbes maîtrisées et fonctionne avec le Purple Lotus.',
          'Conséquences pour les joueurs : l’hybridation de graines revient mais devient moins sûre ; les Skyborne au rang Honoré paient enfin moins cher leur monte ; les Motes of Unstable Magic ne s’échangent plus.']),
  'en': ('November 19, 2026',
         'Batch published on the official page, then titled “WoW: Forever Hotfixes - November 19, 2026”, and relayed by Kaivax on the official US and EU forums on November 20 at 05:00 Paris time.',
         ['Camping: the Seed Hybridizer has been re-enabled; Seed Hybridization has adjusted values and can now fail; Scarce Herb Seeds can no longer be used in it.',
          'Classes: Retribution Paladin: Two-Handed Weapon Specialization now correctly increases all Holy damage dealt while a two-handed weapon is equipped.',
          'Dungeons: City of Dalaran: Shade of the Archmage no longer despawns on entering combat; The Shaper’s Terrace: Vitrix’s Poison Shock deals less damage.',
          'Enemies: Shimmering Flats, a Silithid Hive Drone stuck under the world near Rustmaul Dig Site is fixed; Riverglades, Mosh’gra can drop rare loot again.',
          'Items: Motes of Unstable Magic are now soulbound; Squall-breaker’s Potion can now be deleted.',
          'Quests: fixes in Booty Bay (Rix Xizzix after “Rift Away”), Alterac Mountains (new Ensorcelled Parchment for “Stormpike’s Deciphering”) and for “Hunting for Ectoplasm” (correct creature type).',
          'Races: Skyborne now correctly receive the Honored 10% discount on Apprentice and Journeyman Riding sold by Genn Fairweather on Zephras Isle; Tauren: Cultivation succeeds more reliably on herbs you have the skill for and works on Purple Lotus.',
          'What it means for players: seed hybridization is back but riskier; Honored Skyborne finally pay less for riding; Motes of Unstable Magic can no longer be traded.'])},
 'nov17': {
  'fr': ('17 novembre 2026',
         'Lot publié sur la page officielle, alors titrée « WoW: Forever Hotfixes - November 17, 2026 », et relayé par Kaivax sur les forums officiels US et EU le 18 novembre à 04:24 heure de Paris. Les noms de sorts, PNJ, objets et quêtes sont repris en anglais.',
         ['Camping : impossible désormais de dormir à dos de monture sur le Cozy Sleeping Bag ; il peut être posé à certains endroits comme les pièges de chasseur et affiche une aura de repos dans sa zone d’effet.',
          'Classes : Might of Stormwind et Warchief’s Blessing s’annulent bien à la mort et ne s’appliquent plus aux non-joueurs ; Chaman : Flurry ne perd plus de charges à tort quand les attaques du totem Windfury touchent.',
          'Donjons : la vie et les dégâts des ennemis de Upper Blackrock Spire étaient nettement trop bas ; c’est corrigé, et Blizzard précise que le donjon demande de nouveau un groupe complet et appliqué.',
          'Ennemis : corrections de créatures coincées dans la roche à Thousand Needles (Pesterhide Snarler, Needles Cougar, Gravelsnout Digger/Surveyor).',
          'Objets : les prêtres Ombre peuvent tenir Night Watchman’s Torch ; Escape Plan a des valeurs de portée et de dégâts correctes ; Whiteout Staff et Crackling Staff ont désormais les mêmes caractéristiques (25 Endurance, 25 Intelligence, 74 puissance des sorts). Paladin : Soulforge Armor (set de donjon amélioré pour tanks) donne de la puissance des sorts au lieu de la Force, Blizzard voulant que les tanks paladins misent davantage sur la puissance des sorts.',
          'Legacy : la Reagent Economy ne doit plus cesser de fonctionner au hasard.',
          'JcJ : plus de monture dans les salles de départ du Goulet des Chanteguerres ; les quêtes de la bataille d’Alterac exigent le niveau 58.',
          'Métiers : correction de certaines conversions de Waylaid Crate ; Forge : la quête « The Old Ways » donne la recette Orcish War Leggings via un objet (remplacement auprès de Sumi), Bronze Mace devient liée quand équipée ; Herboristerie : Cultivation fonctionne sur Mageroyal ; Dépeçage : quelques créatures non dépeçables ne le sont plus.',
          'Quêtes : corrections pour « The Manor, Ravenholdt » (lettre de Mathias Shaw), « Blisters on the Land », « Step One: Rock », « A New Ore Sample », « Agamaggan’s Blood » (plus une quête de donjon) et plusieurs quêtes Shen’dralas (« Powering the Pylons », « Heart of Crystal », « Going Home ») ; Spectral Iron Ore apparaît plus souvent et se détecte.',
          'Interface : la liste d’ignorés persiste après déconnexion.',
          'Conséquences pour les joueurs : les groupes qui enchaînaient Upper Blackrock Spire facilement doivent s’attendre à un donjon nettement plus dur ; les tanks paladins équipés du Soulforge Armor gagnent de la puissance des sorts.']),
  'en': ('November 17, 2026',
         'Batch published on the official page, then titled “WoW: Forever Hotfixes - November 17, 2026”, and relayed by Kaivax on the official US and EU forums on November 18 at 04:24 Paris time.',
         ['Camping: mounted players can no longer sleep on the Cozy Sleeping Bag; it can be placed in specific spots such as hunter traps and shows a Resting aura within its area of effect.',
          'Classes: Might of Stormwind and Warchief’s Blessing now correctly cancel on death and no longer apply to non-players; Shaman: Flurry no longer wrongly loses stacks when Windfury totem attacks land.',
          'Dungeons: enemy health and damage in Upper Blackrock Spire were significantly too low; this is fixed, and Blizzard says the dungeon again needs a full group of diligent players.',
          'Enemies: fixes for creatures stuck in rocks in Thousand Needles (Pesterhide Snarler, Needles Cougar, Gravelsnout Digger/Surveyor).',
          'Items: Shadow priests can hold Night Watchman’s Torch; Escape Plan has correct range and damage; Whiteout Staff and Crackling Staff now share the same stats (25 Stamina, 25 Intellect, 74 Spell Power). Paladin: Soulforge Armor (upgraded tank dungeon set) now has Spell Power instead of Strength, as Blizzard leans into Paladin tanks favoring Spell Power.',
          'Legacy: the Reagent Economy should no longer randomly stop working.',
          'PvP: no more mounting in the Warsong Gulch starting rooms; the Battle for Alterac Valley quests require level 58.',
          'Professions: fix for some Waylaid Crate conversions; Blacksmithing: “The Old Ways” grants the Orcish War Leggings recipe via an item (replacement from Sumi), Bronze Mace is now bind-on-equip; Herbalism: Cultivation works on Mageroyal; Skinning: a few normally unskinnable creatures can no longer be skinned.',
          'Quests: fixes for “The Manor, Ravenholdt” (Mathias Shaw’s letter), “Blisters on the Land”, “Step One: Rock”, “A New Ore Sample”, “Agamaggan’s Blood” (no longer a dungeon quest) and several Shen’dralas quests (“Powering the Pylons”, “Heart of Crystal”, “Going Home”); Spectral Iron Ore spawns more and can be tracked.',
          'UI: ignore lists now persist after logging out.',
          'What it means for players: groups used to clearing Upper Blackrock Spire easily should expect a much harder dungeon; Paladin tanks wearing Soulforge Armor gain Spell Power.'])},
}
KEY = {
 'nov20': {'fr': '20 novembre : chaque joueur ne peut plus réinitialiser et entrer dans un donjon que 5 fois par heure (contre 10) ; bonus de la Stormshroud Armor réduit, bug de Demonic Aegis corrigé, forge de Summit of Eternity de nouveau utilisable.',
           'en': 'November 20: players can now reset and enter each dungeon at most 5 times per hour (was 10); Stormshroud Armor bonus lowered, Demonic Aegis bug fixed, Summit of Eternity forge usable again.'},
 'nov19': {'fr': '19 novembre : le Seed Hybridizer est réactivé, avec des valeurs ajustées et un risque d’échec ; corrections pour le paladin Vindicte, des donjons, des quêtes, la réduction de monte des Skyborne et la Cultivation des Taurens.',
           'en': 'November 19: the Seed Hybridizer is re-enabled, with adjusted values and a chance to fail; fixes for Retribution Paladin, dungeons, quests, the Skyborne riding discount and Tauren Cultivation.'},
 'nov17': {'fr': '17 novembre : la vie et les dégâts des ennemis de Upper Blackrock Spire sont corrigés à la hausse ; le Soulforge Armor des tanks paladins donne de la puissance des sorts au lieu de la Force ; corrections de JcJ, de métiers et de quêtes.',
           'en': 'November 17: Upper Blackrock Spire enemy health and damage are raised back; the Paladin tanks’ Soulforge Armor now gives Spell Power instead of Strength; PvP, profession and quest fixes.'},
}
ANAL = {
 'fr': [' Le rétablissement de la difficulté de Upper Blackrock Spire est le changement le plus visible du lot du 17 novembre ; le reste confirme une direction assumée pour les tanks paladins, orientés puissance des sorts.',
        ' Le lot du 19 novembre est plus léger ; le retour encadré du Seed Hybridizer, avec un risque d’échec, suggère une volonté de limiter les abus économiques plutôt que de retirer la fonction.',
        ' La limite de réinitialisation réduite de moitié le 20 novembre vise visiblement le farm intensif d’instances ; c’est un levier économique de plus après l’affaire du Repaire des Noiregueules (Blackmaw Hold), au prix d’un peu de souplesse pour les groupes qui recommencent souvent.'],
 'en': [' Restoring Upper Blackrock Spire’s difficulty is the most visible change in the November 17 batch; the rest confirms a deliberate direction for Paladin tanks, built around Spell Power.',
        ' The November 19 batch is lighter; bringing back the Seed Hybridizer with a failure chance suggests a wish to curb economic abuse rather than remove the feature.',
        ' Halving the reset limit on November 20 clearly targets intensive instance farming; it is one more economic lever after the Blackmaw Hold affair, at some cost in flexibility for groups that restart often.'],
}
TL = {
 'fr': [('2026-11-17', '17 novembre 2026', 'Lot du 17 novembre (Upper Blackrock Spire, tanks paladins, JcJ, métiers, quêtes, interface), publié le 18 novembre à 04:24 heure de Paris.', 'nov17'),
        ('2026-11-19', '19 novembre 2026', 'Lot du 19 novembre (Seed Hybridizer, Vindicte, donjons, objets, quêtes, Skyborne, Cultivation), publié le 20 novembre à 05:00 heure de Paris.', 'nov19'),
        ('2026-11-20', '20 novembre 2026', 'Lot du 20 novembre (Blade Flurry, Demonic Aegis, limite de 5 donjons par heure, Stormshroud Armor, forge de Summit of Eternity, quêtes, recherche de groupe), publié le 21 novembre à 01:18 heure de Paris.', 'nov20')],
 'en': [('2026-11-17', '17 November 2026', 'November 17 batch (Upper Blackrock Spire, Paladin tanks, PvP, professions, quests, UI), published on November 18 at 04:24 Paris time.', 'nov17'),
        ('2026-11-19', '19 November 2026', 'November 19 batch (Seed Hybridizer, Retribution, dungeons, items, quests, Skyborne, Cultivation), published on November 20 at 05:00 Paris time.', 'nov19'),
        ('2026-11-20', '20 November 2026', 'November 20 batch (Blade Flurry, Demonic Aegis, 5 dungeons per hour limit, Stormshroud Armor, Summit of Eternity forge, quests, group finder), published on November 21 at 01:18 Paris time.', 'nov20')],
}
INTRO = {'fr': [('désormais titrée « WoW: Forever Hotfixes - November 16, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11, 13 et 16 novembre.',
                 'désormais titrée « WoW: Forever Hotfixes - November 20, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11, 13, 16, 17, 19 et 20 novembre.')],
         'en': [('now titled “WoW: Forever Hotfixes - November 16, 2026”. It covers the November 5, 6, 8, 9, 10, 11, 13 and 16 batches.',
                 'now titled “WoW: Forever Hotfixes - November 20, 2026”. It covers the November 5, 6, 8, 9, 10, 11, 13, 16, 17, 19 and 20 batches.')]}
SEARCH = {'fr': ' 17 19 20 novembre upper blackrock spire soulforge armor seed hybridizer stormshroud armor demonic aegis blade flurry summit of eternity reinitialisation donjon 5 par heure goulet des chanteguerres cultivation skyborne',
          'en': ' november 17 19 20 upper blackrock spire soulforge armor seed hybridizer stormshroud armor demonic aegis blade flurry summit of eternity dungeon reset 5 per hour warsong gulch cultivation skyborne'}
# Podcast : épisode 8
POD = {
 'fr': (' Épisode 8 (19 nov.) : le point sur les classes, avec Aidan Moon (concepteur de jeu senior) et Kris Zierhut (concepteur de jeu principal), animé par Countdown To Classic, pour une discussion consacrée à la conception des classes.',
        'Sean Copeland (historien en chef de l’univers), animé par Countdown To Classic.'),
 'en': (' Episode 8 (Nov 19): catching up on classes, with Senior Game Designer Aidan Moon and Principal Game Designer Kris Zierhut, hosted by Countdown To Classic, in a conversation about class design.',
        'Sean Copeland (Lore Historian Lead), hosted by Countdown To Classic.'),
}
POD_SRC = {'fr': ('https://news.blizzard.com/fr-fr/article/24317086', 'Découvrez le podcast WoW: Forever – Le point sur les classes', 'fr'),
           'en': ('https://news.blizzard.com/en-us/article/24317086', 'Watch the WoW: Forever Podcast – Catching up on Classes', 'en')}

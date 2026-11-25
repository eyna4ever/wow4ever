import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-raids', code: 'AR05', category: 'instances', subcategory: 'raids',
  title: C('Raids et donjons de World of Warcraft: Forever', 'Raids and dungeons in World of Warcraft: Forever'),
  description: C('Neuf donjons à cinq joueurs au lancement, puis trois raids le 9 décembre 2026 : profondeurs des Saisons, sommet d’Hyjal et repaire d’Onyxia.', 'Nine five-player dungeons at launch, then three raids on December 9, 2026: Barrow Deeps, Hyjal Summit and Onyxia’s Lair.'),
  slug: C('raids-et-donjons', 'raids-and-dungeons'), illustration: 'instances',
  relations: ['forever-raid-barrow-deeps', 'forever-raid-hyjal-summit', 'forever-dungeon-hall-of-thanes', 'forever-creature-onyxia', 'article-forever-calendar', 'article-forever-zones'],
  lead: I('World of Warcraft: Forever ouvre neuf nouveaux donjons à cinq joueurs, du niveau 13 au niveau 60. Le 9 décembre 2026, trois raids de niveau 60 s’ajoutent : les profondeurs des Saisons (10 joueurs), le sommet d’Hyjal (20 joueurs) et le repaire d’Onyxia (40 joueurs).',
    'World of Warcraft: Forever opens nine new five-player dungeons from level 13 to 60. On December 9, 2026 three level-60 raids unlock: Barrow Deeps (10 players), Hyjal Summit (20 players) and Onyxia’s Lair (40 players).',
    'bz-dungeons', 'bz-raids', 'bz-whatsnext'),
  keyPoints: [
    I('Neuf donjons à cinq joueurs, répartis entre les royaumes de l’Est et Kalimdor.', 'Nine five-player dungeons across the Eastern Kingdoms and Kalimdor.', 'bz-dungeons'),
    I('Raids ouverts le 9 décembre 2026 aux personnages de niveau 60.', 'Raids unlock on December 9, 2026 for level-60 characters.', 'bz-raids', 'bz-whatsnext'),
    I('Le repaire d’Onyxia exige l’amulette drakefeu en plus du niveau 60.', 'Onyxia’s Lair also requires the Drakefire Amulet, not only level 60.', 'bz-raids'),
    I('D’autres raids et donjons sont annoncés après le lancement, sans date.', 'More raids and dungeons are announced after launch, with no date.', 'bz-whatsnext')
  ],
  sections: [
    S('donjons', 'Les neuf donjons du lancement', 'The nine launch dungeons',
      P('Blizzard présente neuf donjons à cinq joueurs « ancrés dans le World of Warcraft d’origine », avec de nouvelles menaces, quêtes et aventures.', 'Blizzard presents nine five-player dungeons “rooted in the original World of Warcraft”, with new threats, quests and adventures.', 'bz-dungeons'),
      TB(C('Donjons annoncés et niveaux', 'Announced dungeons and levels'), [C('Donjon', 'Dungeon'), C('Niveaux', 'Levels'), C('Lieu', 'Location')], [
        [C('Salle des Thanes', 'Hall of Thanes'), C('13–18'), C('Sous Forgefer, Dun Morogh', 'Beneath Ironforge, Dun Morogh')],
        [C('Ruines de Lordaeron', 'Ruins of Lordaeron'), C('15–20'), C('Ruines au-dessus de Fossoyeuse, Clairières de Tirisfal', 'Ruins above the Undercity, Tirisfal Glades')],
        [C('Excavations', 'Excavation Site'), C('24–29'), C('Au-dessus des excavations de Whelgar, Paluns', 'Above Whelgar’s Excavation, Wetlands')],
        [C('Cité de Dalaran', 'City of Dalaran'), C('28–33'), C('Montagnes d’Alterac', 'Alterac Mountains')],
        [C('La cité Submergée', 'The Drowned City'), C('35–40'), C('Au large de la vallée de Strangleronce', 'Off the coast of Stranglethorn Vale')],
        [C('Bastion Krol’dok', 'Krol’dok Stronghold'), C('40–45'), C('Rives Claires', 'Riverglades')],
        [C('Prison d’Alcaz', 'Alcaz Prison'), C('48–53'), C('Île d’Alcaz, marécage d’Âprefange', 'Alcaz Island, Dustwallow Marsh')],
        [C('Repaire des Noiregueules', 'Blackmaw Hold'), C('55–60'), C('Azshara')],
        [C('La terrasse du Façonneur', 'Shaper’s Terrace'), C('58–60'), C('Cratère d’Un’Goro', 'Un’Goro Crater')]
      ], 'bz-dungeons'),
      P('Pour la salle des Thanes, l’Alliance accède facilement depuis sa capitale ; la Horde doit traverser un territoire allié.', 'For Hall of Thanes, Alliance players reach the entrance easily from their capital; Horde groups must travel into Alliance territory.', 'bz-dungeons')
    ),
    S('raids', 'Les trois raids du 9 décembre', 'The three December 9 raids',
      TB(C('Raids de niveau 60', 'Level-60 raids'), [C('Raid'), C('Taille', 'Size'), C('Lieu', 'Location')], [
        [C('Profondeurs des Saisons', 'Barrow Deeps'), C('10 joueurs', '10 players'), C('Sous le mont Hyjal ; entrées via Hyjal, Berceau-de-l’Hiver et repaire des Noiregueules', 'Within Mount Hyjal; entrances via Hyjal, Winterspring and Blackmaw Hold')],
        [C('Sommet d’Hyjal', 'Hyjal Summit'), C('20 joueurs', '20 players'), C('Sommet du mont Hyjal, près de Nordrassil', 'Summit of Mount Hyjal near Nordrassil')],
        [C('Repaire d’Onyxia', 'Onyxia’s Lair'), C('40 joueurs', '40 players'), C('Marécage d’Âprefange', 'Dustwallow Marsh')]
      ], 'bz-raids'),
      P('Les profondeurs des Saisons sont la prison où Illidan Stormrage a été détenu dix mille ans. Les joueurs y descendent pour apprendre ce qu’il est advenu de ceux qui y sont restés.', 'Barrow Deeps is the prison that held Illidan Stormrage for 10,000 years; players descend to learn what became of those left behind.', 'bz-raids'),
      P('Pour entrer dans le repaire d’Onyxia, il faut d’abord obtenir l’amulette drakefeu. Blizzard détaille le parcours d’attunement dans l’article sur les raids.', 'Entering Onyxia’s Lair first requires earning the Drakefire Amulet; Blizzard details that attunement in the raid overview.', 'bz-raids')
    ),
    S('suite', 'Après le 9 décembre', 'After December 9',
      P('La feuille de route annonce d’autres raids et donjons après le lancement, sans calendrier publié.', 'The roadmap lists more raids and dungeons after launch, with no published schedule.', 'bz-whatsnext')
    )
  ],
  confirmed: [
    I('Neuf donjons à cinq joueurs au lancement, avec les niveaux listés ci-dessus.', 'Nine five-player dungeons at launch, with the level ranges listed above.', 'bz-dungeons'),
    I('Trois raids le 9 décembre : 10, 20 et 40 joueurs.', 'Three raids on December 9: 10, 20 and 40 players.', 'bz-raids'),
    I('Amulette drakefeu requise pour Onyxia.', 'Drakefire Amulet required for Onyxia.', 'bz-raids')
  ],
  pending: [
    Q('Aucune date n’est donnée pour les raids et donjons suivants, ni pour la « refonte d’un raid emblématique ».', 'No date is given for later raids and dungeons, or for the “revamped iconic raid”.'),
    Q('Les sources ne publient pas encore les détails de chaque boss hors aperçus généraux.', 'Sources do not yet publish full boss details beyond the general overviews.')
  ],
  notes: [
    I('L’annonce de la bêta parlait d’une fermeture « through October 21 » ; le forum a confirmé le 23 octobre. Cela n’affecte pas les dates de raids.', 'The beta announcement said “through October 21”; the forum confirmed October 23. That does not change the raid dates.', 'bz-beta', 'forum-kaivax1023')
  ],
  dates: [
    D('2026-10-20', 'Publication des aperçus donjons et raids.', 'Dungeon and raid overviews published.', 'bz-dungeons', 'bz-raids'),
    D('2026-11-04', 'Lancement (donjons disponibles avec le jeu).', 'Launch (dungeons available with the game).', 'bz-roundup'),
    D('2026-12-09', 'Ouverture des trois raids de niveau 60.', 'The three level-60 raids unlock.', 'bz-raids', 'bz-whatsnext')
  ]
}
];

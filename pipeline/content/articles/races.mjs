import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-skyborne', code: 'AR07', category: 'races', subcategory: 'skyborne',
  title: C('Les Éolides : race jouable de l’île de Zéphras', 'The Skyborne: playable race of Zephras Isle'),
  description: C('Nouvelle race de Forever. Le choix de faction ouvre le chaman (Horde) ou le mage (Alliance), avec un départ niveau 1–12 sur Zéphras.', 'Forever’s new race. Faction choice unlocks Shaman (Horde) or Mage (Alliance), with a level 1–12 start on Zephras.'),
  slug: C('les-eolides', 'the-skyborne'), illustration: 'races',
  relations: ['forever-race-skyborne', 'forever-zone-zephras-isle', 'article-forever-zones', 'article-forever-classes'],
  lead: I('Les Éolides (Skyborne) sont la nouvelle race jouable de World of Warcraft: Forever. Ils commencent sur l’île de Zéphras (niveaux 1–12). En choisissant la Horde (Sculpte-vents) ou l’Alliance (Ordre suprême), le joueur débloque le chaman ou le mage, en plus des classes communes.',
    'The Skyborne are World of Warcraft: Forever’s new playable race. They begin on Zephras Isle (levels 1–12). Choosing the Horde (Windshaper) or the Alliance (High Order) unlocks Shaman or Mage, on top of the shared classes.',
    'bz-skyborne', 'bz-whatsnext'),
  keyPoints: [
    I('Départ : île de Zéphras, niveaux 1 à 12.', 'Start: Zephras Isle, levels 1–12.', 'bz-skyborne'),
    I('Horde (Sculpte-vents) : druide, chasseur, voleur, chaman, guerrier.', 'Horde (Windshaper): Druid, Hunter, Rogue, Shaman, Warrior.', 'bz-skyborne'),
    I('Alliance (Ordre suprême) : druide, chasseur, mage, voleur, guerrier.', 'Alliance (High Order): Druid, Hunter, Mage, Rogue, Warrior.', 'bz-skyborne'),
    I('Ancestralité : exilés bien-nés liés aux esprits élémentaires du vent, civilisation dans Mur-Céleste.', 'Ancestry: Highborne exiles bound to elemental wind spirits, with a civilization in Skywall.', 'bz-skyborne')
  ],
  sections: [
    S('origine', 'Origine et crise', 'Origin and crisis',
      P('Il y a des milliers d’années, des exilés bien-nés ont scellé un pacte avec des esprits élémentaires du vent et bâti une civilisation dans Mur-Céleste. Sur Zéphras, cette civilisation est en crise : les esprits de l’air ont disparu, des structures anciennes faiblissent, et les communautés se divisent sur la suite.',
        'Thousands of years ago, Highborne exiles forged a pact with elemental wind spirits and built a civilization within Skywall. On Zephras that civilization is in crisis: the air spirits have vanished, ancient structures are failing, and communities are divided over what comes next.',
        'bz-skyborne')
    ),
    S('factions', 'Deux visions, deux factions', 'Two visions, two factions',
      TB(C('Éolides selon la faction', 'Skyborne by faction'), [C('Branche', 'Branch'), C('Faction'), C('Classes')], [
        [C('Sculpte-vents', 'Windshaper'), C('Horde'), C('Druide, chasseur, voleur, chaman, guerrier', 'Druid, Hunter, Rogue, Shaman, Warrior')],
        [C('Ordre suprême', 'High Order'), C('Alliance'), C('Druide, chasseur, mage, voleur, guerrier', 'Druid, Hunter, Mage, Rogue, Warrior')]
      ], 'bz-skyborne'),
      P('Les deux branches partagent aussi de nouvelles formes de druide Éolide, des raciales, des personnalisations, des voix et une danse propre.', 'Both branches also share new Skyborne druid forms, racials, customizations, voices and their own dance.', 'bz-skyborne', 'bz-whatsnext')
    ),
    S('acces', 'Accès et offres', 'Access and upgrades',
      P('L’accès à la race et à l’expérience de départ de Zéphras figure dans les packs héroïque et épique des Éolides, ainsi que dans la collection Warcraft Forever.', 'Access to the race and the Zephras starting experience is included in the Skyborne Heroic and Epic Packs and in the Warcraft Forever Collection.', 'bz-roundup')
    )
  ],
  confirmed: [
    I('Race jouable avec départ 1–12 sur Zéphras.', 'Playable race with a 1–12 start on Zephras.', 'bz-skyborne'),
    I('Chaman réservé à la branche Horde ; mage à la branche Alliance.', 'Shaman locked to the Horde branch; Mage to the Alliance branch.', 'bz-skyborne')
  ],
  pending: [
    Q('Le détail numérique de chaque raciale n’est pas entièrement publié dans l’article de présentation.', 'Full numeric detail for every racial is not fully published in the preview article.'),
    Q('Les sources ne listent pas ici toutes les options cosmétiques une à une.', 'Sources do not list every cosmetic option one by one here.')
  ],
  notes: [],
  dates: [
    D('2026-09-22', 'Publication de la présentation des Éolides.', 'Skyborne preview published.', 'bz-skyborne'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
},
{
  id: 'article-forever-races-classes', code: 'AR16', category: 'races', subcategory: 'races-et-classes',
  title: C('Races et classes : toutes les combinaisons de World of Warcraft: Forever', 'Races and classes: every combination in World of Warcraft: Forever'),
  description: C('Neuf races jouables, neuf classes et six combinaisons inédites (mage orc, démoniste troll, paladin mort-vivant, chasseur humain, prêtre gnome, chaman nain), plus les deux branches des Éolides.', 'Nine playable races, nine classes and six new combinations (Orc Mage, Troll Warlock, Undead Paladin, Human Hunter, Gnome Priest, Dwarf Shaman), plus the two Skyborne branches.'),
  slug: C('races-et-classes', 'races-and-classes'), illustration: 'races',
  relations: ['forever-race-human', 'forever-race-dwarf', 'forever-race-gnome', 'forever-race-night-elf', 'forever-race-orc', 'forever-race-tauren', 'forever-race-troll', 'forever-race-undead', 'forever-race-skyborne', 'article-forever-skyborne', 'article-forever-classes'],
  lead: I('World of Warcraft: Forever propose neuf classes et neuf races jouables : les huit races du jeu d’origine et les Éolides. Blizzard publie pour chaque faction un tableau des combinaisons autorisées. Six d’entre elles n’existaient pas dans le World of Warcraft d’origine.',
    'World of Warcraft: Forever offers nine classes and nine playable races: the eight original races plus the Skyborne. Blizzard publishes a table of allowed combinations for each faction. Six of them did not exist in original World of Warcraft.',
    'bz-hero', 'bz-return'),
  keyPoints: [
    I('Nouvelles combinaisons côté Alliance : chasseur humain, chaman nain, prêtre gnome.', 'New Alliance combinations: Human Hunter, Dwarf Shaman, Gnome Priest.', 'bz-return'),
    I('Nouvelles combinaisons côté Horde : mage orc, démoniste troll, paladin mort-vivant.', 'New Horde combinations: Orc Mage, Troll Warlock, Undead Paladin.', 'bz-return'),
    I('Les Éolides rejoignent l’une ou l’autre faction : chaman côté Horde (Sculpte-vents), mage côté Alliance (Ordre suprême).', 'The Skyborne join either faction: Shaman on the Horde side (Windshapers), Mage on the Alliance side (High Order).', 'bz-hero'),
    I('Jouer un Éolide demande le pack héroïque des Éolides ou une offre supérieure.', 'Playing a Skyborne requires the Skyborne Heroic Pack or a higher upgrade.', 'bz-return')
  ],
  sections: [
    S('horde', 'Horde : races et classes', 'Horde: races and classes',
      TB(C('Classes disponibles par race (Horde)', 'Available classes by race (Horde)'), [C('Race'), C('Classes'), C('Nouveauté Forever', 'New in Forever')], [
        [C('Orc / Orque', 'Orc'), C('Chasseur, mage, voleur, chaman, démoniste, guerrier', 'Hunter, Mage, Rogue, Shaman, Warlock, Warrior'), C('Mage')],
        [C('Tauren / Taurène', 'Tauren'), C('Druide, chasseur, chaman, guerrier', 'Druid, Hunter, Shaman, Warrior'), C('—')],
        [C('Troll / Trollesse', 'Troll'), C('Chasseur, mage, prêtre, voleur, chaman, démoniste, guerrier', 'Hunter, Mage, Priest, Rogue, Shaman, Warlock, Warrior'), C('Démoniste', 'Warlock')],
        [C('Mort-vivant / Morte-vivante', 'Undead'), C('Mage, paladin, prêtre, voleur, démoniste, guerrier', 'Mage, Paladin, Priest, Rogue, Warlock, Warrior'), C('Paladin')],
        [C('Éolide (Sculpte-vents)', 'Skyborne (Windshaper)'), C('Druide, chasseur, voleur, chaman, guerrier', 'Druid, Hunter, Rogue, Shaman, Warrior'), C('Nouvelle race', 'New race')]
      ], 'bz-hero'),
      P('Blizzard décrit la Horde comme une alliance de circonstance entre des peuples fiers, attachés à la force et à l’honneur, qui veulent bâtir un monde où vivre libres.', 'Blizzard describes the Horde as an alliance of convenience between proud peoples who value strength and honour and want to build a world where they can live free.', 'bz-hero')
    ),
    S('alliance', 'Alliance : races et classes', 'Alliance: races and classes',
      TB(C('Classes disponibles par race (Alliance)', 'Available classes by race (Alliance)'), [C('Race'), C('Classes'), C('Nouveauté Forever', 'New in Forever')], [
        [C('Humain / Humaine', 'Human'), C('Chasseur, mage, paladin, prêtre, voleur, démoniste, guerrier', 'Hunter, Mage, Paladin, Priest, Rogue, Warlock, Warrior'), C('Chasseur', 'Hunter')],
        [C('Nain / Naine', 'Dwarf'), C('Chasseur, paladin, prêtre, voleur, chaman, guerrier', 'Hunter, Paladin, Priest, Rogue, Shaman, Warrior'), C('Chaman', 'Shaman')],
        [C('Gnome'), C('Mage, prêtre, voleur, démoniste, guerrier', 'Mage, Priest, Rogue, Warlock, Warrior'), C('Prêtre', 'Priest')],
        [C('Elfe de la nuit', 'Night Elf'), C('Druide, chasseur, prêtre, voleur, guerrier', 'Druid, Hunter, Priest, Rogue, Warrior'), C('—')],
        [C('Éolide (Ordre suprême)', 'Skyborne (High Order)'), C('Druide, chasseur, mage, voleur, guerrier', 'Druid, Hunter, Mage, Rogue, Warrior'), C('Nouvelle race', 'New race')]
      ], 'bz-hero'),
      P('Pour Blizzard, les peuples de l’Alliance partagent des traditions de noblesse, d’honneur, de foi, de justice et de sacrifice, et mettent leur savoir technique, arcanique et spirituel au service d’un monde juste.', 'Blizzard presents the Alliance peoples as sharing traditions of nobility, honour, faith, justice and sacrifice, putting their technical, arcane and spiritual knowledge toward a just world.', 'bz-hero')
    ),
    S('choisir', 'Choisir sa combinaison', 'Choosing a combination',
      P('Blizzard conseille de penser à la fois à la classe voulue et aux races qui peuvent la jouer. Chaque race a ses propres traits raciaux, qui s’ajoutent à la classe choisie.', 'Blizzard suggests thinking about both the class you want and the races that can play it. Each race has its own racial traits on top of the chosen class.', 'bz-hero'),
      P('À la création de chaque personnage, on choisit aussi des modèles en haute ou en définition standard. Ce choix ne touche que l’apparence et se modifie plus tard dans les options ou chez un coiffeur.', 'When creating each character you also choose high- or standard-definition models. This only affects appearance and can be changed later in the options or at a Barbershop.', 'bz-golive')
    )
  ],
  confirmed: [
    I('Neuf classes et neuf races jouables, avec les tableaux de combinaisons publiés par Blizzard.', 'Nine classes and nine playable races, with the combination tables published by Blizzard.', 'bz-hero'),
    I('Six combinaisons inédites : chasseur humain, chaman nain, prêtre gnome, mage orc, démoniste troll, paladin mort-vivant.', 'Six new combinations: Human Hunter, Dwarf Shaman, Gnome Priest, Orc Mage, Troll Warlock, Undead Paladin.', 'bz-return'),
    I('Accès aux Éolides avec le pack héroïque ou une offre supérieure.', 'Skyborne access with the Heroic Pack or a higher upgrade.', 'bz-return')
  ],
  pending: [
    Q('Blizzard ne publie pas de fiche complète et à jour des traits raciaux de chaque race. Seules des modifications ponctuelles figurent dans les notes de développement de la bêta.', 'Blizzard has not published a complete, up-to-date sheet of every race’s racial traits. Only individual changes appear in the beta development notes.'),
    Q('Les noms français officiels des traits raciaux ne sont pas publiés dans ces sources.', 'Official French names for racial traits are not published in these sources.')
  ],
  notes: [],
  dates: [
    D('2026-09-22', 'Publication de l’article sur les races et les classes.', 'Races and classes article published.', 'bz-hero'),
    D('2026-10-29', 'Récapitulatif des nouvelles combinaisons dans le guide du retour.', 'New combinations recapped in the returning players guide.', 'bz-return')
  ]
}
];

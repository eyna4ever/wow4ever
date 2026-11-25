import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-quests', code: 'AR11', category: 'quests', subcategory: 'progression',
  title: C('Quêtes et progression : plus de mille nouvelles aventures, héritage et Valthalak', 'Quests and progression: a thousand+ new adventures, Legacy and Valthalak'),
  description: C('Parcours 1–60 enrichi, système d’héritage à l’échelle du compte, et suites de quêtes documentées comme celle du seigneur Valthalak.', 'Enriched 1–60 journey, account-wide Legacy system, and documented questlines such as Lord Valthalak’s.'),
  slug: C('quetes-et-progression', 'quests-and-progression'), illustration: 'quests',
  relations: ['forever-quests-new-adventures', 'forever-progression-legacy', 'forever-questline-lord-valthalak', 'article-forever-legacy', 'article-forever-zones'],
  lead: I('Forever annonce plus de mille nouvelles quêtes sur le parcours du niveau 1 au niveau 60. À côté de ces aventures, le système d’héritage récompense des défis à l’échelle du compte. Des suites précises, comme celle du seigneur Valthalak, sont aussi documentées.',
    'Forever announces more than a thousand new quests across levels 1–60. Alongside them, the Legacy system rewards account-wide challenges. Specific questlines, such as Lord Valthalak’s, are also documented.',
    'bz-whatsnext', 'bz-legacy'),
  keyPoints: [
    I('Plus de mille nouvelles quêtes annoncées pour les niveaux 1–60.', 'More than a thousand new quests announced for levels 1–60.', 'bz-whatsnext'),
    I('L’héritage s’ouvre en général au niveau 25, ou via d’autres seuils (métier, carte).', 'Legacy usually unlocks at level 25, or via other thresholds (tradeskill, map).', 'bz-legacy'),
    I('Plafond annoncé : 16 points d’héritage dépensés par personnage au lancement.', 'Announced launch cap: 16 Legacy Points spent per character.', 'bz-legacy'),
    I('D’autres quêtes 1–60 sont prévues après le lancement.', 'Additional 1–60 quests are planned after launch.', 'bz-whatsnext')
  ],
  sections: [
    S('aventure', 'Nouvelles aventures 1–60', 'New adventures 1–60',
      P('Blizzard situe Forever après Warcraft III Reforged: Forsaken Kingdom et avant Cœur de Magma. Les joueurs reviennent sur les continents d’origine avec des histoires nouvelles ou réinventées.',
        'Blizzard sets Forever after Warcraft III Reforged: Forsaken Kingdom and before Molten Core. Players return to the original continents with new or reimagined stories.',
        'bz-whatsnext', 'bz-roundup'),
      P('Les Rives Claires à elles seules comptent plus de 150 nouvelles quêtes sur une large part des niveaux 30 à 40.', 'The Riverglades alone hold more than 150 new quests across much of levels 30–40.', 'bz-whatsnext')
    ),
    S('heritage', 'Progression par l’héritage', 'Legacy progression',
      P('Le système d’héritage est une progression horizontale à l’échelle du compte : défis, avantages et récompenses. Il s’ouvre dès le premier point d’héritage, souvent au niveau 25, ou en atteignant 150 dans un métier principal hors récolte, ou en explorant toute la carte.',
        'Legacy is account-wide horizontal progression: challenges, perks and rewards. It opens with the first Legacy Point—often at level 25, or by reaching 150 in a non-gathering primary tradeskill, or by exploring the entire world map.',
        'bz-legacy'),
      P('Les personnages hors Extrême partagent les points acquis, mais choisissent leurs avantages séparément. Le plafond de dépense annoncé au lancement est de 16 points par personnage.',
        'Non-Hardcore characters share earned points but choose perks separately. The announced launch spending cap is 16 points per character.',
        'bz-legacy')
    ),
    S('valthalak', 'Suite du seigneur Valthalak', 'Lord Valthalak questline',
      P('Une suite de quêtes du seigneur Valthalak est recensée dans la base documentaire du wiki, avec ses sources. Comme pour toute suite précise, seuls les éléments confirmés par ces sources sont repris.',
        'A Lord Valthalak questline is recorded in the wiki’s documentary set with its sources. As with any specific line, only what those sources confirm is repeated.',
        'bz-deepdive')
    )
  ],
  confirmed: [
    I('Plus de mille nouvelles quêtes annoncées.', 'More than a thousand new quests announced.', 'bz-whatsnext'),
    I('Système d’héritage avec plafond de 16 points dépensés par personnage au lancement.', 'Legacy system with a 16-point per-character spending cap at launch.', 'bz-legacy')
  ],
  pending: [
    Q('Le détail de chaque défi d’héritage n’est pas recopié ici ; voir l’article héritage et les fiches liées.', 'Every Legacy challenge is not copied here; see the Legacy article and related notices.'),
    Q('Des quêtes supplémentaires 1–60 sont annoncées après le lancement, sans date.', 'Additional 1–60 quests are announced after launch, with no date.')
  ],
  notes: [],
  dates: [
    D('2026-09-13', 'Annonce du volume de quêtes et des zones.', 'Quest volume and zones announced.', 'bz-whatsnext'),
    D('2026-09-23', 'Présentation du système d’héritage.', 'Legacy system presented.', 'bz-legacy'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
}
];

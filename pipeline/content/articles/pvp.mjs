import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-pvp', code: 'AR06', category: 'pvp', subcategory: 'progression',
  title: C('JcJ dans World of Warcraft: Forever : honneur, rangs et îles des Sombrelances', 'PvP in World of Warcraft: Forever: honor, ranks and Darkspear Islands'),
  description: C('Deux progressions distinctes (honneur et points de rang), saisons, et un champ de bataille 15 contre 15 annoncé.', 'Two distinct progressions (honor and rank points), seasons, and an announced 15-versus-15 battleground.'),
  slug: C('jcj-honneur-et-rangs', 'pvp-honor-and-ranks'), illustration: 'pvp',
  relations: ['forever-pvp-honor', 'forever-pvp-rank-points', 'forever-pvp-darkspear-islands', 'forever-guide-track-pvp', 'article-forever-rulesets'],
  lead: I('Le JcJ de Forever reprend l’esprit du système d’honneur d’origine, en le simplifiant. La progression se sépare en deux : l’honneur (monnaie) et les points de rang (progression de rang). Un nouveau champ de bataille, les îles des Sombrelances, est annoncé en 15 contre 15.',
    'Forever PvP keeps the spirit of the original Honor System while simplifying it. Progression splits into honor (currency) and rank points (rank progression). A new battleground, Darkspear Islands, is announced as 15-versus-15.',
    'bz-pvp', 'bz-whatsnext'),
  keyPoints: [
    I('L’honneur s’obtient en combattant, en terminant des champs de bataille et des quêtes JcJ.', 'Honor comes from combat, finishing battlegrounds and PvP quests.', 'bz-pvp'),
    I('Les points de rang font progresser le rang ; ils sont distincts de l’honneur.', 'Rank points advance rank and are separate from honor.', 'bz-pvp'),
    I('Îles des Sombrelances : 15 contre 15, contrôle de positions et capture de drapeaux.', 'Darkspear Islands: 15-versus-15, control points and flag captures.', 'bz-whatsnext', 'bz-roundup'),
    I('Des mises à jour JcJ sont prévues après le lancement, sans date.', 'PvP updates are planned after launch, with no date.', 'bz-whatsnext')
  ],
  sections: [
    S('honneur', 'Honneur', 'Honor',
      P('L’honneur est une monnaie gagnée en participant au contenu JcJ : combats, champs de bataille et quêtes associées. Les champs de bataille mis en avant pendant leurs semaines de fête donnent davantage d’honneur.', 'Honor is currency earned by taking part in PvP: combat, battlegrounds and related quests. Highlighted battlegrounds during their holiday weeks award increased Honor.', 'bz-pvp'),
      P('Blizzard indique avoir revu les gains d’honneur entre champs de bataille pour les rendre plus cohérents, afin que les joueurs puissent profiter de toute la liste de cartes.', 'Blizzard says Honor gains across battlegrounds were reviewed for more consistent rates, so players can enjoy the full map list.', 'bz-pvp')
    ),
    S('rangs', 'Points de rang et saisons', 'Rank points and seasons',
      P('Les points de rang font progresser le rang du personnage. Ils ne se confondent pas avec l’honneur dépensé chez les vendeurs.', 'Rank points advance a character’s rank. They are not the same as honor spent at vendors.', 'bz-pvp'),
      P('Le système est pensé pour donner des raisons de jouer tout au long de la saison, tout en restant familier.', 'The system is meant to give reasons to play throughout the season while staying familiar.', 'bz-pvp')
    ),
    S('sombrelances', 'Îles des Sombrelances', 'Darkspear Islands',
      P('Les îles des Sombrelances sont annoncées comme un champ de bataille 15 contre 15 mêlant contrôle de positions et capture de drapeaux. Aucune carte tactique détaillée n’est publiée dans les sources consultées.', 'Darkspear Islands is announced as a 15-versus-15 battleground combining control points and flag captures. No detailed tactical map appears in the sources consulted.', 'bz-whatsnext', 'bz-roundup')
    ),
    S('ensembles', 'Lien avec les ensembles de règles', 'Link with rulesets',
      P('Sur l’ensemble JcJ, un compte ne crée des personnages que d’une seule faction. Les champs de bataille peuvent mélanger des joueurs d’ensembles différents, sauf l’Extrême.', 'On the PvP ruleset an account only creates characters of one faction. Battlegrounds may mix players from other rulesets, except Hardcore.', 'bz-rulesets')
    )
  ],
  confirmed: [
    I('Honneur = monnaie ; points de rang = progression de rang.', 'Honor = currency; rank points = rank progression.', 'bz-pvp'),
    I('Champ de bataille 15 contre 15 des îles des Sombrelances annoncé.', 'Darkspear Islands 15-versus-15 battleground announced.', 'bz-whatsnext')
  ],
  pending: [
    Q('Le calendrier exact des saisons et des récompenses de rang n’est pas entièrement publié.', 'The exact season calendar and full rank rewards are not fully published.'),
    Q('Aucune carte officielle détaillée des îles des Sombrelances n’est dans les sources consultées.', 'No detailed official Darkspear Islands map is in the sources consulted.')
  ],
  notes: [],
  dates: [
    D('2026-10-07', 'Publication de l’aperçu de la progression JcJ.', 'PvP progression overview published.', 'bz-pvp'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
}
];

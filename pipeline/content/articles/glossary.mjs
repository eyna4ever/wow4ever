import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-legacy', code: 'AR12', category: 'glossary', subcategory: 'legacy',
  title: C('Points d’héritage et jeu sans royaumes : lexique Forever', 'Legacy Points and realmless play: Forever glossary'),
  description: C('Définitions sourcées : points d’héritage, défis, avantages, ensembles de règles, et ce qui change en Extrême.', 'Sourced definitions: Legacy Points, challenges, perks, rulesets, and what changes in Hardcore.'),
  slug: C('lexique-heritage-et-ensembles', 'legacy-and-ruleset-glossary'), illustration: 'glossary',
  relations: ['forever-glossary-legacy-points', 'forever-glossary-realmless', 'forever-progression-legacy', 'article-forever-rulesets', 'article-forever-quests'],
  lead: I('Forever introduit des termes qui ne se réduisent pas aux notices courtes. Cet article fixe le sens des points d’héritage et du passage aux ensembles de règles, d’après les textes officiels uniquement.',
    'Forever introduces terms that short notices cannot fully carry. This article fixes the meaning of Legacy Points and the move to rulesets, from official texts only.',
    'bz-legacy', 'bz-rulesets', 'bz-deepdive'),
  keyPoints: [
    I('Un point d’héritage s’obtient en accomplissant un défi d’héritage.', 'A Legacy Point is earned by completing a Legacy Challenge.', 'bz-legacy'),
    I('Points acquis et plafond de dépense par personnage sont deux notions distinctes.', 'Earned points and each character’s spending cap are separate ideas.', 'bz-legacy'),
    I('Plus d’écran de royaume : on choisit d’abord un ensemble de règles.', 'No realm screen: you first choose a ruleset.', 'bz-rulesets'),
    I('L’Extrême aura des règles d’héritage différentes.', 'Hardcore will use different Legacy rules.', 'bz-legacy', 'bz-rulesets')
  ],
  sections: [
    S('points', 'Points d’héritage', 'Legacy Points',
      P('Les défis d’héritage fonctionnent de façon proche des hauts faits d’autres versions de WoW. Les points gagnés alimentent des avantages et récompenses. Au lancement, Blizzard annonce un plafond de 16 points dépensés par personnage.',
        'Legacy Challenges work similarly to achievements in other WoW versions. Earned points feed perks and rewards. At launch Blizzard announces a spending cap of 16 points per character.',
        'bz-legacy'),
      P('On ouvre le panneau via l’icône d’héritage (bouclier) ou le raccourci par défaut Y, une fois le premier point obtenu.',
        'Open the panel via the Legacy icon (shield) or the default hotkey Y once the first point is earned.',
        'bz-legacy')
    ),
    S('sans-royaumes', 'Sans royaumes', 'Realmless play',
      P('Forever remplace le choix de royaume par un choix d’ensemble de règles. Chaque ensemble est un vaste écosystème, pas un royaume unique géant. Voir le guide dédié pour le comparatif Normal / JcJ / JdR / JdR-JcJ / Extrême.',
        'Forever replaces realm selection with a ruleset choice. Each ruleset is a broad ecosystem, not one giant realm. See the dedicated guide for the Normal / PvP / RP / RP-PvP / Hardcore comparison.',
        'bz-rulesets', 'bz-deepdive')
    ),
    S('extreme', 'Cas de l’Extrême', 'Hardcore case',
      P('Ce qui est gagné en Extrême peut servir ailleurs, mais la progression des autres ensembles ne remonte pas vers l’Extrême. Les règles exactes d’héritage en Extrême restent à préciser à la sortie de ce mode.',
        'Hardcore progress can carry elsewhere, but progress from other rulesets does not flow back into Hardcore. Exact Hardcore Legacy rules remain to be detailed when that mode ships.',
        'bz-rulesets', 'bz-legacy')
    )
  ],
  confirmed: [
    I('Points d’héritage issus de défis ; plafond de dépense 16 au lancement.', 'Legacy Points from challenges; spending cap 16 at launch.', 'bz-legacy'),
    I('Ensembles de règles à la place des royaumes.', 'Rulesets instead of realms.', 'bz-rulesets')
  ],
  pending: [
    Q('Liste complète des défis et avantages : voir l’article officiel héritage ; non recopiée ici.', 'Full challenge and perk lists: see the official Legacy article; not copied here.'),
    Q('Date de l’Extrême non annoncée.', 'Hardcore date not announced.')
  ],
  notes: [],
  dates: [
    D('2026-09-21', 'Article sur les ensembles de règles (mis à jour le 22/10).', 'Rulesets article (updated 10/22).', 'bz-rulesets'),
    D('2026-09-23', 'Article sur l’héritage.', 'Legacy article.', 'bz-legacy')
  ]
}
];

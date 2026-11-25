import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-creatures', code: 'AR13', category: 'creatures', subcategory: 'documented',
  title: C('Créatures documentées : Onyxia et la famille des renards', 'Documented creatures: Onyxia and the fox family'),
  description: C('Rubrique encore mince dans les sources officielles. Ce wiki ne retient que ce qui est publié : Onyxia comme défi d’héritage / raid, et la famille de familiers renards.', 'A still-thin official category. This wiki only keeps what is published: Onyxia as a Legacy / raid challenge, and the fox pet family.'),
  slug: C('creatures-documentees', 'documented-creatures'), illustration: 'creatures',
  relations: ['forever-creature-onyxia', 'forever-creature-family-fox', 'article-forever-raids', 'forever-class-hunter'],
  lead: I('Les sources officielles de Forever parlent peu des créatures hors contexte de quête, de raid ou de familier. Pour éviter d’inventer un bestiaire, cet article se limite à Onyxia et à la famille des renards, déjà présentes dans la base documentaire.',
    'Official Forever sources say little about creatures outside quest, raid or pet context. To avoid inventing a bestiary, this article sticks to Onyxia and the fox family, already in the documentary set.',
    'bz-legacy', 'bz-raids'),
  keyPoints: [
    I('Vaincre Onyxia figure parmi les défis d’héritage de la catégorie Raids.', 'Defeating Onyxia is listed among raid-category Legacy Challenges.', 'bz-legacy'),
    I('Onyxia est aussi le boss du raid 40 joueurs du 9 décembre, dans le marécage d’Âprefange.', 'Onyxia is also the December 9 40-player raid boss in Dustwallow Marsh.', 'bz-raids'),
    I('Une famille de familiers renards est documentée pour les chasseurs.', 'A fox pet family is documented for Hunters.', 'bz-cls-hd'),
    I('Aucun autre bestiaire officiel complet n’est publié dans les sources consultées.', 'No other complete official bestiary appears in the sources consulted.', 'bz-legacy')
  ],
  sections: [
    S('onyxia', 'Onyxia', 'Onyxia',
      P('Le repaire d’Onyxia ouvre le 9 décembre 2026 pour 40 joueurs de niveau 60, après obtention de l’amulette drakefeu. Vaincre Onyxia est aussi cité comme défi d’héritage.',
        'Onyxia’s Lair unlocks on December 9, 2026 for 40 level-60 players after earning the Drakefire Amulet. Defeating Onyxia is also cited as a Legacy Challenge.',
        'bz-raids', 'bz-legacy')
    ),
    S('renards', 'Famille des renards', 'Fox family',
      P('L’aperçu du chasseur documente une famille de familiers renards. Au-delà de cette mention, ce wiki n’ajoute pas de statistiques de familier non publiées.',
        'The Hunter preview documents a fox pet family. Beyond that mention, this wiki does not add unpublished pet statistics.',
        'bz-cls-hd')
    ),
    S('limites', 'Limites documentaires', 'Documentary limits',
      P('Tant que Blizzard ne publie pas davantage, la rubrique créatures reste volontairement courte. Mieux vaut une rubrique mince que des fiches inventées.',
        'Until Blizzard publishes more, the creatures category stays intentionally short. A thin category beats invented notices.',
        'bz-legacy')
    )
  ],
  confirmed: [
    I('Onyxia : raid 40 joueurs le 9 décembre + défi d’héritage.', 'Onyxia: 40-player raid on December 9 + Legacy Challenge.', 'bz-raids', 'bz-legacy'),
    I('Famille de familiers renards mentionnée pour le chasseur.', 'Fox pet family mentioned for Hunters.', 'bz-cls-hd')
  ],
  pending: [
    Q('Pas de bestiaire officiel étendu dans les sources du 24–27 octobre 2026.', 'No extended official bestiary in the 24–27 October 2026 sources.'),
    Q('Compétences précises des familiers renards non détaillées ici.', 'Exact fox-pet abilities not detailed here.')
  ],
  notes: [],
  dates: [
    D('2026-09-23', 'Défis d’héritage (dont raids) présentés.', 'Legacy Challenges (including raids) presented.', 'bz-legacy'),
    D('2026-10-20', 'Aperçu du raid Onyxia.', 'Onyxia raid overview.', 'bz-raids'),
    D('2026-12-09', 'Ouverture du repaire d’Onyxia.', 'Onyxia’s Lair unlocks.', 'bz-raids')
  ]
}
];

import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-classes', code: 'AR09', category: 'classes', subcategory: 'overview',
  title: C('Les neuf classes de World of Warcraft: Forever', 'The nine classes of World of Warcraft: Forever'),
  description: C('Synthèse des présentations officielles : neuf classes, voies de talents, et ce que Blizzard a déjà détaillé — sans inventer de chiffres.', 'Summary of the official previews: nine classes, talent paths, and what Blizzard has detailed — with no invented numbers.'),
  slug: C('classes-forever', 'forever-classes'), illustration: 'classes',
  relations: ['forever-class-hunter', 'forever-class-druid', 'forever-class-warrior', 'forever-class-paladin', 'forever-class-mage', 'forever-class-shaman', 'forever-class-rogue', 'forever-class-warlock', 'article-forever-skyborne'],
  lead: I('Forever propose neuf classes. Blizzard publie des présentations détaillées par classe. Ce wiki résume uniquement ce qui est écrit dans ces articles : les voies, les intentions de design, et les changements annoncés. Aucune statistique inventée.',
    'Forever ships nine classes. Blizzard publishes per-class deep dives. This wiki only summarizes what those articles state: talent paths, design intent and announced changes. No invented statistics.',
    'bz-cls-hd', 'bz-cls-pw', 'bz-cls-ms', 'bz-cls-rw', 'bz-cls-pal'),
  keyPoints: [
    I('Neuf classes jouables au lancement.', 'Nine playable classes at launch.', 'bz-cls-hd'),
    I('Chaque présentation détaille des voies de talents et des axes de design.', 'Each preview details talent paths and design goals.', 'bz-cls-pw', 'bz-cls-hd'),
    I('Les Éolides n’ouvrent le chaman qu’en Horde et le mage qu’en Alliance.', 'Skyborne only unlock Shaman on Horde and Mage on Alliance.', 'bz-skyborne'),
    I('Une contradiction FR/EN sur Flèches multiples / Visée est recensée et exclue des fiches.', 'A FR/EN contradiction on Multi-Shot / Aimed Shot is logged and kept out of the notices.', 'bz-cls-hd')
  ],
  sections: [
    S('liste', 'Classes couvertes par les aperçus', 'Classes covered by the previews',
      P('Des présentations officielles existent notamment pour le chasseur, le prêtre, le mage/démoniste (et apparentés), le voleur et le paladin. D’autres classes sont jouables ; ce wiki ne leur invente pas de détail absent des sources.',
        'Official previews exist notably for Hunter, Priest, Mage/Warlock-related coverage, Rogue and Paladin. Other classes are playable; this wiki does not invent detail the sources omit.',
        'bz-cls-hd', 'bz-cls-pw', 'bz-cls-ms', 'bz-cls-rw', 'bz-cls-pal'),
      TB(C('Exemples tirés des aperçus', 'Examples from the previews'), [C('Classe', 'Class'), C('Voies citées', 'Paths cited'), C('Point marquant annoncé', 'Notable announced point')], [
        [C('Chasseur', 'Hunter'), C('Maîtrise des bêtes, Précision, Survie', 'Beast Mastery, Marksmanship, Survival'), C('Pièges utilisables pendant le combat', 'Traps usable during combat')],
        [C('Paladin'), C('Sacré, Protection, Vindicte', 'Holy, Protection, Retribution'), C('Sceaux et jugements renforcés', 'Seals and Judgements strengthened')],
        [C('Prêtre', 'Priest'), C('selon l’aperçu officiel', 'per the official preview'), C('Détails dans la fiche dédiée (brouillon CL3 à corriger)', 'Details in the dedicated notice (CL3 draft still to correct)')]
      ], 'bz-cls-hd', 'bz-cls-pal', 'bz-cls-pw')
    ),
    S('methode', 'Méthode de ce wiki', 'This wiki’s method',
      P('Chaque fiche de classe courte cite ses URL. Les articles longs ne recopient pas les tableaux de chiffres absents des sources. En cas de contradiction entre versions linguistiques, le détail litigieux est exclu.',
        'Each short class notice cites its URLs. Long articles do not copy number tables the sources do not provide. Where language versions contradict, the disputed detail is left out.',
        'bz-cls-hd')
    )
  ],
  confirmed: [
    I('Neuf classes au lancement.', 'Nine classes at launch.', 'bz-cls-hd'),
    I('Présentations officielles publiées pour plusieurs classes entre fin septembre et mi-octobre 2026.', 'Official previews published for several classes from late September to mid-October 2026.', 'bz-cls-hd', 'bz-cls-pal')
  ],
  pending: [
    Q('Toutes les classes n’ont pas encore le même niveau de détail public.', 'Not every class yet has the same level of public detail.'),
    Q('La fiche prêtre (CL3) reste un brouillon à corriger : formulation sur la bêta.', 'The priest notice (CL3) remains a draft to correct: wording about the beta.')
  ],
  notes: [
    I('Contradiction FR/EN sur Flèches multiples/Multi-Shot et Visée/Aimed Shot dans l’article 24301515 ; exclue des fiches.', 'FR/EN contradiction on Multi-Shot and Aimed Shot in article 24301515; excluded from notices.', 'bz-cls-hd')
  ],
  dates: [
    D('2026-09-30', 'Aperçus chasseur et prêtre.', 'Hunter and priest previews.', 'bz-cls-hd', 'bz-cls-pw'),
    D('2026-10-08', 'Aperçus mage/démoniste et voleur.', 'Mage/warlock and rogue previews.', 'bz-cls-ms', 'bz-cls-rw'),
    D('2026-10-15', 'Aperçu paladin.', 'Paladin preview.', 'bz-cls-pal')
  ]
}
];

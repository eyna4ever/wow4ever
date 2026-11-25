import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-items', code: 'AR14', category: 'items', subcategory: 'documented',
  title: C('Objets documentés : anneau de Ladimore, talisman anti-worgens et récompenses d’abonnement', 'Documented items: Ladimore ring, Worgenbane talisman and subscription rewards'),
  description: C('Seuls les objets explicitement décrits par Blizzard sont repris. Pas de listes de butin inventées.', 'Only items Blizzard explicitly describes are included. No invented loot tables.'),
  slug: C('objets-documentes', 'documented-items'), illustration: 'items',
  relations: ['forever-item-ladimore-heirloom-ring', 'forever-item-worgenbane-talisman', 'article-forever-campfire', 'forever-news-access'],
  lead: I('Forever n’a pas encore de base d’objets publique complète. Ce wiki ne catalogue que les objets nommés dans les articles officiels : récompenses de quête mises en avant, objets de campement, et bonus d’offres d’abonnement liés à Forever.',
    'Forever does not yet have a full public item database. This wiki only lists items named in official articles: highlighted quest rewards, camp objects, and subscription-offer bonuses tied to Forever.',
    'bz-deepdive', 'bz-campfire', 'bz-sub-year'),
  keyPoints: [
    I('Anneau d’héritage de Ladimore : récompense annoncée pour lanceurs de sorts (quête de Mor’Ladim, bois de la Pénombre).', 'Ladimore Heirloom Ring: announced caster reward (Mor’ladim quest, Duskwood).', 'bz-deepdive'),
    I('Talisman de fléau des Worgens : objet nommé dans les sources du lot objets.', 'Worgenbane Talisman: item named in the items batch sources.', 'bz-deepdive'),
    I('Objets de campement (meule, bannière, encens…) : voir l’article campement.', 'Camp objects (sharpening wheel, banner, incense…): see the camping article.', 'bz-campfire'),
    I('Offre d’abonnement 12 mois : tabard, sac à dos et mascotte Azurky pour Forever, une fois le jeu lancé.', '12-month subscription offer: tabard, backpack and Azurky pet for Forever once the game launches.', 'bz-sub-year')
  ],
  sections: [
    S('quetes', 'Récompenses de quête mises en avant', 'Highlighted quest rewards',
      P('L’anneau d’héritage de Ladimore est cité comme récompense pour les lanceurs de sorts dans la quête liée à Mor’Ladim au bois de la Pénombre. Le talisman de fléau des Worgens apparaît dans le même ensemble documentaire.',
        'The Ladimore Heirloom Ring is cited as a caster reward on the Mor’ladim-related quest in Duskwood. The Worgenbane Talisman appears in the same documentary set.',
        'bz-deepdive')
    ),
    S('abonnement', 'Bonus d’abonnement liés à Forever', 'Subscription bonuses tied to Forever',
      P('L’offre spéciale d’abonnement 6 ou 12 mois inclut des bonus utilisables dans Forever après le lancement de novembre : tabard de l’Exploration éternelle, sac à dos d’explorateur éternel et mascotte Azurky (noms anglais : Tabard of Eternal Exploration, Eternal Explorer’s Backpack, Azurky).',
        'The special 6- or 12-month subscription offer includes bonuses usable in Forever after the November launch: Tabard of Eternal Exploration, Eternal Explorer’s Backpack and the Azurky pet.',
        'bz-sub-year'),
      P('Les bonus arrivent au plus tard le 31 octobre 2026 et doivent être récupérés avant le 30 avril 2027. L’accès au jeu Forever reste inclus avec l’abonnement ou le temps de jeu à partir du 4 novembre.',
        'Bonuses arrive by October 31, 2026 and must be redeemed by April 30, 2027. Forever access itself remains included with a subscription or Game Time from November 4.',
        'bz-sub-year', 'bz-roundup')
    ),
    S('limites', 'Ce que ce wiki ne fait pas', 'What this wiki does not do',
      P('Aucune table de butin de donjon ou de raid n’est inventée. Quand Blizzard publiera davantage, de nouvelles fiches pourront s’ajouter en brouillon.',
        'No dungeon or raid loot table is invented. When Blizzard publishes more, new draft notices can be added.',
        'bz-raids')
    )
  ],
  confirmed: [
    I('Anneau de Ladimore et talisman anti-worgens nommés dans les sources deep dive / lots.', 'Ladimore ring and Worgenbane talisman named in deep-dive / batch sources.', 'bz-deepdive'),
    I('Bonus cosmétiques Forever dans l’offre d’abonnement 12 mois.', 'Forever cosmetic bonuses in the 12-month subscription offer.', 'bz-sub-year')
  ],
  pending: [
    Q('Stats précises des objets de quête : non recopiées si absentes du texte officiel consulté.', 'Exact item stats: not copied when absent from the consulted official text.'),
    Q('Tables de butin des raids du 9 décembre : non publiées dans l’aperçu raids.', 'Loot tables for the December 9 raids: not published in the raid overview.')
  ],
  notes: [
    I('L’article d’abonnement date du 15 octobre 2026 ; il est ajouté au catalogue de sources le 27 octobre lors de la reprise.', 'The subscription article is dated October 15, 2026; it was added to the source catalog on October 27 during the resume.', 'bz-sub-year')
  ],
  dates: [
    D('2026-09-13', 'Deep dive (exemples d’objets de quête).', 'Deep dive (quest-item examples).', 'bz-deepdive'),
    D('2026-10-15', 'Offre d’abonnement avec bonus Forever.', 'Subscription offer with Forever bonuses.', 'bz-sub-year'),
    D('2026-10-31', 'Date limite d’arrivée des bonus d’abonnement.', 'Deadline for subscription bonuses to arrive.', 'bz-sub-year'),
    D('2026-11-04', 'Lancement ; accès Forever via abonnement / temps de jeu.', 'Launch; Forever access via subscription / Game Time.', 'bz-roundup')
  ]
}
];

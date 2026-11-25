import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-campfire', code: 'AR10', category: 'professions', subcategory: 'camping',
  title: C('Campement et artisanat : le feu de cuisine devient un lieu partagé', 'Camping and crafting: the cooking fire becomes a shared campsite'),
  description: C('Le système de campement transforme le feu de cuisine en camp de base. Jusqu’à trois objets artisanaux y apportent des services ; les effets de classe équivalents ne se cumulent pas.', 'The camping system turns the cooking fire into a shared camp. Up to three crafted objects provide services there; equivalent class buffs do not stack.'),
  slug: C('campement-et-artisanat', 'camping-and-crafting'), illustration: 'professions',
  relations: ['forever-professions-camping', 'forever-professions-blueprints', 'article-forever-items'],
  lead: I('Dans Forever, le feu de cuisine devient un feu de camp de base. Une fois posé, il crée un campement partagé où les joueurs proches peuvent se reposer et profiter d’objets artisanaux avant de repartir. Blizzard veut que ces pauses deviennent des rencontres utiles.',
    'In Forever, the cooking fire becomes a Basic Campfire. Once placed it creates a shared campsite where nearby players can rest and benefit from crafted camp features before moving on. Blizzard wants those pauses to become useful encounters.',
    'bz-campfire', 'bz-deepdive'),
  keyPoints: [
    I('Un feu de camp de base accueille jusqu’à trois objets spéciaux fabriqués.', 'A Basic Campfire supports up to three special crafted objects.', 'bz-campfire'),
    I('Chaque joueur proche peut en ajouter un.', 'Each nearby player may add one.', 'bz-campfire'),
    I('Exemples : meule (force), bannière de faction (esprit), encens d’herboriste.', 'Examples: sharpening wheel (Strength), faction banner (Spirit), herbalist incense.', 'bz-campfire'),
    I('Des recettes et plans avancés sont annoncés à part.', 'Advanced recipes and blueprints are announced separately.', 'bz-deepdive')
  ],
  sections: [
    S('fonctionnement', 'Fonctionnement du campement', 'How camping works',
      P('Le système élargit le feu de cuisine de la cuisine. Posé, le feu de camp de base crée un lieu partagé. Les objets de camp donnent aux métiers un rôle plus visible dans le monde.',
        'The system expands Cooking’s cooking fire. Once placed, the Basic Campfire creates a shared space. Camp features give professions a more visible role in the world.',
        'bz-campfire'),
      L(
        I('Un forgeron peut poser une meule qui augmente la Force pendant une heure.', 'A blacksmith can place a Sharpening Wheel that increases Strength for an hour.', 'bz-campfire'),
        I('Un tailleur peut poser une bannière de faction qui augmente l’Esprit.', 'A tailor can place a Faction Banner that increases Spirit.', 'bz-campfire'),
        I('Un herboriste peut poser un encens.', 'An herbalist can place incense.', 'bz-campfire')
      ),
      P('Les effets de classe équivalents ne se cumulent pas avec ces objets de camp.', 'Equivalent class buffs do not stack with these camp objects.', 'bz-campfire', 'bz-deepdive')
    ),
    S('plans', 'Recettes et plans avancés', 'Recipes and advanced blueprints',
      P('Blizzard annonce aussi des recettes et plans avancés pour l’artisanat. Les fiches courtes du wiki les résument sans inventer de listes de composants non publiées.',
        'Blizzard also announces advanced recipes and blueprints for crafting. The wiki’s short notices summarize them without inventing unpublished reagent lists.',
        'bz-deepdive')
    )
  ],
  confirmed: [
    I('Feu de camp de base + jusqu’à trois objets artisanaux.', 'Basic Campfire + up to three crafted objects.', 'bz-campfire'),
    I('Pas de cumul avec les buffs de classe équivalents.', 'No stacking with equivalent class buffs.', 'bz-campfire')
  ],
  pending: [
    Q('La liste complète des objets de camp par métier n’est pas dans l’article consulté.', 'The full per-profession camp-object list is not in the article consulted.'),
    Q('Les durées et valeurs exactes hors exemples cités restent à confirmer article par article.', 'Exact durations and values beyond the cited examples remain to confirm article by article.')
  ],
  notes: [],
  dates: [
    D('2026-10-21', 'Publication de l’aperçu du campement.', 'Camping preview published.', 'bz-campfire'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
}
];

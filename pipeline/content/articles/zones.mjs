import {P, I, L, C, TB, S, D, Q} from '../helpers.mjs';

export default [
{
  id: 'article-forever-zones', code: 'AR08', category: 'zones', subcategory: 'regions',
  title: C('Zones nouvelles et réinventées : Zéphras, Rives Claires, Hyjal et Shen’dralas', 'New and reimagined zones: Zephras, Riverglades, Hyjal and Shen’dralas'),
  description: C('Quatre régions mises en avant par Blizzard pour le parcours 1–60, avec plus de mille nouvelles quêtes annoncées.', 'Four regions highlighted by Blizzard for the 1–60 journey, with more than a thousand new quests announced.'),
  slug: C('zones-forever', 'forever-zones'), illustration: 'zones',
  relations: ['forever-zone-zephras-isle', 'forever-zone-riverglades', 'forever-zone-mount-hyjal', 'forever-zone-shendralas', 'article-forever-skyborne', 'article-forever-quests'],
  lead: I('Forever renvoie les joueurs sur les continents d’origine, avec des régions nouvelles ou réinventées. Blizzard met surtout en avant l’île de Zéphras, les Rives Claires, le mont Hyjal et Shen’dralas, et annonce plus de mille nouvelles quêtes sur le parcours 1–60.',
    'Forever returns players to the original continents with new or reimagined regions. Blizzard especially highlights Zephras Isle, the Riverglades, Mount Hyjal and Shen’dralas, and announces more than a thousand new quests across levels 1–60.',
    'bz-whatsnext', 'bz-photos'),
  keyPoints: [
    I('Zéphras : départ 1–12 des Éolides, esthétique classique mêlée d’inspiration de Mur-Céleste.', 'Zephras: Skyborne 1–12 start, classic aesthetics mixed with Skywall-inspired architecture.', 'bz-skyborne', 'bz-whatsnext'),
    I('Rives Claires : frontière de milieux de niveaux (milieu des 30 aux milieu des 40), plus de 150 quêtes.', 'Riverglades: mid-30s to mid-40s frontier, more than 150 quests.', 'bz-whatsnext'),
    I('Mont Hyjal : suites de la défaite d’Archimonde, gorge de Murmure-sombre.', 'Mount Hyjal: aftermath of Archimonde’s defeat, Darkwhisper Gorge.', 'bz-whatsnext'),
    I('Shen’dralas : mystère entre Mulgore et Désolace, lié aux Shen’dralar et à Hache-Tripes.', 'Shen’dralas: mystery between Mulgore and Desolace, tied to the Shen’dralar and Dire Maul.', 'bz-whatsnext')
  ],
  sections: [
    S('zephras', 'Île de Zéphras', 'Zephras Isle',
      P('Zéphras sert d’expérience de départ niveaux 1–12. L’architecture mêle l’esthétique classique de Warcraft à des influences de Mur-Céleste. C’est aussi le foyer des Éolides.',
        'Zephras is the level 1–12 starting experience. Its architecture blends classic Warcraft aesthetics with Skywall-inspired design, and it is home to the Skyborne.',
        'bz-skyborne', 'bz-whatsnext')
    ),
    S('rives', 'Rives Claires', 'Riverglades',
      P('Les Rives Claires sont décrites comme une frontière rude de rivières, prairies, routes commerciales, communautés en difficulté et vieilles rancunes. Plus de 150 nouvelles quêtes y couvrent une large part de l’expérience du milieu des niveaux 30 aux milieu des niveaux 40.',
        'The Riverglades are described as a rugged frontier of rivers, grasslands, trade routes, struggling communities and old grudges, with more than 150 new quests across much of the mid-30s to mid-40s experience.',
        'bz-whatsnext'),
      P('Le bastion Krol’dok, donjon niveaux 40–45, s’y trouve.', 'Krol’dok Stronghold, a level 40–45 dungeon, is located there.', 'bz-dungeons')
    ),
    S('hyjal', 'Mont Hyjal', 'Mount Hyjal',
      P('Le mont Hyjal invite à explorer les suites de la défaite d’Archimonde, à traverser la gorge de Murmure-sombre et à contribuer à l’avenir d’une terre en reconstruction. Les profondeurs des Saisons et le sommet d’Hyjal s’y rattachent pour les raids.',
        'Mount Hyjal invites players to explore the aftermath of Archimonde’s defeat, travel through Darkwhisper Gorge and help shape the future of a recovering land. Barrow Deeps and Hyjal Summit raids are tied to it.',
        'bz-whatsnext', 'bz-raids')
    ),
    S('shendralas', 'Shen’dralas', 'Shen’dralas',
      P('Shen’dralas révèle un mystère longtemps caché entre Mulgore et Désolace, lié aux Shen’dralar, à Eldre’Thalas / Hache-Tripes et aux tribus centaures de la région.',
        'Shen’dralas uncovers a long-hidden mystery between Mulgore and Desolace, tied to the Shen’dralar, Eldre’Thalas / Dire Maul and the centaur tribes of the region.',
        'bz-whatsnext')
    )
  ],
  confirmed: [
    I('Plus de mille nouvelles quêtes annoncées sur le parcours 1–60.', 'More than a thousand new quests announced across levels 1–60.', 'bz-whatsnext'),
    I('Quatre régions mises en avant : Zéphras, Rives Claires, Hyjal, Shen’dralas.', 'Four highlighted regions: Zephras, Riverglades, Hyjal, Shen’dralas.', 'bz-whatsnext')
  ],
  pending: [
    Q('La liste exhaustive de toutes les sous-zones et PNJ n’est pas publiée.', 'A full list of every subzone and NPC is not published.'),
    Q('D’autres mises à jour de contenu extérieur sont annoncées après le lancement, sans date.', 'Further outdoor content updates are announced after launch, with no date.')
  ],
  notes: [],
  dates: [
    D('2026-09-13', 'Présentation des zones dans la conférence « L’avenir ».', 'Zones presented in the “What’s Next” panel.', 'bz-whatsnext'),
    D('2026-11-04', 'Lancement.', 'Launch.', 'bz-roundup')
  ]
}
];

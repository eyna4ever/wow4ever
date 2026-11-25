/**
 * Wowkipedia v2 — information architecture (proposal, branch refonte-v2, 30/10/2026).
 * Four plain sections under the home page: Actualités · Le jeu · Guides · Communauté.
 * Every published entry belongs to exactly ONE section (and one sub-section). Entry URLs are unchanged:
 * the section only decides menus, listings and breadcrumbs. A few entries are filed by meaning rather than by
 * their data category (PLACEMENT): two practical guides published as news, and the official Discord article.
 */
export const SECTIONS = Object.freeze([
  {id: 'actualites', label: {fr: 'Actualités', en: 'News'}, categories: ['news']},
  {id: 'jeu', label: {fr: 'Le jeu', en: 'The game'}, slug: {fr: 'le-jeu', en: 'the-game'},
    intro: {fr: 'Tout ce que Blizzard a présenté de World of Warcraft: Forever : classes, races, zones, donjons et raids, créatures, quêtes, JcJ, métiers et objets.', en: 'Everything Blizzard has presented about World of Warcraft: Forever: classes, races, zones, dungeons and raids, creatures, quests, PvP, professions and items.'},
    categories: ['classes', 'races', 'zones', 'instances', 'creatures', 'quests', 'pvp', 'professions', 'items']},
  {id: 'guides', label: {fr: 'Guides', en: 'Guides'}, categories: ['guides', 'glossary']},
  {id: 'communaute', label: {fr: 'Communauté', en: 'Community'}, categories: []}
]);

/** Short, plain labels for the menus (the catalogue keeps its longer category names for page titles). */
export const CATEGORY_LABELS = Object.freeze({
  news: {fr: 'Actualités', en: 'News'},
  classes: {fr: 'Classes', en: 'Classes'}, races: {fr: 'Races', en: 'Races'}, zones: {fr: 'Zones', en: 'Zones'},
  instances: {fr: 'Donjons et raids', en: 'Dungeons and raids'}, creatures: {fr: 'Créatures', en: 'Creatures'},
  quests: {fr: 'Quêtes et progression', en: 'Quests and progression'}, pvp: {fr: 'JcJ', en: 'PvP'},
  professions: {fr: 'Métiers', en: 'Professions'}, items: {fr: 'Objets', en: 'Items'},
  guides: {fr: 'Bien débuter', en: 'Getting started'}, glossary: {fr: 'Glossaire', en: 'Glossary'}
});

/** Entries filed by meaning: entry id -> listing category (URL unchanged). Community entries are listed in the Community menu. */
export const PLACEMENT = Object.freeze({
  'forever-news-starter-guide': 'guides',
  'forever-news-return-guide': 'guides',
  'forever-news-portal-room': 'community',
  'forever-news-podcast-series': 'community' // v10: official podcast, filed under Community
});

export const listingCategory = entry => PLACEMENT[entry.id] ?? entry.category;
export const sectionOf = entry => {
  const cat = listingCategory(entry);
  if (cat === 'community') return 'communaute';
  return SECTIONS.find(section => section.categories.includes(cat))?.id ?? '';
};
export const inListing = (entries, category) => entries.filter(entry => listingCategory(entry) === category);

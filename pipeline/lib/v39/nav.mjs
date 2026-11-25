/**
 * v39 (test UI, Mathieu t386u/t387u) — navigation model for the new interface: main menu, category tree, groups.
 * Pure functions over the PUBLISHED entries only. Nothing here invents data: groups come from existing fields
 * (subcategory) or from text already on the page (the continent written in the zone description, e.g. « Tanaris (Kalimdor) : … »).
 * Empty categories and empty groups are never shown. URLs are the existing ones (categoryPath / entryPath).
 */
import {listingCategory} from '../v2/structure.mjs';

/** Main menu (mockup order). Short UI labels; each item is an existing category with published pages. */
export const MENU = Object.freeze([
  {id: 'zones', label: {fr: 'Zones', en: 'Zones'}},
  {id: 'instances', label: {fr: 'Donjons & raids', en: 'Dungeons & raids'}},
  {id: 'creatures', label: {fr: 'Créatures', en: 'Creatures'}},
  {id: 'professions', label: {fr: 'Métiers', en: 'Professions'}},
  {id: 'items', label: {fr: 'Objets', en: 'Items'}},
  {id: 'quests', label: {fr: 'Quêtes', en: 'Quests'}},
  {id: 'pvp', label: {fr: 'JcJ', en: 'PvP'}},
  {id: 'news', label: {fr: 'Actualités', en: 'News'}}
]);
/** Categories not in the main bar: reachable from « Plus » and from the side tree. */
export const MORE = Object.freeze(['classes', 'races', 'guides', 'glossary']);
export const TREE_ORDER = Object.freeze([...MENU.map(item => item.id), ...MORE]);

/** Continent read from the zone description already published (« Nom (Kalimdor) : … »). */
export function continentOf(entry) {
  if (entry.category !== 'zones' || entry.subcategory !== 'zone') return '';
  const fr = /^[^:(]*\(([^)]+)\)/.exec(entry.description?.fr ?? '')?.[1] ?? '';
  if (/^Kalimdor$/.test(fr)) return 'kalimdor';
  if (/^Royaumes de l[’']Est$/.test(fr)) return 'eastern-kingdoms';
  return '';
}
const continentLabel = (entry, lang) => /^[^:(]*\(([^)]+)\)/.exec(entry.description?.[lang] ?? '')?.[1] ?? '';
export {continentLabel};

export const GROUP_LABELS = Object.freeze({
  'overview': {fr: 'Vue d’ensemble', en: 'Overview'},
  'kalimdor': {fr: 'Kalimdor', en: 'Kalimdor'},
  'eastern-kingdoms': {fr: 'Royaumes de l’Est', en: 'Eastern Kingdoms'},
  'forever-regions': {fr: 'Régions Forever', en: 'Forever regions'},
  'other-zones': {fr: 'Autres zones', en: 'Other zones'},
  'dungeons': {fr: 'Donjons', en: 'Dungeons'},
  'classic-dungeons': {fr: 'Donjons classiques', en: 'Classic dungeons'},
  'raids': {fr: 'Raids', en: 'Raids'},
  'bestiary': {fr: 'Bestiaire', en: 'Bestiary'},
  'recipes': {fr: 'Recettes', en: 'Recipes'},
  'camping': {fr: 'Campement', en: 'Camping'}
});
const GROUP_ORDER = {
  zones: ['kalimdor', 'eastern-kingdoms', 'forever-regions', 'other-zones', 'overview'],
  instances: ['dungeons', 'classic-dungeons', 'raids', 'overview'],
  creatures: ['bestiary', 'overview'],
  professions: ['recipes', 'camping', 'overview']
};
/** Group key of an entry inside its listing category ('' = category shown as a flat list). */
export function groupOf(entry) {
  const cat = listingCategory(entry), sub = entry.subcategory ?? '';
  if (cat === 'zones') {
    if (sub === 'zone') return continentOf(entry) || 'other-zones';
    if (sub === 'region-annoncee' || sub === 'zone-de-depart-annoncee') return 'forever-regions';
    return 'overview';
  }
  if (cat === 'instances') return sub === 'raid-annonce' ? 'raids' : sub === 'donjon-annonce' ? 'dungeons' : sub === 'donjon-classique' ? 'classic-dungeons' : 'overview';
  if (cat === 'creatures') return sub.startsWith('bestiaire') ? 'bestiary' : 'overview';
  if (cat === 'professions') return sub === 'recettes' ? 'recipes' : (sub === 'campement' || sub === 'camping') ? 'camping' : 'overview';
  return '';
}
/** [{key, label, items}] in a stable order; flat categories return one group with key ''. Empty groups are dropped. */
export function groupsFor(cat, entries, lang) {
  const items = entries.filter(entry => listingCategory(entry) === cat)
    .sort((a, b) => a.title[lang].localeCompare(b.title[lang], lang));
  const order = GROUP_ORDER[cat];
  if (!order) return items.length ? [{key: '', label: '', items}] : [];
  return order.map(key => ({key, label: GROUP_LABELS[key][lang], items: items.filter(entry => groupOf(entry) === key)}))
    .filter(group => group.items.length);
}

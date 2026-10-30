/** Browser-safe helpers. Publication validation belongs to documentary.mjs on the server. */
export const SUPPORTED_LANGUAGES = Object.freeze(['fr', 'en']);
export const STORAGE_KEY = 'wow-forever-personal-v1';

export function normalizeQuery(value) {
  return typeof value === 'string'
    ? value.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('en').replace(/\s+/gu, ' ').trim()
    : '';
}

export function normalizeLanguage(value) {
  return SUPPORTED_LANGUAGES.includes(value) ? value : 'fr';
}

export function localized(value, lang = 'fr') {
  if (typeof value === 'string') return value;
  if (!value || typeof value !== 'object') return '';
  return typeof value[normalizeLanguage(lang)] === 'string' ? value[normalizeLanguage(lang)] : '';
}

export function entryTitle(entry, lang = 'fr') {
  return localized(entry?.title, lang);
}

/** Defense in depth; source data must already pass the server publication review gate. */
export function isDisplayableEntry(entry) {
  return Boolean(entry && typeof entry === 'object' &&
    typeof entry.id === 'string' && /^[a-z0-9][a-z0-9-]{2,99}$/.test(entry.id) &&
    entry.status === 'published' && entry.publicationValidated === true &&
    ['fr', 'en'].every(lang => entryTitle(entry, lang).trim() && localized(entry.description, lang).trim()) &&
    Array.isArray(entry.sources) && entry.sources.length > 0 &&
    entry.sources.every(source => safeSourceURL(source?.url) && typeof source?.license === 'string' && source.license.trim() && typeof source?.accessedAt === 'string'));
}

export function safeSourceURL(value) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && url.hostname && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}

export function searchEntries(entries, {query = '', category = '', favoritesOnly = false, favorites = [], lang = 'fr'} = {}) {
  const terms = normalizeQuery(query).split(' ').filter(Boolean);
  const saved = new Set(Array.isArray(favorites) ? favorites : []);
  const language = normalizeLanguage(lang);
  return (Array.isArray(entries) ? entries : []).filter(entry => {
    if (!isDisplayableEntry(entry) || (category && entry.category !== category) || (favoritesOnly && !saved.has(entry.id))) return false;
    const searchable = normalizeQuery(`${entryTitle(entry, language)} ${localized(entry.description, language)} ${entry.subcategory ?? ''} ${localized(entry.searchText, language)}`);
    return terms.every(term => searchable.includes(term));
  }).sort((first, second) => entryTitle(first, language).localeCompare(entryTitle(second, language), language));
}

export function searchSuggestions(entries, options = {}, limit = 5) {
  if (!normalizeQuery(options.query)) return [];
  const count = Number.isSafeInteger(limit) ? Math.max(0, Math.min(10, limit)) : 5;
  return searchEntries(entries, options).slice(0, count);
}

function cleanStrings(value, maximum = 10_000) {
  return Array.isArray(value) ? [...new Set(value.filter(item => typeof item === 'string' && item.length > 0 && item.length < 200))].slice(0, maximum) : [];
}

export function defaultPersonalState() {
  return {version: 1, lang: 'fr', favorites: [], progress: []};
}

export function readPersonalState(storage) {
  try {
    const value = JSON.parse(storage?.getItem(STORAGE_KEY) ?? 'null');
    if (!value || value.version !== 1 || typeof value !== 'object' || Array.isArray(value)) return defaultPersonalState();
    return {version: 1, lang: normalizeLanguage(value.lang), favorites: cleanStrings(value.favorites), progress: cleanStrings(value.progress)};
  } catch { return defaultPersonalState(); }
}

export function savePersonalState(storage, value) {
  const clean = {version: 1, lang: normalizeLanguage(value?.lang), favorites: cleanStrings(value?.favorites), progress: cleanStrings(value?.progress)};
  try {
    if (!storage || typeof storage.setItem !== 'function') return false;
    storage.setItem(STORAGE_KEY, JSON.stringify(clean));
    return true;
  } catch { return false; }
}

export function toggleValue(values, value) {
  const clean = cleanStrings(values);
  return clean.includes(value) ? clean.filter(item => item !== value) : [...clean, value];
}

export function progressKey(entry, index) {
  if (!entry || !Number.isSafeInteger(entry.version) || !Number.isSafeInteger(index) || index < 0) return null;
  return `${entry.id}:v${entry.version}:step:${index}`;
}

export function guideProgress(entry, completed = []) {
  const steps = Array.isArray(entry?.steps) ? entry.steps : [];
  const saved = new Set(Array.isArray(completed) ? completed : []);
  const done = steps.reduce((count, _, index) => count + (saved.has(progressKey(entry, index)) ? 1 : 0), 0);
  return {done, total: steps.length, percent: steps.length ? Math.round(done * 100 / steps.length) : 0};
}

export function relatedEntries(entry, entries) {
  const links = new Set(Array.isArray(entry?.relations) ? entry.relations : []);
  return (Array.isArray(entries) ? entries : []).filter(item => isDisplayableEntry(item) && links.has(item.id) && item.id !== entry?.id);
}

/** Relative-to-root page path of an entry for a language, or null when unsafe. */
export function entryPagePath(entry, lang = 'fr') {
  const path = localized(entry?.url, lang);
  return /^(fr|en)\/[a-z0-9-]+\/[a-z0-9-]+\/$/.test(path) ? path : null;
}

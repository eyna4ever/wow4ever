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

/**
 * v17 — search while typing, tuned for phones: the haystacks are normalized ONCE when the index loads
 * (prepareSearch), so each keystroke only runs String.includes over cached strings (searchPrepared).
 * Same matching rule as searchEntries (every term must appear), ranked: title starts with a term >
 * title contains > description > article text only; then alphabetical. Pure function, no DOM.
 */
export function prepareSearch(entries) {
  return (Array.isArray(entries) ? entries : []).filter(isDisplayableEntry).map(entry => {
    const prepared = {entry};
    for (const lang of SUPPORTED_LANGUAGES) {
      const title = normalizeQuery(entryTitle(entry, lang)), description = normalizeQuery(localized(entry.description, lang));
      prepared[lang] = {title, description, all: `${title} ${description} ${normalizeQuery(entry.subcategory ?? '')} ${normalizeQuery(localized(entry.searchText, lang))}`};
    }
    return prepared;
  });
}
export function searchPrepared(prepared, {query = '', lang = 'fr', limit = 8} = {}) {
  const terms = normalizeQuery(query).split(' ').filter(Boolean);
  if (!terms.length || !Array.isArray(prepared)) return {total: 0, results: []};
  const language = normalizeLanguage(lang);
  const scored = [];
  for (const item of prepared) {
    const text = item[language];
    if (!terms.every(term => text.all.includes(term))) continue;
    let score = 0;
    for (const term of terms) score += text.title.split(' ').some(word => word.startsWith(term)) ? 3 : text.title.includes(term) ? 2 : text.description.includes(term) ? 1 : 0;
    scored.push({score, item});
  }
  scored.sort((a, b) => b.score - a.score || entryTitle(a.item.entry, language).localeCompare(entryTitle(b.item.entry, language), language));
  return {total: scored.length, results: scored.slice(0, Math.max(0, limit)).map(({item}) => item.entry), terms};
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

/**
 * v42b (t409u/t410u) — detailed search: NPCs, creatures, bosses, quests, quest and vendor items, materials, recipes,
 * mounts, pets, toys, legacy rewards, classes, places and page sections, each pointing to its exact anchor.
 * The per-language index (search-detail-fr.json / -en.json) is compact: [name, type, page, anchor, detail];
 * an empty anchor means detailAnchor(name); a numeric detail points into the shared detail table.
 */
export function detailAnchor(name) {
  const base = String(name ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40);
  return `r-${base || 'x'}`;
}
export function prepareDetails(data, lang = 'fr') {
  if (!data || !Array.isArray(data.r) || !Array.isArray(data.pages) || !Array.isArray(data.types)) return null;
  const language = normalizeLanguage(lang), col = language === 'en' ? 2 : 1;
  const types = data.types.map(type => ({key: String(type[0]), label: String(type[col] ?? '')}));
  const pages = data.pages.map(page => ({path: String(page[0] ?? ''), title: String(page[1] ?? '')}));
  const table = Array.isArray(data.d) ? data.d : [];
  const items = [];
  // t411u: hidden French keywords for creatures whose names exist only in English (FR index only; page text unchanged).
  const syn = Array.isArray(data.syn) ? data.syn.filter(pair => Array.isArray(pair) && typeof pair[0] === 'string' && typeof pair[1] === 'string')
    .map(([word, keywords]) => [normalizeQuery(word), normalizeQuery(keywords)]) : [];
  for (const row of data.r) {
    if (!Array.isArray(row) || typeof row[0] !== 'string' || !types[row[1]] || !pages[row[2]]) continue;
    const detail = typeof row[4] === 'number' ? String(table[row[4]] ?? '') : String(row[4] ?? '');
    const name = row[0], type = types[row[1]], page = pages[row[2]];
    const anchor = row[3] ? String(row[3]) : detailAnchor(name);
    const text = typeof row[5] === 'string' ? row[5] : '';
    if (!/^(fr|en)\/[a-z0-9-]+\/[a-z0-9-]+\/$/.test(page.path) || !/^[a-z0-9-]{1,80}$/.test(anchor)) continue;
    const folded = normalizeQuery(name), words = folded.split(/[\s'’(),.:/-]+/).filter(Boolean);
    const hidden = syn.length && (type.key === 'creature' || type.key === 'boss')
      ? syn.filter(([word]) => word.includes(' ') ? folded.includes(word) : words.some(w => w === word || w === `${word}s`)).map(([, keywords]) => keywords).join(' ') : '';
    items.push({name, type: row[1], detail, text, page: row[2], anchor, folded, words, syn: hidden,
      rest: normalizeQuery(`${detail} ${text} ${type.label} ${type.key.replace('_', ' ')}`), where: normalizeQuery(page.title)});
  }
  return {types, pages, items};
}
export function searchDetails(prepared, {query = '', type = -1, limit = 20} = {}) {
  const terms = normalizeQuery(query).split(' ').filter(Boolean);
  const empty = {total: 0, counts: {}, results: [], terms};
  if (!terms.length || !prepared) return empty;
  const scored = [], counts = {};
  for (const item of prepared.items) {
    let score = 0, ok = true;
    for (const term of terms) {
      if (item.syn && item.syn.split(' ').some(word => word.startsWith(term))) score += 5;  // t411u: « sanglier » lists the boars first
      else if (item.words.some(word => word.startsWith(term))) score += 4;
      else if (item.folded.includes(term)) score += 2;
      else if (item.rest.includes(term)) score += 1;
      else if (item.where.includes(term)) score += 0;
      else { ok = false; break; }
    }
    if (!ok || (score === 0 && terms.length === 1)) continue;
    counts[item.type] = (counts[item.type] ?? 0) + 1;
    if (type >= 0 && item.type !== type) continue;
    scored.push({score, item});
  }
  scored.sort((a, b) => b.score - a.score || a.item.name.length - b.item.name.length || a.item.type - b.item.type || a.item.name.localeCompare(b.item.name));
  const total = Object.values(counts).reduce((sum, n) => sum + n, 0);
  return {total, shown: scored.length, counts, results: scored.slice(0, Math.max(0, limit)).map(({item}) => item), terms};
}

// v42b: short excerpt of an article passage around the first matching term (same length per character, so positions match).
export function detailSnippet(item, terms = [], size = 90) {
  if (!item || !item.text) return item?.detail ?? '';
  const chars = [...item.text], folded = chars.map(c => c.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('en').slice(0, 1) || ' ').join('');
  const hits = terms.map(term => folded.indexOf(term)).filter(i => i >= 0), at = hits.length ? Math.min(...hits) : 0;
  const from = Math.max(0, at - 25), part = chars.slice(from, from + size).join('').trim();
  return (from > 0 ? '… ' : '') + part + (from + size < chars.length ? ' …' : '');
}

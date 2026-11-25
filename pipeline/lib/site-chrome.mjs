/**
 * Wowkipedia shared site chrome (lot L1, 2026-10-30): ONE header (wordmark + original emblem, mega-menu,
 * mobile drawer, search overlay trigger, FR/EN switch, Discord sign-in) and ONE footer, used by every
 * wiki page (home template, category pages, entry pages). No inline script or style: behaviour lives in
 * public/wiki/wk-header.js, styles in public/wiki/site.css, so pages keep running under the strict CSP.
 * The menu only lists categories and entries that have published content (no placeholders); the search overlay reads search-index.json
 * (published DTO fields only, built by scripts/build-static.mjs).
 */
import {categoryPath, entryPath} from './articles.mjs';

export const SITE_NAME = 'Wowkipedia';
const esc = value => String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const T = (lang, fr, en) => lang === 'en' ? en : fr;
const other = lang => lang === 'fr' ? 'en' : 'fr';

/** Top-level group of a category (for aria-current styling). */
export function groupOf(category) {
  return NAV_GROUPS.find(group => group.columns.some(column => column.items.some(item => item.category === category)))?.id ?? '';
}

/**
 * Menu structure (lot L1b, approved by Mathieu on 2026-10-30): six plain-language entries.
 * Category items show the number of published entries; entry items link to one published page.
 * Anything without published content (categories, draft entries such as the Priest class) is not rendered:
 * no "coming soon" placeholders. Retail-only topics (talents, guilds, expansions...) are out of scope.
 */
const cls = (entry, fr, en) => ({entry, label: {fr, en}, sort: true});
export const NAV_GROUPS = Object.freeze([
  {id: 'actualites', label: {fr: 'Actualités', en: 'News'}, columns: [
    {items: [
      {category: 'news', label: {fr: 'Toutes les actualités', en: 'All news'}},
      {entry: 'article-forever-calendar', label: {fr: 'Calendrier', en: 'Schedule'}},
      {entry: 'forever-news-golive-nov4', label: {fr: 'Lancement du 4 novembre', en: 'November 4 launch'}}
    ]}
  ]},
  {id: 'monde', label: {fr: 'Le monde', en: 'The world'}, columns: [
    {items: [
      {category: 'races', label: {fr: 'Races et factions', en: 'Races and factions'}},
      {category: 'zones', label: {fr: 'Zones', en: 'Zones'}},
      {category: 'creatures', label: {fr: 'Créatures et boss', en: 'Creatures and bosses'}},
      // No "Lore" category exists: the item links straight to the published short story (content untouched).
      {entry: 'forever-news-story-unbowed', label: {fr: 'Histoire et récits', en: 'Lore and stories'}, hint: {fr: 'Nouvelle « Unbowed »', en: 'Short story “Unbowed”'}}
    ]}
  ]},
  {id: 'classes', label: {fr: 'Classes', en: 'Classes'}, columns: [
    {items: [
      {category: 'classes', label: {fr: 'Toutes les classes', en: 'All classes'}},
      {entry: 'article-forever-classes', label: {fr: 'Vue d’ensemble des classes', en: 'Classes overview'}}
    ]},
    {label: {fr: 'Fiches de classe', en: 'Class pages'}, items: [
      cls('forever-class-shaman', 'Chaman', 'Shaman'), cls('forever-class-hunter', 'Chasseur', 'Hunter'),
      cls('forever-class-warlock', 'Démoniste', 'Warlock'), cls('forever-class-druid', 'Druide', 'Druid'),
      cls('forever-class-warrior', 'Guerrier', 'Warrior'), cls('forever-class-mage', 'Mage', 'Mage'),
      cls('forever-class-paladin', 'Paladin', 'Paladin'), cls('forever-class-rogue', 'Voleur', 'Rogue')
    ]}
  ]},
  {id: 'guides', label: {fr: 'Guides', en: 'Guides'}, columns: [
    {items: [
      {category: 'guides', label: {fr: 'Bien débuter', en: 'Getting started'}},
      {category: 'quests', label: {fr: 'Quêtes et progression', en: 'Quests and progression'}},
      {category: 'glossary', label: {fr: 'Glossaire', en: 'Glossary'}}
    ]}
  ]},
  {id: 'activites', label: {fr: 'Activités', en: 'Activities'}, columns: [
    {items: [
      {category: 'instances', label: {fr: 'Donjons et raids', en: 'Dungeons and raids'}},
      {category: 'pvp', label: {fr: 'JcJ', en: 'PvP'}},
      {category: 'professions', label: {fr: 'Métiers et artisanat', en: 'Professions and crafting'}},
      {category: 'items', label: {fr: 'Objets et équipement', en: 'Items and equipment'}}
    ]}
  ]},
  {id: 'communaute', label: {fr: 'Communauté', en: 'Community'}, columns: [
    {items: [
      {href: '/community/', label: {fr: 'Forums', en: 'Forums'}, community: true},
      {entry: 'forever-news-portal-room', label: {fr: 'Discord officiel', en: 'Official Discord'}, hint: {fr: 'Article : WoW Portal Room', en: 'Article: WoW Portal Room'}},
      {href: '/account/', label: {fr: 'Mon compte', en: 'My account'}, community: true}
    ]}
  ]}
]);

let NAV = {categories: new Map(), entries: new Map(), counts: new Map()};
/** Declare the catalogue used by the menu: category names and the published entries (drafts are ignored). */
export function setNavCatalog({categories, entries}) {
  const published = (entries ?? []).filter(entry => entry.status === 'published');
  const counts = new Map();
  for (const entry of published) counts.set(entry.category, (counts.get(entry.category) ?? 0) + 1);
  NAV = {
    categories: new Map((categories ?? []).filter(([id]) => counts.has(id)).map(([id, fr, en]) => [id, {fr, en}])),
    entries: new Map(published.map(entry => [entry.id, entry])),
    counts
  };
}

/** Href of the "Tout le wiki" registry page (/fr/wiki/, /en/wiki/). */
export const wikiPath = lang => `${lang}/wiki/`;

/** Original emblem: an open book under a four-pointed star inside a ring (no shield, no "W", no official mark). */
export function emblem(cls = 'wk-emblem') {
  return `<svg class="${cls}" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><circle cx="24" cy="24" r="21.5" class="wk-emblem-ring"/><circle cx="24" cy="24" r="18" class="wk-emblem-inner"/><path class="wk-emblem-star" d="M24 7.5l1.9 5.2 5.2 1.9-5.2 1.9L24 21.7l-1.9-5.2-5.2-1.9 5.2-1.9z"/><path class="wk-emblem-book" d="M11.5 22.5c4.6-.9 9 .2 12.5 3 3.5-2.8 7.9-3.9 12.5-3v13c-4.6-.9-9 .2-12.5 3-3.5-2.8-7.9-3.9-12.5-3z"/><path class="wk-emblem-spine" d="M24 25.5v13"/></svg>`;
}

export function wordmark() {
  return `<span class="wk-wordmark">Wow<span class="wk-wordmark-ki">ki</span>pedia</span>`;
}

function itemLink(item, lang, prefix, preview) {
  const label = esc(item.label[lang]);
  const hint = item.hint ? `<span class="wk-hint">${esc(item.hint[lang])}</span>` : '';
  if (item.category) {
    if (!NAV.categories.has(item.category)) return '';
    const n = NAV.counts.get(item.category) ?? 0;
    const unit = T(lang, n > 1 ? 'fiches publiées' : 'fiche publiée', n > 1 ? 'published entries' : 'published entry');
    return `<li><a href="${prefix}${categoryPath(item.category, lang)}${preview ? 'index.html' : ''}"><span class="wk-label">${label}</span><span class="wk-count">${n}<span class="visually-hidden"> ${unit}</span></span></a></li>`;
  }
  if (item.entry) {
    const entry = NAV.entries.get(item.entry);
    if (!entry) return '';
    return `<li><a href="${prefix}${entryPath(entry, lang)}${preview ? 'index.html' : ''}"><span class="wk-label">${label}${hint}</span></a></li>`;
  }
  if (item.href) return preview ? '' : `<li><a href="${esc(item.href)}"${item.community ? ' data-community-link' : ''}><span class="wk-label">${label}</span></a></li>`;
  return '';
}

function columnItems(column, lang) {
  return column.items.some(item => item.sort) ? [...column.items].sort((a, b) => a.label[lang].localeCompare(b.label[lang], lang)) : column.items;
}

const SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>';
const CHEVRON = '<svg class="wk-chevron" viewBox="0 0 12 12" aria-hidden="true" focusable="false"><path d="m3 4.5 3 3 3-3"/></svg>';

/**
 * Shared header. lang: page language; prefix: relative path to the web root; switchHref: same page in the other
 * language; home: href of the home page in this language; current: top-level group to mark (aria-current), if any.
 */
export function siteHeader({lang, prefix, switchHref, home, current = '', preview = false}) {
  const homeHref = home ?? `${prefix}${lang}/${preview ? 'index.html' : ''}`;
  // The registry page is not built in the local draft preview: no "Tout le wiki" link there.
  const wikiHref = preview ? '' : `${prefix}${wikiPath(lang)}`;
  const allLink = cls => wikiHref ? `<a class="${cls}" href="${wikiHref}"${current === 'wiki' ? ' aria-current="page"' : ''}>${T(lang, 'Tout le wiki', 'The whole wiki')} <span aria-hidden="true">→</span></a>` : '';
  const groups = NAV_GROUPS.map(group => {
    const columns = group.columns.map(column => {
      const links = columnItems(column, lang).map(item => itemLink(item, lang, prefix, preview)).filter(Boolean);
      return links.length ? `<div class="wk-col">${column.label ? `<p class="wk-col-title">${esc(column.label[lang])}</p>` : ''}<ul>${links.join('')}</ul></div>` : '';
    }).filter(Boolean);
    if (!columns.length) return '';
    const id = `wk-panel-${group.id}`;
    return `<li class="wk-item wk-has-panel${current === group.id ? ' is-current' : ''}"><button type="button" class="wk-top" aria-expanded="false" aria-controls="${id}">${esc(group.label[lang])}${CHEVRON}</button><div class="wk-panel wk-cols-${columns.length}" id="${id}" hidden><div class="wk-panel-inner">${columns.join('')}</div>${allLink('wk-all')}</div></li>`;
  }).join('');
  const discord = preview ? '' : `<a class="wk-discord" href="/account/" data-community-link><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8.5 7.5c2.3-.7 4.7-.7 7 0M7.5 16.5c2.9 1.1 6.1 1.1 9 0M9 3.9 8 5.5C6.4 6 5 6.7 3.8 7.6 2.5 10.6 2 13.6 2.3 16.6c1.5 1.1 3.1 1.9 4.9 2.4l1.1-1.7M15 3.9l1 1.6c1.6.5 3 1.2 4.2 2.1 1.3 3 1.8 6 1.5 9-1.5 1.1-3.1 1.9-4.9 2.4l-1.1-1.7"/><circle cx="9" cy="12.5" r="1.3"/><circle cx="15" cy="12.5" r="1.3"/></svg><span>${T(lang, 'Connexion', 'Sign in')}<span class="wk-discord-x">${T(lang, ' Discord', ' with Discord')}</span></span></a>`;
  const language = switchHref ? `<a class="wk-lang" href="${esc(switchHref)}" hreflang="${other(lang)}" lang="${other(lang)}"><span aria-hidden="true"><b>${lang.toUpperCase()}</b> / ${other(lang).toUpperCase()}</span><span class="visually-hidden">${T(lang, 'Read in English', 'Lire en français')}</span></a>` : '';
  const searchHref = preview ? homeHref : `${wikiHref}#search-input`;
  return `<header class="wk-header" data-wk-header data-lang="${lang}">
<div class="wk-bar">
<a class="wk-brand" href="${homeHref}"${current === 'home' ? ' aria-current="page"' : ''}>${emblem()}${wordmark()}<span class="visually-hidden"> — ${T(lang, 'Accueil', 'Home')}</span></a>
<nav class="wk-nav" id="wk-nav" aria-label="${T(lang, 'Navigation principale', 'Main navigation')}">
<ul class="wk-menu">${groups}</ul>
<div class="wk-drawer-extra">${allLink('wk-all wk-all-drawer')}${discord}</div>
</nav>
<div class="wk-tools">
<a class="wk-icon wk-search-open" href="${searchHref}" data-wk-search-open aria-keyshortcuts="/" title="${T(lang, 'Rechercher (touche /)', 'Search (/ key)')}">${SEARCH_ICON}<span class="visually-hidden">${T(lang, 'Rechercher dans le wiki', 'Search the wiki')}</span></a>
${language}
${discord}
<button type="button" class="wk-icon wk-burger" id="wk-menu-toggle" aria-expanded="false" aria-controls="wk-nav" hidden><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="wk-burger-lines" d="M4 7h16M4 12h16M4 17h16"/><path class="wk-burger-close" d="m6 6 12 12M18 6 6 18"/></svg><span class="visually-hidden">${T(lang, 'Menu', 'Menu')}</span></button>
</div>
</div>
</header>
${searchOverlay({lang, target: preview ? homeHref : wikiHref, preview})}`;
}

/** Search overlay (dialog). Hidden by default; without JavaScript the magnifier is a plain link to the home search. */
export function searchOverlay({lang, target, preview = false}) {
  return `<div class="wk-search" id="wk-search" role="dialog" aria-modal="true" aria-labelledby="wk-search-title" data-registry="${esc(target)}" hidden>
<div class="wk-search-backdrop" data-wk-search-close></div>
<div class="wk-search-box">
<h2 id="wk-search-title" class="wk-search-title">${T(lang, 'Rechercher dans le wiki', 'Search the wiki')}</h2>
<form class="wk-search-form" role="search" action="${esc(target)}" method="get"${preview ? ' data-preview' : ''}><label for="wk-search-input" class="visually-hidden">${T(lang, 'Mots-clés', 'Keywords')}</label>${SEARCH_ICON}<input id="wk-search-input" name="q" type="search" maxlength="120" autocomplete="off" spellcheck="false" placeholder="${T(lang, 'Une classe, une zone, un guide…', 'A class, a zone, a guide…')}" aria-describedby="wk-search-hint" aria-controls="wk-search-results"><button type="button" class="wk-icon wk-search-close" data-wk-search-close><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m6 6 12 12M18 6 6 18"/></svg><span class="visually-hidden">${T(lang, 'Fermer la recherche', 'Close search')}</span></button></form>
<p id="wk-search-hint" class="wk-search-hint">${T(lang, 'Fiches et articles publiés uniquement. Échap pour fermer.', 'Published entries and articles only. Esc to close.')}</p>
<p id="wk-search-status" class="wk-search-status" role="status" aria-live="polite"></p>
<ul id="wk-search-results" class="wk-search-results" aria-label="${T(lang, 'Résultats', 'Results')}"></ul>
<p class="wk-search-all" hidden><a id="wk-search-all" href="${esc(target)}">${T(lang, 'Voir tous les résultats dans « Tout le wiki »', 'See all results in “The whole wiki”')}</a></p>
</div>
</div>`;
}

/**
 * v17 — lighter search index: the article text is only used for "every term appears" matching, so each language keeps
 * its normalized words once (same results as the full text: a search term never contains a space). Titles and
 * descriptions stay intact for display.
 */
const foldText = value => String(value ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase('en').replace(/\s+/gu, ' ').trim();
export function compactSearchText(searchText) {
  return Object.fromEntries(Object.entries(searchText ?? {}).map(([lang, text]) => [lang, [...new Set(foldText(text).split(' ').filter(Boolean))].join(' ')]));
}
/** Search index for the overlay: published entries only, minimal DTO fields accepted by ui-core isDisplayableEntry. */
export function searchIndex({categories, entries}) {
  const published = entries.filter(entry => entry.status === 'published' && entry.publicationValidated === true);
  return {
    categories: categories.filter(([id]) => published.some(entry => entry.category === id)),
    entries: published.map(entry => ({
      id: entry.id, status: entry.status, publicationValidated: true, category: entry.category,
      ...(entry.subcategory === undefined ? {} : {subcategory: entry.subcategory}),
      title: entry.title, description: entry.description, url: entry.url,
      ...(entry.searchText === undefined ? {} : {searchText: compactSearchText(entry.searchText)}),
      ...(entry.hasArticle ? {hasArticle: true} : {}),
      ...(entry.verification === undefined ? {} : {verification: entry.verification}),   // V2.1 étape 03: « à confirmer » only
      sources: entry.sources.map(source => ({url: source.url, license: source.license, accessedAt: source.accessedAt}))
    }))
  };
}

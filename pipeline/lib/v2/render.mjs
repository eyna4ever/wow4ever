/**
 * Wowkipedia v2 page templates (proposal, branch refonte-v2). Look taken from the kit mockup
 * (wowki4ever_handoff/design/maquette_ecrans.png): compact header with tagline, cinematic home hero with two actions,
 * three editorial cards, image banners with breadcrumb + title, tabs, left section menu, right "Sommaire" card.
 * Content: published World of Warcraft: Forever entries only (no retail content, no invented data).
 * No inline script/style: behaviour = wk-header.js (unchanged), styles = v2.css. Same footer notice as v8.
 */
import {categoryPath, entryPath, readingMinutes, sourceGroups} from '../articles.mjs';
import {visualFor} from '../visuals.mjs';
import {entryPicture as entryPictureBase, entryContent, discussionBlock, formatDate, statusBadge, unconfirmedPill, gameDataPill, UNOFFICIAL, ART_LABEL, CATEGORY_INTROS} from '../pages.mjs';
import {searchOverlay, SITE_NAME} from '../site-chrome.mjs';
import {readFileSync} from 'node:fs';
/** t390u: official in-game images (© Blizzard Entertainment) for zone pages — self-hosted, resized only (no crop, no filter), source linked in the caption. */
const ZONE_IMAGES = JSON.parse(readFileSync(new URL('../../data/zone-images.json', import.meta.url), 'utf8'));
function zoneFigure(entry, prefix, lang) {
  const img = ZONE_IMAGES[entry.id];
  if (!img) return '';
  const base = `${prefix}assets/${img.asset}`, sizes = '(min-width: 1221px) 760px, (min-width: 700px) 92vw, 100vw';
  const name = entry.title?.[lang] ?? entry.title?.fr ?? '';
  const alt = T(lang, `Image du jeu World of Warcraft: Forever — ${name}`, `World of Warcraft: Forever game image — ${name}`);
  return `<figure class="v39-figure is-game"><picture><source type="image/avif" srcset="${base}-640.avif 640w, ${base}-1024.avif 1024w" sizes="${sizes}"><img class="v2-img" src="${base}-1024.webp" srcset="${base}-640.webp 640w, ${base}-1024.webp 1024w" sizes="${sizes}" width="${img.width}" height="${img.height}" alt="${esc(alt)}" fetchpriority="high" decoding="async"></picture>`
    + `<figcaption><span>${T(lang, 'Image du jeu © Blizzard Entertainment', 'Game image © Blizzard Entertainment')}</span> <span class="v39-credit"><a href="${esc(img.source)}" rel="noopener" target="_blank">${T(lang, 'source de l’image', 'image source')}</a></span></figcaption></figure>`;
}
import {gameDataGroupKeys, unofficialGroupKeys, VERIFICATION} from '../source-policy.mjs';
import {SECTIONS, CATEGORY_LABELS, PLACEMENT, listingCategory, sectionOf, inListing} from './structure.mjs';
import {MENU, MORE, TREE_ORDER, groupsFor, continentLabel} from '../v39/nav.mjs';

const esc = value => String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const T = (lang, fr, en) => lang === 'en' ? en : fr;
const other = lang => lang === 'fr' ? 'en' : 'fr';
const label = (cat, lang) => CATEGORY_LABELS[cat]?.[lang] ?? cat;
const section = id => SECTIONS.find(item => item.id === id);
export const gamePath = lang => `${lang}/${section('jeu').slug[lang]}/`;
export const wikiIndexPath = lang => `${lang}/wiki/`;
const date = (iso, lang) => `<time datetime="${esc(String(iso).slice(0, 10))}">${formatDate(iso, lang)}</time>`;
const byDate = (a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt));

const ICONS = {
  home: '<path d="M4 11.5 12 5l8 6.5M6.5 10v9h11v-9"/>',
  actualites: '<path d="M6 4h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V8"/><path d="M9 8h7M9 12h7M9 16h4"/>',
  jeu: '<path d="M5 19 15 9M14 5l5 5M13 6l5 5M5 15l4 4M4 20l2-2"/>',
  guides: '<path d="M4 6c3-1 6-1 8 1 2-2 5-2 8-1v12c-3-1-6-1-8 1-2-2-5-2-8-1z"/><path d="M12 7v12"/>',
  classes: '<path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z"/><path d="M12 8v8M9 11h6"/>',
  races: '<circle cx="12" cy="7.5" r="3.5"/><path d="M5 20c.8-4 3.6-6.5 7-6.5s6.2 2.5 7 6.5"/>',
  zones: '<path d="m3 19 6-11 4 6 3-4 5 9z"/><path d="M14.5 6.5a1.6 1.6 0 1 0 0-.1"/>',
  instances: '<path d="M5 21V10a7 7 0 0 1 14 0v11"/><path d="M9 21v-7a3 3 0 0 1 6 0v7M3 21h18"/>',
  creatures: '<path d="M7 14c-2 0-3-1.5-3-3s1-2 2-2M17 14c2 0 3-1.5 3-3s-1-2-2-2"/><path d="M8 7c0-1.5 1-3 1.5-3S11 5.5 11 7M13 7c0-1.5 1-3 1.5-3S16 5.5 16 7"/><path d="M7 15c0 3 2.2 5 5 5s5-2 5-5-2.2-5-5-5-5 2-5 5z"/>',
  quests: '<path d="M7 4h10a2 2 0 0 1 2 2v1H9"/><path d="M9 7v11a2 2 0 0 1-4 0v-2h4M9 18h8a2 2 0 0 0 2-2V7"/><path d="M12 10.5h4M12 13.5h4"/>',
  pvp: '<path d="m4 4 9 9M4 4h4M4 4v4M20 4l-9 9M20 4h-4M20 4v4"/><path d="m8 16-3 3M16 16l3 3M7 14l3 3M17 14l-3 3"/>',
  professions: '<path d="M14 4a4 4 0 0 0 4.8 5.2L20 10l-2 2-6.5-6.5 2-2z"/><path d="M12.5 7.5 4 16a2.1 2.1 0 0 0 3 3l8.5-8.5"/>',
  items: '<path d="M7 4h10l3 5-8 11L4 9z"/><path d="M4 9h16M9.5 4 12 9l2.5-5M12 9v11"/>',
  glossary: '<path d="M6 4h11a2 2 0 0 1 2 2v14H8a2 2 0 0 1-2-2z"/><path d="M6 18a2 2 0 0 1 2-2h11"/><path d="m10 12 2-5 2 5M10.6 10.5h2.8"/>',
  info: '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8h.01"/>',
  list: '<path d="M9 6.5h10M9 12h10M9 17.5h10M5 6.5h.01M5 12h.01M5 17.5h.01"/>',
  star: '<path d="m12 4 2.4 5 5.4.6-4 3.7 1.1 5.4L12 16l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  chart: '<path d="M4 20h16M7 16v-5M12 16V7M17 16v-8"/>',
  flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  calendar: '<rect x="4" y="5.5" width="16" height="14.5" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
  sparkle: '<path d="M12 2.5c.6 4.8 2.7 6.9 7.5 7.5-4.8.6-6.9 2.7-7.5 7.5-.6-4.8-2.7-6.9-7.5-7.5 4.8-.6 6.9-2.7 7.5-7.5z"/>',
  communaute: '<circle cx="9" cy="9" r="3"/><circle cx="16.5" cy="10" r="2.5"/><path d="M3.5 19c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5M14.5 15c2.6-.4 4.6.9 5.5 3.5"/>'
};
ICONS.news = ICONS.actualites; ICONS.guides_cat = ICONS.guides; ICONS.community = ICONS.communaute;
const icon = name => `<svg class="v2-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONS[name]}</svg>`;
const EMBLEM = '<svg class="wk-emblem v2-emblem" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><circle cx="24" cy="24" r="22" class="v2-em-outer"/><circle cx="24" cy="24" r="19.2" class="v2-em-ring"/><circle cx="24" cy="24" r="16" class="v2-em-inner"/><path class="v2-em-spikes" d="M24 1.5v4M24 42.5v4M1.5 24h4M42.5 24h4M8.1 8.1l2.8 2.8M37.1 37.1l2.8 2.8M8.1 39.9l2.8-2.8M37.1 10.9l2.8-2.8"/><path class="v2-em-w" d="M13.5 16.5h5l-1.3 1.2 2.6 9.4 3.3-10.6h1.8l3.3 10.6 2.6-9.4-1.3-1.2h5L33 18l-4.6 14.5h-2.1L24 25l-2.3 7.5h-2.1L15 18z"/></svg>';
const DISCORD = '<svg class="v2-discord-logo" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M19.3 5.4a16.5 16.5 0 0 0-4.1-1.3l-.5 1.1a15 15 0 0 0-5.4 0l-.5-1.1a16.5 16.5 0 0 0-4.1 1.3C2.1 9.3 1.4 13.1 1.7 16.8a16.6 16.6 0 0 0 5 2.6l1.1-1.7a10.6 10.6 0 0 1-1.7-.8l.4-.3a11.7 11.7 0 0 0 11 0l.4.3c-.5.3-1.1.6-1.7.8l1.1 1.7a16.6 16.6 0 0 0 5-2.6c.4-4.3-.7-8-3-11.4z"/><ellipse class="v2-dl-eye" cx="8.6" cy="13" rx="1.7" ry="1.9"/><ellipse class="v2-dl-eye" cx="15.4" cy="13" rx="1.7" ry="1.9"/></svg>';
const SEARCH = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>';
const CHEVRON = '<svg class="wk-chevron" viewBox="0 0 12 12" aria-hidden="true" focusable="false"><path d="m3 4.5 3 3 3-3"/></svg>';

/** Site context: published entries + catalogue names. */
let CTX = {entries: [], byId: new Map()};
/** Official podcast (v10): filed under Community, published only. */
const podcast = () => CTX.byId.get('forever-news-podcast-series');
export function setV2Catalog(entries) {
  const published = entries.filter(entry => entry.status === 'published');
  CTX = {entries: published, byId: new Map(published.map(entry => [entry.id, entry]))};
}
const count = cat => inListing(CTX.entries, cat).length;
const catHref = (cat, lang, prefix) => cat === 'community' ? '/community/' : `${prefix}${categoryPath(cat, lang)}`;
const sectionHref = (id, lang, prefix) => id === 'actualites' ? `${prefix}${categoryPath('news', lang)}` : id === 'jeu' ? `${prefix}${gamePath(lang)}` : id === 'guides' ? `${prefix}${categoryPath('guides', lang)}` : '/community/';

/* ---- v39 (test UI) : en-tête, menu principal fixe, arbre des catégories, gabarit 3 colonnes ---- */
const X_ICON = '<svg class="v2-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m6 6 12 12M18 6 6 18"/></svg>';
const catIcon = cat => icon(cat === 'news' ? 'actualites' : cat === 'guides' ? 'guides_cat' : cat);
/** current: 'home' | a category id | 'more' (classes, races, guides, glossary, community) | ''. self: true when the page IS that category page. */
function header({lang, prefix, switchHref, current, self = false}) {
  const home = `${prefix}${lang}/`;
  const top = (iconName, href, text, id, extra = '') => `<li class="wk-item${current === id ? ' is-current' : ''}"><a class="wk-top" href="${href}"${current === id ? (self || id === 'home' ? ' aria-current="page"' : ' aria-current="true"') : ''}${extra}>${icon(iconName)}<span>${text}</span></a></li>`;
  const panelLink = (href, text, n, attrs = '') => `<li><a href="${href}"${attrs}><span class="wk-label">${esc(text)}</span>${n === undefined ? '' : `<span class="wk-count">${n}<span class="visually-hidden"> ${T(lang, n > 1 ? 'fiches' : 'fiche', n > 1 ? 'entries' : 'entry')}</span></span>`}</a></li>`;
  const menu = MENU.filter(item => count(item.id)).map(item => top(item.id === 'news' ? 'actualites' : item.id, catHref(item.id, lang, prefix), esc(item.label[lang]), item.id));
  const portal = CTX.byId.get('forever-news-portal-room');
  const more = [...MORE.filter(count).map(cat => panelLink(catHref(cat, lang, prefix), label(cat, lang), count(cat))),
    panelLink('/community/', T(lang, 'Forums', 'Forums'), undefined, ' data-community-link'),
    portal ? panelLink(`${prefix}${entryPath(portal, lang)}`, T(lang, 'Discord officiel (WoW Portal Room)', 'Official Discord (WoW Portal Room)')) : '',
    podcast() ? panelLink(`${prefix}${entryPath(podcast(), lang)}`, T(lang, 'Podcast officiel WoW: Forever', 'Official WoW: Forever podcast')) : '',
    panelLink('/account/', T(lang, 'Mon compte', 'My account'), undefined, ' data-community-link')].filter(Boolean);
  const all = `<a class="wk-all" href="${prefix}${wikiIndexPath(lang)}">${T(lang, 'Tout le wiki de A à Z', 'The whole wiki, A to Z')} <span aria-hidden="true">→</span></a>`;
  const game = `<a class="wk-all" href="${prefix}${gamePath(lang)}">${T(lang, 'Vue d’ensemble du jeu', 'Game overview')} <span aria-hidden="true">→</span></a>`;
  const plus = `<li class="wk-item wk-has-panel v39-more${current === 'more' ? ' is-current' : ''}"><button type="button" class="wk-top" aria-expanded="false" aria-controls="wk-panel-plus">${icon('list')}<span>${T(lang, 'Plus', 'More')}</span>${CHEVRON}</button><div class="wk-panel" id="wk-panel-plus" hidden><ul class="v2-panel-list">${more.join('')}</ul>${game}${all}</div></li>`;
  const discord = `<a class="wk-discord" href="/account/" data-community-link>${DISCORD}<span>${T(lang, 'Se connecter', 'Sign in')}<span class="visually-hidden"> ${T(lang, 'avec Discord', 'with Discord')}</span></span></a>`;
  const seg = ['fr', 'en'].map(code => code === lang ? `<b>${code.toUpperCase()}</b>` : `<span>${code.toUpperCase()}</span>`).join('');
  return `<header class="wk-header v2-header v39-header" data-wk-header data-lang="${lang}">
<div class="wk-bar">
<a class="wk-brand v24-brand" href="${home}">${EMBLEM}<span class="v2-brandtext"><span class="wk-wordmark">Wowkipedia</span></span><span class="visually-hidden"> — ${T(lang, 'Accueil', 'Home')}</span></a>
<a class="wk-search-open v39-search" href="${prefix}${wikiIndexPath(lang)}" data-wk-search-open aria-keyshortcuts="/" title="${T(lang, 'Rechercher (touche /)', 'Search (/ key)')}">${SEARCH}<span class="v39-search-ph" aria-hidden="true">${T(lang, 'Rechercher une zone, un objet, une recette…', 'Search a zone, an item, a recipe…')}</span><kbd class="v39-kbd" aria-hidden="true">/</kbd><span class="visually-hidden">${T(lang, 'Rechercher dans le wiki', 'Search the wiki')}</span></a>
<div class="wk-tools">
${switchHref ? `<a class="wk-lang" href="${esc(switchHref)}" hreflang="${other(lang)}" lang="${other(lang)}"><span class="v39-seg" aria-hidden="true">${seg}</span><span class="visually-hidden">${T(lang, 'Read in English', 'Lire en français')}</span></a>` : ''}
${discord}
<button type="button" class="wk-icon wk-burger" id="wk-menu-toggle" aria-expanded="false" aria-controls="wk-nav"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="wk-burger-lines" d="M4 7h16M4 12h16M4 17h16"/><path class="wk-burger-close" d="m6 6 12 12M18 6 6 18"/></svg><span class="visually-hidden">Menu</span></button>
</div>
</div>
<nav class="wk-nav v39-nav" id="wk-nav" aria-label="${T(lang, 'Navigation principale', 'Main navigation')}">
<ul class="wk-menu">${top('home', home, T(lang, 'Accueil', 'Home'), 'home')}${menu.join('')}${plus}</ul>
<div class="wk-drawer-extra">${all}${discord}</div>
</nav>
</header>
${searchOverlay({lang, target: `${prefix}${wikiIndexPath(lang)}`})}`;
}

function page({lang, prefix, title, description, switchHref, current, self = false, body, bodyClass = '', head = ''}) {
  return `<!doctype html><html lang="${lang}" data-theme="wow"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#0d1118"><link rel="icon" href="${prefix}assets/favicon.svg" type="image/svg+xml"><title>${esc(title)} — ${SITE_NAME}</title><meta name="description" content="${esc(description)}">${switchHref ? `<link rel="alternate" hreflang="${other(lang)}" href="${esc(switchHref)}">` : ''}<link rel="stylesheet" href="${prefix}v2.css"><link rel="stylesheet" href="${prefix}theme-wow.css"><script src="${prefix}theme.js"></script><link rel="modulepreload" href="${prefix}wk-header.js"><link rel="modulepreload" href="${prefix}ui-core.mjs">${head}</head><body class="v2 v39${bodyClass ? ` ${bodyClass}` : ''}">
<a href="#main-content" class="skip-link">${T(lang, 'Aller au contenu', 'Skip to content')}</a>
${header({lang, prefix, switchHref, current, self})}
<main id="main-content" tabindex="-1">${body}</main>
${footer(lang, prefix)}
<script type="module" src="${prefix}wk-header.js"></script></body></html>`;
}

/** Left column: collapsible category tree. Only the current category is unfolded (groups as native <details>). */
function sideTree(lang, prefix, currentCat = '', currentId = '') {
  const leaf = entry => `<li><a href="${prefix}${entryPath(entry, lang)}"${entry.id === currentId ? ' aria-current="page"' : ''}>${esc(entry.title[lang])}</a></li>`;
  const row = cat => {
    const isCur = cat === currentCat;
    const link = `<a class="v39-tree-cat" href="${catHref(cat, lang, prefix)}"${isCur && !currentId ? ' aria-current="page"' : ''}>${catIcon(cat)}<span class="wk-label">${esc(label(cat, lang))}</span><span class="wk-count">${count(cat)}</span></a>`;
    if (!isCur) return `<li class="v39-tree-item">${link}</li>`;
    const inner = groupsFor(cat, CTX.entries, lang).map(group => group.key
      ? `<li class="v39-tree-group"><details${group.items.some(entry => entry.id === currentId) ? ' open' : ''}><summary><span>${esc(group.label)}</span><span class="wk-count">${group.items.length}</span></summary><ul>${group.items.map(leaf).join('')}</ul></details></li>`
      : group.items.map(leaf).join('')).join('');
    return `<li class="v39-tree-item is-current">${link}<ul class="v39-tree-sub">${inner}</ul></li>`;
  };
  const community = [CTX.byId.get('forever-news-portal-room'), podcast()].filter(Boolean);
  const isCommunity = currentCat === 'community';
  const communityRow = `<li class="v39-tree-item${isCommunity ? ' is-current' : ''}"><a class="v39-tree-cat" href="/community/" data-community-link>${icon('communaute')}<span class="wk-label">${T(lang, 'Communauté', 'Community')}</span></a>${isCommunity ? `<ul class="v39-tree-sub">${community.map(leaf).join('')}</ul>` : ''}</li>`;
  return `<nav class="v39-side" id="v39-side" aria-labelledby="v39-side-title"><div class="v39-side-head"><p class="v39-side-title" id="v39-side-title">${T(lang, 'Catégories', 'Categories')}</p><button type="button" class="v39-side-close" hidden>${X_ICON}<span class="visually-hidden">${T(lang, 'Fermer les catégories', 'Close categories')}</span></button></div><ul class="v39-tree">${TREE_ORDER.filter(count).map(row).join('')}${communityRow}</ul><a class="v2-side-all" href="${prefix}${wikiIndexPath(lang)}">${icon('list')}${T(lang, 'Tout le wiki (A–Z)', 'The whole wiki (A–Z)')}</a></nav>`;
}
const sideToggle = lang => `<button type="button" class="v39-side-toggle" aria-controls="v39-side" aria-expanded="false" hidden>${icon('list')}<span>${T(lang, 'Catégories', 'Categories')}</span></button>`;
/** Anchor « tabs » to the real sections of the page (no hidden content, no JS needed). */
const sectionTabs = (lang, items) => items.length > 1 ? `<nav class="v39-tabs" aria-label="${T(lang, 'Sections de la page', 'Page sections')}"><ul>${items.map(([id, text]) => `<li><a href="#${id}">${esc(text)}</a></li>`).join('')}</ul></nav>` : '';
/** Layout: main first in the source (reading order), then the right rail, then the side tree (moved left by CSS). */
const layout = ({lang, prefix, cat = '', id = '', main, rail = '', cls = ''}) => `<div class="v39-layout${rail ? '' : ' no-rail'}${cls ? ` ${cls}` : ''}"><div class="v39-main">${sideToggle(lang)}${main}</div>${rail}${sideTree(lang, prefix, cat, id)}<div class="v39-backdrop" hidden></div></div>`;

function footer(lang, prefix) {
  const portal = CTX.byId.get('forever-news-portal-room');
  return `<footer class="v2-footer"><div class="v2-footer-inner">
<div class="v2-footer-brand">${EMBLEM}<p><strong>${SITE_NAME}</strong><br>${T(lang, 'Le wiki communautaire de World of Warcraft: Forever, vérifié et sourcé.', 'The community wiki for World of Warcraft: Forever, reviewed and sourced.')}</p></div>
<nav class="v2-footer-nav" aria-label="${T(lang, 'Pied de page', 'Footer')}"><ul><li><a href="${sectionHref('actualites', lang, prefix)}">${T(lang, 'Actualités', 'News')}</a></li><li><a href="${prefix}${gamePath(lang)}">${T(lang, 'Le jeu', 'The game')}</a></li><li><a href="${sectionHref('guides', lang, prefix)}">${T(lang, 'Guides', 'Guides')}</a></li><li><a href="${prefix}${wikiIndexPath(lang)}">${T(lang, 'Tout le wiki (A–Z)', 'The whole wiki (A–Z)')}</a></li></ul>
<ul><li><a href="/community/" data-community-link>${T(lang, 'Forums', 'Forums')}</a></li>${portal ? `<li><a href="${prefix}${entryPath(portal, lang)}">${T(lang, 'Discord officiel', 'Official Discord')}</a></li>` : ''}${podcast() ? `<li><a href="${prefix}${entryPath(podcast(), lang)}">${T(lang, 'Podcast officiel', 'Official podcast')}</a></li>` : ''}<li><a href="/privacy/" data-community-link>${T(lang, 'Confidentialité', 'Privacy')}</a></li></ul></nav>
</div><p class="independence">${UNOFFICIAL.fr}${lang === 'en' ? ` ${UNOFFICIAL.en}` : ''} ${T(lang, 'Illustrations : illustrations d’ambiance originales ou images du jeu © Blizzard Entertainment.', 'Illustrations: original ambiance artwork or game images © Blizzard Entertainment.')}</p></footer>`;
}

const tag = (text, kind = '') => `<span class="v2-tag${kind ? ` is-${kind}` : ''}">${esc(text)}</span>`;
const SINGULAR = {news: ['Actualité', 'News'], classes: ['Classe', 'Class'], races: ['Race', 'Race'], zones: ['Zone', 'Zone'], instances: ['Donjon & raid', 'Dungeon & raid'], creatures: ['Créature', 'Creature'], quests: ['Quêtes', 'Quests'], pvp: ['JcJ', 'PvP'], professions: ['Métier', 'Profession'], items: ['Objet', 'Item'], guides: ['Guide', 'Guide'], glossary: ['Glossaire', 'Glossary'], community: ['Communauté', 'Community']};
/** v11 mobile-first image sizes (rendered widths measured at 360–1440 px; phones first). */
const SIZES = {
  card: '(max-width: 640px) 118px, (max-width: 900px) 50vw, 350px',
  featured: '(max-width: 640px) calc(100vw - 28px), (max-width: 900px) 50vw, 384px',
  tile: '(max-width: 640px) calc(100vw - 28px), (max-width: 900px) 50vw, 350px',
  lead: '(max-width: 900px) calc(100vw - 50px), 484px',
  info: '(max-width: 640px) 84px, (max-width: 1100px) 176px, 226px'
};
const entryPicture = (entry, prefix, lang, opts = {}) => entryPictureBase(entry, prefix, lang, {...opts, avif: true});
const tagFor = (entry, lang) => { const cat = listingCategory(entry); const sid = sectionOf(entry); return tag(SINGULAR[cat]?.[lang === 'en' ? 1 : 0] ?? cat, sid); };
function card(entry, lang, prefix, {sizes = SIZES.card, big = false} = {}) {
  const cat = listingCategory(entry);
  return `<a class="v2-card${big ? ' is-big' : ''}" href="${prefix}${entryPath(entry, lang)}"><span class="v2-card-img">${entryPicture(entry, prefix, lang, {sizes, cls: 'v2-img'})}${tagFor(entry, lang)}</span><span class="v2-card-body"><strong>${esc(entry.title[lang])}</strong><span class="v2-card-text">${esc(entry.description[lang])}</span><span class="v2-card-meta">${entry.article ? `${T(lang, 'Article', 'Article')} · ${readingMinutes(entry, lang)} min · ` : `${T(lang, 'Fiche', 'Entry')} · `}${date(entry.updatedAt, lang)}${entry.verification === VERIFICATION.unconfirmed ? ` · ${unconfirmedPill(lang)}` : entry.verification === VERIFICATION.gameData ? ` · ${gameDataPill(lang)}` : ''}</span></span></a>`;
}
const crumbs = (lang, items) => `<nav class="v2-crumbs" aria-label="${T(lang, 'Fil d’Ariane', 'Breadcrumb')}"><ol>${items.map(([text, href], i) => i === items.length - 1 ? `<li><span aria-current="page">${esc(text)}</span></li>` : `<li><a href="${href}">${esc(text)}</a></li>`).join('')}</ol></nav>`;
const artPicture = (cat, prefix, lang, eager = true) => `<picture><source type="image/avif" srcset="${prefix}assets/art-${cat}-480.avif 480w, ${prefix}assets/art-${cat}-1024.avif 1024w" sizes="${SIZES.tile}"><img class="v2-img" src="${prefix}assets/art-${cat}-1024.webp" srcset="${prefix}assets/art-${cat}-640.webp 640w, ${prefix}assets/art-${cat}-1024.webp 1024w" sizes="${SIZES.tile}" width="1024" height="576" alt="${esc(ART_LABEL[lang])}"${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async"></picture>`;
/** V2c: six original ambiance illustrations approved on 30/10/2026 (1280×720 sources, see ops/v2/build-art.py). */
const ART = {
  'hero-accueil': ['Une prêtresse elfe de la nuit tenant un bâton lumineux, devant une cité illuminée sous une lune violette.', 'A night elf priestess holding a glowing staff, in front of a lit city under a violet moon.'],
  'banniere-le-jeu': ['Une cité sombre aux lueurs rouges, un dragon et un arbre immense et lumineux sous un ciel violet.', 'A dark city with red lights, a dragon and a huge glowing tree under a violet sky.'],
  'banniere-classes': ['Cinq aventuriers vus de dos sur un promontoire, face à une citadelle sous un ciel violet.', 'Five adventurers seen from behind on a ledge, facing a citadel under a violet sky.'],
  'banniere-actualites': ['Un héraut lit un parchemin sur un balcon dominant une cité nocturne, un griffon dans le ciel.', 'A herald reads a scroll on a balcony above a city at night, a gryphon in the sky.'],
  'banniere-guides': ['Un aventurier étudie une carte lumineuse à la lueur des bougies, près d’une arche ouverte sur les montagnes.', 'An adventurer studies a glowing map by candlelight, next to an arch opening onto the mountains.'],
  'banniere-communaute': ['Des aventuriers de plusieurs peuples réunis autour d’un feu de camp dans une forêt nocturne.', 'Adventurers of several peoples gathered around a campfire in a forest at night.']
};
const artKey = cat => cat === 'news' ? 'banniere-actualites' : cat === 'classes' ? 'banniere-classes' : ['guides', 'glossary'].includes(cat) ? 'banniere-guides' : cat === 'community' ? 'banniere-communaute' : 'banniere-le-jeu';
const v2Art = (key, prefix, lang, {eager = true, cls = 'v2-img', sizes = '100vw'} = {}) => `<picture><source type="image/avif" srcset="${prefix}assets/v2-${key}-480.avif 480w, ${prefix}assets/v2-${key}-960.avif 960w, ${prefix}assets/v2-${key}-1280.avif 1280w" sizes="${sizes}"><source type="image/webp" srcset="${prefix}assets/v2-${key}-640.webp 640w, ${prefix}assets/v2-${key}-1024.webp 1024w, ${prefix}assets/v2-${key}-1280.webp 1280w" sizes="${sizes}"><img class="${cls}" src="${prefix}assets/v2-${key}-1280.jpg" width="1280" height="720" alt="${esc(ART[key][lang === 'en' ? 1 : 0])}"${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async"></picture>`;
// v25: under the header, the frame continues the original world map of the banner (no picture, no caption);
// v26: the Discord page gets the same map frame (Mathieu, t310u).
const MAP_FRAME = '<div class="v2-banner-art v25-map" aria-hidden="true"></div>';
function banner({lang, picture, crumbs: trail, kicker, title, text, meta, cls = '', keep = false}) {
  return `<section class="v2-banner${cls ? ` ${cls}` : ''}" aria-labelledby="page-title">${keep ? `<figure class="v2-banner-art">${picture}<figcaption>${esc(ART_LABEL[lang])}</figcaption></figure>` : MAP_FRAME}<div class="v2-banner-copy">${trail}${kicker ? `<p class="v2-kicker">${esc(kicker)}</p>` : ''}<h1 id="page-title">${esc(title)}</h1>${text ? `<p class="v2-banner-text">${esc(text)}</p>` : ''}${meta ?? ''}</div></section>`;
}
function sideMenu(lang, prefix, sectionId, currentCat) {
  const sec = section(sectionId);
  const cats = sec.categories.filter(count);
  return `<nav class="v2-side" aria-label="${esc(sec.label[lang])}"><p class="v2-side-title">${icon(sectionId)}${esc(sec.label[lang])}</p><ul>${cats.map(cat => `<li><a href="${catHref(cat, lang, prefix)}"${cat === currentCat ? ' aria-current="page"' : ''}>${icon(cat === 'guides' ? 'guides_cat' : cat)}<span class="v2-side-label">${esc(label(cat, lang))}</span><span class="wk-count">${count(cat)}</span></a></li>`).join('')}</ul><a class="v2-side-all" href="${prefix}${wikiIndexPath(lang)}">${icon('list')}${T(lang, 'Tout le wiki (A–Z)', 'The whole wiki (A–Z)')}</a></nav>`;
}
const chip = (name, text) => `<li class="v2-chip">${icon(name)}<span>${text}</span></li>`;

/**
 * v22 — « À la une » (home, FR + EN): automatic, computed at build time from the published data only (t297u).
 * Rule: the 3 most recently updated published entries that have an article body, news first (news listing,
 * newest update day first; same day: most recent event date, then latest update time), then filled with the most recently updated other articles if there are fewer than 3 news.
 * Ties are broken by title so the build stays reproducible. Every publication via review.mjs refreshes it.
 */
export const FEATURED_COUNT = 3;
/** v22 — newest-updated first; ties broken by title (reproducible build). */
export const newestFirst = lang => (a, b) => byDate(a, b) || a.title[lang].localeCompare(b.title[lang], lang);
/**
 * v22 — automatic « À lire aussi »: published entries sharing the most tags with this one or in the same category
 * (score = shared tags × 2 + same category), excluding itself, max 3; ties: newest update first, then title.
 */
export const READ_NEXT = 3;
export const DISCORD_UNTOUCHED = new Set(['forever-news-portal-room']);
export function readNext(entry, entries, lang = 'fr') {
  const tags = new Set((entry.tags ?? []).map(t => t.fr));
  const score = item => 2 * (item.tags ?? []).filter(t => tags.has(t.fr)).length + (listingCategory(item) === listingCategory(entry) ? 1 : 0);
  return entries.filter(item => item.id !== entry.id && item.status === 'published' && score(item) > 0)
    .sort((a, b) => score(b) - score(a) || newestFirst(lang)(a, b)).slice(0, READ_NEXT);
}
export function featuredEntries(entries, lang = 'fr') {
  const day = entry => String(entry.updatedAt).slice(0, 10);
  const order = (a, b) => day(b).localeCompare(day(a))                       // freshest update day first
    || String(b.eventDate ?? '').localeCompare(String(a.eventDate ?? ''))     // same day: most recent event date first
    || byDate(a, b) || a.title[lang].localeCompare(b.title[lang], lang);
  const withArticle = entries.filter(entry => entry.status === 'published' && entry.article);
  const news = inListing(withArticle, 'news').sort(order);
  const others = withArticle.filter(entry => !news.includes(entry)).sort(order);
  return [...news, ...others].slice(0, FEATURED_COUNT);
}
/**
 * v17 — « Quoi de neuf » (home): computed at build time from the published data only. The 3 latest news items
 * (news listing, newest update first) and the most recently updated other pages (any section except news).
 * Ties are broken by title so the build stays reproducible.
 */
export const WHATS_NEW = Object.freeze({news: 3, pages: 5});
export function whatsNew(entries, lang = 'fr') {
  const order = (a, b) => byDate(a, b) || a.title[lang].localeCompare(b.title[lang], lang);
  const news = inListing(entries, 'news').sort(order).slice(0, WHATS_NEW.news);
  const pages = entries.filter(entry => entry.category !== 'news').sort(order).slice(0, WHATS_NEW.pages);
  return {news, pages};
}
function whatsNewBlock(lang, prefix) {
  const {news, pages} = whatsNew(CTX.entries, lang);
  const newsItems = news.map(entry => `<li><a href="${prefix}${entryPath(entry, lang)}"><span class="v2-list-thumb">${entryPicture(entry, prefix, lang, {sizes: '120px', cls: 'v2-img'})}</span><span><strong>${esc(entry.title[lang])}</strong><span class="v2-list-meta">${date(entry.updatedAt, lang)}</span></span></a></li>`).join('');
  const pageItems = pages.map(entry => `<li><a href="${prefix}${entryPath(entry, lang)}">${tagFor(entry, lang)}<strong>${esc(entry.title[lang])}</strong><span class="v2-list-meta">${T(lang, 'Mis à jour le', 'Updated')} ${date(entry.updatedAt, lang)}</span></a></li>`).join('');
  return `<section class="v2-home-main v17-whatsnew" aria-labelledby="news-title"><h2 id="news-title" class="v2-h2">${T(lang, 'Quoi de neuf', 'What’s new')}</h2>`
    + `<h3 class="v17-sub">${icon('actualites')}${T(lang, 'Dernières actualités', 'Latest news')}</h3><ul class="v2-list">${newsItems}</ul>`
    + `<h3 class="v17-sub">${icon('clock')}${T(lang, 'Dernières mises à jour', 'Latest updates')}</h3><ul class="v17-updates">${pageItems}</ul>`
    + `<p class="v2-more"><a href="${sectionHref('actualites', lang, prefix)}">${T(lang, 'Toutes les actualités', 'All news')} <span aria-hidden="true">→</span></a> · <a href="${prefix}${wikiIndexPath(lang)}">${T(lang, 'Tout le wiki (A–Z)', 'The whole wiki (A–Z)')} <span aria-hidden="true">→</span></a></p></section>`;
}
const menuCurrent = cat => MENU.some(item => item.id === cat) ? cat : 'more';
const pageHead = (title, lede = '', kicker = '') => `<header class="v39-pagehead">${kicker ? `<p class="v2-kicker">${esc(kicker)}</p>` : ''}<h1 id="page-title" class="v39-h1">${esc(title)}</h1>${lede ? `<p class="v39-lede">${esc(lede)}</p>` : ''}</header>`;
export function renderHome(lang, prefix = '../') {
  const featured = featuredEntries(CTX.entries, lang);
  const starters = inListing(CTX.entries, 'guides').sort(newestFirst(lang)).slice(0, 6);   // v22: newest-updated guides
  const portal = CTX.byId.get('forever-news-portal-room');
  const hero = `<section class="v2-hero v39-hero" aria-labelledby="hero-title"><div class="v2-hero-art v25-map" aria-hidden="true"></div><div class="v2-hero-shade"></div><div class="v2-hero-copy"><span class="v2-hero-spark">${icon('sparkle')}</span><h1 id="hero-title" class="v2-hero-title">Wowkipedia</h1><p class="v2-hero-kicker"><span class="v2-hero-k1">${T(lang, 'Le wiki communautaire', 'The community wiki')}</span><span class="v2-hero-k2">World of Warcraft: Forever</span></p><p class="v2-hero-text">${T(lang, 'Des guides, les classes, les zones, les donjons et toutes les actualités du jeu, vérifiés et sourcés.', 'Guides, classes, zones, dungeons and all the game news, reviewed and sourced.')}</p><a class="v39-hero-search" href="${prefix}${wikiIndexPath(lang)}" data-v39-search>${SEARCH}<span>${T(lang, 'Rechercher une zone, un objet, une recette…', 'Search a zone, an item, a recipe…')}</span></a><p class="v2-hero-actions"><a class="v2-btn is-gold" href="${prefix}${gamePath(lang)}">${T(lang, 'Explorer le jeu', 'Explore the game')} <span aria-hidden="true">→</span></a><a class="v2-btn is-outline" href="/community/" data-community-link>${DISCORD}${T(lang, 'Rejoindre la communauté', 'Join the community')}</a></p></div></section>`;
  const explore = `<section class="v39-explore" aria-labelledby="explore-title"><h2 id="explore-title" class="v2-h2">${T(lang, 'Explorer le wiki', 'Explore the wiki')}</h2><ul class="v39-explore-grid">${TREE_ORDER.filter(count).map(cat => `<li><a href="${catHref(cat, lang, prefix)}">${catIcon(cat)}<strong>${esc(label(cat, lang))}</strong><span class="wk-count">${count(cat)}<span class="visually-hidden"> ${T(lang, 'fiches', 'entries')}</span></span></a></li>`).join('')}</ul></section>`;
  const main = `${explore}
<section class="v2-featured" aria-labelledby="featured-title"><h2 id="featured-title" class="v2-h2">${T(lang, 'À la une', 'Featured')}</h2><div class="v2-cards">${featured.map(entry => card(entry, lang, prefix, {sizes: SIZES.featured})).join('')}</div><p class="v2-more"><a href="${sectionHref('actualites', lang, prefix)}">${T(lang, 'Voir toutes les actualités', 'See all news')} <span aria-hidden="true">→</span></a></p></section>
<div class="v2-home-grid v39-home-grid">
${whatsNewBlock(lang, prefix)}
<aside class="v2-home-right" aria-labelledby="start-title"><div class="v2-start-box"><h2 id="start-title" class="v2-h3">${icon('guides')}${T(lang, 'Bien débuter', 'Getting started')}</h2><ul class="v2-links">${starters.map(entry => `<li><a href="${prefix}${entryPath(entry, lang)}"><span>${esc(entry.title[lang])}</span></a></li>`).join('')}</ul></div>
<div class="v2-community-box"><h2 class="v2-h3">${icon('communaute')}${T(lang, 'Communauté', 'Community')}</h2><p>${(podcast() ? T(lang, 'Forums du wiki, Discord officiel et podcast officiel de Blizzard pour les joueurs Forever.', 'Wiki forums, plus Blizzard’s official Discord and podcast for Forever players.') : T(lang, 'Forums du wiki et Discord officiel de Blizzard pour les joueurs Forever.', 'Wiki forums and Blizzard’s official Discord for Forever players.'))}</p><ul class="v2-links"><li><a href="/community/" data-community-link><span>${T(lang, 'Forums', 'Forums')}</span></a></li>${portal ? `<li><a href="${prefix}${entryPath(portal, lang)}"><span>${T(lang, 'Discord officiel (WoW Portal Room)', 'Official Discord (WoW Portal Room)')}</span></a></li>` : ''}${podcast() ? `<li><a href="${prefix}${entryPath(podcast(), lang)}"><span>${T(lang, 'Podcast officiel WoW: Forever', 'Official WoW: Forever podcast')}</span></a></li>` : ''}</ul></div></aside>
</div>`;
  const body = hero + layout({lang, prefix, main, cls: 'is-home'});
  return page({lang, prefix, title: T(lang, 'Le wiki communautaire de World of Warcraft: Forever', 'The World of Warcraft: Forever community wiki'), description: T(lang, 'Wiki communautaire indépendant de World of Warcraft: Forever.', 'Independent community wiki for World of Warcraft: Forever.'), switchHref: `${prefix}${other(lang)}/`, current: 'home', body, bodyClass: 'is-home'});
}

export function renderGame(lang) {
  const prefix = '../../';
  const sec = section('jeu');
  const cats = sec.categories.filter(count);
  const main = crumbs(lang, [[T(lang, 'Accueil', 'Home'), `${prefix}${lang}/`], [sec.label[lang], '']]) + pageHead(sec.label[lang], sec.intro[lang])
    + `<ul class="v2-cat-grid">${cats.map(cat => `<li><a class="v2-cat" href="${catHref(cat, lang, prefix)}"><span class="v2-card-img">${artPicture(cat, prefix, lang, false)}</span><span class="v2-cat-body"><strong>${esc(label(cat, lang))}</strong><span class="v2-card-text">${esc(CATEGORY_INTROS[cat][lang])}</span><span class="wk-count">${count(cat)}<span class="visually-hidden"> ${T(lang, 'fiches', 'entries')}</span></span></span></a></li>`).join('')}</ul>`;
  return page({lang, prefix, title: sec.label[lang], description: sec.intro[lang], switchHref: `${prefix}${gamePath(other(lang))}`, current: 'more', body: layout({lang, prefix, main})});
}


/** V2.1 étape 03: honest source count — non-official sources are never counted as official. */
function sourceCount(entry, groups, lang) {
  const unofficial = unofficialGroupKeys(entry);
  const gameData = gameDataGroupKeys(entry);
  const n = groups.filter(group => !unofficial.has(group.key)).length, m = groups.length - n;
  if (!m) return `<a href="#sources">${groups.length} ${groups.length > 1 ? T(lang, 'sources officielles', 'official sources') : T(lang, 'source officielle', 'official source')}</a>`;
  const count = `<a href="#sources">${n} ${n > 1 ? T(lang, 'sources officielles', 'official sources') : T(lang, 'source officielle', 'official source')} + ${m} ${m > 1 ? T(lang, 'sources non officielles', 'non-official sources') : T(lang, 'source non officielle', 'non-official source')}</a>`;
  const stillUnconfirmed = [...unofficial].some(key => !gameData.has(key));
  return stillUnconfirmed ? `${count} ${unconfirmedPill(lang)}` : `${count} ${gameDataPill(lang)}`;
}

export function renderCategory(cat, lang) {
  const prefix = '../../';
  const sid = SECTIONS.find(item => item.categories.includes(cat)).id;
  const items = inListing(CTX.entries, cat);
  const articles = items.filter(entry => entry.article).sort(newestFirst(lang));
  const notices = items.filter(entry => !entry.article).sort(newestFirst(lang));   // v22: newest-updated first
  const [lead, ...moreArticles] = articles;
  const trail = [[T(lang, 'Accueil', 'Home'), `${prefix}${lang}/`], ...(sid === 'actualites' || cat === 'guides' ? [] : [[section(sid).label[lang], sectionHref(sid, lang, prefix)]]), [label(cat, lang), '']];
  // v39: grouped categories (zones by continent, dungeons/raids, bestiary, recipes, camping) list EVERY page of the category
  // by group, A→Z, as compact rows (title + published description); the lead article stays on top. Flat categories: as in v38.
  const allGroups = groupsFor(cat, CTX.entries, lang);
  const grouped = allGroups.some(group => group.key);
  const groups = grouped ? allGroups.map(group => ({...group, items: group.items.filter(entry => entry !== lead)})).filter(group => group.items.length) : [];
  const tabs = sectionTabs(lang, [...(lead ? [['apercu', T(lang, 'Aperçu', 'Overview')]] : []),
    ...(grouped ? groups.map(group => [`fiches-${group.key}`, `${group.label} (${group.items.length})`])
      : [...(moreArticles.length ? [['articles', `${T(lang, 'Articles', 'Articles')} (${articles.length})`]] : []), ...(notices.length ? [['fiches', `${T(lang, 'Fiches', 'Entries')} (${notices.length})`]] : [])])]);
  const leadBlock = lead ? `<article class="v2-lead" id="apercu" aria-labelledby="lead-title"><a class="v2-lead-img" href="${prefix}${entryPath(lead, lang)}" tabindex="-1" aria-hidden="true">${entryPicture(lead, prefix, lang, {sizes: SIZES.lead, cls: 'v2-img'})}</a><div class="v2-lead-copy"><h2 id="lead-title" class="v2-lead-title">${esc(lead.title[lang])}</h2><p>${esc(lead.description[lang])}</p><ul class="v2-chips">${chip(cat === 'guides' ? 'guides_cat' : cat, `${items.length} ${T(lang, 'pages', 'pages')}`)}${chip('clock', `${readingMinutes(lead, lang)} min`)}${chip('link', `${sourceGroups(lead).length} sources`)}</ul><a class="v2-btn is-gold-outline is-big" href="${prefix}${entryPath(lead, lang)}">${T(lang, 'Lire l’article', 'Read the article')} <span aria-hidden="true">→</span></a></div></article>` : '';
  const row = entry => `<li><a class="v39-row" href="${prefix}${entryPath(entry, lang)}"><strong>${esc(entry.title[lang])}</strong><span class="v39-row-text">${esc(entry.description[lang])}</span><span class="v2-card-meta">${entry.article ? T(lang, 'Article', 'Article') : T(lang, 'Fiche', 'Entry')} · ${date(entry.updatedAt, lang)}${entry.verification === VERIFICATION.unconfirmed ? ` · ${unconfirmedPill(lang)}` : entry.verification === VERIFICATION.gameData ? ` · ${gameDataPill(lang)}` : ''}</span></a></li>`;
  const listBlock = grouped
    ? `<section id="fiches" aria-labelledby="notices-title"><h2 id="notices-title" class="v2-h2">${T(lang, 'Toutes les pages', 'All pages')}</h2>${groups.map(group => `<section class="v39-group" id="fiches-${group.key}" aria-labelledby="fiches-${group.key}-title"><h3 id="fiches-${group.key}-title" class="v39-h3">${esc(group.label)} <span class="wk-count">${group.items.length}</span></h3><ul class="v39-rows">${group.items.map(row).join('')}</ul></section>`).join('')}</section>`
    : (moreArticles.length ? `<section id="articles" aria-labelledby="more-title"><h2 id="more-title" class="v2-h2">${T(lang, 'Autres articles', 'More articles')}</h2><div class="v2-cards is-2">${moreArticles.map(entry => card(entry, lang, prefix)).join('')}</div></section>` : '')
      + (notices.length ? `<section id="fiches" aria-labelledby="notices-title"><h2 id="notices-title" class="v2-h2">${T(lang, 'Fiches', 'Entries')}</h2><div class="v2-cards is-2">${notices.map(entry => card(entry, lang, prefix)).join('')}</div></section>` : '');
  const main = crumbs(lang, trail) + pageHead(label(cat, lang), CATEGORY_INTROS[cat][lang]) + tabs + leadBlock + listBlock
    + `<p class="v2-art-note">${T(lang, 'Vignettes : illustrations d’ambiance — ne constituent pas une source.', 'Thumbnails: ambiance illustrations — not a source.')}</p>`;
  return page({lang, prefix, title: label(cat, lang), description: CATEGORY_INTROS[cat][lang], switchHref: `${prefix}${categoryPath(cat, other(lang))}`, current: menuCurrent(cat), self: true, body: layout({lang, prefix, cat, main})});
}


/** v18 — beginner path: the six beginner guides in reading order (race-history pages hang under guide 3), with a
 * "next step" button and real links to every wiki page the guide text names (all published relations, not only 3). */
const BEGINNER_PATH = [
  ['guide-debutant-avant-de-jouer'], ['guide-debutant-premiere-connexion'],
  ['guide-debutant-premier-personnage', ['guide-debutant-histoire-alliance', 'guide-debutant-histoire-horde', 'guide-debutant-histoire-eolides']],
  ['guide-debutant-premiers-pas'], ['guide-debutant-equipement-metiers'], ['guide-debutant-jouer-a-plusieurs']
];
const PATH_IDS = BEGINNER_PATH.flatMap(([id, subs = []]) => [id, ...subs]);
// v19: the 3 race-history annexes are unnumbered extras of step 3; from step 3 and from each annex, the next step is guide 4.
const NEXT_STEP = {'guide-debutant-premier-personnage': 'guide-debutant-premiers-pas', 'guide-debutant-histoire-alliance': 'guide-debutant-premiers-pas', 'guide-debutant-histoire-horde': 'guide-debutant-premiers-pas', 'guide-debutant-histoire-eolides': 'guide-debutant-premiers-pas'};
export function beginnerPath(entry, lang, prefix) {
  if (!PATH_IDS.includes(entry.id)) return '';
  const get = id => CTX.byId.get(id);
  const item = id => { const e = get(id); if (!e) return ''; return id === entry.id ? `<li aria-current="page"><strong>${esc(e.title[lang])}</strong> <span class="v18-here">${T(lang, '(vous êtes ici)', '(you are here)')}</span>` : `<li><a href="${prefix}${entryPath(e, lang)}">${esc(e.title[lang])}</a>`; };
  const list = BEGINNER_PATH.map(([id, subs = []]) => { const head = item(id); if (!head) return ''; const inner = subs.map(item).filter(Boolean).map(li => `${li}</li>`).join(''); return `${head}${inner ? `<p class="v19-path-more">${T(lang, 'Pour aller plus loin : histoire des races', 'Going further: race history')}</p><ul>${inner}</ul>` : ''}</li>`; }).join('');
  const nextId = NEXT_STEP[entry.id] ?? PATH_IDS[PATH_IDS.indexOf(entry.id) + 1];
  const next = nextId && get(nextId) ? `<p><a class="v2-btn is-gold-outline" href="${prefix}${entryPath(get(nextId), lang)}">${T(lang, 'Étape suivante', 'Next step')} : ${esc(get(nextId).title[lang])} <span aria-hidden="true">→</span></a></p>` : `<p>${T(lang, 'Vous êtes arrivé au bout du parcours débutant. Bonne aventure en Azeroth !', 'You have reached the end of the beginner path. Enjoy your adventure in Azeroth!')}</p>`;
  const cited = (entry.relations ?? []).filter(id => !PATH_IDS.includes(id)).map(get).filter(Boolean);
  const pages = cited.length ? `<h3>${T(lang, 'Pages du wiki citées dans ce guide', 'Wiki pages mentioned in this guide')}</h3><ul>${cited.map(e => `<li><a href="${prefix}${entryPath(e, lang)}">${esc(e.title[lang])}</a></li>`).join('')}</ul>` : '';
  return `<section class="article-section v18-path" id="parcours" aria-labelledby="parcours-title"><h2 id="parcours-title">${T(lang, 'Le parcours débutant', 'The beginner path')}</h2><ol class="v18-path-list">${list}</ol>${next}${pages}</section>`;
}

const TOC_ICONS = ['info', 'star', 'list', 'clock', 'chart', 'flag', 'calendar'];
export function renderEntry(entry, lang) {
  const prefix = '../../../';
  const cat = listingCategory(entry);
  const sid = sectionOf(entry);
  const {body: content, toc, sources} = entryContent(entry, lang);
  const path = beginnerPath(entry, lang, prefix);
  if (path) toc.push(['parcours', T(lang, 'Le parcours débutant', 'The beginner path')]);
  toc.push(['sources', T(lang, 'Sources', 'Sources')]);
  const v16 = entry.article?.format === 2; // v16 opt-in layout: closing Discussion part
  if (v16) toc.push(['discussion', T(lang, 'Discussion', 'Discussion')]);
  const groups = sourceGroups(entry);
  const trail = [[T(lang, 'Accueil', 'Home'), `${prefix}${lang}/`]];
  if (sid === 'communaute') trail.push([T(lang, 'Communauté', 'Community'), '/community/']);
  else { if (sid === 'jeu') trail.push([section('jeu').label[lang], `${prefix}${gamePath(lang)}`]); trail.push([label(cat, lang), catHref(cat, lang, prefix)]); }
  trail.push([entry.title[lang], '']);
  // v22: automatic (tags / category). Exception: the official Discord page keeps its related pages untouched (standing rule).
  // v39 « Pages liées »: the entry's own published relations first, then the automatic « À lire aussi » (max 6, never itself).
  const own = (entry.relations ?? []).map(id => CTX.byId.get(id)).filter(item => item && item.id !== entry.id);
  const related = DISCORD_UNTOUCHED.has(entry.id) ? own.slice(0, 3) : [...new Map([...own, ...readNext(entry, CTX.entries, lang)].map(item => [item.id, item])).values()].slice(0, 6);
  const rubrique = cat === 'community' ? T(lang, 'Communauté', 'Community') : label(cat, lang);
  const continent = continentLabel(entry, lang) && entry.subcategory === 'zone' ? continentLabel(entry, lang) : '';
  const info = [
    ...(continent ? [[T(lang, 'Continent', 'Continent'), esc(continent)]] : []),
    [T(lang, 'Rubrique', 'Section'), cat === 'community' ? `<a href="/community/" data-community-link>${esc(rubrique)}</a>` : `<a href="${catHref(cat, lang, prefix)}">${esc(rubrique)}</a>`],
    [T(lang, 'Type', 'Type'), entry.article ? T(lang, 'Article', 'Article') : T(lang, 'Fiche', 'Entry')],
    [T(lang, 'Statut', 'Status'), statusBadge(entry.status, lang, entry.verification)],
    [T(lang, 'Mis à jour', 'Updated'), date(entry.updatedAt, lang)],
    ...(entry.eventDate ? [[T(lang, 'Date de l’événement', 'Event date'), date(entry.eventDate, lang)]] : []),
    [T(lang, 'Version du jeu', 'Game version'), esc(entry.gameVersion)],
    ...(entry.article ? [[T(lang, 'Lecture', 'Reading time'), `${readingMinutes(entry, lang)} min`]] : []),
    [T(lang, 'Sources', 'Sources'), sourceCount(entry, groups, lang)]
  ];
  const infocard = `<section class="v2-infocard v39-infobox" aria-labelledby="info-title"><p id="info-title" class="v39-box-title">${icon('info')}${T(lang, 'En résumé', 'At a glance')}</p><dl class="v2-info">${info.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('')}</dl><p class="v2-info-desc">${esc(entry.description[lang])}</p>${entry.tags?.length ? `<ul class="v16-tags" aria-label="${T(lang, 'Mots-clés', 'Tags')}">${entry.tags.map(item => `<li class="v16-tag">${esc(item[lang])}</li>`).join('')}</ul>` : ''}</section>`;
  const tocNav = `<nav class="v2-toc v39-toc" aria-labelledby="toc-title"><p id="toc-title" class="v39-box-title">${icon('guides')}${T(lang, 'Sur cette page', 'On this page')}</p><ol>${toc.map(([id, text]) => `<li><a href="#${id}"><span>${esc(text)}</span></a></li>`).join('')}</ol></nav>`;
  const links = related.length ? `<nav class="v2-related v39-related" aria-labelledby="related-title"><p id="related-title" class="v39-box-title">${icon('link')}${T(lang, 'Pages liées', 'Related pages')}</p><ul class="v39-linklist">${related.map(item => `<li><a href="${prefix}${entryPath(item, lang)}">${catIcon(listingCategory(item))}<span>${esc(item.title[lang])}</span></a></li>`).join('')}</ul>${cat === 'community' ? '' : `<a class="v39-more-link" href="${catHref(cat, lang, prefix)}">${T(lang, 'Toute la rubrique', 'Whole section')} · ${esc(rubrique)} <span aria-hidden="true">→</span></a>`}</nav>` : '';
  const figure = zoneFigure(entry, prefix, lang) || `<figure class="v39-figure">${entryPicture(entry, prefix, lang, {eager: true, sizes: '(min-width: 1221px) 760px, (min-width: 700px) 92vw, 100vw', cls: 'v2-img'})}<figcaption>${esc(ART_LABEL[lang])}</figcaption></figure>`;
  const main = crumbs(lang, trail) + pageHead(entry.title[lang], '', rubrique) + figure + sectionTabs(lang, toc)
    + `<article class="v2-article" aria-labelledby="page-title">${content}${path}${sources}${v16 ? discussionBlock(lang, entry.category) : ''}<p class="article-version">${T(lang, 'Version documentaire', 'Documentary version')} : ${esc(entry.gameVersion)} · ${T(lang, 'révision', 'revision')} ${entry.version}</p></article>`;
  const rail = `<aside class="v2-rail">${infocard}${tocNav}${links}</aside>`;
  return page({lang, prefix, title: entry.title[lang], description: entry.description[lang], switchHref: `${prefix}${entryPath(entry, other(lang))}`, current: menuCurrent(cat), body: layout({lang, prefix, cat, id: entry.id, main, rail, cls: 'is-entry'})});
}

/** "Tout le wiki" A–Z: every published entry, grouped by section and category (static, no script needed). */
export function renderIndex(lang) {
  const prefix = '../../';
  const groups = SECTIONS.map(sec => {
    const cats = sec.id === 'communaute' ? ['community'] : sec.categories;
    const blocks = cats.map(cat => {
      const items = inListing(CTX.entries, cat).sort((a, b) => a.title[lang].localeCompare(b.title[lang], lang));
      return items.length ? `<div class="v2-index-cat"><h3>${cat === 'community' ? '' : `<a href="${catHref(cat, lang, prefix)}">`}${esc(cat === 'community' ? T(lang, 'Discord et forums', 'Discord and forums') : label(cat, lang))}${cat === 'community' ? '' : '</a>'} <span class="wk-count">${items.length}</span></h3><ul>${items.map(item => `<li><a href="${prefix}${entryPath(item, lang)}">${esc(item.title[lang])}</a>${item.article ? ` <span class="v2-tag is-article">${T(lang, 'Article', 'Article')}</span>` : ''}</li>`).join('')}</ul></div>` : '';
    }).join('');
    return blocks ? `<section class="v2-index-sec" aria-labelledby="idx-${sec.id}"><h2 id="idx-${sec.id}" class="v2-h2">${icon(sec.id)}${esc(sec.label[lang])}</h2><div class="v2-index-grid">${blocks}</div></section>` : '';
  }).join('');
  const body = layout({lang, prefix, main: `<div class="v2-index">${crumbs(lang, [[T(lang, 'Accueil', 'Home'), `${prefix}${lang}/`], [T(lang, 'Tout le wiki', 'The whole wiki'), '']])}<h1 id="page-title" class="v2-h1">${T(lang, 'Tout le wiki de A à Z', 'The whole wiki, A to Z')}</h1><p class="v2-lede">${CTX.entries.length} ${T(lang, 'fiches et articles publiés, vérifiés et sourcés. Utilisez la loupe pour chercher un mot.', 'published, reviewed and sourced entries and articles. Use the magnifier to search a word.')}</p>${groups}</div>`});
  return page({lang, prefix, title: T(lang, 'Tout le wiki', 'The whole wiki'), description: T(lang, 'Index complet du wiki.', 'Full wiki index.'), switchHref: `${prefix}${wikiIndexPath(other(lang))}`, current: '', body});
}
/**
 * v15 — page left at the address of an entry merged into another one (addresses unchanged rule).
 * Static, no script: an HTML meta refresh (not governed by the CSP) sends the reader to the kept page,
 * with a visible link as fallback. The merged entry itself is never rendered (it is no longer published).
 */
export function renderMoved(retired, target, lang, mergedAt) {
  const prefix = '../../../';
  const href = `${prefix}${entryPath(target, lang)}`;
  const head = `<meta http-equiv="refresh" content="0; url=${esc(href)}"><link rel="canonical" href="${esc(href)}">`;
  const when = mergedAt ? ` ${T(lang, 'le', 'on')} ${date(mergedAt, lang)}` : '';
  const body = `<div class="v2-wrap v2-moved">${crumbs(lang, [[T(lang, 'Accueil', 'Home'), `${prefix}${lang}/`], [T(lang, 'Page fusionnée', 'Merged page'), '']])}<h1 id="page-title" class="v2-h1">${T(lang, 'Cette page a été fusionnée', 'This page has been merged')}</h1><p class="v2-lede">${T(lang, `« ${esc(retired.title[lang])} » a été réunie${when} avec « ${esc(target.title[lang])} », qui regroupe désormais tous les faits et toutes les sources officielles des deux pages.`, `“${esc(retired.title[lang])}” was merged${when} into “${esc(target.title[lang])}”, which now gathers all the facts and all the official sources of both pages.`)}</p><p><a class="v2-btn is-gold" href="${esc(href)}">${T(lang, 'Lire la page', 'Read the page')} « ${esc(target.title[lang])} » <span aria-hidden="true">→</span></a></p></div>`;
  return page({lang, prefix, title: T(lang, 'Page fusionnée', 'Merged page'), description: T(lang, `Page fusionnée avec « ${target.title[lang]} ».`, `Page merged into “${target.title[lang]}”.`), switchHref: `${prefix}${entryPath(target, other(lang))}`, current: '', body, head});
}

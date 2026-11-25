// v39 BUILD DE TEST (nouvelle interface, Mathieu t386u/t387u) — garde-fous : forum intact (règles et script cantonnés à
// body.v39), arbre des catégories = pages publiées seulement, aucune donnée inventée, FR/EN à parité, CSP, accessibilité.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {entryPath, categoryPath} from '../lib/articles.mjs';
import {setV2Catalog, renderHome, renderCategory, renderEntry} from '../lib/v2/render.mjs';
import {MENU, MORE, TREE_ORDER, groupsFor, continentOf} from '../lib/v39/nav.mjs';
import {inListing} from '../lib/v2/structure.mjs';

const css = await readFile(new URL('../public/v39/v39.css', import.meta.url), 'utf8');
const js = await readFile(new URL('../public/v39/v39-nav.js', import.meta.url), 'utf8');
const categories = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories;
const published = (await siteEntries()).filter(entry => entry.status === 'published');
setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published);

test('v39 CSS: every rule is scoped to the wiki (body.v39), no external resource, no font file, no 100vw box', () => {
  const plain = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const selectors = [...plain.matchAll(/(?:^|[{}])\s*([^{}@]+?)\s*\{/g)].map(m => m[1].trim()).filter(sel => sel && !/^(from|to|\d+%)$/.test(sel));
  assert.ok(selectors.length > 100);
  for (const rule of selectors) for (const sel of rule.split(',')) {
    assert.match(sel.trim(), /^(\.v39(\b|-)|body\.v39|html:has\(body\.v39\)|html\.v39-side-open|\[data-theme=wow\] (body)?\.v39\b)/, sel);
  }
  assert.doesNotMatch(css, /@import|https?:|url\(|@font-face|\.woff|100vw|backdrop-filter/);
});

test('v39 JS: inert outside the wiki, no network, no cookie, no HTML injection', () => {
  assert.match(js, /^\/\*\*[\s\S]*?\*\/\nif \(document\.body\?\.classList\.contains\('v39'\)\) \{/);
  assert.doesNotMatch(js, /fetch\(|XMLHttpRequest|document\.cookie|localStorage|innerHTML|insertAdjacentHTML|eval\(|https?:/);
});

test('v39 navigation: menu and tree list only categories with published pages; groups cover every page once', () => {
  for (const id of TREE_ORDER) assert.ok(inListing(published, id).length > 0, `${id} is empty — it must be hidden`);
  for (const lang of ['fr', 'en']) for (const cat of TREE_ORDER) {
    const groups = groupsFor(cat, published, lang);
    const ids = groups.flatMap(group => group.items.map(entry => entry.id));
    assert.equal(ids.length, inListing(published, cat).length, cat);
    assert.equal(new Set(ids).size, ids.length, cat);
  }
  const zones = Object.fromEntries(groupsFor('zones', published, 'fr').map(group => [group.key, group.items.length]));
  assert.deepEqual(zones, {kalimdor: 21, 'eastern-kingdoms': 26, 'forever-regions': 4, overview: 3});
  // continent: read from the published description only (« Nom (Kalimdor) : … »), never guessed
  for (const entry of published.filter(entry => continentOf(entry))) assert.match(entry.description.fr, /^[^:(]*\((Kalimdor|Royaumes de l’Est)\)/);
  assert.equal(MENU.length + MORE.length, TREE_ORDER.length);
});

test('v39 pages: one h1, noindex, no inline code, header hooks, tree with the current page, FR/EN parity', () => {
  const tanaris = published.find(entry => entry.id === 'forever-zone-tanaris');
  const pages = {};
  for (const lang of ['fr', 'en']) pages[lang] = [renderHome(lang), renderCategory('zones', lang), renderEntry(tanaris, lang), renderEntry(published.find(e => e.id === 'forever-recipes-alchemy') ?? published.find(e => e.category === 'professions'), lang)];
  for (const lang of ['fr', 'en']) for (const html of pages[lang]) {
    assert.equal((html.match(/<h1[ >]/g) ?? []).length, 1);
    assert.match(html, /<meta name="robots" content="noindex,nofollow">/);
    assert.doesNotMatch(html, /<script(?![^>]*\bsrc=")[^>]*>|<style|\sstyle="/);
    assert.equal((html.match(/<script type="module" src="(\.\.\/)*wk-header\.js"><\/script>/g) ?? []).length, 1);
    for (const hook of ['data-wk-header', 'id="wk-nav"', 'id="wk-menu-toggle"', 'data-wk-search-open', 'id="wk-search"', 'id="v39-side"', 'class="v39-side-toggle"']) assert.ok(html.includes(hook), hook);
    assert.ok(html.includes('<body class="v2 v39'));
  }
  const tree = html => (html.match(/<nav class="v39-side"[\s\S]*?<\/nav>/)?.[0].match(/<a /g) ?? []).length;
  for (let i = 0; i < pages.fr.length; i++) assert.equal(tree(pages.fr[i]), tree(pages.en[i]), `tree parity #${i}`);
  const fr = renderEntry(tanaris, 'fr');
  assert.match(fr, /<li><a href="\.\.\/\.\.\/\.\.\/fr\/zones\/tanaris\/" aria-current="page">Tanaris<\/a><\/li>/);
  assert.match(fr, /<details open><summary><span>Kalimdor<\/span>/);
  assert.match(fr, /<dt>Continent<\/dt><dd>Kalimdor<\/dd>/);
  assert.match(renderEntry(tanaris, 'en'), /<dt>Continent<\/dt><dd>Kalimdor<\/dd>/);
  // every tree / related link points to a published page or a category page
  const known = new Set(['fr', 'en'].flatMap(lang => [...published.map(entry => entryPath(entry, lang)), ...TREE_ORDER.map(cat => categoryPath(cat, lang))]));
  for (const href of fr.match(/<nav class="v39-side"[\s\S]*?<\/nav>|<nav class="v2-related v39-related"[\s\S]*?<\/nav>/g).join('').match(/href="\.\.\/\.\.\/\.\.\/[^"]+"/g)) {
    const path = href.slice(15, -1);
    if (!path.endsWith('/wiki/')) assert.ok(known.has(path), path);
  }
});

test('t390u — zone images: official Blizzard game images only, unmodified (resize only), self-hosted, captioned © Blizzard with source link', async () => {
  const {readFile: rf, access, readdir} = await import('node:fs/promises');
  const imgs = JSON.parse(await rf(new URL('../data/zone-images.json', import.meta.url), 'utf8'));
  const official = /^https:\/\/(worldofwarcraft\.blizzard\.com|news\.blizzard\.com|blizzard\.gamespress\.com)\//;
  for (const [id, img] of Object.entries(imgs)) {
    assert.match(id, /^forever-zone-/, id);
    assert.equal(img.copyright, '© Blizzard Entertainment', id);
    assert.match(img.source, official, id);
    assert.doesNotMatch(`${img.source} ${img.image}`, /wowhead|wiki\.gg|wikimedia|fandom|map/i, id);
    assert.ok(img.identification, id);
    // aspect ratio preserved (no crop): stored 1024 height matches the original ratio
    assert.equal(img.height, Math.round(img.original[1] * 1024 / img.original[0]), id);
    for (const w of [640, 1024]) for (const ext of ['webp', 'avif']) await access(new URL(`../public/v2/assets/${img.asset}-${w}.${ext}`, import.meta.url));
  }
  assert.equal(Object.keys(imgs).length, 14);
  const assets = await readdir(new URL('../public/v2/assets/', import.meta.url));
  assert.equal(assets.filter(f => f.startsWith('zone-') && !f.startsWith('zone-jeu-')).length, 0, 'no Wikimedia photo left');
  for (const lang of ['fr', 'en']) {
    const slug = lang === 'fr' ? 'mulgore' : 'mulgore';
    const html = await rf(new URL(`../dist-v2/${lang}/zones/${slug}/index.html`, import.meta.url), 'utf8');
    assert.match(html, /v39-figure is-game/);
    assert.match(html, /assets\/zone-jeu-mulgore-1024\.webp/);
    assert.match(html, lang === 'fr' ? /Image du jeu © Blizzard Entertainment/ : /Game image © Blizzard Entertainment/);
    assert.match(html, /href="https:\/\/worldofwarcraft\.blizzard\.com\/en-us\/forever"/);
    assert.doesNotMatch(html, /(src|srcset)="https?:/);
    assert.doesNotMatch(html, /CC BY|Wikimedia|paysage réel|real-world/i);
  }
  // a zone with no identifiable official image keeps the original ambiance artwork
  const tan = await rf(new URL('../dist-v2/fr/zones/tanaris/index.html', import.meta.url), 'utf8');
  assert.doesNotMatch(tan, /is-game/);
  const fig = tan.slice(tan.indexOf('<figure class="v39-figure"'), tan.indexOf('</figure>', tan.indexOf('<figure class="v39-figure"')));
  assert.ok(fig.length > 0); assert.doesNotMatch(fig, /© Blizzard/);
  // t391u : pied de page approuvé par Mathieu (FR + EN)
  assert.match(tan, /Illustrations : illustrations d’ambiance originales ou images du jeu © Blizzard Entertainment\./);
  const tanEn = await rf(new URL('../dist-v2/en/zones/tanaris/index.html', import.meta.url), 'utf8');
  assert.match(tanEn, /Illustrations: original ambiance artwork or game images © Blizzard Entertainment\./);
});

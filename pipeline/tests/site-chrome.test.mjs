import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {setNavCatalog, siteHeader, searchIndex, NAV_GROUPS, SITE_NAME} from '../lib/site-chrome.mjs';
import {sitePayload, siteEntries, siteMarkup, wikiTemplate} from '../lib/site.mjs';
import {entryPath} from '../lib/articles.mjs';

const categories = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories;
const entry = (id, category, status = 'published') => ({id, category, status, publicationValidated: status === 'published', title: {fr: id, en: id}, description: {fr: 'd', en: 'd'}, url: {fr: `fr/x/${id}/`, en: `en/x/${id}/`}, sources: [{url: 'https://news.blizzard.com/x', license: 'l', accessedAt: '2026-10-30', title: 't'}], history: [{at: 'x', note: 'private note'}]});

test('L1 header: Wowkipedia brand (v21 rename), accessible controls, menu limited to categories with published content', () => {
  setNavCatalog({categories, entries: [entry('a', 'zones'), entry('b', 'classes', 'draft')]});
  const html = siteHeader({lang: 'fr', prefix: '../../', switchHref: '../../en/zones/', home: '../../fr/'});
  assert.equal(SITE_NAME, 'Wowkipedia');
  assert.match(html, /<span class="wk-wordmark">Wow<span class="wk-wordmark-ki">ki<\/span>pedia<\/span>/);
  assert.match(html, /href="\.\.\/\.\.\/fr\/zones\/"/);
  assert.doesNotMatch(html, /fr\/classes\//, 'a category with drafts only is not in the menu');
  assert.doesNotMatch(html, /wk-panel-guides/, 'an empty group is not rendered');
  for (const id of ['wk-nav', 'wk-menu-toggle', 'wk-search', 'wk-search-input', 'wk-search-results', 'wk-search-status']) assert.match(html, new RegExp(`id="${id}"`));
  // L1b: the "Univers" group became "Le monde" (wk-panel-monde).
  assert.match(html, /aria-expanded="false" aria-controls="wk-panel-monde"/);
  assert.match(html, /role="dialog" aria-modal="true" aria-labelledby="wk-search-title"/);
  assert.match(html, /<a class="wk-discord" href="\/account\/" data-community-link>/);
  assert.match(html, /<a class="wk-lang" href="\.\.\/\.\.\/en\/zones\/" hreflang="en" lang="en">/);
  assert.doesNotMatch(html, /<script|style="|https?:\/\//, 'no inline script/style, no external resource');
  setNavCatalog({categories: [], entries: []});
});

test('L1 header: no retail or invented menu entries (Forever categories only)', () => {
  const labels = JSON.stringify(NAV_GROUPS);
  for (const word of ['Midnight', 'Nerub', 'Saison 3', 'Season 3', 'Chevalier de la mort', 'Death Knight', 'Talent', 'Extension', 'Expansion', 'Hauts faits', 'Achievement', 'Guilde', 'Guild', 'Mythique', 'Mythic']) assert.ok(!labels.includes(word), word);
  const known = new Set(categories.map(([id]) => id));
  for (const group of NAV_GROUPS) for (const column of group.columns) for (const item of column.items) if (item.category) assert.ok(known.has(item.category), item.category);
});

test('L1 search index: published entries only, minimal public fields, drafts AC2/CL3 absent', async () => {
  const index = searchIndex({categories, entries: [entry('a', 'zones'), entry('b', 'classes', 'draft')]});
  assert.deepEqual(index.entries.map(item => item.id), ['a']);
  assert.ok(!('history' in index.entries[0]));
  assert.deepEqual(index.categories.map(([id]) => id), ['zones']);
  const real = searchIndex(await sitePayload());
  const ids = real.entries.map(item => item.id);
  assert.equal(ids.length, (await siteEntries()).length);
  assert.ok(!ids.includes('forever-news-beta') && ids.includes('forever-class-priest'));
  for (const item of real.entries) assert.deepEqual(Object.keys(item).filter(key => !['id', 'status', 'publicationValidated', 'category', 'subcategory', 'title', 'description', 'url', 'searchText', 'hasArticle', 'sources'].includes(key)), []);
});

test('L1b menu: six entries in the approved order, logo = home, counts, "Tout le wiki" in each panel and in the drawer', async () => {
  assert.deepEqual(NAV_GROUPS.map(group => group.label.fr), ['Actualités', 'Le monde', 'Classes', 'Guides', 'Activités', 'Communauté']);
  assert.deepEqual(NAV_GROUPS.map(group => group.label.en), ['News', 'The world', 'Classes', 'Guides', 'Activities', 'Community']);
  const payload = await sitePayload();
  const published = await siteEntries();
  setNavCatalog({categories: payload.categories, entries: published});
  const fr = siteHeader({lang: 'fr', prefix: '../../', switchHref: '../../en/zones/', home: '../../fr/', current: 'monde'});
  const en = siteHeader({lang: 'en', prefix: '../../', switchHref: '../../fr/zones/', home: '../../en/'});
  const tops = html => [...html.matchAll(/<button type="button" class="wk-top"[^>]*>([^<]+)</g)].map(match => match[1]);
  assert.deepEqual(tops(fr), ['Actualités', 'Le monde', 'Classes', 'Guides', 'Activités', 'Communauté']);
  assert.deepEqual(tops(en), ['News', 'The world', 'Classes', 'Guides', 'Activities', 'Community']);
  assert.doesNotMatch(fr, /class="wk-top" href=/, 'no separate "Accueil" item: the logo is the home link');
  assert.match(fr, /<a class="wk-brand" href="\.\.\/\.\.\/fr\/">/);
  // Counts = published entries per category.
  const count = id => published.filter(entry => entry.category === id).length;
  for (const [id, slug] of [['news', 'actualites'], ['zones', 'zones'], ['classes', 'classes'], ['instances', 'donjons-raids'], ['glossary', 'glossaire']]) {
    assert.match(fr, new RegExp(`href="\\.\\./\\.\\./fr/${slug}/"><span class="wk-label">[^<]+</span><span class="wk-count">${count(id)}<`), id);
  }
  assert.equal(count('news'), 19); // v35 (t347u): + factions JcJ ; v31: + équilibrage + correctifs ; v30: + poussière + Taldramir ; v23 : + tradition ; v22 : + golive + notes
  // "Tout le wiki" in each of the six panels + once at the bottom of the drawer.
  assert.equal((fr.match(/class="wk-all" href="\.\.\/\.\.\/fr\/wiki\/"/g) ?? []).length, 6);
  assert.match(fr, /<div class="wk-drawer-extra"><a class="wk-all wk-all-drawer" href="\.\.\/\.\.\/fr\/wiki\/">Tout le wiki/);
  assert.match(en, /class="wk-all" href="\.\.\/\.\.\/en\/wiki\/">The whole wiki/);
  // Search overlay: form, magnifier and "see all results" lead to the registry page.
  assert.match(fr, /<form class="wk-search-form" role="search" action="\.\.\/\.\.\/fr\/wiki\/" method="get">/);
  assert.match(fr, /data-wk-search-open[^>]*>|href="\.\.\/\.\.\/fr\/wiki\/#search-input"/);
  assert.match(fr, /data-registry="\.\.\/\.\.\/fr\/wiki\/"/);
  assert.match(fr, /<a class="wk-discord" href="\/account\/" data-community-link>/);
  // Classes: eight published class pages, alphabetical; the Priest (draft CL3) is absent, as is any placeholder.
  const classes = [...fr.matchAll(/href="\.\.\/\.\.\/fr\/classes\/[a-z0-9-]+\/"><span class="wk-label">([^<]+)</g)].map(match => match[1]);
  assert.deepEqual(classes, ['Vue d’ensemble des classes', 'Chaman', 'Chasseur', 'Démoniste', 'Druide', 'Guerrier', 'Mage', 'Paladin', 'Voleur']);
  for (const html of [fr, en]) {
    assert.doesNotMatch(html, /Prêtre|Priest|bientôt|coming soon|Montures|Mounts|Réputations|Reputations|Mascottes|Hauts faits/i);
    assert.doesNotMatch(html, /forever-news-beta|acces-a-la-beta|beta-access/);
  }
  // "Histoire et récits" links to the published short story itself (no lore category, no content moved).
  const story = published.find(entry => entry.id === 'forever-news-story-unbowed');
  assert.ok(story && story.status === 'published');
  assert.match(fr, /href="\.\.\/\.\.\/fr\/actualites\/[a-z0-9-]+\/"><span class="wk-label">Histoire et récits<span class="wk-hint">Nouvelle « Unbowed »<\/span>/);
  assert.match(fr, /aria-controls="wk-panel-monde"/);
  assert.match(fr, /class="wk-item wk-has-panel is-current"><button type="button" class="wk-top" aria-expanded="false" aria-controls="wk-panel-monde"/);
  // Preview (local drafts) header: no registry link, never a draft class in the menu.
  const preview = siteHeader({lang: 'fr', prefix: '../', preview: true});
  assert.doesNotMatch(preview, /wiki\//);
  setNavCatalog({categories: [], entries: []});
});

test('L1b "Tout le wiki" page: registry, filters and search form without the home hero/featured/tools', async () => {
  const template = await readFile(new URL('../public/wiki/template.html', import.meta.url), 'utf8');
  const wiki = wikiTemplate(template);
  for (const id of ['search-form', 'search-input', 'archives', 'categories', 'catalog-section', 'results', 'result-summary', 'entry-panel', 'feature-panel', 'account-dialog', 'info-dialog']) assert.match(wiki, new RegExp(`id="${id}"`), id);
  assert.equal((wiki.match(/<h1\b/g) ?? []).length, 1);
  assert.match(wiki, /<h1 id="wiki-title"[^>]*>Tout le wiki<\/h1>/);
  assert.doesNotMatch(wiki, /class="hero ornate"|class="feature-grid"|hero-title/);
  assert.equal((wiki.match(/data-category="/g) ?? []).length, 12);
  assert.match(wiki, /Site indépendant et non officiel de Blizzard Entertainment\./);
  const en = await siteMarkup({lang: 'en', prefix: '../../', page: 'wiki'});
  assert.match(en, /<h1 id="wiki-title"[^>]*>The whole wiki<\/h1>/);
  assert.match(en, /<a class="wk-lang" href="\.\.\/\.\.\/fr\/wiki\/"/, 'FR/EN keeps the registry page');
  assert.doesNotMatch(en, /<script(?! id="wiki-data" type="application\/json")|style="/);
  assert.doesNotMatch(en, /"forever-news-beta"/);
});

test('L1b menu links on home and registry pages use the real page paths (article slugs), never title-derived guesses', async () => {
  const published = await siteEntries();
  const paths = new Set(published.flatMap(entry => [entryPath(entry, 'fr'), entryPath(entry, 'en')]));
  for (const [lang, prefix, page] of [['fr', '../', 'home'], ['en', '../', 'home'], ['fr', '../../', 'wiki'], ['en', '../../', 'wiki']]) {
    const html = await siteMarkup({lang, prefix, page});
    const header = html.slice(html.indexOf('<header class="wk-header"'), html.indexOf('</header>'));
    const links = [...header.matchAll(/href="((?:\.\.\/)+)((?:fr|en)\/[a-z0-9-]+\/[a-z0-9-]+\/)"/g)].map(match => match[2]);
    assert.ok(links.length >= 12, `${lang} ${page}: ${links.length}`);
    for (const link of links) assert.ok(paths.has(link), `${lang} ${page}: ${link}`);
  }
});

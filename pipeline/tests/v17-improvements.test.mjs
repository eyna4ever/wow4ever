// v17 (ameliorations-v17) — approuvé par Mathieu (« 1 2 3 4 5 », 01/11/2026) : B « Quoi de neuf » sur l'accueil, C recherche
// instantanée plus rapide sur mobile, E guides débutant (BROUILLONS, sources officielles Blizzard datées uniquement).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {siteEntries, sitePayload} from '../lib/site.mjs';
import {searchIndex, compactSearchText} from '../lib/site-chrome.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderHome, renderEntry, whatsNew, WHATS_NEW} from '../lib/v2/render.mjs';
import {inListing} from '../lib/v2/structure.mjs';
import {entryPath, sourcedBlocks} from '../lib/articles.mjs';
import {searchEntries, prepareSearch, searchPrepared} from '../lib/ui-core.mjs';
import {draftToEntry} from '../lib/v16/draft.mjs';
import {validate} from '../lib/documentary.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
const published = (await siteEntries()).filter(e => e.status === 'published');
const records = JSON.parse(await readFile(join(dirname(fileURLToPath(import.meta.url)), '../runtime/entries.json'), 'utf8'));
const setup = () => { setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published); };

test('v17 B « Quoi de neuf »: 3 latest news + recently updated pages, from published data, reproducible', () => {
  setup();
  for (const lang of ['fr', 'en']) {
    const {news, pages} = whatsNew(published, lang);
    assert.equal(news.length, WHATS_NEW.news); assert.equal(pages.length, WHATS_NEW.pages);
    const allNews = inListing(published, 'news').map(e => e.updatedAt).sort().reverse();
    assert.deepEqual(news.map(e => e.updatedAt), allNews.slice(0, 3), 'newest news first');
    assert.ok(pages.every(e => e.category !== 'news' && e.status === 'published'));
    const others = published.filter(e => e.category !== 'news').map(e => e.updatedAt).sort().reverse();
    assert.deepEqual(pages.map(e => e.updatedAt), others.slice(0, 5));
    assert.deepEqual(whatsNew([...published].reverse(), lang), {news, pages}, 'order of the data does not matter');
    const html = renderHome(lang);
    assert.match(html, new RegExp(`<h2 id="news-title" class="v2-h2">${lang === 'fr' ? 'Quoi de neuf' : 'What’s new'}</h2>`));
    for (const e of [...news, ...pages]) assert.ok(html.includes(`href="../${entryPath(e, lang)}"`) && html.includes(e.title[lang].replace(/&/g, '&amp;').replace(/"/g, '&quot;')), e.id);
    assert.doesNotMatch(html, /<script(?! type="module" src="\.\.\/wk-header\.js")(?! src="\.\.\/theme\.js"><\/script>)|style=|<style/);
    assert.match(html, /<meta name="robots" content="noindex,nofollow">/);
    assert.ok(html.includes('Site indépendant et non officiel de Blizzard Entertainment.'));
    assert.ok(!['forever-news-beta'].some(id => html.includes(id)));
  }
  setVisualLinks([]);
});

test('v17 C search: prepared search finds exactly what the previous search found, ranks titles first, compact index loses nothing', async () => {
  const payload = await sitePayload();
  const full = searchIndex({...payload, entries: payload.entries}).entries;
  const withFullText = payload.entries.filter(e => e.status === 'published' && e.publicationValidated === true);
  const prepared = prepareSearch(full);
  const preparedFull = prepareSearch(withFullText);
  const queries = ['lancement', 'Éolides', 'raid', 'chaman', 'ensemble regles', 'pvp', 'mont hyjal', 'pret', 'zéphras', 'heritage', 'podcast', 'discord', 'x', 'zzzz'];
  for (const lang of ['fr', 'en']) for (const query of queries) {
    const before = searchEntries(withFullText, {query, lang}).map(e => e.id).sort();
    assert.deepEqual(searchPrepared(preparedFull, {query, lang, limit: 999}).results.map(e => e.id).sort(), before, `${lang} ${query} (same rule)`);
    assert.deepEqual(searchPrepared(prepared, {query, lang, limit: 999}).results.map(e => e.id).sort(), before, `${lang} ${query} (compact index)`);
  }
  const {results, total} = searchPrepared(prepared, {query: 'lancement', lang: 'fr', limit: 8});
  assert.ok(total >= results.length && results.length <= 8);
  assert.ok(results[0].title.fr.toLowerCase().includes('lancement'), 'a title match comes first');
  assert.equal(searchPrepared(prepared, {query: '   ', lang: 'fr'}).total, 0);
  assert.deepEqual(compactSearchText({fr: 'Le Mont  Hyjal, le mont.', en: 'A b a'}), {fr: 'le mont hyjal, mont.', en: 'a b'});
  assert.ok(Buffer.byteLength(JSON.stringify({entries: full})) < Buffer.byteLength(JSON.stringify({entries: searchIndex({...payload, entries: payload.entries}).entries.map((e, i) => ({...e, searchText: withFullText.find(x => x.id === e.id)?.searchText}))})), 'index is lighter');
});

test('v17 C wk-header.js: results while typing, prefetch on intent, DOM-only rendering, same-origin index only', async () => {
  const js = await readFile(join(root, 'public/wiki/wk-header.js'), 'utf8');
  assert.match(js, /prepareSearch\(data\.entries\)/);
  assert.match(js, /addEventListener\('input', \(\) => \{ clearTimeout\(timer\); if \(prepared\) render\(\);/);
  assert.match(js, /\['pointerdown', 'touchstart', 'mouseenter', 'focus'\]/);
  assert.doesNotMatch(js, /innerHTML|outerHTML|insertAdjacentHTML|eval\(|new Function|https?:\/\//);
  assert.equal((js.match(/fetch\(/g) ?? []).length, 1);
  assert.match(js, /new URL\('search-index\.json', import\.meta\.url\)/);
});

test('v17 E guides débutant: drafts only, official Blizzard sources with publication and access dates, every fact cited', async () => {
  const dir = join(root, '../ops/v17/guides');
  const files = (await readdir(dir)).filter(f => f.endsWith('.md'));
  assert.ok(files.length >= 1);
  for (const file of files) {
    const {entry, errors} = draftToEntry(await readFile(join(dir, file), 'utf8'), {file});
    assert.deepEqual(errors, [], file);
    assert.deepEqual(validate(entry), []);
    assert.equal(entry.status, 'draft'); assert.equal(entry.identityConfirmed, false); assert.equal(entry.review, undefined);
    assert.equal(entry.category, 'guides'); assert.equal(entry.article.format, 2);
    // v17 published (review.mjs, Mathieu, t255u): the published record is exactly the draft plus the human review.
    const pub = published.find(e => e.id === entry.id);
    const revisedV18 = records.find(e => e.id === entry.id)?.history?.some(h => /^revise: v18/.test(h.note ?? ''));
    if (pub && !revisedV18) {  // v18: once revised, the published record follows ops/v18/guides (see v18-guides.test.mjs)
      const rec = records.find(e => e.id === entry.id);   // runtime record (the public DTO carries no review data)
      assert.equal(rec.status, 'published'); assert.equal(rec.review?.reviewer, 'Mathieu'); assert.equal(rec.review?.approved, true);
      assert.equal(rec.identityConfirmed, true); assert.ok(rec.review.rightsConfirmed && rec.review.translationsConfirmed);
      assert.ok(rec.history.some(h => /t255u/.test(h.note ?? '')), 'decision t255u recorded in history');
      assert.deepEqual(pub.article, entry.article); assert.deepEqual(pub.sources, entry.sources); assert.deepEqual(pub.title, entry.title);
    }
    for (const source of entry.sources) {
      const host = new URL(source.url).hostname;
      assert.ok(['news.blizzard.com', 'worldofwarcraft.blizzard.com'].includes(host), source.url);
      assert.equal(source.accessedAt, '2026-11-01');
      if (host === 'news.blizzard.com') assert.match(source.publishedAt, /^2026-\d{2}-\d{2}$/);
      else { assert.equal(source.undated, true); assert.equal(source.publishedAt, undefined); assert.match(source.url, /\/game\/races\/[a-z-]+$/); }
    }
    assert.ok(entry.article.sections.every(s => s.blocks.every(b => b.type !== 'analysis')), 'guides: facts only, no opinion block');
    for (const {where, block} of sourcedBlocks(entry.article)) assert.ok(block.src?.length, `${file} ${where}`);
    setup();
    const html = renderEntry(entry, 'fr');
    for (const date of new Set(entry.sources.filter(x => x.language === 'fr' && x.publishedAt).map(x => x.publishedAt))) assert.match(html, new RegExp(`publié le <time datetime="${date}">`));
    assert.match(html, /consulté le <time datetime="2026-11-01">/);
    if (entry.sources.some(x => x.undated)) assert.match(html, /date de publication non indiquée · consulté le/);
    setVisualLinks([]);
  }
});

test('v17 E sources: only an official non-news page may be undated, and never with an invented date', async () => {
  const {validateArticle} = await import('../lib/articles.mjs');
  const base = published.find(e => e.article?.format === 2) ?? published.find(e => e.article);
  const withSource = source => validateArticle({...base, sources: [source]}).filter(e => /publishedAt/.test(e));
  const page = {key: 'p-fr', language: 'fr', url: 'https://worldofwarcraft.blizzard.com/fr-fr/game/races/orc', title: 'Orc', accessedAt: '2026-11-01', license: 'x'};
  assert.deepEqual(withSource({...page, undated: true}), []);
  assert.equal(withSource(page).length, 1, 'undated must be explicit');
  assert.equal(withSource({...page, url: 'https://news.blizzard.com/fr-fr/article/1/x', undated: true}).length, 1, 'news articles always need their date');
});

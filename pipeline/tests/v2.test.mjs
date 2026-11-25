import {test, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks, UNOFFICIAL} from '../lib/pages.mjs';
import {SECTIONS, sectionOf, listingCategory, inListing} from '../lib/v2/structure.mjs';
import {setV2Catalog, renderHome, renderGame, renderCategory, renderEntry, renderIndex} from '../lib/v2/render.mjs';

const categories = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories;
const published = (await siteEntries()).filter(entry => entry.status === 'published');
const setup = () => { setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published); };
afterEach(() => setVisualLinks([])); // keep the shared module state as the other suites expect (--test-isolation=none)

test('v2 structure: every published entry sits in exactly one section and one listing; no empty section', () => {
  setup();
  const cats = SECTIONS.flatMap(section => section.categories).concat('community');
  for (const entry of published) {
    assert.ok(SECTIONS.some(section => section.id === sectionOf(entry)), entry.id);
    assert.equal(cats.filter(cat => inListing(published, cat).some(item => item.id === entry.id)).length, 1, entry.id);
    assert.equal(listingCategory(entry) === 'community' ? 'communaute' : SECTIONS.find(s => s.categories.includes(listingCategory(entry))).id, sectionOf(entry));
  }
  const totals = Object.fromEntries(SECTIONS.map(s => [s.id, published.filter(e => sectionOf(e) === s.id).length]));
  assert.equal(Object.values(totals).reduce((a, b) => a + b, 0), published.length);
  for (const [id, n] of Object.entries(totals)) assert.ok(n > 0, `section ${id} is empty`);
});

test('v2 pages: no draft, no inline script/style, independence notice on every page, FR/EN symmetric', () => {
  setup();
  const drafts = ['forever-news-beta']; // v22: CL3 published
  assert.ok(drafts.every(id => !published.some(entry => entry.id === id)), 'AC2 must stay a draft');
  const pages = [];
  for (const lang of ['fr', 'en']) {
    pages.push(renderHome(lang), renderGame(lang), renderIndex(lang));
    for (const cat of SECTIONS.flatMap(s => s.categories)) if (inListing(published, cat).length) pages.push(renderCategory(cat, lang));
    for (const entry of published) pages.push(renderEntry(entry, lang));
  }
  assert.equal(pages.length, 2 * (3 + 12 + published.length));
  for (const html of pages) {
    assert.ok(html.includes(UNOFFICIAL.fr), 'footer notice');
    assert.doesNotMatch(html, /<script(?![^>]*\bsrc=)[^>]*>/, 'inline script');
    assert.doesNotMatch(html, /<style|\sstyle="/, 'inline style');
    for (const id of drafts) assert.ok(!html.includes(id), `draft ${id} leaked`);
    assert.doesNotMatch(html, /\bMidnight\b|Nerub-ar|Nerub’ar|Nerub'ar|Chevalier de la mort|Death Knight|[Bb]uilder de talents|[Tt]alent builder|[Cc]onstructeur de talents/, 'retail/out-of-scope content');
  }
  const fr = renderHome('fr'), en = renderHome('en');
  assert.equal((fr.match(/<a /g) ?? []).length, (en.match(/<a /g) ?? []).length);
});

// V34 — recettes à butin par zone (Mathieu t345u, 2026-11-12): the three published
// sheets, slugs unchanged, official + « à confirmer » loot-by-zone, no third-party
// names in visible page text, v34 sheets still published; page count at least 249.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {classifySource, entryVerification} from '../lib/source-policy.mjs';
import {selectPublicEntries} from '../lib/public-catalog.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry} from '../lib/v2/render.mjs';
import {entryPath} from '../lib/articles.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
const IDS = Object.freeze({
  blueprints: 'forever-professions-blueprints',
  features: 'forever-camp-features',
  camping: 'forever-professions-camping',
});
const SLUGS = {
  [IDS.blueprints]: {fr: 'fr/metiers/recettes-et-plans-avances/', en: 'en/professions/recipes-and-advanced-blueprints/'},
  [IDS.features]: {fr: 'fr/metiers/campement-fonctionnalites/', en: 'en/professions/camping-features/'},
  [IDS.camping]: {fr: 'fr/metiers/artisanat-du-campement/', en: 'en/professions/campsite-crafting/'},
};
const VERSIONS = {[IDS.blueprints]: 24, [IDS.features]: 8, [IDS.camping]: 16}; // v38 (t361u): blueprints + liens v40 ; v36 (t351u): blueprints revised+republished
const by = id => records.find(e => e.id === id);

test('v34 — three sheets published by Mathieu (t345u), slugs and versions, history kept', () => {
  for (const id of Object.values(IDS)) {
    const e = by(id);
    assert.ok(e, id);
    assert.equal(e.status, 'published', id);
    assert.equal(e.version, VERSIONS[id], id);
    assert.equal(entryPath(e, 'fr'), SLUGS[id].fr, id);
    assert.equal(entryPath(e, 'en'), SLUGS[id].en, id);
    assert.equal(e.review.reviewer, 'Mathieu', id);
    assert.ok(e.history.some(h => h.actor === 'Mathieu' && /t345u/.test(h.note)), `${id}: t345u`);
    // earlier Mathieu approvals kept (not overwritten)
    assert.ok(e.history.some(h => h.actor === 'Mathieu' && !/t345u/.test(h.note || '')), `${id}: earlier Mathieu history kept`);
  }
  const published = records.filter(e => e.status === 'published');
  assert.ok(published.length >= 108, 'at least the v34 published set');
  assert.equal(published.filter(e => ['forever-professions-blueprints','forever-camp-features','forever-professions-camping'].includes(e.id)).length, 3);
});

test('v34 — blueprints: official rules plus « à confirmer » loot-by-zone (55) and vendors; no invented drop rates', () => {
  const e = by(IDS.blueprints);
  assert.equal(e.verification, 'données du jeu');
  // mixed official + client-extract (guides / vendor / item index)
  const kinds = e.sources.map(s => classifySource(s.url));
  assert.ok(kinds.some(k => k === 'officiel'));
  assert.ok(kinds.some(k => k !== 'officiel'));
  assert.ok(e.sources.length >= 10 && e.sources.length <= 20);
  const fr = JSON.stringify(e.article);
  assert.match(fr, /55/);
  assert.match(fr, /The Deadmines/);
  assert.match(fr, /Blackfathom Deeps/);
  assert.match(fr, /Zerril Softbreeze/);
  assert.match(fr, /Ruines de Lordaeron/);
  assert.doesNotMatch(fr, /Eternadex|Wowhead|wiki\.gg/i);
  // no drop-rate percentages invented
  assert.doesNotMatch(JSON.stringify(e.article.sections), /\d+(?:\.\d+)?\s*%/);
});

test('v34 — camping: official 140+ rule and the two named exceptions (Tanning Rack 125, Journeyman Campfire Kit Cooking 90)', () => {
  const e = by(IDS.camping);
  const blob = JSON.stringify(e.article);
  assert.match(blob, /Tanning Rack/);
  assert.match(blob, /125/);
  assert.match(blob, /Journeyman Campfire Kit/);
  assert.match(blob, /90/);
  assert.doesNotMatch(blob, /Eternadex|Wowhead|wiki\.gg/i);
  assert.ok(e.history.some(h => /t345u/.test(h.note)));
});

test('v34 — rendered FR/EN pages: no Eternadex/Wowhead/wiki.gg in visible text; noindex; à confirmer allowed; source hrefs may cite client extract', () => {
  const pub = selectPublicEntries(records);
  setCategoryNames(categories); setVisualLinks(pub); setV2Catalog(pub);
  for (const id of Object.values(IDS)) {
    for (const lang of ['fr', 'en']) {
      const html = renderEntry(pub.find(e => e.id === id), lang);
      const where = `${id}/${lang}`;
      assert.match(html, /<meta name="robots" content="noindex,nofollow">/, where);
      assert.equal((html.match(/<h1[\s>]/g) ?? []).length, 1, where);
      const text = html.replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '')
        .replace(/<[^>]+>/g, ' ');
      assert.doesNotMatch(text, /Eternadex|Wowhead|wiki\.gg/i, where);
      // hrefs: wiki.gg never; eternadex/wowhead allowed only as href (v33 accepted rule)
      assert.doesNotMatch(html, /wiki\.gg/i, where);
    }
  }
});

test('v34 — built dist-v2: 249+ html, no sitemap, slugs present, menu counts current', async () => {
  const dist = join(root, 'dist-v2');
  const list = async (dir, acc=[]) => {
    const entries = await readdir(dir, {withFileTypes: true});
    for (const e of entries) {
      const p = join(dir, e.name);
      if (e.isDirectory()) await list(p, acc);
      else acc.push(p);
    }
    return acc;
  };
  const files = await list(dist);
  assert.ok(!files.some(f => /sitemap/i.test(f)));
  const htmls = files.filter(f => f.endsWith('.html') && !f.endsWith('PROPOSITION-V2-LOCALE.txt'));
  // dist-v2 includes 249 wiki pages (same as v33)
  const rel = f => f.slice(dist.length + 1);
  const pages = htmls.filter(f => !rel(f).includes('PROPOSITION'));
  // count index.html page files at content paths — build said 249
  const {readdirSync, statSync, readFileSync} = await import('node:fs');
  const {join: j} = await import('node:path');
  function walk(d, a=[]) {
    for (const n of readdirSync(d)) {
      const p = j(d, n);
      if (statSync(p).isDirectory()) walk(p, a);
      else if (n.endsWith('.html')) a.push(p);
    }
    return a;
  }
  const all = walk(dist);
  assert.ok(all.length >= 249, 'v34 page count is a floor; v35 adds pages');
  const home = readFileSync(j(dist, 'fr/index.html'), 'utf8');
  for (const [lab, c] of [['Zones',54],['Créatures',14],['Quêtes et progression',23],['Objets',8],['Métiers',18],['Classes',11],['Donjons et raids',26]]  /* v39 (t391u) */) {
    assert.ok(home.includes(`<span class="wk-label">${lab}</span><span class="wk-count">${c}<`), lab);
  }
  for (const slugs of Object.values(SLUGS)) {
    assert.ok(all.some(f => f.endsWith('/' + slugs.fr + 'index.html') || f.endsWith('/' + slugs.fr.replace(/\/$/, '') + '/index.html')));
    assert.ok(all.some(f => f.includes('/' + slugs.en)));
  }
});

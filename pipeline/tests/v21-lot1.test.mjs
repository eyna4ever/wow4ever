// V2.1 étape 03 — lot 1 (isolated test tree): referential integrity, sources/status rules, idempotence, Android HTML
// and basic accessibility checks. Skips itself when lot 1 is not present (production dataset).
import {test, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditDataset, merge, validate} from '../lib/documentary.mjs';
import {selectPublicEntries} from '../lib/public-catalog.mjs';
import {classifySource, entryVerification} from '../lib/source-policy.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry, renderCategory} from '../lib/v2/render.mjs';
import {entryPath} from '../lib/articles.mjs';
import {LOT1_IDS, lot1Published} from './lot1-ids.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const batchPath = join(root, 'tests/fixtures/lot1.entries.json');   // v32: the imported lot-1 batch (patches/04-lot1.entries.json)
const present = lot1Published(records) === LOT1_IDS.length && existsSync(batchPath);
const skip = !present && 'lot 1 not published in this dataset';
const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
const lot = records.filter(e => LOT1_IDS.includes(e.id));
afterEach(() => setVisualLinks([]));

test('lot 1 — referential integrity: dataset audit clean, every relation and block source resolves', {skip}, () => {
  const audit = auditDataset(records);
  assert.deepEqual(audit.errors, []);
  const published = new Set(records.filter(e => e.status === 'published').map(e => e.id));
  for (const entry of lot) {
    assert.deepEqual(validate(entry), [], entry.id);
    for (const id of entry.relations) assert.ok(published.has(id), `${entry.id} → ${id} must be a published entry`);
    assert.ok(entry.relations.length >= 1, `${entry.id} is linked`);
  }
  const pub = selectPublicEntries(records);
  for (const id of LOT1_IDS) assert.ok(pub.some(e => e.id === id), `${id} public`);
  const slugs = pub.flatMap(e => ['fr', 'en'].map(l => e.url[l]));
  assert.equal(new Set(slugs).size, slugs.length, 'no URL collision');
});

test('lot 1 — sources and status: official Blizzard only, never third-party, approved by Mathieu (t338u/t339u)', {skip}, () => {
  for (const entry of lot) {
    assert.ok(entry.sources.length >= 1);
    for (const s of entry.sources) {
      assert.equal(classifySource(s.url), 'officiel', `${entry.id}: ${s.url}`);
      assert.doesNotMatch(s.url, /wiki\.gg|eternadex|wowhead|wago\.tools|wow\.tools/);
      assert.match(s.license, /Blizzard/);
      // camp-features was re-consulted on 2026-11-12 (v34, Mathieu t345u); other lot-1 sheets keep 2026-11-09.
      assert.equal(s.accessedAt, entry.id === 'forever-camp-features' ? '2026-11-12' : '2026-11-09');
    }
    assert.equal(entryVerification(entry), 'officiel confirmé');
    assert.equal(entry.verification, 'officiel confirmé');
    assert.ok(entry.article.pending.length >= 1, `${entry.id}: says what is not confirmed`);
    // v32: real approval by Mathieu (t338u validation + t339u « Oui », 2026-11-09), no test approval left.
    assert.equal(entry.review.reviewer, 'Mathieu', entry.id);
    assert.ok(entry.history.some(h => h.actor === 'Mathieu' && /t338u/.test(h.note) && /t339u/.test(h.note)), `${entry.id}: t338u + t339u recorded`);
    if (entry.id === 'forever-camp-features') {
      assert.ok(entry.history.some(h => h.actor === 'Mathieu' && /t345u/.test(h.note)), `${entry.id}: t345u recorded`);
    }
    assert.ok(!entry.history.some(h => /TEST-ISOLE/.test(h.actor)), `${entry.id}: no test-only approval`);
  }
});

test('lot 1 — counted facts match the official articles (65 challenges, 21 perks, 4 rewards, 11 camp items)', {skip}, () => {
  const by = id => lot.find(e => e.id === id);
  const rows = by('forever-legacy-challenges').article.sections[0].blocks[0].rows;
  assert.deepEqual(rows.map(r => Number(r[1].fr)), [27, 18, 12, 2, 3, 3]);
  assert.equal(rows.reduce((n, r) => n + Number(r[1].fr), 0), 65);
  const perks = by('forever-legacy-perks').article.sections.map(s => s.blocks[0].rows.length);
  assert.deepEqual(perks, [7, 7, 7]);
  assert.equal(by('forever-legacy-rewards').article.sections[0].blocks[0].rows.length, 4);
  assert.equal(by('forever-camp-features').article.sections[0].blocks[0].rows.length, 11);
  assert.equal(by('forever-questline-gelkis-magram').article.sections[0].blocks[0].items.length, 16);
});

test('lot 1 — idempotence: re-importing the batch inserts nothing (5 duplicates; camp-features v8 and legacy-rewards v8 conflict with the v1 fixture, existing kept)', {skip}, async () => {
  const batch = JSON.parse(await readFile(batchPath, 'utf8'));
  const {records: after, report} = merge(records, batch, {now: '2026-11-09T12:00:00Z'});
  assert.deepEqual(report.inserted, []);
  assert.deepEqual(report.invalid, []);
  assert.deepEqual(report.quarantined, []);
  assert.equal(report.duplicates.length, 5);
  assert.equal(report.conflicts.length, 2);
  const conflicts = Object.fromEntries(report.conflicts.map(c => [c.id, c]));
  assert.deepEqual(Object.keys(conflicts).sort(), ['forever-camp-features', 'forever-legacy-rewards']);
  assert.equal(conflicts['forever-camp-features'].existingVersion, 8);
  assert.equal(conflicts['forever-camp-features'].incomingVersion, 1);
  assert.equal(conflicts['forever-legacy-rewards'].existingVersion, 12);
  assert.equal(conflicts['forever-legacy-rewards'].incomingVersion, 1);
  assert.equal(JSON.stringify(after), JSON.stringify(records));
});

test('lot 1 — Android/accessibility: viewport, lang, noindex, one h1, no heading skip, captioned tables, no inline script/style', {skip}, async () => {
  const pub = selectPublicEntries(records);
  setCategoryNames(categories); setVisualLinks(pub); setV2Catalog(pub);
  const pages = [];
  for (const lang of ['fr', 'en']) {
    for (const id of LOT1_IDS) pages.push([id, lang, renderEntry(pub.find(e => e.id === id), lang)]);
    for (const cat of ['quests', 'professions']) pages.push([cat, lang, renderCategory(cat, lang)]);
  }
  for (const [id, lang, html] of pages) {
    const where = `${id}/${lang}`;
    assert.match(html, /<meta name="viewport" content="width=device-width,initial-scale=1">/, where);
    assert.match(html, new RegExp(`<html lang="${lang}"`), where);
    assert.match(html, /<meta name="robots" content="noindex,nofollow">/, where);
    assert.match(html, /<title>[^<]{10,}<\/title>/, where);
    assert.equal((html.match(/<h1[\s>]/g) ?? []).length, 1, `${where}: one h1`);
    const levels = [...html.matchAll(/<h([1-6])[\s>]/g)].map(m => Number(m[1]));
    for (let i = 1; i < levels.length; i++) assert.ok(levels[i] <= levels[i - 1] + 1, `${where}: heading skip h${levels[i - 1]}→h${levels[i]}`);
    assert.doesNotMatch(html, /<script(?![^>]*\bsrc=)[^>]*>/, `${where}: inline script`);
    assert.doesNotMatch(html, /\sstyle=|<style/, `${where}: inline style`);
    for (const table of html.match(/<table>[\s\S]*?<\/table>/g) ?? []) {
      assert.match(table, /<caption>/, where); assert.match(table, /<th scope="col">/, where);
    }
    // Android: every table sits in a focusable horizontal-scroll region
    assert.equal((html.match(/<table>/g) ?? []).length, (html.match(/<div class="table-wrap" role="region" aria-label="[^"]+" tabindex="0"><table>/g) ?? []).length, where);
    assert.ok(!html.includes('status-pill is-draft">À confirmer<') && !html.includes('status-pill is-draft">Unconfirmed'), `${where}: official lot shows no unconfirmed pill`);
  }
  // the built tree carries no sitemap (owner decision: noindex, no sitemap)
  const top = await readdir(join(root, 'dist-v2')).catch(() => []);
  assert.ok(!top.some(name => /sitemap/i.test(name)));
});

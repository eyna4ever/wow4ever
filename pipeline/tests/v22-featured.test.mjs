// v22 (t297u) — « À la une » is automatic: computed at build time from published entries (news first, freshest first).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {featuredEntries, FEATURED_COUNT} from '../lib/v2/render.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const art = (id, category, updatedAt, extra = {}) => ({id, category, subcategory: 'x', status: 'published', updatedAt, title: {fr: id, en: id}, article: {format: 2}, ...extra});

test('v22 featured: current data shows the three freshest published news articles (FR and EN)', () => {
  for (const lang of ['fr', 'en']) assert.deepEqual(featuredEntries(records, lang).map(e => e.id), ['forever-news-hotfixes-nov5-6', 'forever-news-class-tuning-nov10', 'forever-news-story-unbowed'] /* v38 (t361u): same update day 2026-11-14; Unbowed is now a format-2 article */);
});

test('v22 featured: rule — articles only, published only, news first, newest first, fallback to other articles', () => {
  const news = n => art(`news-${n}`, 'news', `2026-11-0${n}T10:00:00Z`);
  const guide = art('guide-new', 'guides', '2026-11-09T10:00:00Z');
  assert.equal(FEATURED_COUNT, 3);
  assert.deepEqual(featuredEntries([news(1), news(2), news(3), news(4), guide]).map(e => e.id), ['news-4', 'news-3', 'news-2']);
  assert.deepEqual(featuredEntries([news(1), guide, art('g2', 'guides', '2026-11-05T00:00:00Z')]).map(e => e.id), ['news-1', 'guide-new', 'g2']);
  assert.deepEqual(featuredEntries([{...news(5), status: 'draft'}, {...news(6), article: undefined}, news(1)]).map(e => e.id), ['news-1']);
  // a new publication via review.mjs (fresh updatedAt) takes the top spot automatically
  assert.equal(featuredEntries([...records, art('brand-new', 'news', '2099-01-01T00:00:00Z')])[0].id, 'brand-new');
  // same day: the most recent event date wins
  assert.deepEqual(featuredEntries([art('a', 'news', '2026-11-04T13:00:00Z', {eventDate: '2026-11-02'}), art('b', 'news', '2026-11-04T12:00:00Z', {eventDate: '2026-11-05'})]).map(e => e.id), ['b', 'a']);
});

test('v22 featured: the built home pages render those cards in the centered featured block', async () => {
  for (const [lang, path] of [['fr', 'fr/index.html'], ['en', 'en/index.html']]) {
    const html = await readFile(join(root, '../site/wiki', path), 'utf8');
    const block = html.slice(html.indexOf('<section class="v2-featured"'), html.indexOf('</section>', html.indexOf('<section class="v2-featured"')));
    for (const e of featuredEntries(records, lang)) assert.ok(block.includes(entryPathOf(e, lang)), `${lang} ${e.id}`);
  }
});
import {entryPath as entryPathOf} from '../lib/articles.mjs';

import {readNext, READ_NEXT, newestFirst} from '../lib/v2/render.mjs';
test('v22 dynamic: « À lire aussi » is automatic (shared tags, then same category), never itself, max 3', () => {
  const tag = (fr) => ({fr, en: fr});
  const me = art('me', 'guides', '2026-11-01T00:00:00Z', {tags: [tag('Manette'), tag('Débutant')]});
  const both = art('both', 'news', '2026-10-01T00:00:00Z', {tags: [tag('Manette'), tag('Débutant')]});
  const one = art('one', 'news', '2026-11-03T00:00:00Z', {tags: [tag('Débutant')]});
  const cat1 = art('cat1', 'guides', '2026-11-02T00:00:00Z'), cat2 = art('cat2', 'guides', '2026-11-05T00:00:00Z');
  const none = art('none', 'news', '2026-11-09T00:00:00Z');
  assert.equal(READ_NEXT, 3);
  assert.deepEqual(readNext(me, [me, none, cat1, cat2, one, both]).map(e => e.id), ['both', 'one', 'cat2']);
  for (const e of records.filter(e => e.status === 'published')) { const r = readNext(e, records); assert.ok(r.length <= 3 && !r.some(x => x.id === e.id || x.status !== 'published'), e.id); }
});
test('v22 dynamic: category pages list entries newest-updated first; home shows « Dernières mises à jour » with dates', async () => {
  const html = await readFile(join(root, '../site/wiki/fr/index.html'), 'utf8');
  assert.match(html, /Dernières mises à jour/); assert.match(html, /Mis à jour le/);
  const en = await readFile(join(root, '../site/wiki/en/index.html'), 'utf8'); assert.match(en, /Latest updates/);
  const news = records.filter(e => e.status === 'published' && e.category === 'news' && e.article).sort(newestFirst('fr'));
  const page = await readFile(join(root, '../site/wiki/fr/actualites/index.html'), 'utf8');
  const pos = news.map(e => page.indexOf(entryPathOf(e, 'fr').split('/').at(-2) + '/')).filter(i => i >= 0);
  assert.ok(pos.length >= 3); assert.deepEqual(pos, [...pos].sort((a, b) => a - b));
});

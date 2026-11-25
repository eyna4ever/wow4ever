// v18 (guides-v18) — the 9 beginner guides completed: revision drafts in ops/v18/guides, same IDs and URLs as v17,
// official Blizzard sources only, every fact cited, no navigation line left in « Reste à confirmer », beginner path block.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks, discussionBlock} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry} from '../lib/v2/render.mjs';
import {sourcedBlocks} from '../lib/articles.mjs';
import {draftToEntry} from '../lib/v16/draft.mjs';
import {validate} from '../lib/documentary.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
const published = (await siteEntries()).filter(e => e.status === 'published');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const load = async dir => Promise.all((await readdir(dir)).filter(f => f.endsWith('.md')).sort().map(async file => ({file, ...draftToEntry(await readFile(join(dir, file), 'utf8'), {file})})));

test('v18 guides débutant: 9 revision drafts, same IDs/URLs as v17, official sources, every fact cited, no stub navigation', async () => {
  const v18 = await load(join(root, '../ops/v18/guides')), v17 = await load(join(root, '../ops/v17/guides'));
  assert.equal(v18.length, 9);
  assert.deepEqual(v18.map(d => d.entry.id).sort(), v17.map(d => d.entry.id).sort());
  for (const {file, entry, errors} of v18) {
    assert.deepEqual(errors, [], file); assert.deepEqual(validate(entry), [], file);
    assert.equal(entry.status, 'draft'); assert.equal(entry.review, undefined);
    const old = v17.find(d => d.entry.id === entry.id).entry;
    assert.deepEqual(entry.article.slug, old.article.slug, `${file}: URLs unchanged`);
    for (const source of entry.sources) {
      assert.ok(['news.blizzard.com', 'worldofwarcraft.blizzard.com', 'us.forums.blizzard.com'].includes(new URL(source.url).hostname), source.url);
      assert.ok(['2026-11-01', '2026-11-03'].includes(source.accessedAt), source.url);
    }
    for (const {where, block} of sourcedBlocks(entry.article)) if (!where.startsWith('pending')) assert.ok(block.src?.length, `${file} ${where}`);
    for (const item of entry.article.pending) assert.doesNotMatch(`${item.fr} ${item.en}`, /La suite|Next:|guide \d\/6/, `${file}: navigation line in pending`);
    // a revised record must be exactly the v18 draft (plus the human review); otherwise it is still the v17 text
    const pub = published.find(e => e.id === entry.id), rec = records.find(e => e.id === entry.id);
    const lastRevise = [...(rec?.history ?? [])].reverse().find(h => /^revise: /.test(h.note ?? ''));
    if (/^revise: v18/.test(lastRevise?.note ?? '')) {  // v19 revisions are checked in v19-numbering.test.mjs
      assert.equal(rec.status, 'published'); assert.equal(rec.review?.reviewer, 'Mathieu'); assert.equal(rec.review?.approved, true);
      assert.deepEqual(pub.article, entry.article); assert.deepEqual(pub.sources, entry.sources); assert.deepEqual(pub.title, entry.title);
    }
  }
});

test('v18 rendering: beginner path block with next step and cited wiki pages; guide wording in Discussion', () => {
  setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published);
  const g3 = published.find(e => e.id === 'guide-debutant-premier-personnage');
  const html = renderEntry(g3, 'fr');
  assert.match(html, /<section class="article-section v18-path" id="parcours"/);
  assert.match(html, /<li aria-current="page"><strong>/);
  assert.equal((html.match(/<section class="article-section v18-path"[\s\S]*?<\/section>/)[0].match(/<a /g) ?? []).length, 8 + 1 + g3.relations.filter(id => !id.startsWith('guide-debutant-')).length);
  assert.match(html, /Étape suivante : Guide débutant \(4\/6\)/);
  assert.match(renderEntry(published.find(e => e.id === 'guide-debutant-jouer-a-plusieurs'), 'en'), /end of the beginner path/);
  assert.doesNotMatch(renderEntry(published.find(e => e.id === 'article-forever-rulesets'), 'fr'), /v18-path/);
  assert.match(discussionBlock('fr', 'guides'), /sur ce guide/); assert.match(discussionBlock('fr', 'news'), /cette actualité/);
  setVisualLinks([]);
});

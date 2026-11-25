import test from 'node:test';
import assert from 'node:assert/strict';
import {readdir, readFile} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {CATEGORY_SLUGS, ILLUSTRATIONS} from '../lib/articles.mjs';
import {validate} from '../lib/documentary.mjs';
import {selectPublicEntries, selectPreviewEntries} from '../lib/public-catalog.mjs';
import {lot1Published} from './lot1-ids.mjs';
import {isLot2, isLot2New, lot2NewPublished} from './lot2-ids.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

test('authored elite articles cover every category and validate as drafts-shaped content', async () => {
  const dir = join(root, 'content/articles');
  const files = (await readdir(dir)).filter(name => name.endsWith('.mjs'));
  assert.ok(files.length >= 12);
  const entries = [];
  const sourcesCatalog = JSON.parse(await readFile(join(root, 'content/sources-2026-10-24.json'), 'utf8'));
  for (const name of files) {
    const mod = await import(pathToFileURL(join(dir, name)).href);
    for (const raw of mod.default) {
      const keys = new Set();
      const add = src => { for (const k of src ?? []) keys.add(k); };
      add(raw.lead?.src);
      for (const p of raw.keyPoints ?? []) add(p.src);
      for (const s of raw.sections ?? []) for (const b of s.blocks ?? []) {
        if (b.type === 'list') for (const i of b.items ?? []) add(i.src);
        else add(b.src);
      }
      for (const p of raw.confirmed ?? []) add(p.src);
      for (const p of raw.notes ?? []) add(p.src);
      for (const p of raw.dates ?? []) add(p.src);
      const sources = [];
      for (const key of keys) {
        for (const [full, meta] of Object.entries(sourcesCatalog)) {
          if (full === key || full.startsWith(`${key}-`)) {
            sources.push({key: full, url: meta.url, title: meta.title, language: meta.language, publishedAt: meta.publishedAt, accessedAt: meta.accessedAt, license: 'x', gameVersion: 'World of Warcraft: Forever — annonces et bêta, état documentaire 2026-10-27'});
          }
        }
      }
      const entry = {
        id: raw.id, title: raw.title, description: raw.description, category: raw.category,
        subcategory: raw.subcategory ?? 'article', sources, status: 'draft', updatedAt: new Date().toISOString(),
        version: 1, gameVersion: 'World of Warcraft: Forever — annonces et bêta, état documentaire 2026-10-27',
        relations: (raw.relations ?? []).filter(id => !String(id).startsWith('article-')),
        history: [{at: new Date().toISOString(), actor: 'test', note: 'unit', version: 1}],
        article: {format: 1, slug: raw.slug, illustration: raw.illustration, lead: raw.lead, keyPoints: raw.keyPoints, sections: raw.sections, confirmed: raw.confirmed, pending: raw.pending, ...(raw.notes ? {notes: raw.notes} : {}), ...(raw.dates ? {dates: raw.dates} : {})}
      };
      assert.equal(validate(entry).length, 0, `${raw.id}: ${validate(entry).join('; ')}`);
      assert.ok(ILLUSTRATIONS.includes(raw.illustration));
      assert.ok(CATEGORY_SLUGS[raw.category]);
      entries.push(entry);
    }
  }
  const cats = new Set(entries.map(e => e.category));
  for (const cat of Object.keys(CATEGORY_SLUGS)) assert.ok(cats.has(cat), `missing category ${cat}`);
  assert.ok(entries.length >= 12);
});

test('public catalog exposes published elite articles and still hides AC2/CL3 drafts', async () => {
  const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
  const pub = selectPublicEntries(records);
  const prev = selectPreviewEntries(records);
  assert.equal(pub.every(e => e.status === 'published'), true);
  // 49 published on 2026-10-28 + 6 news approved by Mathieu on 2026-10-30.
  // 49 published on 2026-10-28 + 6 news approved by Mathieu on 2026-10-30 + 26 v10 entries approved on 2026-10-30 (22:30).
  // v15: duplicates merged on Mathieu's decision (data/merges.json) leave the catalogue once withdrawn via review.mjs reject.
  const merges = JSON.parse(await readFile(join(root, 'data/merges.json'), 'utf8'));
  const applied = new Set(merges.map(m => m.retired).filter(id => records.find(e => e.id === id)?.status !== 'published'));
  // v17: + the 9 beginner guides published via review.mjs on Mathieu's « Oui » (t255u, 2026-11-01 17:16 Europe/Paris).
  const v17 = records.filter(e => e.id.startsWith('guide-debutant-') && e.status === 'published' && e.review?.reviewer === 'Mathieu').length;
  assert.ok(v17 === 0 || v17 === 9, `v17 guides: ${v17}`);
  assert.equal(pub.length, 81 - applied.size + v17 + 9 + lot1Published(records) + lot2NewPublished(records) + 26 + 48 + 26); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ; // v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; // v33 (t341u): + lot 2 // V2.1 étape 03: + lot 1 ; // v31: + équilibrage + correctifs ; v30: +2 news ; v23: + tradition ; v22: + CL3, launch notes, gamepad (golive-nov4 republished)
  for (const id of ['forever-news-golive-nov4', 'forever-news-return-guide', 'forever-news-starter-guide', 'forever-news-podcast-tech', 'forever-news-story-unbowed', 'forever-news-portal-room']) {
    if (applied.has(id)) { assert.ok(records.find(e => e.id === id).history.some(h => h.note.startsWith('reject:')), `${id} withdrawn without review.mjs reject`); continue; }
    assert.ok(pub.some(e => e.id === id && e.status === 'published'), `missing published ${id}`);
  }
  assert.equal(pub.filter(e => e.id.startsWith('article-')).length, 18); // v23: + article 03 ; v22: + notes de lancement // + AR16 races et classes (v10)
  assert.equal(pub.some(e => e.id === 'forever-news-beta'), false);
  assert.ok(pub.some(e => e.id === 'forever-class-priest')); // v22: CL3 published (Oui de Mathieu), AC2 still a draft
  assert.ok(pub.every(e => e.id.startsWith('article-') ? e.article : true));
  assert.ok(prev.some(e => e.id === 'forever-news-beta' && e.status === 'draft'));
  assert.ok(prev.some(e => e.article && e.status === 'published'));
});

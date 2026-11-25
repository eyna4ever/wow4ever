// v19 (guides-v19) — numbering fix requested by Mathieu (t261u): only the 6 real beginner guides carry « n/6 »; the 3 race
// history annexes are unnumbered sub-items of step 3; « Étape suivante » from step 3 and from each annex goes to guide 4.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry, renderHome, renderCategory, renderIndex} from '../lib/v2/render.mjs';
import {draftToEntry} from '../lib/v16/draft.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
const published = (await siteEntries()).filter(e => e.status === 'published');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const MAIN = ['guide-debutant-avant-de-jouer', 'guide-debutant-premiere-connexion', 'guide-debutant-premier-personnage', 'guide-debutant-premiers-pas', 'guide-debutant-equipement-metiers', 'guide-debutant-jouer-a-plusieurs'];
const ANNEX = ['guide-debutant-histoire-alliance', 'guide-debutant-histoire-horde', 'guide-debutant-histoire-eolides'];
const byId = id => published.find(e => e.id === id);

test('v19 titles: guides 1/6–6/6 numbered once each, annexes unnumbered; v19 drafts = published annexes, content unchanged', async () => {
  for (const lang of ['fr', 'en']) {
    MAIN.forEach((id, i) => assert.match(byId(id).title[lang], new RegExp(`\\(${i + 1}/6\\)`), id));
    for (const id of ANNEX) assert.doesNotMatch(byId(id).title[lang], /\d\/6/, id);
    const numbered = published.filter(e => /\d\/6/.test(e.title[lang])).map(e => e.id);
    assert.deepEqual(numbered.sort(), [...MAIN].sort());
  }
  const dir = join(root, '../ops/v19/guides');
  for (const file of (await readdir(dir)).filter(f => f.endsWith('.md'))) {
    const {entry, errors} = draftToEntry(await readFile(join(dir, file), 'utf8'), {file});
    assert.deepEqual(errors, [], file);
    const pub = byId(entry.id), rec = records.find(e => e.id === entry.id);
    if (['guide-debutant-premiers-pas', 'guide-debutant-equipement-metiers'].includes(entry.id)) { assert.ok(rec.history.some(h => /^revise: .*v22/.test(h.note ?? '')), entry.id); continue; } // v22: dated update (notes du 2 novembre)
    assert.deepEqual(pub.title, entry.title, file); assert.deepEqual(pub.article, entry.article, file); assert.deepEqual(pub.sources, entry.sources, file);
    if (ANNEX.includes(entry.id)) assert.ok(rec.history.some(h => /^revise: v19/.test(h.note ?? '')) && rec.history.some(h => /t261u/.test(h.note ?? '') && /t260u/.test(h.note ?? '')), entry.id);
  }
});

test('v19 rendering: each step number appears once per path block, wherever the reader is; next step is guide 4 from step 3 and annexes', () => {
  setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published);
  for (const lang of ['fr', 'en']) {
    for (const id of [...MAIN, ...ANNEX]) {
      const html = renderEntry(byId(id), lang);
      const block = html.match(/<section class="article-section v18-path"[\s\S]*?<\/section>/)[0];
      for (let n = 1; n <= 6; n += 1) assert.equal((block.match(new RegExp(`\\(${n}/6\\)`, 'g')) ?? []).length - (block.includes('Étape suivante') || block.includes('Next step') ? (NEXTN(id) === n ? 1 : 0) : 0), 1, `${id} ${lang} step ${n}`);
      assert.match(block, lang === 'fr' ? /Pour aller plus loin : histoire des races/ : /Going further: race history/);
      if (id === 'guide-debutant-premier-personnage' || ANNEX.includes(id)) assert.match(block, /(Étape suivante|Next step) : (Guide débutant|Beginner guide) \(4\/6\)/);
    }
    for (const html of [renderHome(lang), renderCategory('guides', lang), renderIndex(lang)]) {
      for (const m of html.matchAll(/(?:Guide débutant|Beginner guide) \((\d)\/6\)[^<]*/g)) assert.match(m[0], new RegExp(MAIN[m[1] - 1] ? '' : 'x'));
      for (const id of ANNEX) assert.ok(!html.includes(`${byId(id).title[lang].replace(/^(Guide débutant|Beginner guide)/, '$1 (3/6)')}`));
    }
  }
  setVisualLinks([]);
});
const NEXTN = id => ({'guide-debutant-avant-de-jouer': 2, 'guide-debutant-premiere-connexion': 3, 'guide-debutant-premier-personnage': 4, 'guide-debutant-premiers-pas': 5, 'guide-debutant-equipement-metiers': 6}[id] ?? (ANNEX.includes(id) ? 4 : 0));

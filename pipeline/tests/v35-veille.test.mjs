import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {test} from 'node:test';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const wiki = join(root, '../site/wiki');

test('v35–v38 — 183 published (t361u zones + v38 policy), Mathieu t347u on the three veille sheets, slugs unchanged, new faction pages', async () => {
  const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
  const published = records.filter(e => e.status === 'published');
  assert.equal(published.length, 209); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ;
  assert.equal(records.length, 211); // t388u : +26 brouillons (rubriques complétées, non publiés) ; v38 (t361u): +48 fiches de zones ; v37 published (t355u): +10 bestiary +1 poissons; 2 leftover news drafts remain

  const ids = {
    'forever-news-hotfixes-nov5-6': {ver: 20,  /* v39 (t391u) : révision t388u (correctif du 14/11) + submit/approve/publish */ fr: 'correctifs-forever-5-et-6-novembre', en: 'forever-hotfixes-november-5-6'},
    'forever-news-class-tuning-nov10': {ver: 12, fr: 'equilibrage-classes-10-novembre', en: 'class-tuning-november-10'},
    'forever-news-pvp-faction-balance': {ver: 4, fr: 'equilibre-des-factions-jcj', en: 'pvp-faction-balance'},
  };
  for (const [id, exp] of Object.entries(ids)) {
    const e = records.find(x => x.id === id);
    assert.ok(e, id);
    assert.equal(e.status, 'published');
    assert.equal(e.version, exp.ver, id);
    assert.equal(e.review?.reviewer, 'Mathieu');
    assert.ok(e.history.some(h => (h.note || '').includes('t347u')), `${id} t347u`);
    assert.equal(e.article?.slug?.fr, exp.fr);
    assert.equal(e.article?.slug?.en, exp.en);
  }

  // AH postponed to 17 Nov is on the hotfix page (official Kaivax), not presented as live.
  const hf = records.find(e => e.id === 'forever-news-hotfixes-nov5-6');
  const text = JSON.stringify(hf.article);
  assert.match(text, /17/);
  assert.match(text, /Auction House|hôtel des ventes|hotel des ventes|Hôtel des ventes/i);
  assert.doesNotMatch(hf.article.lead.fr, /1 cuivre.*en vigueur|dépôt.*1 cuivre.*appliqu/i);

  // 251+ built pages (v36 adds 30 article pages)
  const pages = [];
  async function walk(d) {
    for (const name of await readdir(d, {withFileTypes: true})) {
      const p = join(d, name.name);
      if (name.isDirectory()) await walk(p);
      else if (name.name === 'index.html' || name.name.endsWith('.html')) pages.push(p);
    }
  }
  const dist = join(root, 'dist-v2');
  await walk(dist);
  const html = pages.filter(p => p.endsWith('.html') && !p.includes('PROPOSITION'));
  // build-v2: 251 in v35, more after v36 lists
  assert.equal(html.filter(p => /\/(fr|en)\//.test(p) || p.endsWith('/index.html')).length >= 251, true);
  for (const rel of [
    'fr/actualites/equilibre-des-factions-jcj/index.html',
    'en/news/pvp-faction-balance/index.html',
    'fr/actualites/correctifs-forever-5-et-6-novembre/index.html',
    'en/news/forever-hotfixes-november-5-6/index.html',
    'fr/actualites/equilibrage-classes-10-novembre/index.html',
    'en/news/class-tuning-november-10/index.html',
  ]) {
    await readFile(join(wiki, rel), 'utf8');
  }
});

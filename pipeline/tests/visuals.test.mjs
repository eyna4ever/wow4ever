import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, stat} from 'node:fs/promises';
import {ARTICLE_VISUALS, visualFor} from '../lib/visuals.mjs';
import {entryPicture, renderFeatured, setCategoryNames, ART_LABEL} from '../lib/pages.mjs';

const root = new URL('../', import.meta.url);
const provenance = JSON.parse(await readFile(new URL('design/illustrations-src/provenance.json', root), 'utf8'));

test('every elite article (AR01–AR15) has an original illustration with exports, FR/EN alt text and provenance', async () => {
  const visuals = Object.values(ARTICLE_VISUALS);
  assert.equal(visuals.length, 15);
  assert.deepEqual(visuals.map(v => v.code).sort(), Array.from({length: 15}, (_, i) => `AR${String(i + 1).padStart(2, '0')}`));
  for (const v of visuals) {
    assert.ok(v.alt.fr.length > 20 && v.alt.en.length > 20, `${v.code} alt`);
    assert.match(v.prompt, /No text|No legible text/, `${v.code} prompt forbids text`);
    for (const name of [`${v.file}-640.webp`, `${v.file}-1280.webp`, `${v.file}-1280.jpg`]) {
      const info = await stat(new URL(`public/wiki/assets/art-${name}`, root));
      assert.ok(info.size > 5000 && info.size < 400000, `${name} size ${info.size}`);
    }
    const record = provenance[`article:${v.code}`];
    assert.ok(record, `${v.code} provenance`);
    assert.equal(record.entryId, v.id);
    assert.equal(record.prompt, v.prompt);
    assert.match(record.method, /GenerateImage/);
    assert.equal(record.date, '2026-10-28');
  }
});

test('article picture declares dimensions, webp sources, jpg fallback and lazy loading below the fold', () => {
  const entry = {id: 'article-forever-calendar', category: 'news'};
  const lazy = entryPicture(entry, '../', 'fr');
  assert.match(lazy, /<source type="image\/webp" srcset="[^"]*-640\.webp 640w, [^"]*-1280\.webp 1280w"/);
  assert.match(lazy, /src="[^"]*-1280\.jpg" width="1280" height="720"/);
  assert.match(lazy, /loading="lazy"/);
  assert.doesNotMatch(entryPicture(entry, '../', 'en', {eager: true}), /loading="lazy"/);
  assert.match(entryPicture({id: 'forever-class-mage', category: 'classes'}, '../', 'fr'), /art-classes-1024\.webp" .*width="1024" height="576"/);
  assert.equal(visualFor({id: 'forever-news-beta'}), null);
});

test('home « À la une » lists published articles only, never drafts', () => {
  setCategoryNames([['news', 'Actualités', 'News'], ['guides', 'Guides', 'Guides']]);
  const base = {category: 'news', updatedAt: '2026-10-27', description: {fr: 'd', en: 'd'}, article: {}};
  const html = renderFeatured({lang: 'fr', prefix: '../', entries: [
    {...base, id: 'article-forever-calendar', status: 'published', slug: {fr: 'calendrier', en: 'schedule'}, title: {fr: 'Calendrier', en: 'Schedule'}},
    {...base, id: 'article-forever-draft', status: 'draft', slug: {fr: 'brouillon', en: 'draft'}, title: {fr: 'Brouillon secret', en: 'Secret draft'}}
  ]});
  assert.match(html, /Calendrier/);
  assert.doesNotMatch(html, /Brouillon secret|article-forever-draft/);
  assert.match(html, /ne constituent pas une source/);
  assert.ok(ART_LABEL.fr.includes('ne constitue pas une source'));
});

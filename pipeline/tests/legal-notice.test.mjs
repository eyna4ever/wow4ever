import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {siteMarkup, withSiteHeader} from '../lib/site.mjs';
import {inspectTemplate} from '../scripts/check-release.mjs';

const FR = 'Site indépendant et non officiel de Blizzard Entertainment.';
const EN = 'Independent, unofficial site, not affiliated with Blizzard Entertainment.';

test('the unofficial-site notice is visible in the French and English markup', async () => {
  const payload = {categories: JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories, entries: []};
  const fr = await siteMarkup({payload, lang: 'fr'});
  const en = await siteMarkup({payload, lang: 'en'});
  assert.ok(fr.includes(`>${FR}`), 'French footer text must contain the notice');
  assert.ok(en.includes(`>${EN}`), 'English footer text must contain the notice');
  assert.ok(fr.includes(`data-en="${EN}`), 'notice must stay translatable');
});

test('release inspection rejects a template without the unofficial-site notice', async () => {
  // L1: the home template receives the shared WoWki4ever header at build time; inspect it as built.
  const template = withSiteHeader(await readFile(new URL('../public/wiki/template.html', import.meta.url), 'utf8'));
  assert.doesNotThrow(() => inspectTemplate(template));
  const stripped = template.replaceAll(FR, '').replaceAll(EN, '');
  assert.throws(() => inspectTemplate(stripped), /unofficial-site notice/);
});

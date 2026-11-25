import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, mkdtemp, mkdir, writeFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {inspectTemplate, inspectStandalone, inspectArchive} from '../scripts/check-release.mjs';
import {sitePayload, siteMarkup, scriptJSON, withSiteHeader} from '../lib/site.mjs';
import {transitionRecord} from '../lib/documentary.mjs';

// L1: the home template receives the shared WoWki4ever header at build time; inspect it as built.
const template = withSiteHeader(await readFile(new URL('../public/wiki/template.html', import.meta.url), 'utf8'));

test('integrated template has unique IDs, twelve categories and linked accessible controls', () => {
  const report = inspectTemplate(template);
  assert.equal(report.categories, 12);
  assert.ok(report.ids > 10);
});

test('template integrity rejects broken anchors, ambiguous IDs and unnamed search', () => {
  assert.throws(() => inspectTemplate(template + '<div id="search-input"></div>'), /duplicate/);
  assert.throws(() => inspectTemplate(template + '<a href="#missing-section">Test</a>'), /broken fragment/);
  assert.throws(() => inspectTemplate(template.replace('for="search-input"', 'for="missing-input"')), /search label/);
});

test('standalone asset inspection scopes CSS URLs without confusing JavaScript helper names', async () => {
  const catalog = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8'));
  const html = '<!doctype html><html lang="fr"><head><meta name="viewport" content="width=device-width"><style>body{background:url("data:image/png;base64,AA==")}</style></head><body>' + template
    + '<script id="wiki-data" type="application/json">' + JSON.stringify({categories: catalog.categories, entries: []}) + '</script>'
    + '<script>const source={url:"test"};function safeSourceURL(value){return value;}safeSourceURL(source?.url);</script></body></html>';
  assert.equal(inspectStandalone(html, []).entries, 0);
  assert.throws(() => inspectStandalone(html.replace('data:image/png;base64,AA==', './missing.png'), []), /non-embedded CSS asset/);
});

test('archive inspector rejects non-ZIP and truncated artifacts', () => {
  assert.throws(() => inspectArchive(Buffer.from('not a ZIP'), ''), /ZIP end directory/);
  assert.throws(() => inspectArchive(Buffer.alloc(0), ''), /ZIP end directory/);
});

// Empty stored files have a standard CRC32 of zero; no external ZIP tool is needed.
function emptyArchive(names, {symbolicLink = false, checksum = 0} = {}) {
  const localParts = [], centralParts = [];
  let offset = 0;
  for (const name of names) {
    const filename = Buffer.from(name);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(filename.length, 26);
    localParts.push(local, filename);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50);
    central.writeUInt16LE(20, 6);
    central.writeUInt32LE(checksum, 16);
    central.writeUInt16LE(filename.length, 28);
    if (symbolicLink) central.writeUInt32LE(0xa1ff0000, 38);
    central.writeUInt32LE(offset, 42);
    centralParts.push(central, filename);
    offset += local.length + filename.length;
  }
  const central = Buffer.concat(centralParts);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50);
  end.writeUInt16LE(names.length, 8);
  end.writeUInt16LE(names.length, 10);
  end.writeUInt32LE(central.length, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...localParts, central, end]);
}

const deliveryFiles = ['wow-forever-integre.html', 'site/index.html', 'sources/README.md'];

test('archive inspector accepts a portable delivery and verifies content checksums', () => {
  assert.equal(inspectArchive(emptyArchive(deliveryFiles), '').entries, 3);
  assert.throws(() => inspectArchive(emptyArchive(deliveryFiles, {checksum: 1}), ''), /checksum mismatch/);
});

test('archive inspector rejects paths that escape extraction or expose private trees', () => {
  for (const name of ['../escape', '/absolute', 'C:/absolute', 'sources/..\\escape', 'sources/.env', 'sources/runtime/entries.json', 'sources/.git/config', 'sources/node_modules/pkg/index.js', 'sources/key.pem']) {
    assert.throws(() => inspectArchive(emptyArchive([...deliveryFiles, name]), ''), /unsafe ZIP path|private or generated tree/);
  }
});

test('archive inspector rejects symbolic links and duplicate archive paths', () => {
  assert.throws(() => inspectArchive(emptyArchive(deliveryFiles, {symbolicLink: true}), ''), /symbolic link/);
  assert.throws(() => inspectArchive(emptyArchive([...deliveryFiles, deliveryFiles[0]]), ''), /duplicate ZIP path/);
});

test('embedded catalog JSON round-trips literal markup without closing its script', () => {
  const input = {text: '</script><script>alert("test")</script>&', line: 'Test\u2028Test\u2029Test'};
  const output = scriptJSON(input);
  assert.doesNotMatch(output, /[<>&\u2028\u2029]/);
  assert.deepEqual(JSON.parse(output), input);
});

test('shared site renderer emits only strict public DTOs and escapes literal content', async () => {
  const root = await mkdtemp(join(tmpdir(), 'wow-release-test-'));
  try {
    await mkdir(join(root, 'data'));
    await mkdir(join(root, 'public/wiki'), {recursive: true});
    await writeFile(join(root, 'public/wiki/catalog.json'), JSON.stringify({categories: []}));
    await writeFile(join(root, 'public/wiki/template.html'), '<main>Test template</main>');
    const now = '2026-10-18T00:00:00.000Z';
    const options = {actor: 'PRIVATE-ACTOR', note: 'Synthetic test review', now, humanReview: true, identity: true, rights: true, translations: true};
    const draft = {id: 'test-release-private', title: {fr: 'PRIVATE-DRAFT', en: 'PRIVATE-DRAFT'}, description: {fr: 'Test', en: 'Test'}, category: 'guides', subcategory: 'test', status: 'draft', gameVersion: 'test', version: 1, updatedAt: now, sources: [{url: 'https://example.org/test', accessedAt: now, license: 'Test-only'}], relations: [], history: [{at: now, actor: 'PRIVATE-ACTOR', note: 'Test fixture'}]};
    let records = [{...draft, id: 'test-release-public', title: {fr: 'Test </script>', en: 'Test </script>'}}];
    records = transitionRecord(records, records[0].id, 'submit', options).records;
    records = transitionRecord(records, records[0].id, 'approve', options).records;
    records = transitionRecord(records, records[0].id, 'publish', {...options, publish: true}).records;
    await writeFile(join(root, 'data/entries.json'), JSON.stringify([...records, draft]));
    const payload = await sitePayload({projectRoot: root});
    assert.equal(payload.entries.length, 1);
    assert.equal(payload.entries[0].publicationValidated, true);
    const markup = await siteMarkup({projectRoot: root});
    assert.doesNotMatch(markup, /PRIVATE-|Test <\/script>/);
    assert.match(markup, /\\u003c\/script\\u003e/);
    // A present runtime catalog takes precedence over seed data.
    await mkdir(join(root, 'runtime'));
    await writeFile(join(root, 'runtime/entries.json'), '[]');
    assert.deepEqual((await sitePayload({projectRoot: root})).entries, []);
    // Corrupt working data must fail closed, rather than expose an older seed.
    await writeFile(join(root, 'runtime/entries.json'), '{');
    await assert.rejects(sitePayload({projectRoot: root}), SyntaxError);
  } finally { await rm(root, {recursive: true, force: true}); }
});

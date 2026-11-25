import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, readdir, rm, symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {assertPublicPath, buildPlan, createPublicArchive, freezeRelease, inspectPublicHTML, inventoryStatic, sha256, treeDigest, verifyRelease} from '../scripts/prepare-demo.mjs';

const checks = ['tests', 'check-data', 'build-static', 'check-release'].map(name => ({name, exitCode: 0}));
const payload = {categories: Array.from({length: 12}, (_, index) => ({id: `test-${index}`})), entries: []};
const html = data => '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body><script id="wiki-data" type="application/json">' + JSON.stringify(data) + '</script></body></html>';

async function temporary(task) {
  const root = await mkdtemp(join(tmpdir(), 'wow-demo-test-'));
  try { return await task(root); } finally { await rm(root, {recursive: true, force: true}); }
}
async function fixture(root) {
  const directory = join(root, 'dist');
  for (const path of ['index.html', 'fr/index.html', 'en/index.html', 'site.css', 'app.js', 'ui-core.mjs', 'assets/test.svg']) {
    await mkdir(join(directory, path, '..'), {recursive: true});
    await writeFile(join(directory, path), path.endsWith('.html') ? html(payload) : 'test-only');
  }
  return directory;
}

test('demo checks are sequential and use the same runtime dataset for audit and release inspection', () => {
  const plan = buildPlan(['tests/z.test.mjs', 'tests/a.test.mjs'], 'runtime/entries.json');
  assert.deepEqual(plan.map(step => step.name), ['tests', 'check-data', 'build-static', 'check-release']);
  assert.deepEqual(plan[0].args, ['--test', '--test-isolation=none', 'tests/a.test.mjs', 'tests/z.test.mjs']);
  assert.equal(plan[1].args.at(-1), 'runtime/entries.json');
  assert.equal(plan[3].args.at(-1), 'runtime/entries.json');
  assert.throws(() => buildPlan([], 'data/entries.json'), /tests required/);
});

test('publication boundary rejects source trees, secrets, path traversal and unrelated public output', () => {
  for (const path of ['../escape', '/index.html', 'runtime/entries.json', 'data/entries.json', '.openai/site.json', '.env', 'assets/key.pem', 'assets/key.key', 'assets/../secret.webp', 'assets/nested/test.webp', 'sources/README.md', 'deployment.json']) assert.throws(() => assertPublicPath(path));
  for (const path of ['index.html', 'en/index.html', 'assets/hero.webp', 'assets/frame.svg']) assert.doesNotThrow(() => assertPublicPath(path));
});

test('static catalog inspection excludes drafts and refuses public content without validated source DTOs', () => {
  const draft = {id: 'test-private', status: 'draft', privateNote: 'PRIVATE-FIXTURE'};
  assert.equal(inspectPublicHTML(html(payload), [draft]), 0);
  assert.throws(() => inspectPublicHTML(html({...payload, entries: [draft]}), [draft]), /unvalidated content/);
  assert.throws(() => inspectPublicHTML(html(payload) + html(payload), []), /exactly one/);
  assert.throws(() => inspectPublicHTML(html(payload).replace('noindex,nofollow', 'index,follow'), []), /noindex/);
});

test('release fingerprint is independent of inventory order and changes with bytes or public paths', () => {
  const a = {path: 'index.html', size: 1, sha256: sha256('a')}, b = {path: 'app.js', size: 1, sha256: sha256('b')};
  assert.equal(treeDigest([a, b]), treeDigest([b, a]));
  assert.notEqual(treeDigest([a, b]), treeDigest([{...a, sha256: sha256('c')}, b]));
  assert.notEqual(treeDigest([a]), treeDigest([{...a, path: 'fr/index.html'}]));
  assert.throws(() => treeDigest([a, a]), /duplicate/);
});

test('portable demo ZIP is reproducible and preserves public bytes with CRC32', () => {
  const files = [{path: 'index.html', content: Buffer.from('123456789')}, {path: 'app.js', content: Buffer.from('Test only')}];
  const archive = createPublicArchive(files);
  assert.ok(archive.equals(createPublicArchive([...files].reverse())));
  assert.equal(archive.readUInt32LE(0), 0x04034b50);
  // The first sorted entry is app.js. The second local header follows its exact bytes.
  const offset = 30 + Buffer.byteLength(files[1].path) + files[1].content.length;
  assert.equal(archive.readUInt32LE(offset + 14), 0xcbf43926);
  assert.ok(archive.includes(Buffer.from('123456789')));
  assert.throws(() => createPublicArchive([{path: '.env', content: Buffer.from('PRIVATE')}]), /unapproved/);
  assert.throws(() => createPublicArchive([files[0], files[0]]), /duplicate/);
});

test('inventory refuses symbolic links and missing required files', async () => temporary(async root => {
  const directory = await fixture(root);
  await symlink(join(directory, 'app.js'), join(directory, 'assets/link.svg'));
  await assert.rejects(inventoryStatic(directory), /symbolic link/);
  await rm(join(directory, 'assets/link.svg'));
  await rm(join(directory, 'index.html'));
  await assert.rejects(inventoryStatic(directory), /missing required/);
}));

test('preparation freezes a verified snapshot, reuses identical output and detects later tampering', async () => temporary(async root => {
  const directory = await fixture(root), releaseRoot = join(root, 'releases');
  const result = await freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks, now: '2026-10-18T00:00:00.000Z'});
  assert.equal(result.reused, false);
  const manifest = JSON.parse(await readFile(join(result.directory, 'release.json'), 'utf8'));
  assert.equal(manifest.publishedEntries, 0);
  assert.equal(manifest.deployment.published, false);
  assert.deepEqual(manifest.checks, checks);
  assert.equal((await verifyRelease(result.directory)).id, result.id);
  assert.equal((await freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks})).reused, true);
  assert.deepEqual(await readdir(releaseRoot), [result.id]);
  await writeFile(join(result.directory, 'site/app.js'), 'tampered');
  await assert.rejects(verifyRelease(result.directory), /contents have changed/);
  await assert.rejects(freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks}), /contents have changed/);
}));

test('failed checks cannot create a release, and ZIP corruption is detected before reuse', async () => temporary(async root => {
  const directory = await fixture(root), releaseRoot = join(root, 'releases');
  await assert.rejects(freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks: checks.map(check => ({...check, exitCode: 1}))}), /all preparation checks/);
  await assert.rejects(readdir(releaseRoot), {code: 'ENOENT'});
  const result = await freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks});
  await writeFile(join(result.directory, 'site-demo.zip'), 'bad archive');
  await assert.rejects(verifyRelease(result.directory), /archive differs/);
}));

test('all language entrypoints are checked before freezing a public release', async () => temporary(async root => {
  const directory = await fixture(root);
  await writeFile(join(directory, 'en/index.html'), html({...payload, entries: [{id: 'test-draft', status: 'draft'}]}));
  await assert.rejects(freezeRelease({staticDirectory: directory, releaseRoot: join(root, 'releases'), records: [], checks}), /unvalidated content/);
}));

test('incomplete existing snapshots and altered check evidence fail closed without overwriting', async () => temporary(async root => {
  const directory = await fixture(root), releaseRoot = join(root, 'releases');
  const result = await freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks});
  const path = join(result.directory, 'release.json'), manifest = JSON.parse(await readFile(path, 'utf8'));
  await writeFile(path, JSON.stringify({...manifest, checks: []}));
  await assert.rejects(verifyRelease(result.directory), /all preparation checks/);
  await rm(path);
  await assert.rejects(freezeRelease({staticDirectory: directory, releaseRoot, records: [], checks}), {code: 'ENOENT'});
  await assert.rejects(readFile(path), {code: 'ENOENT'});
  assert.deepEqual(await readdir(releaseRoot), [result.id]);
}));

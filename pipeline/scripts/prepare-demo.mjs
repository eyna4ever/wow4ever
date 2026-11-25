import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {readFile, writeFile, readdir, lstat, mkdir, mkdtemp, rename, rm} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectPublicEntries, homeEntries} from '../lib/public-catalog.mjs';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const lexical = (a, b) => a < b ? -1 : a > b ? 1 : 0;
export const sha256 = value => createHash('sha256').update(value).digest('hex');
const fixedPublicFiles = new Set(['index.html', 'fr/index.html', 'en/index.html', 'site.css', 'app.js', 'ui-core.mjs']);
// L1 (reviewed 2026-10-30): shared header behaviour and the search-overlay index (published DTO fields only, checked by package-web).
const optionalPublicFiles = new Set(['wk-header.js', 'search-index.json']);
const maximumBytes = 128 * 1024 * 1024;

// Static article pages: /fr|en/<category-slug>/index.html and /fr|en/<category-slug>/<entry-slug>/index.html (reviewed 2026-10-24).
const pagePath = /^(?:fr|en)\/[a-z0-9]+(?:-[a-z0-9]+)*\/(?:[a-z0-9]+(?:-[a-z0-9]+)*\/)?index\.html$/;
const pageDirectory = /^(?:fr|en)\/[a-z0-9]+(?:-[a-z0-9]+)*(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)?$/;
// Deliberately narrow: extending the build output requires reviewing this boundary.
export function assertPublicPath(path) {
  assert.equal(typeof path, 'string', 'public path must be a string');
  assert.ok(fixedPublicFiles.has(path) || optionalPublicFiles.has(path) || /^assets\/[a-z0-9][a-z0-9._-]*\.(?:svg|webp|jpe?g|woff2?)$/i.test(path) || pagePath.test(path), `unapproved public file: ${path}`);
  assert.doesNotMatch(path, /(?:^|\/)(?:\.env|\.git|\.openai|runtime|data|sources)(?:[/.]|$)|\.(?:pem|key)$/i, `private public file: ${path}`);
}

export function buildPlan(testFiles, dataset) {
  assert.ok(testFiles.length > 0, 'tests required');
  return [
    {name: 'tests', args: ['--test', '--test-isolation=none', ...[...testFiles].sort(lexical)]},
    {name: 'check-data', args: ['scripts/check-data.mjs', dataset]},
    {name: 'build-static', args: ['scripts/build-static.mjs']},
    {name: 'check-release', args: ['scripts/check-release.mjs', 'artifacts/wow-forever-integre.html', dataset]}
  ];
}

export function inspectPublicHTML(html, records) {
  const matches = [...html.matchAll(/<script\b[^>]*\bid=["']wiki-data["'][^>]*>([\s\S]*?)<\/script>/gi)];
  assert.equal(matches.length, 1, 'exactly one public catalog required');
  const payload = JSON.parse(matches[0][1]);
  assert.deepEqual(payload.entries, homeEntries(selectPublicEntries(records)), 'static HTML contains unvalidated content or differs from the reviewed catalog');
  assert.equal(payload.categories.length, 12, 'twelve categories required');
  assert.match(html, /<meta\b[^>]*name=["']robots["'][^>]*content=["']noindex,nofollow["']/i, 'demo must remain noindex');
  return payload.entries.length;
}

export async function inventoryStatic(directory) {
  const files = [];
  let total = 0;
  async function walk(relative = '') {
    const absolute = join(directory, relative);
    const stat = await lstat(absolute);
    assert.equal(stat.isSymbolicLink(), false, `symbolic link forbidden: ${relative || '.'}`);
    if (stat.isDirectory()) {
      assert.ok(['', 'assets', 'fr', 'en'].includes(relative) || pageDirectory.test(relative), `unapproved public directory: ${relative}`);
      for (const item of (await readdir(absolute)).sort(lexical)) await walk(relative ? `${relative}/${item}` : item);
      return;
    }
    assert.ok(stat.isFile(), `regular public file required: ${relative}`);
    assertPublicPath(relative);
    total += stat.size;
    assert.ok(total <= maximumBytes, 'demo exceeds 128 MiB');
    const content = await readFile(absolute);
    if (relative.endsWith('.html')) assert.doesNotMatch(content.toString('utf8'), /wow4ever-build" content="preview/, `local preview page refused: ${relative}`);
    files.push({path: relative, size: content.length, sha256: sha256(content)});
  }
  await walk();
  for (const path of fixedPublicFiles) assert.ok(files.some(file => file.path === path), `missing required public file: ${path}`);
  return files.sort((a, b) => lexical(a.path, b.path));
}

export function treeDigest(files) {
  const paths = new Set();
  const canonical = [...files].sort((a, b) => lexical(a.path, b.path)).map(file => {
    assertPublicPath(file.path);
    assert.equal(paths.has(file.path), false, `duplicate public file: ${file.path}`);
    paths.add(file.path);
    assert.ok(Number.isSafeInteger(file.size) && file.size >= 0 && /^[a-f0-9]{64}$/.test(file.sha256), 'invalid file fingerprint');
    return {path: file.path, size: file.size, sha256: file.sha256};
  });
  return sha256(JSON.stringify(canonical));
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

/** Reproducible ZIP without a shell, package dependency, timestamps or secrets. */
export function createPublicArchive(items) {
  assert.ok(items.length > 0 && items.length < 10_000, 'archive file count out of bounds');
  const names = new Set(), locals = [], central = [];
  let offset = 0, total = 0;
  for (const item of [...items].sort((a, b) => lexical(a.path, b.path))) {
    assertPublicPath(item.path);
    assert.equal(names.has(item.path), false, `duplicate public file: ${item.path}`);
    names.add(item.path);
    assert.ok(Buffer.isBuffer(item.content), 'archive content must be a Buffer');
    total += item.content.length;
    assert.ok(total <= maximumBytes, 'archive exceeds 128 MiB');
    const name = Buffer.from(item.path), size = item.content.length, checksum = crc32(item.content);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50); local.writeUInt16LE(20, 4); local.writeUInt16LE(0x21, 12);
    local.writeUInt32LE(checksum, 14); local.writeUInt32LE(size, 18); local.writeUInt32LE(size, 22); local.writeUInt16LE(name.length, 26);
    const entry = Buffer.alloc(46);
    entry.writeUInt32LE(0x02014b50); entry.writeUInt16LE(20, 4); entry.writeUInt16LE(20, 6); entry.writeUInt16LE(0x21, 14);
    entry.writeUInt32LE(checksum, 16); entry.writeUInt32LE(size, 20); entry.writeUInt32LE(size, 24); entry.writeUInt16LE(name.length, 28); entry.writeUInt32LE(offset, 42);
    locals.push(local, name, item.content); central.push(entry, name);
    offset += local.length + name.length + size;
  }
  const directory = Buffer.concat(central), end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50); end.writeUInt16LE(items.length, 8); end.writeUInt16LE(items.length, 10);
  end.writeUInt32LE(directory.length, 12); end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, directory, end]);
}

function assertPassedChecks(checks) {
  assert.ok(Array.isArray(checks), 'preparation checks required');
  assert.deepEqual(checks.map(check => [check.name, check.exitCode]), [['tests', 0], ['check-data', 0], ['build-static', 0], ['check-release', 0]], 'all preparation checks must pass in order');
}

export async function verifyRelease(directory) {
  assert.equal((await lstat(directory)).isSymbolicLink(), false, 'release directory cannot be a symbolic link');
  for (const path of ['release.json', 'site-demo.zip']) assert.equal((await lstat(join(directory, path))).isSymbolicLink(), false, `release metadata cannot be a symbolic link: ${path}`);
  const manifest = JSON.parse(await readFile(join(directory, 'release.json'), 'utf8'));
  assert.equal(manifest.schemaVersion, 1, 'unknown release schema');
  assertPassedChecks(manifest.checks);
  const files = await inventoryStatic(join(directory, 'site'));
  assert.deepEqual(files, manifest.files, 'release contents have changed');
  assert.equal(manifest.id, `sha256-${treeDigest(files)}`, 'release fingerprint differs');
  const items = await Promise.all(files.map(async file => ({path: file.path, content: await readFile(join(directory, 'site', file.path))})));
  const archive = await readFile(join(directory, 'site-demo.zip'));
  assert.ok(archive.equals(createPublicArchive(items)), 'release archive differs from verified site');
  return {id: manifest.id, files: files.length, bytes: files.reduce((sum, file) => sum + file.size, 0), archiveSHA256: sha256(archive)};
}

export async function freezeRelease({staticDirectory, releaseRoot, records, checks, now = new Date().toISOString()}) {
  assertPassedChecks(checks);
  const files = await inventoryStatic(staticDirectory);
  for (const path of ['index.html', 'fr/index.html', 'en/index.html']) inspectPublicHTML(await readFile(join(staticDirectory, path), 'utf8'), records);
  const id = `sha256-${treeDigest(files)}`, directory = join(releaseRoot, id);
  await mkdir(releaseRoot, {recursive: true});
  let existing = false;
  try { await lstat(directory); existing = true; } catch (error) { if (error.code !== 'ENOENT') throw error; }
  if (existing) {
    const verification = await verifyRelease(directory);
    return {directory, reused: true, ...verification};
  }
  const staging = await mkdtemp(join(releaseRoot, '.preparing-'));
  try {
    const items = [];
    for (const file of files) {
      const content = await readFile(join(staticDirectory, file.path));
      assert.equal(sha256(content), file.sha256, 'static build changed during snapshot');
      const destination = join(staging, 'site', file.path);
      await mkdir(dirname(destination), {recursive: true});
      await writeFile(destination, content, {flag: 'wx'});
      items.push({path: file.path, content});
    }
    const manifest = {schemaVersion: 1, id, preparedAt: now, files, publishedEntries: selectPublicEntries(records).length, checks,
      deployment: {state: 'prepared-locally', published: false, intendedVisibility: 'private', target: 'Sites demo'},
      notCovered: ['Sites publication', 'HTTPS availability', 'browser rendering', 'Android device validation', 'Next.js build', 'backend authentication']};
    await writeFile(join(staging, 'release.json'), JSON.stringify(manifest, null, 2) + '\n', {flag: 'wx'});
    await writeFile(join(staging, 'site-demo.zip'), createPublicArchive(items), {flag: 'wx'});
    const verification = await verifyRelease(staging);
    await rename(staging, directory);
    return {directory, reused: false, ...verification};
  } finally { await rm(staging, {recursive: true, force: true}); }
}

async function runNode(args, cwd) {
  await new Promise((success, failure) => {
    const child = spawn(process.execPath, args, {cwd, stdio: 'inherit', shell: false});
    child.once('error', error => failure(new Error(`Cannot execute Node check (${error.code ?? error.message}); no release prepared.`)));
    child.once('exit', (code, signal) => code === 0 ? success() : failure(new Error(`Node check failed (${signal ?? code}); no release prepared.`)));
  });
}

export async function main(argv = process.argv.slice(2)) {
  if (argv.length === 1 && argv[0] === '--help') {
    console.log('Usage: node scripts/prepare-demo.mjs\n       node scripts/prepare-demo.mjs --verify artifacts/demo-releases/sha256-<hash>\nLocal preparation only. No network or Sites publication.');
    return;
  }
  if (argv.length === 2 && argv[0] === '--verify') { console.log(JSON.stringify(await verifyRelease(resolve(argv[1])), null, 2)); return; }
  assert.equal(argv.length, 0, 'unknown arguments; use --help');
  let dataset = 'runtime/entries.json';
  try { await lstat(join(projectRoot, dataset)); } catch (error) { if (error.code !== 'ENOENT') throw error; dataset = 'data/entries.json'; }
  const testFiles = (await readdir(join(projectRoot, 'tests'))).filter(name => name.endsWith('.test.mjs')).map(name => `tests/${name}`);
  const checks = [];
  for (const step of buildPlan(testFiles, dataset)) {
    console.log(`[prepare-demo] ${step.name}`);
    await runNode(step.args, projectRoot);
    checks.push({name: step.name, exitCode: 0});
  }
  const records = JSON.parse(await readFile(join(projectRoot, dataset), 'utf8'));
  const result = await freezeRelease({staticDirectory: join(projectRoot, 'dist'), releaseRoot: join(projectRoot, 'artifacts/demo-releases'), records, checks});
  const report = {preparedAt: new Date().toISOString(), ...result, sourceDataset: dataset, deployment: 'not-published-by-this-script', nextAction: 'Sites owner publishes the verified site/ snapshot privately, then records the returned URL and deployment ID.'};
  const temporaryReport = join(projectRoot, 'artifacts', `.demo-latest-${process.pid}.json`);
  await writeFile(temporaryReport, JSON.stringify(report, null, 2) + '\n');
  await rename(temporaryReport, join(projectRoot, 'artifacts/demo-latest.json'));
  console.log(JSON.stringify(report, null, 2));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Demo preparation failed: ${error.message}`); process.exitCode = 1; });
}

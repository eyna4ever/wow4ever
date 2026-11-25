import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, rm, access} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {auditDataset, categories, digest, merge} from '../lib/documentary.mjs';
import {selectPublicEntries} from '../lib/public-catalog.mjs';
import {initialBatches, main as importLibrary} from '../scripts/import-library.mjs';

const root = resolve(import.meta.dirname, '..');
const batches = await Promise.all(initialBatches.map(path => readFile(join(root, path), 'utf8').then(JSON.parse)));
const records = batches.flat();

test('initial source library has unique, valid bilingual records in all twelve categories', () => {
  assert.equal(records.length, 36);
  assert.equal(new Set(records.map(entry => entry.id)).size, records.length);
  assert.deepEqual(auditDataset(records).errors, []);
  assert.deepEqual(new Set(records.map(entry => entry.category)), categories);
  assert.equal(new Set(records.map(entry => entry.gameVersion)).size, 1);
  for (const entry of records) {
    assert.equal(entry.status, 'draft');
    assert.equal(entry.identityConfirmed, false);
    assert.equal(entry.review, undefined);
    for (const source of entry.sources) assert.equal(new URL(source.url).hostname, 'news.blizzard.com');
  }
});

test('initial library cannot cross the publication boundary or import an approval', () => {
  assert.deepEqual(selectPublicEntries(records), []);
  const imported = merge([], records, {now: '2026-10-19T12:00:00Z'});
  assert.equal(imported.report.inserted.length, 36);
  assert.deepEqual(selectPublicEntries(imported.records), []);
  const again = merge(imported.records, records, {now: '2026-10-19T12:00:01Z'});
  assert.equal(again.report.duplicates.length, 36);
  assert.equal(again.report.inserted.length, 0);
  assert.equal(digest(again.records), digest(imported.records));
});

test('library CLI imports once, preserves its seed and resumes without duplicate records', async () => {
  const temporary = await mkdtemp(join(tmpdir(), 'wow-initial-content-'));
  const runtime = join(temporary, 'runtime');
  const seedPath = join(root, 'data/entries.json');
  const seedBefore = await readFile(seedPath, 'utf8');
  const logs = [];
  try {
    const invoke = flags => importLibrary(['--runtime-dir', runtime, '--seed', seedPath, ...flags], {log: value => logs.push(JSON.parse(value)), setExitCode: code => assert.fail(`unexpected exit code ${code}`)});
    await invoke(['--dry-run']);
    assert.equal(logs.at(-1).inserted.length, 36);
    await assert.rejects(access(runtime), {code: 'ENOENT'});
    await invoke([]);
    assert.equal(logs.at(-1).committed, true);
    assert.equal(logs.at(-1).inserted.length, 36);
    const once = await readFile(join(runtime, 'entries.json'), 'utf8');
    await invoke([]);
    assert.equal(logs.at(-1).duplicates.length, 36);
    assert.equal(logs.at(-1).unchanged, true);
    assert.equal(await readFile(join(runtime, 'entries.json'), 'utf8'), once);
    assert.equal(await readFile(seedPath, 'utf8'), seedBefore);
  } finally { await rm(temporary, {recursive: true, force: true}); }
});

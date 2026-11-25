import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, writeFile, readFile, readdir, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {auditDataset, commitDataset, contentDigest, decodeBackup, digest, loadDataset, merge, normalizeEntry, parseArgs, readJSON, transitionRecord, reviseRecord, validate, withDatasetLock} from '../lib/documentary.mjs';

// Synthetic fixtures are confined to tests and temporary directories; never documentary data.
const now = '2026-10-18T00:00:00.000Z';
const fixture = (id = 'test-only') => ({id, title: {fr: 'Test', en: 'Test'}, description: {fr: 'Test', en: 'Test'}, category: 'guides', subcategory: 'test', status: 'draft', gameVersion: 'test', version: 1, updatedAt: now, sources: [{url: 'https://example.org/reference', accessedAt: now, license: 'test-only'}], relations: [], history: [{at: now, actor: 'test', note: 'fixture', version: 1}]});
const approval = {actor: 'Human test reviewer', note: 'Test decision', now, humanReview: true, identity: true, rights: true, translations: true};
const published = () => {
  let records = transitionRecord([fixture()], 'test-only', 'submit', approval).records;
  records = transitionRecord(records, 'test-only', 'approve', approval).records;
  return transitionRecord(records, 'test-only', 'publish', {...approval, publish: true}).records[0];
};
const project = resolve(import.meta.dirname, '..');
async function temporary(task) {
  const root = await mkdtemp(join(tmpdir(), 'wow-documentary-test-'));
  try { return await task(root); } finally { await rm(root, {recursive: true, force: true}); }
}
// Exercise the exported CLI entrypoint in-process: this sandbox blocks Node child stdio.
async function cli(script, args, success = true) {
  const output = [];
  let code = 0, stderr = '';
  const module = await import(join(project, 'scripts', script));
  try { await module.main(args, {log: value => output.push(value), setExitCode: value => { code = value; }}); }
  catch (error) { code = 1; stderr = error.message; }
  if (success) assert.equal(code, 0, stderr);
  else assert.notEqual(code, 0, 'CLI unexpectedly succeeded');
  const stdout = output.join('\n');
  return {code, stderr, stdout, json: stdout ? JSON.parse(stdout) : null};
}

test('valid bilingual fixture passes and validation never mutates it', () => { const entry = fixture(), copy = structuredClone(entry); assert.deepEqual(validate(entry), []); assert.deepEqual(entry, copy); });
test('malformed JSON shapes produce validation errors without throwing', () => {
  for (const value of [null, undefined, false, 12, 'text', [], {}, {sources: {}}, {...fixture(), sources: [null, 3]}, {...fixture(), history: [null]}, {...fixture(), relations: null}, {...fixture(), title: null}]) assert.ok(validate(value).length);
});
test('non-JSON, cyclic, excessively nested and unsafe data are rejected safely', () => {
  const cyclic = fixture(); cyclic.extra = cyclic;
  for (const value of [{...fixture(), extra: 1n}, {...fixture(), extra: undefined}, cyclic, JSON.parse('{"id":"test-only","__proto__":{"polluted":true}}')]) assert.ok(validate(value).length);
  assert.equal({}.polluted, undefined);
});
test('rejects unsourced and untranslated content', () => { const entry = fixture(); entry.sources = []; entry.title.en = ''; assert.ok(validate(entry).some(error => error.includes('sources'))); assert.ok(validate(entry).some(error => error.includes('title.en'))); });
test('rejects non-HTTPS, credential-bearing, and invalid references', () => {
  for (const url of ['javascript:alert(1)', 'http://example.org', 'https://user:password@example.org', 'not-a-url']) { const entry = fixture(); entry.sources[0].url = url; assert.ok(validate(entry).length); }
});
test('rejects impossible dates, invalid versions and unsafe relation IDs', () => {
  for (const value of ['2026-02-30', 'not-a-date', '2026-01-01T99:00:00Z']) { const entry = fixture(); entry.updatedAt = value; assert.ok(validate(entry).length); }
  const entry = fixture(); entry.version = 1.5; entry.relations = ['<script>']; assert.ok(validate(entry).length);
});
test('rejects source and record version contradictions', () => { const entry = fixture(); entry.sources[0].gameVersion = 'other-test-version'; assert.ok(validate(entry).some(error => error.includes('version differs'))); });
test('requires a bounded nonempty source license and consult date', () => { const entry = fixture(); entry.sources[0].license = ''; entry.sources[0].accessedAt = '2026-02-30'; assert.ok(validate(entry).some(error => error.includes('license/date'))); });
test('normalization trims Unicode strings and preserves primitive types', () => { const entry = fixture(); entry.title.fr = '  Cafe\u0301  '; const result = normalizeEntry(entry); assert.equal(result.title.fr, 'Café'); assert.equal(result.version, 1); assert.equal(entry.title.fr, '  Cafe\u0301  '); });
test('normalization deduplicates references and inherits an omitted reference version', () => { const entry = fixture(); entry.sources.push({...entry.sources[0]}); entry.relations = ['test-other', 'test-other']; const result = normalizeEntry(entry); assert.equal(result.sources.length, 1); assert.equal(result.sources[0].gameVersion, entry.gameVersion); assert.deepEqual(result.relations, ['test-other']); });
test('normalization cannot repair an explicitly malformed source version', () => { const entry = fixture(); entry.sources[0].gameVersion = null; const result = merge([], [entry], {now}); assert.equal(result.report.invalid.length, 1); });
test('canonical digests ignore object property order', () => { assert.equal(digest({b: 2, a: 1}), digest({a: 1, b: 2})); });
test('audit reports duplicate IDs and dangling relations without crashing malformed rows', () => { const entry = fixture(); entry.relations = ['missing-test']; const audit = auditDataset([entry, fixture(), null]); assert.ok(audit.errors.some(item => item.errors.includes('duplicate ID'))); assert.ok(audit.errors.some(item => item.errors.some(error => error.includes('dangling')))); });
test('dataset root must be an array', () => { assert.ok(auditDataset({}).errors.length); assert.throws(() => merge({}, []), /arrays/); assert.throws(() => merge([], {}), /arrays/); });
test('resuming a draft batch is idempotent and does not mutate inputs', () => { const entry = fixture(), copy = structuredClone(entry); const first = merge([], [entry], {now}); const resumed = merge(first.records, [entry], {now}); assert.equal(resumed.records.length, 1); assert.deepEqual(resumed.report.duplicates, [entry.id]); assert.deepEqual(entry, copy); });
test('resuming an originally published batch is idempotent', () => { const entry = published(); const first = merge([], [entry], {now}), resumed = merge(first.records, [entry], {now}); assert.equal(first.records[0].status, 'draft'); assert.equal(first.records[0].identityConfirmed, false); assert.equal(first.records[0].review, undefined); assert.deepEqual(resumed.report.duplicates, [entry.id]); });
test('resuming a source batch after local human review preserves the local publication', () => { const entry = fixture(); let records = merge([], [entry], {now}).records; records = transitionRecord(records, entry.id, 'submit', approval).records; records = transitionRecord(records, entry.id, 'approve', approval).records; records = transitionRecord(records, entry.id, 'publish', {...approval, publish: true}).records; const result = merge(records, [entry], {now}); assert.equal(result.records[0].status, 'published'); assert.equal(result.report.duplicates.length, 1); });
test('importing an exported local record is idempotent', () => { const first = merge([], [fixture()], {now}); const result = merge(first.records, first.records, {now}); assert.equal(result.report.duplicates.length, 1); assert.equal(result.report.conflicts.length, 0); });
test('foreign publication approval is not trusted during import', () => { const entry = fixture(); entry.status = 'published'; entry.review = {approved: true}; entry.identityConfirmed = true; const result = merge([], [entry], {now}); assert.equal(result.records[0].status, 'draft'); assert.equal(result.records[0].review, undefined); });
test('conflicts preserve the existing version and explain the disagreement', () => { const entry = fixture(), changed = {...entry, version: 2}; const result = merge([entry], [changed], {now}); assert.equal(result.report.conflicts.length, 1); assert.equal(result.report.conflicts[0].existingVersion, 1); assert.equal(result.records[0].version, 1); });
test('identical IDs in one batch are deduplicated', () => { const entry = fixture(), result = merge([], [entry, entry], {now}); assert.equal(result.records.length, 1); assert.equal(result.report.duplicates.length, 1); });
test('contradictory IDs in one batch are both held back', () => { const entry = fixture(), result = merge([], [entry, {...entry, version: 2}], {now}); assert.equal(result.records.length, 0); assert.equal(result.report.conflicts.length, 1); });
test('valid forward relations are retained in the same batch', () => { const first = fixture('test-first'), second = fixture('test-second'); first.relations = [second.id]; const result = merge([], [first, second], {now}); assert.equal(result.records.length, 2); assert.equal(result.report.invalid.length, 0); });
test('dangling relations are rejected transitively', () => { const first = fixture('test-first'), second = fixture('test-second'); first.relations = [second.id]; second.relations = ['missing-test']; const result = merge([], [first, second], {now}); assert.equal(result.records.length, 0); assert.equal(result.report.invalid.length, 2); });
test('malformed rows do not prevent valid unrelated rows from being imported', () => { const result = merge([], [null, {sources: {}}, fixture()], {now}); assert.equal(result.report.invalid.length, 2); assert.equal(result.records.length, 1); });
test('invalid current stores are never overwritten by a merge', () => { assert.throws(() => merge([null], [fixture()]), /current dataset is invalid/); });
test('batch, bytes, sources and total quotas are enforced', () => {
  assert.throws(() => merge([], [fixture()], {maxRecords: 0}), /batch quota/);
  assert.throws(() => merge([], [fixture()], {maxBytes: 10}), /byte quota/);
  assert.throws(() => merge([], [fixture()], {maxTotalRecords: 0}), /total dataset quota/);
  assert.equal(merge([], [fixture()], {maxSources: 0}).report.invalid.length, 1);
  assert.throws(() => merge([], [], {maxRecords: -1}), /non-negative/);
  assert.throws(() => merge([], [], {maxBytes: Infinity}), /non-negative/);
});
test('staleness includes old references even if the record was recently edited', () => { const entry = fixture(); entry.sources[0].accessedAt = '2020-01-01'; assert.deepEqual(merge([], [entry], {now}).report.stale, [entry.id]); });
test('the local import pipeline spends zero and does not claim semantic verification', () => { const {report} = merge([], [fixture()], {now}); assert.deepEqual(report.cost, {currency: 'EUR', actual: 0, ceiling: 0}); assert.equal(report.stages.verification, 'structural-only'); assert.equal(report.stages.publication, 'human-required'); });
test('direct publication without current human review is rejected', () => { const entry = fixture(); entry.status = 'published'; entry.identityConfirmed = true; entry.review = {approved: true, reviewer: 'human', at: now}; assert.ok(validate(entry).length); });
test('human review requires all explicit attestations and correct state transitions', () => {
  assert.throws(() => transitionRecord([fixture()], 'test-only', 'approve', approval), /submitted/);
  const submitted = transitionRecord([fixture()], 'test-only', 'submit', approval).records;
  assert.throws(() => transitionRecord(submitted, 'test-only', 'approve', {...approval, rights: false}), /attestations/);
  const verified = transitionRecord(submitted, 'test-only', 'approve', approval).records;
  assert.throws(() => transitionRecord(verified, 'test-only', 'publish', approval), /confirm-publish/);
});
test('publication is bound to reviewed content and each decision adds a history revision', () => { const entry = published(); assert.deepEqual(validate(entry), []); assert.equal(entry.version, 4); assert.equal(entry.history.length, 4); assert.equal(entry.review.contentDigest, contentDigest(entry)); entry.description.fr = 'Changed after review'; assert.ok(validate(entry).some(error => error.includes('current human review'))); });
test('rejection withdraws publication and removes approval', () => { const result = transitionRecord([published()], 'test-only', 'reject', approval); assert.equal(result.records[0].status, 'draft'); assert.equal(result.records[0].review, undefined); assert.equal(result.records[0].identityConfirmed, false); });
test('review requires a traceable actor and note', () => { assert.throws(() => transitionRecord([fixture()], 'test-only', 'submit', {actor: '', note: ''}), /actor and review note/); });
test('explicit correction withdraws publication, preserves history and advances local revision', () => { const previous = published(), correction = fixture(); correction.description.fr = 'Corrected test content'; const result = reviseRecord([previous], previous.id, correction, approval); assert.equal(result.records[0].status, 'draft'); assert.equal(result.records[0].version, previous.version + 1); assert.equal(result.records[0].history.length, previous.history.length + 1); assert.equal(result.records[0].review, undefined); assert.equal(result.records[0].description.fr, correction.description.fr); assert.deepEqual(validate(result.records[0]), []); });
test('correction rejects changed stable IDs and dangling relations', () => { assert.throws(() => reviseRecord([fixture()], 'test-only', fixture('changed-test'), approval), /stable entry ID/); const correction = fixture(); correction.relations = ['missing-test']; assert.throws(() => reviseRecord([fixture()], 'test-only', correction, approval), /dangling relation/); });
test('CLI parser rejects misspelled flags, duplicates and missing values', () => { assert.throws(() => parseArgs(['--unknown']), /unknown/); assert.throws(() => parseArgs(['--actor'], {values: ['actor']}), /value required/); assert.throws(() => parseArgs(['--dry-run', '--dry-run'], {flags: ['dry-run']}), /duplicate/); });
test('file reads enforce byte quotas and preserve parse errors', async () => temporary(async root => { const path = join(root, 'large.json'); await writeFile(path, '[1,2,3]'); await assert.rejects(readJSON(path, {maxBytes: 3}), /byte quota/); await writeFile(path, '{'); await assert.rejects(readJSON(path), SyntaxError); }));
test('atomic commits save a checksum-protected backup and restoration is validated', async () => temporary(async root => {
  const before = [fixture()], after = transitionRecord(before, 'test-only', 'submit', approval).records;
  const receipt = await withDatasetLock(root, () => commitDataset(root, before, after, {operation: 'test'}));
  assert.equal(receipt.committed, true);
  assert.deepEqual(await loadDataset({runtimeDir: root}), after);
  const backup = await readJSON(receipt.backup);
  assert.deepEqual(decodeBackup(backup), before);
  backup.records[0].title.fr = 'tampered'; assert.throws(() => decodeBackup(backup), /checksum mismatch/);
  assert.equal((await readJSON(receipt.reportPath)).afterChecksum, digest(after));
}));
test('store lock prevents concurrent writers and is released after failure', async () => temporary(async root => {
  await withDatasetLock(root, async () => { await assert.rejects(withDatasetLock(root, async () => {}), /locked/); });
  await assert.rejects(withDatasetLock(root, async () => { throw new Error('test interruption'); }), /interruption/);
  await withDatasetLock(root, async () => {});
}));
test('CLI import dry-run, resume, review, publish, restore and integrity checks work in isolation', async () => temporary(async root => {
  const seed = join(root, 'seed.json'), batch = join(root, 'batch.json'), runtime = join(root, 'runtime');
  await writeFile(seed, '[]'); await writeFile(batch, JSON.stringify([fixture()]));
  const paths = ['--runtime-dir', runtime, '--seed', seed];
  const dry = await cli('import.mjs', [batch, ...paths, '--dry-run']); assert.equal(dry.json.committed, false); assert.deepEqual(await readdir(root), ['batch.json', 'seed.json']);
  const first = await cli('import.mjs', [batch, ...paths]); assert.equal(first.json.inserted.length, 1);
  const resumed = await cli('import.mjs', [batch, ...paths]); assert.equal(resumed.json.duplicates.length, 1); assert.equal(resumed.json.committed, false);
  assert.equal((await readdir(join(runtime, 'backups'))).length, 1);
  const reviewArgs = [...paths, '--actor', 'Human test reviewer', '--note', 'Synthetic test approval'];
  const preview = await cli('review.mjs', ['preview', 'test-only', ...paths]); assert.equal(preview.json.entry.status, 'draft');
  await cli('review.mjs', ['submit', 'test-only', ...reviewArgs]);
  const denied = await cli('review.mjs', ['approve', 'test-only', ...reviewArgs], false); assert.equal(denied.code, 1);
  await cli('review.mjs', ['approve', 'test-only', ...reviewArgs, '--confirm-human-review', '--confirm-identity', '--confirm-rights', '--confirm-translations']);
  await cli('review.mjs', ['publish', 'test-only', ...reviewArgs, '--confirm-publish']);
  const checked = await cli('check-data.mjs', [join(runtime, 'entries.json')]); assert.equal(checked.json.published, 1); assert.equal(checked.json.errors.length, 0);
  const correction = fixture(); correction.description.fr = 'Changed synthetic content'; const revisionFile = join(root, 'revision.json'); await writeFile(revisionFile, JSON.stringify(correction));
  const revised = await cli('review.mjs', ['revise', 'test-only', revisionFile, ...reviewArgs]); assert.equal(revised.json.status, 'draft'); assert.equal((await loadDataset({runtimeDir: runtime}))[0].description.fr, correction.description.fr);
  const restoreDry = await cli('restore.mjs', [first.json.backup, ...reviewArgs, '--dry-run']); assert.equal(restoreDry.json.restoredEntries, 0); assert.equal((await loadDataset({runtimeDir: runtime})).length, 1);
  const restored = await cli('restore.mjs', [first.json.backup, ...reviewArgs]); assert.equal(restored.json.committed, true); assert.deepEqual(await loadDataset({runtimeDir: runtime}), []);
}));
test('CLI malformed input reports an error and does not create a dataset', async () => temporary(async root => { const path = join(root, 'invalid.json'); await writeFile(path, '{}'); const result = await cli('import.mjs', [path, '--runtime-dir', join(root, 'runtime')], false); assert.equal(result.code, 1); assert.match(result.stderr, /arrays/); await assert.rejects(readFile(join(root, 'runtime', 'entries.json')), {code: 'ENOENT'}); }));
test('CLI check reports malformed rows rather than crashing', async () => temporary(async root => { const path = join(root, 'invalid.json'); await writeFile(path, '[null,{"relations":null}]'); const result = await cli('check-data.mjs', [path], false); assert.equal(result.code, 1); assert.ok(result.json.errors.length >= 2); }));
test('CLI partial import returns exit 2 with a retained audit report', async () => temporary(async root => { const seed = join(root, 'seed.json'), path = join(root, 'partial.json'), runtime = join(root, 'runtime'); await writeFile(seed, '[]'); await writeFile(path, JSON.stringify([null, fixture()])); const result = await cli('import.mjs', [path, '--seed', seed, '--runtime-dir', runtime], false); assert.equal(result.code, 2); assert.equal(result.json.committed, true); assert.equal(result.json.invalid.length, 1); assert.equal((await readJSON(result.json.reportPath)).invalid.length, 1); }));

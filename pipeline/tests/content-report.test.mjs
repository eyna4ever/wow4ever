import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, readdir, rm, symlink, writeFile, mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {contentDigest, transitionRecord} from '../lib/documentary.mjs';
import {createContentReport, main, renderContentReport} from '../scripts/content-report.mjs';

// Fixtures de contrôle uniquement : aucune n’est importée dans le catalogue.
const now = '2026-10-19T12:00:00.000Z';
const asOf = '2026-10-19';
const approval = {actor: 'PRIVATE-REVIEWER', note: 'PRIVATE-AUDIT', now,
  humanReview: true, identity: true, rights: true, translations: true, publish: true};
const fixture = (id = 'report-test') => ({id, title: {fr: 'PRIVATE-TITLE', en: 'PRIVATE-TITLE'},
  description: {fr: 'PRIVATE-DESCRIPTION', en: 'PRIVATE-DESCRIPTION'}, category: 'guides', subcategory: 'test',
  status: 'draft', gameVersion: 'test-version', version: 1, updatedAt: now,
  sources: [{url: 'https://example.org/reference#section', accessedAt: now, license: 'test-only'}],
  relations: [], history: [{at: now, actor: 'PRIVATE-AUTHOR', note: 'PRIVATE-HISTORY', version: 1}]});
function withStatus(status, id) {
  let records = [fixture(id)];
  for (const [action, target] of [['submit', 'review'], ['approve', 'verified'], ['publish', 'published']]) {
    if (records[0].status === status) break;
    records = transitionRecord(records, id, action, approval).records;
    if (target === status) break;
  }
  return records[0];
}
const quiet = {log: () => {}};

test('une base vide produit les douze catégories sans prétendre à la complétude', () => {
  const report = createContentReport([], {asOf});
  assert.equal(report.categories.length, 12);
  assert.equal(new Set(report.categories.map(row => row.category)).size, 12);
  assert.equal(report.totals.records, 0);
  assert.equal(report.totals.publicEligible, 0);
  assert.equal(report.uniqueSources, 0);
  assert.equal(report.nextCategories.length, 12);
  assert.ok(report.categories.every(row => row.records === 0 && row.publicEligible === 0));
  assert.equal(report.validation.valid, true);
  assert.equal(report.completeness.known, false);
  assert.match(renderContentReport(report), /complétude est inconnue/);
  assert.doesNotMatch(renderContentReport(report), /\d\s*%/);
});

test('les quatre statuts sont distincts et seuls les documents publiés admissibles comptent comme publics', () => {
  const records = ['draft', 'review', 'verified', 'published'].map(status => withStatus(status, `report-${status}`));
  const bad = {...withStatus('published', 'report-bad'), identityConfirmed: false};
  const report = createContentReport([...records, bad], {asOf});
  assert.deepEqual(report.totals.statuses, {draft: 1, review: 1, verified: 1, published: 2, unknown: 0});
  assert.equal(report.totals.publicEligible, 1);
  assert.equal(report.totals.invalidRecords, 1);
  assert.equal(report.categories.find(row => row.category === 'guides').publicEligible, 1);
  assert.equal(report.validation.valid, false);
  assert.equal(report.versionScopes[0].publicEligible, 1);
});

test('les références sont dédupliquées et les périmètres de version restent séparés', () => {
  const first = fixture('report-first');
  const second = {...fixture('report-second'), category: 'classes', gameVersion: 'another-version',
    sources: [{url: 'https://example.org/reference#other-section', accessedAt: now, license: 'test-only'}]};
  const report = createContentReport([first, second], {asOf});
  assert.equal(report.uniqueSources, 1);
  assert.equal(report.categories.find(row => row.category === 'guides').uniqueSources, 1);
  assert.equal(report.categories.find(row => row.category === 'classes').uniqueSources, 1);
  assert.deepEqual(report.versionScopes.map(scope => scope.gameVersion), ['another-version', 'test-version']);
  assert.equal(report.missingVersionScope, 0);
  assert.equal(report.validation.valid, true);
});

test('les données invalides et relations manquantes ne deviennent pas des publications admissibles', () => {
  const entry = withStatus('published', 'report-dangling');
  entry.relations = ['report-missing'];
  entry.review.contentDigest = contentDigest(entry);
  const malformed = {...fixture('report-invalid'), category: 'unknown', status: 'archived', gameVersion: '',
    sources: [{url: 'https://private:secret@example.org/', accessedAt: now, license: 'test-only'}]};
  const report = createContentReport([null, malformed, entry], {asOf});
  assert.equal(report.totals.records, 3);
  assert.equal(report.totals.invalidRecords, 3);
  assert.equal(report.totals.uncategorized, 2);
  assert.equal(report.totals.statuses.unknown, 2);
  assert.equal(report.totals.publicEligible, 0);
  assert.equal(report.uniqueSources, 1);
  assert.equal(report.missingVersionScope, 2);
  assert.match(JSON.stringify(report.validation.errors), /dangling relation/);
  assert.doesNotMatch(JSON.stringify(report), /private:secret/);
  assert.equal(createContentReport({}, {asOf}).validation.valid, false);
});

test('les identifiants dupliqués excluent toutes les publications ambiguës', () => {
  const entry = withStatus('published', 'report-duplicate');
  const report = createContentReport([entry, structuredClone(entry)], {asOf});
  assert.equal(report.totals.statuses.published, 2);
  assert.equal(report.totals.publicEligible, 0);
  assert.match(JSON.stringify(report.validation.errors), /duplicate ID/);
});

test('le rapport ne modifie pas les fiches et ne sérialise pas leur contenu ou audit privé', () => {
  const records = [withStatus('published', 'report-private')];
  const before = structuredClone(records);
  const report = createContentReport(records, {asOf});
  assert.deepEqual(records, before);
  assert.doesNotMatch(JSON.stringify(report) + renderContentReport(report), /PRIVATE-/);
  assert.deepEqual(createContentReport(records, {asOf}), report);
});

test('le Markdown neutralise les versions contenant des balises ou séparateurs', () => {
  const entry = {...fixture(), gameVersion: '<script>alert(1)</script>|\n`version`'};
  const markdown = renderContentReport(createContentReport([entry], {asOf}));
  assert.doesNotMatch(markdown, /<script>/);
  assert.match(markdown, /&lt;script&gt;/);
  assert.match(markdown, /&#124;/);
  assert.match(markdown, /&#96;version&#96;/);
});

test('la CLI exige une destination privée et écrit un rapport répétable sans toucher à la base', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-content-report-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'seed.json'), runtime = join(root, 'runtime'), output = join(root, 'reports');
  await writeFile(seed, '[]\n');
  const args = ['--output-dir', output, '--seed', seed, '--runtime-dir', runtime, '--as-of', asOf];
  await assert.rejects(main([], quiet), /output-dir/);
  await main(args, quiet);
  const first = await readFile(join(output, 'content-report.json'), 'utf8');
  const markdown = await readFile(join(output, 'content-report.md'), 'utf8');
  await main(args, quiet);
  assert.equal(await readFile(join(output, 'content-report.json'), 'utf8'), first);
  assert.equal(await readFile(join(output, 'content-report.md'), 'utf8'), markdown);
  assert.equal(await readFile(seed, 'utf8'), '[]\n');
  assert.deepEqual((await readdir(root)).sort(), ['reports', 'seed.json']);
  assert.deepEqual((await readdir(output)).sort(), ['content-report.json', 'content-report.md']);
});

test('la CLI lit le runtime prioritaire, produit les diagnostics puis retourne le code 2', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-content-report-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'seed.json'), runtime = join(root, 'runtime');
  await writeFile(seed, '[]\n');
  await mkdir(runtime);
  const body = JSON.stringify([{id: 'report-invalid', status: 'published'}]);
  await writeFile(join(runtime, 'entries.json'), body);
  let exitCode = 0;
  const report = await main(['--output-dir', join(root, 'reports'), '--seed', seed, '--runtime-dir', runtime, '--as-of', asOf],
    {...quiet, setExitCode: code => { exitCode = code; }});
  assert.equal(report.totals.records, 1);
  assert.equal(report.totals.publicEligible, 0);
  assert.equal(exitCode, 2);
  assert.equal(await readFile(join(runtime, 'entries.json'), 'utf8'), body);
});

test('la CLI refuse public/dist, leurs alias symboliques, et toute collision avec la source', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-content-report-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'content-report.json');
  await writeFile(seed, '[]\n');
  await mkdir(join(root, 'public'));
  await symlink(join(root, 'public'), join(root, 'alias'));
  for (const output of [join(root, 'public'), join(root, 'dist', 'reports'), join(root, 'alias', 'nested')]) {
    await assert.rejects(main(['--output-dir', output, '--seed', seed], quiet), /public\/ ou dist\//);
  }
  await assert.rejects(main(['--output-dir', root, '--seed', seed], quiet), /remplacer une source/);
  assert.equal(await readFile(seed, 'utf8'), '[]\n');
});

test('la date de référence rejette les dates impossibles pour éviter un audit ambigu', () => {
  for (const date of ['2026-02-30', '2026-13-01', '19/10/2026', 'invalid', '2026-10-19T00:00:00Z']) {
    assert.throws(() => createContentReport([], {asOf: date}), /date réelle/);
  }
});

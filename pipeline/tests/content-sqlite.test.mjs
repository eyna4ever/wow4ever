import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtemp, readFile, readdir, rm, symlink, writeFile, mkdir, stat} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {digest, transitionRecord} from '../lib/documentary.mjs';
import {exportContentSQLite, main} from '../scripts/export-content-sqlite.mjs';

// Synthetic validation fixtures only; never imported into documentary seed/runtime.
const now = '2026-10-19T12:00:00.000Z';
const fixture = (id = 'sqlite-draft') => ({id, title: {fr: 'Essai « lié »', en: "Test ' linked"},
  description: {fr: 'Brouillon de test, pas une fiche de jeu.', en: 'Synthetic draft, not game content.'},
  category: 'guides', subcategory: 'test', status: 'draft', gameVersion: 'test-only', version: 1,
  identityConfirmed: false, updatedAt: now, sources: [{url: 'https://example.org/reference', title: 'Source de test',
    gameVersion: 'test-only', accessedAt: now, license: 'synthetic-test-only'}], relations: [],
  history: [{at: now, actor: 'PRIVATE-TEST-AUTHOR', note: 'Synthetic fixture only', version: 1}]});
const quiet = {log: () => {}};

async function store(t, records = []) {
  const root = await mkdtemp(join(tmpdir(), 'wiki-sqlite-export-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seedPath = join(root, 'seed.json'), runtimeDir = join(root, 'runtime'), outputPath = join(root, 'exports', 'wiki.sqlite');
  const source = `${JSON.stringify(records, null, 2)}\n`;
  await writeFile(seedPath, source);
  return {root, seedPath, runtimeDir, outputPath, source};
}

function inspect(path, script) {
  const result = spawnSync('python3', ['-c', `import sqlite3,json,sys\ncon=sqlite3.connect(sys.argv[1])\ncon.execute('PRAGMA foreign_keys=ON')\n${script}\ncon.close()`, path], {encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 10_000});
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

test('une base vide possède le schéma, une empreinte et une intégrité vérifiée', async t => {
  const settings = await store(t);
  const receipt = await exportContentSQLite(settings);
  assert.equal(receipt.records, 0);
  assert.equal(receipt.integrityCheck, 'ok');
  assert.equal(receipt.foreignKeyViolations, 0);
  const result = inspect(settings.outputPath, `print(json.dumps({
    'tables':[row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")],
    'integrity':con.execute('PRAGMA integrity_check').fetchall(),
    'foreign_keys':con.execute('PRAGMA foreign_key_check').fetchall(),
    'checksum':con.execute("SELECT value FROM metadata WHERE key='dataset_checksum'").fetchone()[0]
  }))`);
  assert.deepEqual(result.tables, ['metadata', 'wiki_entries', 'wiki_relations', 'wiki_revisions', 'wiki_sources']);
  assert.deepEqual(result.integrity, [['ok']]);
  assert.deepEqual(result.foreign_keys, []);
  assert.equal(result.checksum, digest([]));
  assert.equal((await stat(settings.outputPath)).mode & 0o777, 0o600);
  assert.equal(await readFile(settings.seedPath, 'utf8'), settings.source);
});

test('les brouillons, sources, relations et événements historiques sont préservés sans attestation créée', async t => {
  const first = fixture('sqlite-first'), second = fixture('sqlite-second');
  first.relations = [second.id];
  first.sources.push({url: 'https://example.org/secondary', accessedAt: now, license: 'test-only'});
  second.history.push({at: now, actor: 'PRIVATE-SECOND-AUTHOR', note: "Event ' original"});
  const records = [first, second], before = structuredClone(records);
  const settings = await store(t, records);
  const receipt = await exportContentSQLite(settings);
  assert.equal(receipt.records, 2);
  assert.equal(receipt.sources, 3);
  assert.equal(receipt.relations, 1);
  assert.equal(receipt.revisions, 3);
  const result = inspect(settings.outputPath, `print(json.dumps({
    'records':[json.loads(row[0]) for row in con.execute('SELECT full_record_json FROM wiki_entries ORDER BY id')],
    'states':con.execute('SELECT status,identity_confirmed,title_fr,title_en FROM wiki_entries ORDER BY id').fetchall(),
    'sources':con.execute('SELECT url,game_version,license,accessed_at,title FROM wiki_sources ORDER BY id').fetchall(),
    'relations':con.execute('SELECT from_id,to_id FROM wiki_relations').fetchall(),
    'revisions':[json.loads(row[0]) for row in con.execute('SELECT snapshotjson FROM wiki_revisions ORDER BY id')],
    'policy':con.execute("SELECT value FROM metadata WHERE key='revision_payload'").fetchone()[0]
  }))`);
  assert.deepEqual(result.records, records);
  assert.deepEqual(result.states.map(row => row.slice(0, 2)), [['draft', 0], ['draft', 0]]);
  assert.equal(result.states[0][2], first.title.fr);
  assert.equal(result.states[0][3], first.title.en);
  assert.deepEqual(result.sources[0], ['https://example.org/reference', 'test-only', 'synthetic-test-only', now, 'Source de test']);
  assert.deepEqual(result.sources[1], ['https://example.org/secondary', null, 'test-only', now, null]);
  assert.deepEqual(result.relations, [['sqlite-first', 'sqlite-second']]);
  assert.deepEqual(result.revisions, [...first.history, ...second.history]);
  assert.match(result.policy, /history-event-only/);
  assert.deepEqual(records, before);
  assert.equal(await readFile(settings.seedPath, 'utf8'), settings.source);
  assert.deepEqual((await readdir(join(settings.root, 'exports'))), ['wiki.sqlite']);
});

test('SQLite refuse une relation absente lorsque les clés étrangères sont activées', async t => {
  const settings = await store(t, [fixture()]);
  await exportContentSQLite(settings);
  const result = inspect(settings.outputPath, `blocked=False
try:
    con.execute("INSERT INTO wiki_relations(from_id,to_id) VALUES ('sqlite-draft','missing-target')")
except sqlite3.IntegrityError:
    blocked=True
print(json.dumps({'blocked':blocked,'foreign_keys':con.execute('PRAGMA foreign_key_check').fetchall()}))`);
  assert.equal(result.blocked, true);
  assert.deepEqual(result.foreign_keys, []);
});

test('tous les statuts locaux restent inchangés, y compris les validations humaines déjà existantes', async t => {
  const approval = {actor: 'PRIVATE-REVIEWER', note: 'Synthetic test approval', now, humanReview: true,
    identity: true, rights: true, translations: true, publish: true};
  const records = [fixture('sqlite-local-draft')];
  for (const [index, target] of ['review', 'verified', 'published'].entries()) {
    let current = [fixture(`sqlite-state-${index}`)];
    for (const [action, status] of [['submit', 'review'], ['approve', 'verified'], ['publish', 'published']]) {
      current = transitionRecord(current, current[0].id, action, approval).records;
      if (target === status) break;
    }
    records.push(current[0]);
  }
  const settings = await store(t, records);
  await exportContentSQLite(settings);
  const result = inspect(settings.outputPath, "print(json.dumps(con.execute('SELECT status,identity_confirmed FROM wiki_entries ORDER BY id').fetchall()))");
  assert.deepEqual(result, [['draft', 0], ['review', 0], ['verified', 1], ['published', 1]]);
  assert.equal(await readFile(settings.seedPath, 'utf8'), settings.source);
});

test('des données invalides préservent le fichier existant et ne créent aucun répertoire de sortie', async t => {
  const invalid = fixture();
  invalid.relations = ['missing-target'];
  const settings = await store(t, [invalid]);
  await assert.rejects(exportContentSQLite(settings), /Données invalides/);
  assert.deepEqual(await readdir(settings.root), ['seed.json']);
  const existing = join(settings.root, 'existing.sqlite');
  await writeFile(existing, 'previous-database');
  await assert.rejects(exportContentSQLite({...settings, outputPath: existing}), /Données invalides/);
  assert.equal(await readFile(existing, 'utf8'), 'previous-database');
  await writeFile(settings.seedPath, '{"not":"an array"}');
  await assert.rejects(exportContentSQLite({...settings, outputPath: existing}), /Données invalides/);
  assert.equal(await readFile(existing, 'utf8'), 'previous-database');
});

test('un échec Python ne remplace jamais la base existante et nettoie les temporaires', async t => {
  const settings = await store(t, [fixture()]);
  await mkdir(join(settings.root, 'exports'));
  await writeFile(settings.outputPath, 'previous-database');
  await assert.rejects(exportContentSQLite(settings, {runPython: () => ({status: 1, stderr: 'PRIVATE-DATA'})}),
    error => /Échec de l’export SQLite/.test(error.message) && !error.message.includes('PRIVATE-DATA'));
  assert.equal(await readFile(settings.outputPath, 'utf8'), 'previous-database');
  assert.deepEqual(await readdir(join(settings.root, 'exports')), ['wiki.sqlite']);
  await assert.rejects(exportContentSQLite(settings, {runPython: () => ({status: 0, stdout: '{"integrityCheck":"ok"}'})}), /Contrôles SQLite incomplets/);
  assert.equal(await readFile(settings.outputPath, 'utf8'), 'previous-database');
  assert.deepEqual(await readdir(join(settings.root, 'exports')), ['wiki.sqlite']);
});

test('public/dist, liens symboliques et collisions avec les sources sont refusés', async t => {
  const settings = await store(t, [fixture()]);
  await mkdir(join(settings.root, 'private'));
  await symlink(join(settings.root, 'private'), join(settings.root, 'alias'));
  const destination = join(settings.root, 'linked.sqlite');
  await symlink(settings.seedPath, destination);
  for (const outputPath of [join(settings.root, 'public', 'wiki.sqlite'), join(settings.root, 'dist', 'wiki.sqlite')]) {
    await assert.rejects(exportContentSQLite({...settings, outputPath}), /public\/ ou dist\//);
  }
  for (const outputPath of [destination, join(settings.root, 'alias', 'wiki.sqlite')]) {
    await assert.rejects(exportContentSQLite({...settings, outputPath}), /liens symboliques/);
  }
  await assert.rejects(exportContentSQLite({...settings, outputPath: settings.seedPath}), /remplacer une source/);
  await mkdir(settings.runtimeDir);
  const runtimeSource = join(settings.runtimeDir, 'entries.json');
  await writeFile(runtimeSource, settings.source);
  await assert.rejects(exportContentSQLite({...settings, outputPath: runtimeSource}), /remplacer une source/);
  assert.equal(await readFile(settings.seedPath, 'utf8'), settings.source);
  assert.equal(await readFile(runtimeSource, 'utf8'), settings.source);
});

test('la CLI exige --output et privilégie le runtime sans modifier les entrées', async t => {
  const settings = await store(t);
  await assert.rejects(main([], quiet), /output explicite/);
  await mkdir(settings.runtimeDir);
  const records = [fixture()];
  const runtimeSource = JSON.stringify(records);
  await writeFile(join(settings.runtimeDir, 'entries.json'), runtimeSource);
  const receipt = await main(['--output', settings.outputPath, '--runtime-dir', settings.runtimeDir, '--seed', settings.seedPath], quiet);
  assert.equal(receipt.records, 1);
  assert.equal(receipt.checksum, digest(records));
  assert.equal(await readFile(join(settings.runtimeDir, 'entries.json'), 'utf8'), runtimeSource);
  assert.equal(await readFile(settings.seedPath, 'utf8'), settings.source);
});

test('une nouvelle exportation remplace atomiquement la précédente après validation complète', async t => {
  const settings = await store(t);
  await exportContentSQLite(settings);
  await writeFile(settings.seedPath, JSON.stringify([fixture()]));
  const receipt = await exportContentSQLite(settings);
  assert.equal(receipt.records, 1);
  assert.equal(inspect(settings.outputPath, "print(json.dumps(con.execute('SELECT COUNT(*) FROM wiki_entries').fetchone()[0]))"), 1);
  assert.deepEqual(await readdir(join(settings.root, 'exports')), ['wiki.sqlite']);
});

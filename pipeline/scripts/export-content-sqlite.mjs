import {spawnSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {lstat, mkdir, open, realpath, rename, rm} from 'node:fs/promises';
import {basename, dirname, join, parse, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditDataset, digest, loadDataset, parseArgs} from '../lib/documentary.mjs';

// Standard library only. The dataset is transferred on stdin, never in argv.
const PYTHON_EXPORT = String.raw`
import json, sqlite3, sys

payload = json.load(sys.stdin)
records = payload['records']
connection = sqlite3.connect(payload['temporaryPath'])
try:
    connection.execute('PRAGMA foreign_keys = ON')
    connection.execute('PRAGMA journal_mode = DELETE')
    connection.execute('PRAGMA synchronous = FULL')
    if connection.execute('PRAGMA foreign_keys').fetchone()[0] != 1:
        raise RuntimeError('foreign keys unavailable')
    connection.executescript('''
        BEGIN IMMEDIATE;
        PRAGMA user_version = 1;
        CREATE TABLE wiki_entries (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            game_version TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('draft','review','verified','published')),
            version INTEGER NOT NULL CHECK(version > 0),
            identity_confirmed INTEGER NOT NULL CHECK(identity_confirmed IN (0,1)),
            title_fr TEXT NOT NULL, title_en TEXT NOT NULL,
            description_fr TEXT NOT NULL, description_en TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            full_record_json TEXT NOT NULL CHECK(json_valid(full_record_json))
        );
        CREATE TABLE wiki_sources (
            id INTEGER PRIMARY KEY,
            entry_id TEXT NOT NULL REFERENCES wiki_entries(id) ON DELETE CASCADE,
            ordinal INTEGER NOT NULL CHECK(ordinal >= 0),
            url TEXT NOT NULL,
            game_version TEXT,
            license TEXT NOT NULL,
            accessed_at TEXT NOT NULL,
            title TEXT,
            UNIQUE(entry_id, ordinal)
        );
        CREATE TABLE wiki_relations (
            from_id TEXT NOT NULL REFERENCES wiki_entries(id) ON DELETE CASCADE,
            to_id TEXT NOT NULL REFERENCES wiki_entries(id) ON DELETE CASCADE,
            PRIMARY KEY(from_id, to_id),
            CHECK(from_id <> to_id)
        );
        CREATE TABLE wiki_revisions (
            id INTEGER PRIMARY KEY,
            entry_id TEXT NOT NULL REFERENCES wiki_entries(id) ON DELETE CASCADE,
            ordinal INTEGER NOT NULL CHECK(ordinal >= 0),
            version INTEGER CHECK(version IS NULL OR version > 0),
            snapshotjson TEXT NOT NULL CHECK(json_valid(snapshotjson)),
            actor TEXT NOT NULL,
            at TEXT NOT NULL,
            UNIQUE(entry_id, ordinal)
        );
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE INDEX wiki_entries_category_status ON wiki_entries(category,status);
        CREATE INDEX wiki_sources_entry ON wiki_sources(entry_id);
        CREATE INDEX wiki_relations_target ON wiki_relations(to_id);
        CREATE INDEX wiki_revisions_entry ON wiki_revisions(entry_id);
    ''')
    encode = lambda value: json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    # Every entry exists before any relation is inserted, including forward references.
    connection.executemany('''INSERT INTO wiki_entries
        (id,category,subcategory,game_version,status,version,identity_confirmed,
         title_fr,title_en,description_fr,description_en,updated_at,full_record_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', [
        (entry['id'], entry['category'], entry['subcategory'], entry['gameVersion'], entry['status'],
         entry['version'], int(entry.get('identityConfirmed', False)), entry['title']['fr'], entry['title']['en'],
         entry['description']['fr'], entry['description']['en'], entry['updatedAt'], encode(entry))
        for entry in records
    ])
    source_count = relation_count = revision_count = 0
    for entry in records:
        for ordinal, source in enumerate(entry['sources']):
            connection.execute('''INSERT INTO wiki_sources
                (entry_id,ordinal,url,game_version,license,accessed_at,title) VALUES (?,?,?,?,?,?,?)''',
                (entry['id'], ordinal, source['url'], source.get('gameVersion'), source['license'],
                 source['accessedAt'], source.get('title')))
            source_count += 1
        for target in entry['relations']:
            connection.execute('INSERT INTO wiki_relations(from_id,to_id) VALUES (?,?)', (entry['id'], target))
            relation_count += 1
        for ordinal, revision in enumerate(entry['history']):
            # These are the actual recorded history events, not fabricated old document snapshots.
            connection.execute('''INSERT INTO wiki_revisions
                (entry_id,ordinal,version,snapshotjson,actor,at) VALUES (?,?,?,?,?,?)''',
                (entry['id'], ordinal, revision.get('version'), encode(revision), revision['actor'], revision['at']))
            revision_count += 1
    connection.executemany('INSERT INTO metadata(key,value) VALUES (?,?)', [
        ('format', '1'), ('dataset_checksum', payload['checksum']),
        ('scope', 'private-editorial-export'),
        ('revision_payload', 'history-event-only; historical full-document snapshots are not available'),
        ('approval_policy', 'Existing states copied verbatim; no identity or human approval created')
    ])
    connection.commit()
    integrity = connection.execute('PRAGMA integrity_check').fetchall()
    foreign_keys = connection.execute('PRAGMA foreign_key_check').fetchall()
    if integrity != [('ok',)] or foreign_keys:
        raise RuntimeError('SQLite integrity or foreign-key check failed')
    print(json.dumps({'format': 1, 'checksum': payload['checksum'], 'records': len(records),
        'sources': source_count, 'relations': relation_count, 'revisions': revision_count,
        'integrityCheck': 'ok', 'foreignKeyViolations': 0}))
except BaseException:
    connection.rollback()
    raise
finally:
    connection.close()
`;

async function physicalPath(path) {
  let parent = resolve(path);
  const suffix = [];
  while (true) {
    try { return join(await realpath(parent), ...suffix); }
    catch (error) {
      if (error.code !== 'ENOENT' || dirname(parent) === parent) throw error;
      suffix.unshift(basename(parent));
      parent = dirname(parent);
    }
  }
}

async function assertSafeOutput(outputPath, inputs) {
  const output = resolve(outputPath);
  const parts = output.slice(parse(output).root.length).split(sep);
  if (parts.some(part => ['public', 'dist'].includes(part))) {
    throw new Error('La base éditoriale privée ne peut pas être exportée dans public/ ou dist/.');
  }
  let current = parse(output).root;
  for (const part of parts) {
    current = join(current, part);
    try {
      const info = await lstat(current);
      if (info.isSymbolicLink()) throw new Error('Les liens symboliques sont interdits dans le chemin de sortie.');
      if (current === output && !info.isFile()) throw new Error('La sortie doit désigner un fichier SQLite.');
    } catch (error) { if (error.code === 'ENOENT') break; throw error; }
  }
  const destination = await physicalPath(output);
  for (const input of inputs) {
    if (destination === await physicalPath(input)) throw new Error('La sortie ne doit pas remplacer une source de données.');
  }
  return output;
}

export async function exportContentSQLite({outputPath, runtimeDir = resolve('runtime'), seedPath = resolve('data/entries.json')},
  {runPython = spawnSync} = {}) {
  if (typeof outputPath !== 'string' || !outputPath.trim()) throw new Error('--output explicite est obligatoire.');
  runtimeDir = resolve(runtimeDir);
  seedPath = resolve(seedPath);
  const inputs = [seedPath, join(runtimeDir, 'entries.json')];
  const output = await assertSafeOutput(outputPath, inputs);
  const records = await loadDataset({runtimeDir, seedPath});
  const audit = auditDataset(records);
  if (audit.errors.length) throw new Error(`Données invalides : export refusé (${audit.errors.length} diagnostic(s)). Exécuter scripts/check-data.mjs.`);
  const checksum = digest(records);
  // No directory or existing output is changed until the input has passed validation.
  await mkdir(dirname(output), {recursive: true, mode: 0o700});
  await assertSafeOutput(output, inputs);
  const temporary = join(dirname(output), `.${basename(output)}.${randomUUID()}.tmp`);
  const inputPath = `${temporary}.stdin`;
  let inputHandle;
  try {
    const handle = await open(temporary, 'wx', 0o600);
    await handle.close();
    // A regular stdin descriptor also works in restricted environments where
    // Node's socket-backed input/shutdown is forbidden. Unlink it immediately;
    // the private payload remains reachable only through this open descriptor.
    inputHandle = await open(inputPath, 'wx+', 0o600);
    await rm(inputPath);
    const payload = Buffer.from(JSON.stringify({records, checksum, temporaryPath: temporary}));
    let offset = 0;
    while (offset < payload.length) {
      // Positional writes leave the descriptor's read offset at zero for Python.
      const {bytesWritten} = await inputHandle.write(payload, offset, payload.length - offset, offset);
      if (!bytesWritten) throw new Error('Transmission du contenu vers stdin impossible.');
      offset += bytesWritten;
    }
    const result = runPython('python3', ['-c', PYTHON_EXPORT], {
      stdio: [inputHandle.fd, 'pipe', 'pipe'],
      encoding: 'utf8', maxBuffer: 1_000_000, timeout: 30_000, windowsHide: true
    });
    await inputHandle.close();
    inputHandle = undefined;
    if (result.error || result.status !== 0) {
      // Do not echo stderr or the stdin payload: they may contain editorial data.
      throw new Error('Échec de l’export SQLite par Python 3 ; le fichier existant a été conservé.');
    }
    let receipt;
    try { receipt = JSON.parse(result.stdout); }
    catch { throw new Error('Reçu de contrôle SQLite invalide ; le fichier existant a été conservé.'); }
    if (receipt.checksum !== checksum || receipt.records !== records.length
      || receipt.integrityCheck !== 'ok' || receipt.foreignKeyViolations !== 0) {
      throw new Error('Contrôles SQLite incomplets ; le fichier existant a été conservé.');
    }
    const durable = await open(temporary, 'r');
    try { await durable.sync(); } finally { await durable.close(); }
    await assertSafeOutput(output, inputs);
    await rename(temporary, output);
    return {outputPath: output, ...receipt};
  } finally {
    if (inputHandle) await inputHandle.close();
    await rm(inputPath, {force: true});
    for (const suffix of ['', '-journal', '-wal', '-shm']) await rm(`${temporary}${suffix}`, {force: true});
  }
}

export async function main(argv = process.argv.slice(2), {log = console.log, runPython = spawnSync} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['output', 'runtime-dir', 'seed'], flags: ['help']});
  if (options.help) {
    log('Usage : node scripts/export-content-sqlite.mjs --output CHEMIN_PRIVE/base.sqlite [--runtime-dir runtime] [--seed data/entries.json]\nExport local en lecture seule. Python 3 et son module sqlite3 standard sont requis. Ne pas publier cette base éditoriale.');
    return;
  }
  if (positional.length || !options.output) throw new Error('--output explicite est obligatoire ; utiliser --help.');
  const receipt = await exportContentSQLite({outputPath: options.output,
    runtimeDir: resolve(options['runtime-dir'] ?? 'runtime'), seedPath: resolve(options.seed ?? 'data/entries.json')}, {runPython});
  log(JSON.stringify(receipt, null, 2));
  return receipt;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Export documentaire impossible : ${error.message}`); process.exitCode = 1; });
}

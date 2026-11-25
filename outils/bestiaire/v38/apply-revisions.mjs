import {readdir, readFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDataset, reviseRecord, withDatasetLock, commitDataset, auditDataset, validate} from '../test-tree-v38/pipeline/lib/documentary.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const tree = resolve(here, '../test-tree-v38/pipeline');
const runtime = resolve(tree, 'runtime');
const revDir = resolve(here, 'revisions');
const NOTE = 't359u : retirer « à confirmer » des faits trouvés dans les fichiers du jeu (client 1.60.1.70862). L’obtention « inconnu », les zones non indiquées et les sources sans tampon de build restent à confirmer. Pas une mise en ligne.';

const dry = process.argv.includes('--dry-run');
const files = (await readdir(revDir)).filter(f => f.endsWith('.json')).sort();

if (process.argv.includes('--validate-only')) {
  const before = await loadDataset({runtimeDir: runtime});
  const audit = auditDataset(before);
  console.log('current dataset', before.length, 'audit errors', audit.errors.length);
  if (audit.errors.length) console.log(JSON.stringify(audit.errors.slice(0, 5), null, 2));
  let bad = 0;
  for (const file of files) {
    const incoming = JSON.parse(await readFile(resolve(revDir, file), 'utf8'));
    const errors = validate(incoming);
    if (errors.length) {
      bad++;
      console.log('INVALID', incoming.id, errors.slice(0, 12));
    }
  }
  console.log('incoming invalid', bad, '/', files.length);
  process.exit(bad || audit.errors.length ? 1 : 0);
}

const execute = async () => {
  let records = await loadDataset({runtimeDir: runtime});
  const before = records;
  const reports = [];
  for (const file of files) {
    const incoming = JSON.parse(await readFile(resolve(revDir, file), 'utf8'));
    const result = reviseRecord(records, incoming.id, incoming, {actor: 'Mathieu', note: NOTE});
    records = result.records;
    reports.push(result.report);
    console.log(`revise ${incoming.id} -> v${result.report.version} ${result.report.status}`);
  }
  if (dry) {
    const audit = auditDataset(records);
    console.log('dry-run audit errors', audit.errors.length, 'published', audit.published, 'entries', audit.entries);
    if (audit.errors.length) console.log(JSON.stringify(audit.errors.slice(0, 8), null, 2));
    return;
  }
  const receipt = await commitDataset(runtime, before, records, {
    format: 1,
    operation: 'revise-batch',
    at: new Date().toISOString(),
    actor: 'Mathieu',
    note: NOTE,
    ids: reports.map(r => r.id),
    versions: Object.fromEntries(reports.map(r => [r.id, r.version])),
  });
  console.log('committed', receipt.reportPath);
};

if (dry) await execute();
else await withDatasetLock(runtime, execute);

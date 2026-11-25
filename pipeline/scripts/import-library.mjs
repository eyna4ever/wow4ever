import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readJSON, loadDataset, merge, parseArgs, withDatasetLock, commitDataset, persistReport} from '../lib/documentary.mjs';

export const initialBatches = Object.freeze([
  'data/batches/forever-classes.json',
  'data/batches/forever-world.json',
  'data/batches/forever-systems.json'
]);

/** One validated transaction for the initial library; imported approvals are never trusted. */
export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }, projectRoot = resolve(import.meta.dirname, '..')} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['runtime-dir', 'seed'], flags: ['dry-run', 'help']});
  if (options.help) {
    log('Usage: node scripts/import-library.mjs [--dry-run] [--runtime-dir runtime] [--seed data/entries.json]');
    return;
  }
  if (positional.length) throw new Error('unexpected positional argument');
  const batches = await Promise.all(initialBatches.map(path => readJSON(resolve(projectRoot, path), {maxBytes: 2_000_000})));
  if (batches.some(batch => !Array.isArray(batch))) throw new Error('each source batch must be an array');
  const incoming = batches.flat();
  const runtimeDir = resolve(options['runtime-dir'] ?? resolve(projectRoot, 'runtime'));
  const execute = async () => {
    const before = await loadDataset({runtimeDir, seedPath: resolve(options.seed ?? resolve(projectRoot, 'data/entries.json'))});
    const {records, report} = merge(before, incoming);
    report.sourceBatches = [...initialBatches];
    // An initial library import is atomic across all batches; reject any invalid/conflicting source.
    if (report.invalid.length || report.conflicts.length) {
      log(JSON.stringify({...report, committed: false}, null, 2));
      setExitCode(2);
      return;
    }
    const changed = report.inserted.length > 0;
    const result = options['dry-run']
      ? {...report, committed: false, dryRun: true}
      : changed
        ? await commitDataset(runtimeDir, before, records, report)
        : await persistReport(runtimeDir, {...report, committed: false, unchanged: true});
    log(JSON.stringify(result, null, 2));
  };
  if (options['dry-run']) await execute();
  else await withDatasetLock(runtimeDir, execute);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Library import failed: ${error.message}`); process.exitCode = 1; });
}

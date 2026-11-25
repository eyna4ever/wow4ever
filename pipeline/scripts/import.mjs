import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {loadDataset, merge, limits, parseArgs, readJSON, withDatasetLock, commitDataset, persistReport} from '../lib/documentary.mjs';

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {
    values: ['runtime-dir', 'seed', 'max-records', 'max-bytes', 'max-total-records', 'max-sources', 'stale-days'], flags: ['dry-run', 'help']
  });
  if (options.help) {
    log('Usage: node scripts/import.mjs batch.json [--dry-run] [--runtime-dir runtime] [--seed data/entries.json] [--max-records 100] [--max-bytes 2000000] [--max-total-records 10000] [--max-sources 20] [--stale-days 180]');
    return;
  }
  if (positional.length !== 1) throw new Error('one authorized, local JSON batch is required; use --help');
  const runtimeDir = resolve(options['runtime-dir'] ?? 'runtime');
  const settings = {};
  for (const key of ['maxRecords', 'maxBytes', 'maxTotalRecords', 'maxSources', 'staleDays']) {
    const flag = key.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`);
    settings[key] = options[flag] === undefined ? limits[key] : Number(options[flag]);
    if (!Number.isSafeInteger(settings[key]) || settings[key] < 0) throw new Error(`--${flag} requires a non-negative integer`);
  }
  const incoming = await readJSON(resolve(positional[0]), {maxBytes: settings.maxBytes});
  const execute = async () => {
    const before = await loadDataset({runtimeDir, seedPath: resolve(options.seed ?? 'data/entries.json')});
    const result = merge(before, incoming, settings);
    const changed = result.report.inserted.length > 0;
    let report = changed && !options['dry-run']
      ? await commitDataset(runtimeDir, before, result.records, result.report)
      : {...result.report, committed: false, dryRun: Boolean(options['dry-run']), unchanged: !changed};
    if (!changed && !options['dry-run']) report = await persistReport(runtimeDir, report);
    log(JSON.stringify(report, null, 2));
    if (report.invalid.length || report.conflicts.length || report.quarantined?.length) setExitCode(2);
  };
  if (options['dry-run']) await execute();
  else await withDatasetLock(runtimeDir, execute);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Import failed: ${error.message}`); process.exitCode = 1; });
}

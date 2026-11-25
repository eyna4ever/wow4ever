import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {digest, loadDataset, parseArgs, readJSON, decodeBackup, withDatasetLock, commitDataset} from '../lib/documentary.mjs';

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['runtime-dir', 'seed', 'actor', 'note'], flags: ['dry-run', 'help']});
  if (options.help) { log('Usage: node scripts/restore.mjs runtime/backups/BACKUP.json --actor "Human name" --note "Reason" [--runtime-dir runtime] [--seed data/entries.json] [--dry-run]'); return; }
  if (positional.length !== 1) throw new Error('one checksum-protected backup is required; use --help');
  if (!options.actor?.trim() || !options.note?.trim()) throw new Error('--actor and --note are required');
  const backupPath = resolve(positional[0]);
  const restored = decodeBackup(await readJSON(backupPath));
  const runtimeDir = resolve(options['runtime-dir'] ?? 'runtime');
  const execute = async () => {
    const before = await loadDataset({runtimeDir, seedPath: resolve(options.seed ?? 'data/entries.json')});
    const report = {format: 1, operation: 'restore', at: new Date().toISOString(), sourceBackup: backupPath, actor: options.actor.trim(), note: options.note.trim(), restoredEntries: restored.length};
    const unchanged = digest(before) === digest(restored);
    const receipt = options['dry-run'] || unchanged ? {...report, dryRun: Boolean(options['dry-run']), committed: false, unchanged} : await commitDataset(runtimeDir, before, restored, report);
    log(JSON.stringify(receipt, null, 2));
  };
  if (options['dry-run']) await execute();
  else await withDatasetLock(runtimeDir, execute);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Restore failed: ${error.message}`); process.exitCode = 1; });
}

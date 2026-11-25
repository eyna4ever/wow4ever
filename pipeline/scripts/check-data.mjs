import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {auditDataset, parseArgs, readJSON} from '../lib/documentary.mjs';

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {flags: ['help']});
  if (options.help) { log('Usage: node scripts/check-data.mjs [data/entries.json | runtime/entries.json]'); return; }
  if (positional.length > 1) throw new Error('at most one dataset path is accepted');
  const path = resolve(positional[0] ?? 'data/entries.json');
  const records = await readJSON(path);
  const audit = auditDataset(records);
  log(JSON.stringify({path, ...audit}, null, 2));
  if (audit.errors.length) setExitCode(1);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Data check failed: ${error.message}`); process.exitCode = 1; });
}

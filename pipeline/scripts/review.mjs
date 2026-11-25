import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {auditDataset, loadDataset, parseArgs, transitionRecord, reviseRecord, readJSON, withDatasetLock, commitDataset} from '../lib/documentary.mjs';

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {
    values: ['runtime-dir', 'seed', 'actor', 'note'],
    flags: ['help', 'dry-run', 'confirm-human-review', 'confirm-identity', 'confirm-rights', 'confirm-translations', 'confirm-publish']
  });
  if (options.help) {
    log('Usage: node scripts/review.mjs preview|submit|approve|publish|reject ID | revise ID revision.json [--actor "Human name"] [--note "Decision"] [--runtime-dir runtime] [--seed data/entries.json] [--dry-run]\napprove requires --confirm-human-review --confirm-identity --confirm-rights --confirm-translations.\npublish requires --confirm-publish. preview is read-only and prints the complete document and integrity audit.');
    return;
  }
  if (positional.length !== (positional[0] === 'revise' ? 3 : 2)) throw new Error('an action and an entry ID are required; use --help');
  const [action, id] = positional;
  if (!['preview', 'submit', 'approve', 'publish', 'reject', 'revise'].includes(action)) throw new Error('unknown action');
  const runtimeDir = resolve(options['runtime-dir'] ?? 'runtime');
  const execute = async () => {
    const before = await loadDataset({runtimeDir, seedPath: resolve(options.seed ?? 'data/entries.json')});
    if (action === 'preview') {
      const audit = auditDataset(before), entry = Array.isArray(before) ? before.find(entry => entry?.id === id) : null;
      if (!entry) throw new Error('entry not found');
      log(JSON.stringify({entry, audit}, null, 2));
      if (audit.errors.length) setExitCode(1);
      return;
    }
    const decision = {
      actor: options.actor, note: options.note,
      humanReview: options['confirm-human-review'], identity: options['confirm-identity'],
      rights: options['confirm-rights'], translations: options['confirm-translations'], publish: options['confirm-publish']
    };
    const result = action === 'revise' ? reviseRecord(before, id, await readJSON(resolve(positional[2]), {maxBytes: 2_000_000}), decision) : transitionRecord(before, id, action, decision);
    const receipt = options['dry-run'] ? {...result.report, committed: false, dryRun: true} : await commitDataset(runtimeDir, before, result.records, result.report);
    log(JSON.stringify(receipt, null, 2));
  };
  if (action === 'preview' || options['dry-run']) await execute();
  else await withDatasetLock(runtimeDir, execute);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Review failed: ${error.message}`); process.exitCode = 1; });
}

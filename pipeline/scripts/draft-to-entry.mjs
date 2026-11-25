// v16 — turn routine drafts (Markdown + front matter) into pipeline DRAFT entries (JSON batch for scripts/import.mjs).
// Usage: node scripts/draft-to-entry.mjs /workspace/wow4ever-chatgpt/veille/articles/*.md [--out batch.json]
// Never writes runtime/entries.json; never publishes. See ops/v16/README.md.
import {readFile, writeFile} from 'node:fs/promises';
import {basename, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {draftToEntry} from '../lib/v16/draft.mjs';
import {parseArgs} from '../lib/documentary.mjs';

export async function main(argv = process.argv.slice(2), {log = console.log, error = console.error, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['out'], flags: ['help']});
  if (options.help || !positional.length) { log('Usage: node scripts/draft-to-entry.mjs draft.md [more.md …] [--out batch.json]'); if (!options.help) setExitCode(2); return; }
  const batch = [];
  let failed = false;
  for (const path of positional) {
    const {entry, errors} = draftToEntry(await readFile(resolve(path), 'utf8'), {file: basename(path)});
    if (errors.length) { failed = true; error(`✗ ${path}\n  - ${errors.join('\n  - ')}`); continue; }
    if (batch.some(item => item.id === entry.id)) { failed = true; error(`✗ ${path}: duplicate id ${entry.id}`); continue; }
    batch.push(entry);
    log(`✓ ${path} → ${entry.id} (brouillon, ${entry.sources.length} sources)`);
  }
  if (failed) { setExitCode(1); error('Nothing written: fix the drafts above.'); return; }
  const json = `${JSON.stringify(batch, null, 2)}\n`;
  if (options.out) { await writeFile(resolve(options.out), json); log(`batch written: ${options.out} (${batch.length} draft entries) — next: node scripts/import.mjs ${options.out} --dry-run`); }
  else log(json);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(err => { console.error(`Draft conversion failed: ${err.message}`); process.exitCode = 1; });
}

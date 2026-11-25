// t388u — applique les révisions puis publie les 26 nouvelles fiches + les fiches révisées.
// Usage : node apply-and-publish.mjs <dossier pipeline> --actor <nom> --note-prefix <texte> [--i-have-mathieus-oui]
// Sans --i-have-mathieus-oui, refuse de tourner ailleurs que dans /tmp (aperçu local).
import {readdir, readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const [tree] = process.argv.slice(2);
const arg = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : undefined; };
const actor = arg('--actor'), prefix = arg('--note-prefix');
if (!tree || !actor || !prefix) throw new Error('usage: apply-and-publish.mjs <pipeline> --actor X --note-prefix Y');
if (!process.argv.includes('--i-have-mathieus-oui') && !resolve(tree).startsWith('/tmp/')) throw new Error('hors /tmp : exige --i-have-mathieus-oui');
const {loadDataset, reviseRecord, transitionRecord, withDatasetLock, commitDataset} = await import(resolve(tree, 'lib/documentary.mjs'));
const here = new URL('..', import.meta.url).pathname;
const runtime = resolve(tree, 'runtime');
const newIds = JSON.parse(await readFile(resolve(here, 'import-batches/t388u-nouvelles-fiches.entries.json'), 'utf8')).map(e => e.id);
await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime}); const before = records;
  const revIds = [];
  for (const f of (await readdir(resolve(here, 'revisions'))).sort()) {
    const inc = JSON.parse(await readFile(resolve(here, 'revisions', f), 'utf8'));
    records = reviseRecord(records, inc.id, inc, {actor, note: `${prefix} révision t388u (quêtes de l’index bêta à confirmer, correctif du 14/11).`}).records; revIds.push(inc.id);
  }
  for (const id of [...newIds, ...revIds]) for (const [action, extra] of [['submit', {}], ['approve', {humanReview: true, identity: true, rights: true, translations: true}], ['publish', {publish: true}]])
    records = transitionRecord(records, id, action, {actor, note: `${prefix} ${action} t388u`, ...extra}).records;
  await commitDataset(runtime, before, records, {format: 1, operation: 't388u-apply-publish', at: new Date().toISOString(), actor, note: prefix, ids: [...newIds, ...revIds]});
  console.log('published', records.filter(e => e.status === 'published').length, 'of', records.length);
});

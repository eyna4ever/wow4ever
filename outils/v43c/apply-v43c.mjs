// v43c — publication approuvée par Mathieu : « Oui » t422u (23/11/2026, Europe/Paris) : brouillons veille 18/11, 20/11, 21/11.
// Pipeline (copie de travail sous /tmp) : ajoute la nouvelle actualité Blackmaw Hold (sortie du convertisseur draft-to-entry), puis submit / approve / publish au nom de Mathieu.
// Les MAJ (correctifs 17/19/20 nov., podcast ép. 8) sont appliquées sur l'arbre HTML (même méthode que la v40b), pas ici.
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const [tree, batch] = process.argv.slice(2);
if (!resolve(tree).startsWith('/tmp/')) throw new Error('aperçu de test : le pipeline doit être sous /tmp');
const {loadDataset, merge, transitionRecord, withDatasetLock, commitDataset, auditDataset} = await import(resolve(tree, 'lib/documentary.mjs'));
const runtime = resolve(tree, 'runtime');
const news = JSON.parse(await readFile(resolve(batch), 'utf8'));
const actor = 'Mathieu', who = 't422u Oui de Mathieu (23/11/2026 Europe/Paris)', note = `${who} : v43c — actualité Blackmaw Hold (brouillon veille du 18/11).`;
await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime}); const before = records;
  const r = merge(records, news, {maxRecords: 100, maxBytes: 4_000_000});
  console.log('inserted', r.report.inserted.length, 'invalid', JSON.stringify(r.report.invalid).slice(0, 2000), 'conflicts', r.report.conflicts.length);
  if (r.report.invalid.length || r.report.inserted.length !== news.length) throw new Error('invalid new entries');
  records = r.records;
  for (const id of news.map(e => e.id)) for (const [action, extra] of [['submit', {}], ['approve', {humanReview: true, identity: true, rights: true, translations: true}], ['publish', {publish: true}]])
    records = transitionRecord(records, id, action, {actor, note: `${who} : ${action} v43c`, ...extra}).records;
  const audit = auditDataset(records);
  console.log('audit entries', audit.entries, 'published', audit.published, 'errors', audit.errors.length, JSON.stringify(audit.errors.slice(0, 3)));
  if (audit.errors.length) throw new Error('audit errors');
  await commitDataset(runtime, before, records, {format: 1, operation: 't422u-v43c-publish', at: new Date().toISOString(), actor, note, ids: news.map(e => e.id)});
  console.log('published', records.filter(e => e.status === 'published').length, 'of', records.length);
});

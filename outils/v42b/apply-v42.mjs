// v42 — publication approuvée par Mathieu : « Oui » t408u (17/11/2026 22:45 Europe/Paris), révision préparée en t407u.
// Applique les fiches nouvelles et révisées dans le pipeline (copie de travail sous /tmp), puis submit / approve / publish au nom de Mathieu.
import {readdir, readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const [tree, dir] = process.argv.slice(2);
if (!resolve(tree).startsWith('/tmp/')) throw new Error('aperçu de test : le pipeline doit être sous /tmp');
const {loadDataset, merge, reviseRecord, transitionRecord, withDatasetLock, commitDataset, validate, auditDataset} = await import(resolve(tree, 'lib/documentary.mjs'));
const runtime = resolve(tree, 'runtime');
const files = (await readdir(dir)).sort();
const news = [], revs = [];
for (const f of files) { const e = JSON.parse(await readFile(resolve(dir, f), 'utf8')); (f.startsWith('new-') ? news : revs).push(e); }
// v42 : révisions d’abord, fiches nouvelles en dernier (accueil « Dernières mises à jour »)
const actor = 'Mathieu', who = 't408u Oui de Mathieu (17/11/2026 22:45 Europe/Paris)', note = `${who} : v42 — matériaux, PNJ des zones, Collections v41, réétiquetage « à confirmer » (révision t407u).`;
await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime}); const before = records;
  const r = merge(records, news, {maxRecords: 100, maxBytes: 4_000_000});
  console.log('inserted', r.report.inserted.length, 'invalid', JSON.stringify(r.report.invalid).slice(0, 2000), 'conflicts', r.report.conflicts.length);
  if (r.report.invalid.length) throw new Error('invalid new entries');
  records = r.records;
  for (const inc of revs) {
    const errs = validate({...inc, status: 'draft'}); if (errs.length) throw new Error(`INVALID ${inc.id}: ${errs.slice(0, 6).join(' | ')}`);
    records = reviseRecord(records, inc.id, inc, {actor, note}).records;
  }
  for (const id of [...revs.map(e => e.id), ...news.map(e => e.id)]) for (const [action, extra] of [['submit', {}], ['approve', {humanReview: true, identity: true, rights: true, translations: true}], ['publish', {publish: true}]])
    records = transitionRecord(records, id, action, {actor, note: `${who} : ${action} v42 (t407u)`, ...extra}).records;
  const audit = auditDataset(records);
  console.log('audit entries', audit.entries, 'published', audit.published, 'errors', audit.errors.length, JSON.stringify(audit.errors.slice(0, 3)));
  await commitDataset(runtime, before, records, {format: 1, operation: 't408u-v42-publish', at: new Date().toISOString(), actor, note, ids: [...news, ...revs].map(e => e.id)});
  console.log('published', records.filter(e => e.status === 'published').length, 'of', records.length);
});

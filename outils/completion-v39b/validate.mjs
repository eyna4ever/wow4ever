import {readFile, readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
const T = '/workspace/wowkipedia-v21-elite/ui-v39-test/tree/pipeline';
const {loadDataset, merge, reviseRecord, auditDataset, validate} = await import(`${T}/lib/documentary.mjs`);
const {entryPath} = await import(`${T}/lib/articles.mjs`);
const here = '/workspace/wowkipedia-v21-elite/completion-v39b';
const batch = JSON.parse(await readFile(`${here}/import-batches/t388u-nouvelles-fiches.entries.json`, 'utf8'));
let records = await loadDataset({runtimeDir: `${T}/runtime`});
console.log('before', records.length, 'published', records.filter(e => e.status === 'published').length);
const r = merge(records, batch, {maxRecords: 100, maxBytes: 2_000_000});
console.log('inserted', r.report.inserted.length, 'invalid', JSON.stringify(r.report.invalid).slice(0, 1500), 'conflicts', r.report.conflicts.length, 'downgraded', r.report.downgraded.length);
records = r.records;
for (const f of (await readdir(`${here}/revisions`)).sort()) {
  const inc = JSON.parse(await readFile(`${here}/revisions/${f}`, 'utf8'));
  const errs = validate({...inc, status: 'draft'}); if (errs.length) { console.log('INVALID REV', f, errs.slice(0, 5)); continue; }
  records = reviseRecord(records, inc.id, inc, {actor: 'GrokBot', note: 'dry-run'}).records;
}
const audit = auditDataset(records);
console.log('after', audit.entries, 'published', audit.published, 'errors', audit.errors.length, JSON.stringify(audit.errors.slice(0, 3)));
const paths = new Map(); for (const e of records) for (const l of ['fr', 'en']) { const p = entryPath(e, l); if (paths.has(p)) console.log('PATH COLLISION', p, e.id, paths.get(p)); paths.set(p, e.id); }

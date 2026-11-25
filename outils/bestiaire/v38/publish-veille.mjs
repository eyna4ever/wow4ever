import {readdir, readFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDataset, reviseRecord, transitionRecord, withDatasetLock, commitDataset, validate} from '../test-tree-v38/pipeline/lib/documentary.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const runtime = resolve(here, '../test-tree-v38/pipeline/runtime');
const revDir = resolve(here, 'veille-revisions');
const REVISE_NOTE = 't361u : mise à jour des fiches d’actualité officielles (équilibrage chaman du 12 novembre, correctifs du 13 novembre et remboursement, épisode 7 du podcast, nouvelle « Le prix de l’honneur »). Aucune rumeur non officielle.';
const NOTES = {
  submit: 't361u : relire les mises à jour d’actualité officielles des 13–14 novembre.',
  approve: 't361u Oui (14 novembre 2026) : validation humaine, identité, droits et traductions.',
  publish: 't361u Oui (14 novembre 2026) : republication des fiches d’actualité révisées, d’un seul tenant.',
};

const files = (await readdir(revDir)).filter(f => f.endsWith('.json') && !f.startsWith('_')).sort();

if (process.argv.includes('--validate-only')) {
  let bad = 0;
  for (const file of files) {
    const incoming = JSON.parse(await readFile(resolve(revDir, file), 'utf8'));
    const errors = validate(incoming);
    if (errors.length) {
      bad++;
      console.log('INVALID', incoming.id, errors.slice(0, 20));
    } else console.log('OK', incoming.id);
  }
  process.exit(bad ? 1 : 0);
}

await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime});
  const before = records;
  const ids = [];
  for (const file of files) {
    const incoming = JSON.parse(await readFile(resolve(revDir, file), 'utf8'));
    const result = reviseRecord(records, incoming.id, incoming, {actor: 'Mathieu', note: REVISE_NOTE});
    records = result.records;
    ids.push(incoming.id);
    console.log(`revise ${incoming.id} -> v${result.report.version} ${result.report.status}`);
  }
  for (const id of ids) {
    for (const [action, extra] of [
      ['submit', {}],
      ['approve', {humanReview: true, identity: true, rights: true, translations: true}],
      ['publish', {publish: true}],
    ]) {
      const result = transitionRecord(records, id, action, {actor: 'Mathieu', note: NOTES[action], ...extra});
      records = result.records;
      console.log(`${action} ${id} -> v${result.report.version} ${result.report.status}`);
    }
  }
  const receipt = await commitDataset(runtime, before, records, {
    format: 1, operation: 'publish-veille-news', at: new Date().toISOString(),
    actor: 'Mathieu', note: NOTES.publish, ids,
  });
  const published = records.filter(e => e.status === 'published').length;
  const drafts = records.filter(e => e.status === 'draft').length;
  console.log(`committed ${receipt.reportPath} published=${published} drafts=${drafts} total=${records.length}`);
});

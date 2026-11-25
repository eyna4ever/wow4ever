import {readFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDataset, transitionRecord, withDatasetLock, commitDataset} from '../test-tree-v38/pipeline/lib/documentary.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const tree = resolve(here, '../test-tree-v38/pipeline');
const runtime = resolve(tree, 'runtime');
const ids = (await readFile(resolve(here, 'IDS.txt'), 'utf8')).trim().split(/\n/).filter(Boolean);
const NOTES = {
  submit: 't359u : relire la révision (retrait de « à confirmer » sur les données du client 1.60.1.70862).',
  approve: 't359u Oui (t361u) : validation humaine, identité, droits et traductions.',
  publish: 't359u Oui (t361u, 14 novembre 2026) : republication des fiches révisées, d’un seul tenant.'
};

await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime});
  const before = records;
  for (const id of ids) {
    for (const [action, extra] of [
      ['submit', {}],
      ['approve', {humanReview: true, identity: true, rights: true, translations: true}],
      ['publish', {publish: true}]
    ]) {
      const result = transitionRecord(records, id, action, {actor: 'Mathieu', note: NOTES[action], ...extra});
      records = result.records;
      console.log(`${action} ${id} -> v${result.report.version} ${result.report.status}`);
    }
  }
  const receipt = await commitDataset(runtime, before, records, {
    format: 1, operation: 'publish-batch', at: new Date().toISOString(),
    actor: 'Mathieu', note: NOTES.publish, ids
  });
  const published = records.filter(e => e.status === 'published').length;
  console.log(`committed ${receipt.reportPath} published=${published} total=${records.length}`);
});

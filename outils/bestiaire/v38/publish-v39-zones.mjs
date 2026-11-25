import {readFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDataset, reviseRecord, transitionRecord, withDatasetLock, commitDataset} from '../test-tree-v38/pipeline/lib/documentary.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const tree = resolve(here, '../test-tree-v38/pipeline');
const runtime = resolve(tree, 'runtime');
const stamped = JSON.parse(await readFile(resolve(here, 'v39-zones.stamped.json'), 'utf8'));
const REVISE_IDS = new Set([
  'forever-zone-zephras-isle',
  'forever-zone-shendralas',
  'forever-zone-mount-hyjal',
  'forever-zone-riverglades',
]);
const ALL_IDS = stamped.map(e => e.id);
const REVISE_NOTE = 't361u : ajouter les listes de PNJ du client 1.60.1.70862 aux fiches de zones officielles, en conservant le texte officiel, les slugs et l’historique.';
const NOTES = {
  submit: 't361u : relire les fiches de zones (52) — listes de PNJ tamponnées client 1.60.1.70862, faits officiels inchangés.',
  approve: 't361u Oui (14 novembre 2026) : validation humaine, identité, droits et traductions.',
  publish: 't361u Oui (14 novembre 2026) : publication des fiches de zones, d’un seul tenant.',
};

await withDatasetLock(runtime, async () => {
  let records = await loadDataset({runtimeDir: runtime});
  const before = records;
  for (const incoming of stamped.filter(e => REVISE_IDS.has(e.id))) {
    const result = reviseRecord(records, incoming.id, incoming, {actor: 'Mathieu', note: REVISE_NOTE});
    records = result.records;
    console.log(`revise ${incoming.id} -> v${result.report.version} ${result.report.status}`);
  }
  for (const id of ALL_IDS) {
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
    format: 1, operation: 'publish-v39-zones', at: new Date().toISOString(),
    actor: 'Mathieu', note: NOTES.publish, ids: ALL_IDS,
  });
  const published = records.filter(e => e.status === 'published').length;
  const drafts = records.filter(e => e.status === 'draft').length;
  console.log(`committed ${receipt.reportPath} published=${published} drafts=${drafts} total=${records.length}`);
});

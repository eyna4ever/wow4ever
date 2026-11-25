/**
 * v15 — merged duplicates (decision of Mathieu, 01/11/2026: « Oui évite les doublons dans le futur »).
 * data/merges.json lists entries merged into another one: {retired, into, at, note}.
 * Rule « adresses inchangées »: the address of a merged entry keeps answering with a small static page that
 * sends the reader to the kept entry (renderMoved). Nothing is deleted from the documentary dataset: the merged
 * entry is withdrawn through scripts/review.mjs (reject → draft) and keeps its full history.
 */
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {entryPath} from '../articles.mjs';

export async function loadMerges(projectRoot) {
  try { return JSON.parse(await readFile(resolve(projectRoot, 'data/merges.json'), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return []; throw error; }
}

/**
 * records: full dataset (drafts included); published: public DTOs actually rendered.
 * Returns {stubs: [{path, lang, retired, target, at}], pending: [ids still published]}.
 * Throws when a merge would break an address: unknown ID, kept entry not published, or a page collision.
 */
export function mergeStubs(records, published, merges) {
  if (!Array.isArray(merges)) throw new Error('data/merges.json must be an array');
  const byId = new Map(records.map(entry => [entry.id, entry]));
  const live = new Map(published.map(entry => [entry.id, entry]));
  const taken = new Set(published.flatMap(entry => ['fr', 'en'].map(lang => entryPath(entry, lang))));
  const seen = new Set(), stubs = [], pending = [];
  for (const merge of merges) {
    const {retired, into, at} = merge ?? {};
    if (!byId.has(retired) || !byId.has(into)) throw new Error(`merge ${retired} -> ${into}: unknown entry`);
    if (retired === into || seen.has(retired)) throw new Error(`merge ${retired}: invalid or duplicated`);
    if (merges.some(other => other.retired === into)) throw new Error(`merge ${retired} -> ${into}: chained merge`);
    seen.add(retired);
    if (live.has(retired)) { pending.push(retired); continue; } // not applied yet: the page itself is still published
    const target = live.get(into);
    if (!target) throw new Error(`merge ${retired} -> ${into}: the kept entry is not published, its address would break`);
    for (const lang of ['fr', 'en']) {
      const path = entryPath(byId.get(retired), lang);
      if (taken.has(path)) throw new Error(`merge ${retired}: ${path} is already a published page`);
      taken.add(path);
      stubs.push({path, lang, retired: byId.get(retired), target, at});
    }
  }
  return {stubs, pending};
}

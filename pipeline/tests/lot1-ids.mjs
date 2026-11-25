// V2.1 étape 03 — the 7 lot-1 entries (isolated test environment). Older count/render freezes exclude them so
// the pre-existing catalogue keeps its exact invariants; tests/v21-lot1.test.mjs covers the lot itself.
export const LOT1_IDS = Object.freeze(['forever-legacy-challenges', 'forever-legacy-perks', 'forever-legacy-rewards', 'forever-camp-features', 'forever-professions-overview', 'forever-quest-rewards-expanded', 'forever-questline-gelkis-magram']);
export const isLot1 = entry => LOT1_IDS.includes(entry?.id);
/** 0 (production dataset) or 7 (lot 1 published in the isolated test tree); anything else is a failure. */
export function lot1Published(records) {
  const n = records.filter(entry => isLot1(entry) && entry.status === 'published').length;
  if (n !== 0 && n !== LOT1_IDS.length) throw new Error(`lot 1 partially published: ${n}`);
  return n;
}

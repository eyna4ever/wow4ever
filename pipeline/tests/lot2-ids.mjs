// V2.1 étape 04 — lot 2 « monde » (v33, validé et publié par Mathieu t341u, 2026-11-09) : 4 nouvelles fiches + 9 fiches donjon existantes révisées.
export const LOT2_NEW_IDS = Object.freeze(['forever-reputations-confirmed', 'forever-exploration-named-places', 'forever-creatures-official-notes', 'forever-items-loot-appearances']);
export const LOT2_REVISED_IDS = Object.freeze(['forever-dungeon-hall-of-thanes', 'forever-dungeon-ruins-of-lordaeron', 'forever-dungeon-excavation-site', 'forever-dungeon-city-of-dalaran', 'forever-dungeon-drowned-city', 'forever-dungeon-kroldok-stronghold', 'forever-dungeon-alcaz-prison', 'forever-dungeon-blackmaw-hold', 'forever-dungeon-shapers-terrace']);
export const LOT2_IDS = Object.freeze([...LOT2_NEW_IDS, ...LOT2_REVISED_IDS]);
export const isLot2 = entry => LOT2_IDS.includes(entry?.id);
export const isLot2New = entry => LOT2_NEW_IDS.includes(entry?.id);

/** 0 (jeu de données v32) ou 4 (v33) ; toute autre valeur est une erreur. */
export function lot2NewPublished(records) {
  const n = records.filter(e => isLot2New(e) && e.status === 'published').length;
  if (n !== 0 && n !== LOT2_NEW_IDS.length) throw new Error(`lot 2 partially published: ${n}`);
  return n;
}

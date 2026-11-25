// v10 (contenu-v10) — garde-fous du lot de brouillons « compléter les catégories ».
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readFileSync} from 'node:fs';
import {lot1Published} from './lot1-ids.mjs';
import {isLot2, isLot2New, lot2NewPublished} from './lot2-ids.mjs';

const batch = JSON.parse(await readFile(new URL('../data/batches/forever-v10-contenu-2026-10-30.json', import.meta.url), 'utf8'));
const runtime = JSON.parse(await readFile(new URL('../runtime/entries.json', import.meta.url), 'utf8'));
const byId = new Map(runtime.map(e => [e.id, e]));
const OFFICIAL = /^(news\.blizzard\.com|worldofwarcraft\.blizzard\.com|(us|eu)\.forums\.blizzard\.com)$/;

test('v10 batch: imported as drafts, then published only through the review flow (submit → approve → publish)', () => {
  assert.ok(batch.length >= 20);
  for (const e of batch) {
    assert.equal(e.status, 'draft', e.id);
    assert.notEqual(e.identityConfirmed, true, e.id);
    assert.ok(!('review' in e), e.id);
    const live = byId.get(e.id);
    assert.equal(live?.status, 'published', e.id);
    assert.equal(live.review?.approved, true, e.id);
    assert.equal(live.review?.reviewer, 'Mathieu', e.id);
    // v33 : les 9 donjons révisés par le lot 2 sont réapprouvés par Mathieu (t341u) ; l'approbation du 30/10 reste dans l'historique.
    if (isLot2(e)) assert.ok(live.history.filter(h => h.actor === 'Mathieu' && h.note.startsWith('approve:')).length >= 2, e.id);
    const steps = live.history.map(h => h.note.split(':')[0]);
    for (const step of ['submit', 'approve', 'publish']) assert.ok(steps.includes(step), `${e.id} lacks ${step}`);
  }
});

test('v10 corrections: official French names, revised through review.mjs revise', () => {
  const text = JSON.stringify(runtime.filter(e => e.status === 'published'));
  assert.doesNotMatch(text, /Cité engloutie|Site de fouilles|Bastion de Krol|Bastion des Blackmaw|Façonneur de vents|Haut Ordre|Planélion/);
  for (const id of ['article-forever-raids', 'article-forever-skyborne', 'article-forever-zones', 'forever-dungeon-hall-of-thanes', 'forever-raid-barrow-deeps', 'forever-raid-hyjal-summit']) {
    const e = byId.get(id);
    assert.equal(e.status, 'published', id);
    assert.ok(e.history.some(h => h.note.startsWith('revise:')), `${id} not revised via review.mjs`);
  }
});

test('v10 batch: official Blizzard sources only (no fan wiki), bilingual text', () => {
  for (const e of batch) {
    for (const s of e.sources) assert.match(new URL(s.url).hostname, OFFICIAL, `${e.id}: ${s.url}`);
    for (const k of ['title', 'description']) for (const l of ['fr', 'en']) assert.ok(e[k][l]?.trim(), `${e.id} ${k}.${l}`);
    assert.doesNotMatch(JSON.stringify(e), /wowhead|fandom|talent builder|\bMidnight\b/i, e.id);
  }
});

test('v10 batch: protected drafts and published entries are untouched', () => {
  assert.equal(byId.get('forever-news-beta')?.status, 'draft');
  assert.equal(byId.get('forever-class-priest')?.status, 'published'); // v22: CL3 published (Oui de Mathieu)
  const ids = new Set(batch.map(e => e.id));
  for (const id of ['forever-news-beta', 'forever-class-priest', 'forever-news-portal-room']) assert.ok(!ids.has(id));
  // v15: minus the duplicates already withdrawn by the merge (data/merges.json), never AC2/CL3.
  const merges = JSON.parse(readFileSync(new URL('../data/merges.json', import.meta.url), 'utf8'));
  const applied = merges.filter(m => byId.get(m.retired)?.status !== 'published').length;
  const v17 = runtime.filter(e => e.id.startsWith('guide-debutant-') && e.status === 'published' && e.review?.reviewer === 'Mathieu').length; // v17 guides (t255u)
  assert.equal(runtime.filter(e => e.status === 'published').length, 81 - applied + v17 + 9 + lot1Published(runtime) + lot2NewPublished(runtime) + 26 + 48 + 26); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ; // v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; v33: + lot 2 ; lot 1 ; v31: +2 news ; v30: +2 news ; v23: + article 03 ; v22: + CL3, launch notes, gamepad
});

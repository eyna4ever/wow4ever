// v15 (fusion-v15) — fusion des doublons décidée par Mathieu le 01/11/2026 (« Oui évite les doublons dans le futur »).
// Garde-fous : adresses inchangées (page de renvoi statique), tous les faits et toutes les sources conservés, sources
// officielles seulement, AC2/CL3 intouchés, aucune attestation écrite par le pipeline.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, mkdtemp} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {entryPath} from '../lib/articles.mjs';
import {reviseRecord, transitionRecord, auditDataset} from '../lib/documentary.mjs';
import {mergeStubs} from '../lib/v2/merges.mjs';
import {setV2Catalog, renderMoved, renderEntry} from '../lib/v2/render.mjs';
import {setVisualLinks} from '../lib/pages.mjs';
import {isLot1} from './lot1-ids.mjs';
import {isLot2, isLot2New, lot2NewPublished} from './lot2-ids.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
const merges = JSON.parse(await readFile(join(root, 'data/merges.json'), 'utf8'));
const byId = new Map(records.map(e => [e.id, e]));
const OFFICIAL = /^news\.blizzard\.com$/;
// After ops/v15/review-v15.sh (Mathieu's final « Oui », 01/11/2026 04:39), the merges are applied in runtime/entries.json.
// v22: the retired golive-nov4 entry was rewritten and republished at its own address (Mathieu's « Oui », 04/11/2026): its merge
// was applied (reject) before, so it still counts as applied; its old redirect page is replaced by the new launch article.
const V22_REPUBLISHED = new Set(['forever-news-golive-nov4']);
const APPLIED = merges.every(m => { const r = byId.get(m.retired); return (r.status === 'draft' && r.history.at(-1).note.startsWith('reject:')) || (V22_REPUBLISHED.has(m.retired) && r.status === 'published' && r.history.some(h => (h.note ?? '').startsWith('reject:'))); });
const PATHS = {
  'forever-news-golive-nov4': ['fr/actualites/lancement-mondial-le-4-novembre-ce-qu-il-faut-savoir/', 'en/news/global-launch-on-november-4-what-to-know/'],
  'forever-news-podcast-tech': ['fr/actualites/podcast-wow-forever-la-technique/', 'en/news/wow-forever-podcast-all-about-tech/'],
  'forever-news-launch': ['fr/actualites/lancement-mondial-annonce/', 'en/news/announced-worldwide-launch/'],
  'forever-news-podcast-series': ['fr/actualites/le-podcast-officiel-wow-forever/', 'en/news/the-official-wow-forever-podcast/']
};
const out = await mkdtemp(join(tmpdir(), 'v15-'));
if (!APPLIED) execFileSync(process.execPath, [join(root, '../ops/v15/make-revisions.mjs')], {cwd: root, env: {...process.env, OUT: out}, stdio: 'ignore'});
const revision = async id => JSON.parse(await readFile(join(out, `${id}.json`), 'utf8'));

// État « après Oui » reconstruit EN MÉMOIRE pour le test uniquement (rien n'est écrit) : revise + reject comme review-v15.sh,
// puis les fiches conservées marquées publiées dans cette copie pour vérifier les adresses.
async function afterMerge() {
  let state = records;
  for (const id of ['forever-news-launch', 'forever-news-podcast-series']) state = reviseRecord(state, id, await revision(id), {actor: 'test', note: 'test'}).records;
  for (const m of merges) state = transitionRecord(state, m.retired, 'reject', {actor: 'test', note: 'test'}).records;
  return state;
}

test('v15 merges: two duplicates, into kept entries, never AC2/CL3', () => {
  assert.deepEqual(merges.map(m => [m.retired, m.into]), [['forever-news-golive-nov4', 'forever-news-launch'], ['forever-news-podcast-tech', 'forever-news-podcast-series']]);
  for (const m of merges) {
    assert.ok(byId.has(m.retired) && byId.has(m.into));
    assert.ok(![m.retired, m.into].some(id => id === 'forever-news-beta' || id === 'forever-class-priest'));
    assert.match(m.at, /^\d{4}-\d{2}-\d{2}$/);
  }
  assert.equal(byId.get('forever-news-beta').status, 'draft');
  assert.equal(byId.get('forever-class-priest').status, 'published'); // v22
});

test('v15 addresses (before the Oui): kept pages keep their URL, merged URLs are served by a redirect page', {skip: APPLIED && 'merges applied'}, async () => {
  for (const [id, [fr, en]] of Object.entries(PATHS)) assert.deepEqual([entryPath(byId.get(id), 'fr'), entryPath(byId.get(id), 'en')], [fr, en], id);
  const state = await afterMerge();
  const kept = ['forever-news-launch', 'forever-news-podcast-series'];
  // kept entries still drafts (awaiting Mathieu): a build must refuse to break the merged addresses
  assert.throws(() => mergeStubs(state, state.filter(e => e.status === 'published'), merges), /not published/);
  const published = state.filter(e => e.status === 'published' || kept.includes(e.id)).map(e => kept.includes(e.id) ? {...e, status: 'published'} : e);
  for (const id of kept) assert.deepEqual([entryPath(published.find(e => e.id === id), 'fr'), entryPath(published.find(e => e.id === id), 'en')], PATHS[id]);
  const {stubs, pending} = mergeStubs(state, published, merges);
  assert.deepEqual(pending, [...V22_REPUBLISHED]); // v22: golive-nov4 republished at its own address, so no redirect page for it
  assert.deepEqual(stubs.map(s => s.path).sort(), [...PATHS['forever-news-podcast-tech']].sort());
  setVisualLinks(published); setV2Catalog(published);
  for (const s of stubs) {
    const html = renderMoved(s.retired, s.target, s.lang, s.at);
    const href = `../../../${entryPath(s.target, s.lang)}`;
    assert.ok(html.includes(`<meta http-equiv="refresh" content="0; url=${href}">`), s.path);
    assert.ok(html.includes(`href="${href}"`) && html.includes('noindex'), s.path);
    assert.doesNotMatch(html.replace(/<script type="module" src="[^"]+"><\/script>/g, ''), /<script|<style|style=/, s.path);
    assert.ok(html.includes('Site indépendant et non officiel de Blizzard Entertainment.'), s.path);
  }
  // collision guard: a merged address can never shadow a published page
  assert.throws(() => mergeStubs(records, records.filter(e => e.status === 'published' || e.id === 'forever-news-golive-nov4').map(e => ({...e, status: 'published'})).filter(e => e.id !== 'forever-news-golive-nov4').concat([{...byId.get('forever-news-beta'), status: 'published', title: byId.get('forever-news-golive-nov4').title}]), [merges[0]]), /already a published page/);
});

test('v15 current data: merges not applied yet, the published pages are unchanged until Mathieu says « Oui »', () => {
  const live = records.filter(e => e.status === 'published');
  const applied = merges.filter(m => byId.get(m.retired).status !== 'published');
  if (applied.length) return; // after review-v15.sh the other tests cover the merged state
  const {stubs, pending} = mergeStubs(records, live, merges);
  assert.equal(stubs.length, 0);
  assert.deepEqual(pending.sort(), ['forever-news-golive-nov4', 'forever-news-podcast-tech']);
});

test('v15 revisions (before the Oui): every fact source of both duplicates kept, official Blizzard only, FR/EN, no attestation', {skip: APPLIED && 'merges applied'}, async () => {
  for (const m of merges) {
    const rev = await revision(m.into), kept = byId.get(m.into), merged = byId.get(m.retired);
    assert.deepEqual(rev.title, kept.title, 'title (= address) unchanged');
    assert.equal(rev.category, kept.category); assert.equal(rev.id, kept.id);
    const urls = new Set(rev.sources.map(s => s.url));
    for (const s of [...kept.sources, ...merged.sources]) assert.ok(urls.has(s.url), `${m.into} lost ${s.url}`);
    for (const s of rev.sources) {
      assert.match(new URL(s.url).hostname, OFFICIAL, s.url);
      assert.ok(['fr', 'en'].includes(s.language), s.url);
      assert.match(s.publishedAt, /^2026-\d{2}-\d{2}$/, s.url);
      assert.equal(s.url.includes('/fr-fr/'), s.language === 'fr', s.url);
    }
    for (const k of ['fr', 'en']) assert.ok(rev.description[k].length > kept.description[k].length, `${m.into} ${k} not enriched`);
    assert.ok(!('review' in rev) && !('importMeta' in rev));
    assert.ok(!rev.relations.includes(m.retired) && !rev.relations.includes(m.into));
    assert.doesNotMatch(JSON.stringify(rev), /wowhead|fandom|reddit/i);
    assert.doesNotMatch(JSON.stringify(rev), /\bMidnight\b/); // retail expansion name (the word « midnight » for the hour is fine)
  }
  const launch = await revision('forever-news-launch');
  for (const fact of ['15 h PST', '5 novembre à 0 h', '1 000', 'Éolides', 'Classique ou Amélioré', 'ensemble de règles', 'abonnement']) assert.ok(launch.description.fr.includes(fact), fact);
  const pod = await revision('forever-news-podcast-series');
  for (const fact of ['Épisode 6 (29 oct.)', 'Shobek', 'Greenfield', 'Resendez', 'Frank Williams']) assert.ok(pod.description.fr.includes(fact), fact);
});

test('v15 history (before the Oui): correction entries recorded by review.mjs, dataset valid, AC2/CL3 untouched', {skip: APPLIED && 'merges applied'}, async () => {
  const state = await afterMerge();
  assert.equal(auditDataset(state).errors.length, 0);
  for (const id of ['forever-news-launch', 'forever-news-podcast-series']) {
    const e = state.find(x => x.id === id);
    assert.ok(e.history.length > byId.get(id).history.length && e.history.at(-1).note.startsWith('revise:'));
    assert.equal(e.status, 'draft'); assert.ok(!e.review, 'revision drops the old attestation: Mathieu must approve again');
  }
  for (const m of merges) assert.ok(state.find(x => x.id === m.retired).history.at(-1).note.startsWith('reject:'));
  for (const id of ['forever-news-beta']) assert.deepEqual(state.find(x => x.id === id), byId.get(id));
});

test('v15 source list: no empty « () » language label when a source has no language', async () => {
  const published = records.filter(e => e.status === 'published');
  setVisualLinks(published); setV2Catalog(published);
  const noLang = published.find(e => e.sources.some(s => !s.language));
  const html = renderEntry(noLang, 'fr');
  assert.doesNotMatch(html, /source-lang">\(\)|hreflang=""/);
  assert.ok(html.includes(noLang.sources.find(s => !s.language).url));
});

// État après le « Oui » final de Mathieu (01/11/2026 04:39, Europe/Paris) : vérifications sur les données réelles.
const EXPECTED_SOURCES = {
  'forever-news-launch': ['https://news.blizzard.com/fr-fr/article/24315820/world-of-warcraft-forever-sort-partout-dans-le-monde-le-5-novembre', 'https://news.blizzard.com/en-us/article/24315820/world-of-warcraft-forever-goes-live-globally-november-4', 'https://news.blizzard.com/fr-fr/article/24301145/world-of-warcraft-a-la-blizzcon-2026-resume-des-actualites', 'https://news.blizzard.com/en-us/article/24301145/world-of-warcraft-at-blizzcon-2026-news-round-up'],
  'forever-news-podcast-series': ['24304076', '24298592', '24310653', '24304079', '24302577', '24315819'].flatMap(id => ['fr-fr', 'en-us'].map(l => `${l}/article/${id}/`))
};
test('v15 applied: kept entries re-approved by Mathieu after the revision, duplicates withdrawn, addresses served', {skip: !APPLIED && 'merges not applied yet'}, () => {
  assert.equal(records.filter(e => e.status === 'published' && !e.id.startsWith('guide-debutant-') && !isLot1(e) && !isLot2New(e)).length, 189); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ; // v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; v33: lot 2 excluded ; lot 1 excluded ; v31: +2 ; v30: +2 ; v23: + article 03 ; v22: + CL3, launch, notes, gamepad // + v17 guides
  for (const id of ['forever-news-beta']) assert.equal(byId.get(id).status, 'draft');
  for (const m of merges) {
    const kept = byId.get(m.into), gone = byId.get(m.retired);
    assert.equal(kept.status, 'published'); assert.equal(kept.review?.approved, true); assert.equal(kept.review?.reviewer, 'Mathieu');
    const steps = kept.history.map(h => h.note.split(':')[0]);
    const r = steps.lastIndexOf('revise');
    assert.ok(r >= 0 && steps.slice(r + 1).join() === 'submit,approve,publish', `${m.into}: ${steps}`);
    assert.ok(kept.history.at(-1).note.includes('Mathieu') || kept.history.some(h => h.note.includes('2026-11-01 04:39')));
    if (V22_REPUBLISHED.has(m.retired)) { assert.equal(gone.status, 'published'); assert.ok(gone.history.some(h => (h.note ?? '').includes(`Fusionnée dans ${m.into}`)) && /v2[278]|v30/.test(gone.history.at(-1).note)); }   // v30/v28/v27: golive republished
    else assert.ok(!gone.review && gone.identityConfirmed === false && gone.history.at(-1).note.includes(`Fusionnée dans ${m.into}`));
    for (const s of kept.sources) { assert.match(new URL(s.url).hostname, OFFICIAL); assert.ok(['fr', 'en'].includes(s.language)); }
    for (const want of EXPECTED_SOURCES[m.into]) assert.ok(kept.sources.some(s => s.url.includes(want)), `${m.into} lost ${want}`);
    if (!V22_REPUBLISHED.has(m.retired)) for (const s of gone.sources) assert.ok(kept.sources.some(k => k.url === s.url), `${m.into} lost ${s.url}`);
  }
  for (const [id, paths] of Object.entries(PATHS)) assert.deepEqual([entryPath(byId.get(id), 'fr'), entryPath(byId.get(id), 'en')], paths, id);
  const published = records.filter(e => e.status === 'published');
  const {stubs, pending} = mergeStubs(records, published, merges);
  assert.deepEqual(pending, [...V22_REPUBLISHED]); // v22: golive-nov4 republished at its own address, so no redirect page for it
  assert.deepEqual(stubs.map(s => s.path).sort(), [...PATHS['forever-news-podcast-tech']].sort());
  setVisualLinks(published); setV2Catalog(published);
  for (const s of stubs) assert.ok(renderMoved(s.retired, s.target, s.lang, s.at).includes(`<meta http-equiv="refresh" content="0; url=../../../${entryPath(s.target, s.lang)}">`));
  for (const fact of ['15 h PST', '5 novembre à 0 h', '1 000', 'Éolides', 'Classique ou Amélioré', 'ensemble de règles', 'abonnement']) assert.ok(byId.get('forever-news-launch').description.fr.includes(fact), fact);
  for (const fact of ['Épisode 6 (29 oct.)', 'Shobek', 'Greenfield', 'Resendez', 'Frank Williams']) assert.ok(byId.get('forever-news-podcast-series').description.fr.includes(fact), fact);
  assert.equal(byId.get('forever-news-access').status, 'published'); // not merged (decision of Mathieu)
});

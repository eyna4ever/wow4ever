// V2.1 étape 03 — regression tests for the source policy (decisions of 09/11/2026):
// Eternadex/client-extract only => « à confirmer »; wiki.gg refused; official Blizzard still official;
// mixing official + Eternadex never upgrades the Eternadex-only claims.
import {test, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {contentDigest, merge, validate} from '../lib/documentary.mjs';
import {selectPublicEntries} from '../lib/public-catalog.mjs';
import {classifySource, entryVerification, applySourcePolicy, FOREVER_CLIENT_BUILD, VERIFICATION} from '../lib/source-policy.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry, renderCategory} from '../lib/v2/render.mjs';
import {searchIndex} from '../lib/site-chrome.mjs';

const categories = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories;
afterEach(() => setVisualLinks([]));
const GV = 'World of Warcraft: Forever — test politique de sources';
const PILL = {fr: 'status-pill is-draft">À confirmer<', en: 'status-pill is-draft">Unconfirmed — to be confirmed<'};
const BZ = (lang, key) => ({key: `${key}-${lang}`, language: lang, publishedAt: '2026-09-23', url: `https://news.blizzard.com/${lang === 'fr' ? 'fr-fr' : 'en-us'}/article/24307383/test`, title: `Blizzard ${lang}`, accessedAt: '2026-11-09', license: 'Droits réservés Blizzard ; synthèse originale.', gameVersion: GV});
const ETX = {key: 'etx', language: 'en', undated: true, url: 'https://eternadex.com/en/datenbank/', title: 'Eternadex', accessedAt: '2026-11-09', license: 'Aucune licence publiée', gameVersion: GV, verification: 'officiel confirmé'};
const WIKIGG = {url: 'https://warcraft.wiki.gg/wiki/Quest', title: 'wiki.gg', accessedAt: '2026-11-09', license: 'CC BY-SA', gameVersion: GV};

function base(id, sources, extra = {}) {
  return {id, title: {fr: `Titre ${id}`, en: `Title ${id}`}, description: {fr: 'Description test.', en: 'Test description.'}, category: 'professions', subcategory: 'test-politique',
    sources, status: 'draft', updatedAt: '2026-11-09', gameVersion: GV, version: 1, relations: [], history: [{at: '2026-11-09', actor: 'test', note: 'fixture', version: 1}], ...extra};
}
function publish(entry) {
  const e = structuredClone(entry);
  e.status = 'published'; e.identityConfirmed = true; delete e.importMeta;
  e.review = {approved: true, reviewer: 'test-fixture', at: '2026-11-09', rightsConfirmed: true, translationsConfirmed: true};
  e.review.contentDigest = contentDigest(e);
  return e;
}
const render = (dto, lang) => { setCategoryNames(categories); setV2Catalog([dto]); return renderEntry(dto, lang); };

test('policy 1 — Eternadex-only record: accepted only as « à confirmer », shown with the mention, never official', () => {
  const raw = base('test-eternadex-only', [ETX], {verification: 'officiel confirmé', facts: [{id: 'f1', src: ['etx'], status: 'vérifié en jeu', fr: 'x', en: 'x'}]});
  assert.equal(classifySource(ETX.url), 'extrait_client');
  // direct edit claiming official is rejected
  assert.ok(validate(raw).some(e => /aucune source officielle/.test(e)));
  assert.ok(validate(raw).some(e => /extrait_client ne peut pas être « officiel confirmé »/.test(e)));
  // import: inserted as draft but downgraded and reported
  const {records, report} = merge([], [raw], {now: '2026-11-09T12:00:00Z'});
  assert.deepEqual(report.inserted, ['test-eternadex-only']);
  assert.equal(report.downgraded.length, 1);
  const stored = records[0];
  assert.equal(stored.verification, 'à confirmer');
  assert.equal(stored.sources[0].verification, 'à confirmer');
  assert.equal(stored.facts[0].status, 'à confirmer');
  assert.deepEqual(validate(stored), []);
  // published output: DTO + page + listing + search index carry the mention
  const [dto] = selectPublicEntries([publish(stored)]);
  assert.equal(dto.verification, 'à confirmer');
  assert.equal(dto.sources[0].tier, 'extrait_client');
  const fr = render(dto, 'fr'), en = render(dto, 'en');
  assert.ok(fr.includes(PILL.fr) && en.includes(PILL.en));
  assert.match(fr, /0 source officielle \+ 1 source non officielle/);
  assert.match(fr, /Source non officielle — à confirmer/);
  assert.match(en, /Non-official source — unconfirmed/);
  assert.doesNotMatch(fr, />1 source officielle</);
  assert.doesNotMatch(fr, /officiel confirmé|vérifié en jeu/);
  assert.match(fr, /Aucune source officielle Blizzard pour cette fiche/);
  assert.doesNotMatch(fr, /Sources officielles Blizzard Entertainment \(droits réservés\)/);
  assert.match(en, /No official Blizzard source for this entry/);
  assert.ok(fr.match(/<section[^>]*id="en-bref"[\s\S]*?<\/section>/)[0].includes(PILL.fr), 'brief paragraph marked');
  assert.ok(renderCategory('professions', 'fr').includes(PILL.fr));
  assert.equal(searchIndex({categories, entries: [{...dto, url: dto.url}]}).entries[0].verification, 'à confirmer');
});

test('policy 2 — a wiki.gg URL is refused (quarantined on import, invalid on direct edit)', () => {
  assert.equal(classifySource('https://warcraft.wiki.gg/wiki/Legacy'), 'refuse');
  assert.equal(classifySource('https://anything.wiki.gg/'), 'refuse');
  const raw = base('test-wikigg', [WIKIGG]);
  assert.ok(validate(raw).some(e => /wiki\.gg exclu/.test(e)));
  const mixed = base('test-wikigg-mixed', [BZ('fr', 'bz'), WIKIGG]);
  const {records, report} = merge([], [raw, mixed], {now: '2026-11-09T12:00:00Z'});
  assert.deepEqual(records, []);
  assert.deepEqual(report.inserted, []);
  assert.deepEqual(report.quarantined.map(q => q.id), ['test-wikigg', 'test-wikigg-mixed']);
  assert.deepEqual(selectPublicEntries([publish({...raw, verification: 'à confirmer'})]), [], 'never public even if hand-published');
});

test('policy 3 — a record sourced only by official Blizzard pages still publishes as official', () => {
  const raw = base('test-official-only', [BZ('fr', 'bz'), BZ('en', 'bz')]);
  assert.equal(entryVerification(raw), 'officiel confirmé');
  const {records, report} = merge([], [raw], {now: '2026-11-09T12:00:00Z'});
  assert.deepEqual(report.downgraded, []);
  assert.equal(records[0].verification, undefined, 'nothing forced on official records');
  const [dto] = selectPublicEntries([publish(records[0])]);
  assert.equal(dto.verification, undefined);
  assert.ok(!dto.sources.some(s => 'tier' in s));
  const fr = render(dto, 'fr');
  assert.match(fr, />1 source officielle</);
  assert.ok(!fr.includes(PILL.fr));
  for (const url of ['https://worldofwarcraft.blizzard.com/fr-fr/news/1', 'https://eu.forums.blizzard.com/fr/wow/t/x/1', 'https://us.forums.blizzard.com/en/wow/t/x/1', 'https://x.com/BlizzardCS/status/1'])
    assert.equal(classifySource(url), 'officiel', url);
  for (const url of ['https://x.com/someone/status/1', 'http://news.blizzard.com/en-us/x', 'https://news.blizzard.com.evil.example/x', 'https://www.wowhead.com/x'])
    assert.notEqual(classifySource(url), 'officiel', url);
});

test('policy 4 — mixed official + Eternadex: the Eternadex-only claims are never upgraded to official', () => {
  const article = {format: 1, slug: {fr: 'test-mixte', en: 'test-mixed'}, illustration: 'professions',
    lead: {fr: 'Intro officielle.', en: 'Official intro.', src: ['bz']},
    keyPoints: [{fr: 'Point officiel.', en: 'Official point.', src: ['bz']}, {fr: 'Point Eternadex.', en: 'Eternadex point.', src: ['etx']}],
    sections: [{id: 'detail', title: {fr: 'Détail', en: 'Detail'}, blocks: [
      {type: 'p', fr: 'PHRASE-OFFICIELLE.', en: 'OFFICIAL-SENTENCE.', src: ['bz']},
      {type: 'p', fr: 'PHRASE-ETERNADEX.', en: 'ETERNADEX-SENTENCE.', src: ['etx'], status: 'officiel confirmé'}]}],
    confirmed: [{fr: 'Confirmé officiel.', en: 'Confirmed official.', src: ['bz']}, {fr: 'Faux confirmé Eternadex.', en: 'Fake confirmed Eternadex.', src: ['etx']}],
    pending: [{fr: 'Reste à confirmer.', en: 'Still pending.'}]};
  const raw = base('test-mixed', [BZ('fr', 'bz'), BZ('en', 'bz'), {...ETX}], {article, verification: 'officiel confirmé',
    facts: [{id: 'f-bz', src: ['bz'], status: 'officiel confirmé'}, {id: 'f-etx', src: ['etx'], status: 'officiel confirmé'}]});
  const errors = validate(raw);
  assert.ok(errors.some(e => /confirmed\[1\].*sans source officielle/.test(e)));
  assert.ok(errors.some(e => /facts\[1\]/.test(e)));
  assert.ok(errors.some(e => /blocks\[1\].*interdit sans source officielle/.test(e)));
  assert.ok(!errors.some(e => /facts\[0\]|confirmed\[0\]/.test(e)), 'official claims stay valid');
  const {records, report} = merge([], [raw], {now: '2026-11-09T12:00:00Z'});
  assert.deepEqual(report.invalid, []);
  assert.deepEqual(report.inserted, ['test-mixed']);
  assert.ok(report.downgraded[0].changes.some(c => c.where === 'article.sections[0].blocks[1]'));
  const stored = records[0];
  assert.equal(stored.verification, 'officiel confirmé', 'entry has an official source');
  assert.equal(stored.facts[0].status, 'officiel confirmé');
  assert.equal(stored.facts[1].status, 'à confirmer');
  assert.equal(stored.sources.find(s => s.key === 'etx').verification, 'à confirmer');
  assert.deepEqual(stored.article.confirmed.map(c => c.en), ['Confirmed official.']);
  assert.ok(stored.article.pending.some(p => p.en === 'Fake confirmed Eternadex.'));
  assert.equal(stored.article.sections[0].blocks[1].status, 'à confirmer');
  assert.deepEqual(validate(stored), []);
  const [dto] = selectPublicEntries([publish(stored)]);
  for (const [lang, own, etx] of [['fr', 'PHRASE-OFFICIELLE.', 'PHRASE-ETERNADEX.'], ['en', 'OFFICIAL-SENTENCE.', 'ETERNADEX-SENTENCE.']]) {
    const html = render(dto, lang);
    const after = text => html.slice(html.indexOf(text), html.indexOf('</p>', html.indexOf(text)));
    assert.ok(after(etx).includes(PILL[lang]), `${lang}: Eternadex sentence marked`);
    assert.ok(!after(own).includes(PILL[lang]), `${lang}: official sentence not marked`);
  }
  assert.match(render(dto, 'fr'), /1 source officielle \+ 1 source non officielle/);
  assert.match(render(dto, 'fr'), /Sources officielles Blizzard Entertainment \(droits réservés\)[^<]*Les sources marquées « à confirmer »/);
});

test('policy — the step-02 failing case (Eternadex-only quest count) is now downgraded, never silently inserted', async () => {
  const batch = JSON.parse(await readFile(new URL('./fixtures/etape02_import_dry_run_batch.json', import.meta.url), 'utf8'));
  const {records, report} = merge([], batch, {now: '2026-11-09T12:00:00Z'});
  const rec = records.find(r => r.id === 'q-eternadex-quest-count-test');
  assert.ok(rec, 'still importable as a draft');
  assert.equal(rec.verification, 'à confirmer');
  assert.equal(rec.sources[0].verification, 'à confirmer');
  assert.ok(report.downgraded.some(d => d.id === 'q-eternadex-quest-count-test'));
  assert.equal(applySourcePolicy(rec).downgraded.length, 0, 'idempotent');
});


test('policy 5 — t359u: a 70862-stamped client extract may be « données du jeu », never official, and is not marked « à confirmer »', () => {
  const stamped = {
    ...ETX,
    title: `Item database — game data, WoW Forever client build ${FOREVER_CLIENT_BUILD}, as of 7 November 2026`,
    clientBuild: FOREVER_CLIENT_BUILD,
    verification: VERIFICATION.gameData
  };
  const officialAttempt = {...stamped, verification: 'officiel confirmé'};
  assert.ok(validate(base('test-gamedata-official-claim', [officialAttempt], {verification: 'officiel confirmé'})).some(e => /extrait_client ne peut pas être « officiel confirmé »/.test(e)));
  // import of a stamped extract still claiming official: downgraded to « à confirmer », never auto-upgraded
  const {records: down} = merge([], [base('test-gamedata-downgrade', [officialAttempt], {verification: 'officiel confirmé'})], {now: '2026-11-13T12:00:00Z'});
  assert.equal(down[0].verification, 'à confirmer');
  assert.equal(down[0].sources[0].verification, 'à confirmer');
  // already marked « données du jeu » + stamp is preserved, still not official (short entry, no article)
  const raw = base('test-gamedata-kept', [stamped], {verification: VERIFICATION.gameData});
  assert.deepEqual(validate(raw), []);
  const {records, report} = merge([], [raw], {now: '2026-11-13T12:00:00Z'});
  assert.deepEqual(report.downgraded, []);
  assert.equal(records[0].verification, 'données du jeu');
  assert.equal(records[0].sources[0].verification, 'données du jeu');
  assert.deepEqual(validate(records[0]), []);
  const [dto] = selectPublicEntries([publish(records[0])]);
  assert.equal(dto.verification, 'données du jeu');
  assert.equal(dto.sources[0].verification, 'données du jeu');
  const fr = render(dto, 'fr'), en = render(dto, 'en');
  assert.ok(!fr.includes(PILL.fr) && !en.includes(PILL.en), 'no « à confirmer » pill');
  assert.match(fr, /Données du jeu — client 1\.60\.1\.70862/);
  assert.match(en, /Game data — client 1\.60\.1\.70862/);
  assert.match(fr, /viennent des fichiers du client WoW Forever/);
  assert.doesNotMatch(fr, /tout son contenu reste à confirmer/);
  assert.doesNotMatch(fr, /officiel confirmé|vérifié en jeu/);
  assert.equal(applySourcePolicy(records[0]).downgraded.length, 0, 'idempotent');
  // mixed official + stamped extract: the client-only sentence is marked « données du jeu », not « à confirmer »
  const mixed = base('test-gamedata-mixed', [BZ('fr', 'bz'), BZ('en', 'bz'), stamped], {
    verification: VERIFICATION.gameData,
    article: {format: 1, slug: {fr: 'test-donnees-jeu', en: 'test-game-data'}, illustration: 'professions',
      lead: {fr: 'Intro officielle.', en: 'Official intro.', src: ['bz']},
      keyPoints: [{fr: 'Point officiel.', en: 'Official point.', src: ['bz']}, {fr: 'Point données du jeu.', en: 'Game-data point.', src: ['etx']}],
      sections: [{id: 'detail', title: {fr: 'Détail', en: 'Detail'}, blocks: [
        {type: 'p', fr: 'PHRASE-OFFICIELLE.', en: 'OFFICIAL-SENTENCE.', src: ['bz']},
        {type: 'p', fr: 'PHRASE-DONNEES-JEU.', en: 'GAME-DATA-SENTENCE.', src: ['etx']}]}],
      confirmed: [{fr: 'Confirmé officiel.', en: 'Confirmed official.', src: ['bz']}],
      pending: [{fr: 'Zone non indiquée.', en: 'Zone not given.'}]}
  });
  assert.deepEqual(validate(mixed), []);
  const {records: mixedRec} = merge([], [mixed], {now: '2026-11-13T12:00:00Z'});
  assert.equal(mixedRec[0].sources.find(s => s.key === 'etx').verification, 'données du jeu');
  const [mixedDto] = selectPublicEntries([publish(mixedRec[0])]);
  const mixedFr = render(mixedDto, 'fr');
  const after = text => mixedFr.slice(mixedFr.indexOf(text), mixedFr.indexOf('</p>', mixedFr.indexOf(text)));
  assert.ok(after('PHRASE-DONNEES-JEU.').includes('Données du jeu (client 1.60.1.70862)'), 'client sentence marked game data');
  assert.ok(!after('PHRASE-DONNEES-JEU.').includes(PILL.fr), 'client sentence not unconfirmed');
  assert.ok(!after('PHRASE-OFFICIELLE.').includes(PILL.fr), 'official sentence unmarked');
  // unstamped Eternadex still cannot carry « données du jeu »
  const unstamped = {...ETX, verification: VERIFICATION.gameData};
  assert.ok(validate(base('test-unstamped-gamedata', [unstamped], {verification: VERIFICATION.gameData})).some(e => /données du jeu/.test(e)));
});

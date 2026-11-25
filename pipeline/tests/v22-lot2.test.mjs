// V2.1 étape 04 — lot 2 « monde », v33 : validé et publié par Mathieu (t341u, 2026-11-09).
// Décisions t341u : sans notes de bêta ; réputations de champ de bataille reportées à l'étape 05 ; noms de bases tierces retirés ;
// noms anglais conservés sans traduction officielle ; 9 fiches donjon réécrites (URL inchangées) ; 4 sous-catégories validées.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir, access} from 'node:fs/promises';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validate, auditDataset} from '../lib/documentary.mjs';
import {classifySource} from '../lib/source-policy.mjs';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry} from '../lib/v2/render.mjs';
import {entryPath} from '../lib/articles.mjs';
import {LOT2_NEW_IDS, LOT2_REVISED_IDS, LOT2_IDS, lot2NewPublished} from './lot2-ids.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const FIX = join(root, 'tests/fixtures');
const exists = p => access(p).then(() => true, () => false);
const readJSON = async p => JSON.parse(await readFile(p, 'utf8'));
const runtime = () => readJSON(join(root, 'runtime/entries.json'));
const strip = e => { const {history, review, importMeta, ...rest} = e; return rest; };   // contenu publié (hors historique)
const stripUrls = e => { const rest = strip(e); if (Array.isArray(rest.sources)) rest.sources = rest.sources.map(({url, ...s}) => s); return rest; };
const visibleHtml = html => html.replace(/<script[\s\S]*?<\/script>/g, '').replace(/\s(?:href|src)="[^"]*"/g, '').replace(/<[^>]+>/g, ' ');

// Aucune URL tierce, aucun chiffre en quarantaine (5167 quêtes, 48 factions), aucun nom de base tierce (t341u, point 7).
const THIRD = /wiki\.gg|eternadex|wowhead|5[\s\u202f\u00a0.]?167|\b48 factions/i;
// Notes de bêta retirées (t341u, point 3) : URL des « Beta Development Notes », mentions « bêta » et contenus identifiés.
const T391_BETA_QUESTS = new Set(['forever-dungeon-city-of-dalaran', 'forever-dungeon-excavation-site', 'forever-dungeon-hall-of-thanes', 'forever-dungeon-ruins-of-lordaeron']);
const BETA = /2360696|b[êe]ta\b|Beta Development|peut avoir évolué|may have changed since|Shen.dar|Nightclaw|Mother Fang|Snow Leopard|Stitches|Alliance Outrunners|Dalaran Summoners|satyr|Titan Relic|Elder Knowledge|Frightened Request|Bloodied Insignia|26 à 31|26–31|baguettes|Wands|attaqué[es]* à vue|on sight/i;
const BETA_NO_WORD = new RegExp(BETA.source.replace('b[êe]ta\\b|', ''), 'i');
const BG_REP = /champs? de bataille|battleground|4 points|Sombrelances|Darkspear|Theramore/i;
const batch = async () => [...await readJSON(join(FIX, 'lot2.entries.json')),
  ...await Promise.all((await readdir(join(FIX, 'lot2-revisions'))).sort().map(f => readJSON(join(FIX, 'lot2-revisions', f))))];

test('lot 2 batch: 4 new valid drafts + 9 revisions, official Blizzard sources only, no beta notes, no third-party names', async () => {
  const all = await batch();
  assert.deepEqual(all.map(e => e.id).sort(), [...LOT2_IDS].sort());
  for (const e of all) {
    if (LOT2_NEW_IDS.includes(e.id)) { assert.equal(e.status, 'draft', e.id); assert.ok(!('review' in e), e.id); assert.deepEqual(validate(e), [], e.id); }
    assert.ok(e.sources.length >= 4, e.id);
    for (const s of e.sources) assert.equal(classifySource(s.url), 'officiel', `${e.id} ${s.url}`);
    const text = JSON.stringify(strip(e));
    assert.doesNotMatch(text, THIRD, e.id);
    assert.doesNotMatch(text, BETA, e.id);
  }
});

test('lot 2: battleground reputations moved to step 05 (not in the reputations entry)', async () => {
  const rep = (await batch()).find(e => e.id === 'forever-reputations-confirmed');
  assert.doesNotMatch(JSON.stringify(strip(rep)), BG_REP);
  assert.deepEqual(rep.title, {fr: 'Réputations : ce que Blizzard a confirmé (Kirin Tor, Diplomatie)', en: 'Reputations: what Blizzard has confirmed (Kirin Tor, Diplomat)'});
});

test('lot 2 revisions: same id, title and URL as v32, only beta-note sources dropped', async () => {
  const v32 = new Map((await readJSON(join(FIX, 'lot2-v32-dungeons.json'))).map(e => [e.id, e]));
  for (const id of LOT2_REVISED_IDS) {
    const rev = await readJSON(join(FIX, 'lot2-revisions', `${id}.json`)), old = v32.get(id);
    assert.deepEqual(rev.title, old.title, id);
    assert.deepEqual(rev.history, old.history, `${id}: history kept`);
    for (const s of old.sources) assert.ok(rev.sources.some(n => n.url === s.url) || s.url.includes('/t/2360696/'), `${id} lost ${s.url}`);
    for (const lang of ['fr', 'en']) assert.equal(entryPath(rev, lang), entryPath(old, lang), `${id} ${lang}: URL changed`);
  }
});

test('lot 2 published by Mathieu (t341u), integrity, earlier history kept', async () => {
  const records = await runtime();
  assert.deepEqual(auditDataset(records).errors, []);
  if (lot2NewPublished(records) === 0) return; // jeu de données v32
  const byId = new Map(records.map(e => [e.id, e]));
  for (const id of LOT2_IDS) {
    const e = byId.get(id);
    assert.equal(e.status, 'published', id); assert.equal(e.review.reviewer, 'Mathieu', id); assert.equal(e.review.approved, true, id);
    for (const step of ['submit', 'approve', 'publish']) assert.ok(e.history.some(h => h.actor === 'Mathieu' && h.note.startsWith(`${step}:`) && h.note.includes('t341u')), `${id} ${step}`);
    assert.ok(!e.history.some(h => /TEST ISOLÉ/.test(h.actor)), `${id}: no test approval`);
    for (const rel of e.relations ?? []) assert.equal(byId.get(rel)?.status, 'published', `${id} -> ${rel}`);
    assert.doesNotMatch(JSON.stringify(stripUrls(e)), THIRD, id);
    if (T391_BETA_QUESTS.has(id)) {
      // t391u : liste de quêtes de l'index bêta (section quetes-liste + source client-quetes-index), chaque mention marquée à confirmer
      const strings = []; const walk = v => typeof v === 'string' ? strings.push(v) : v && typeof v === 'object' && Object.values(v).forEach(walk);
      walk(e.article);   // contenu publié seulement (l’historique interne garde ses notes d’origine)
      for (const t of strings) if (/b[êe]ta\b/i.test(t)) assert.match(t, /à confirmer|to be confirmed|t388u|t391u/i, `${id}: ${t.slice(0, 120)}`);
      const rest = {...stripUrls(e), sources: e.sources.filter(x => x.key !== 'client-quetes-index-en' && x.key !== 'client-quetes-index-fr'), history: [],
        article: {...e.article, sections: e.article.sections.filter(x => x.id !== 'quetes-liste')}};
      assert.doesNotMatch(JSON.stringify(rest), BETA_NO_WORD, id);
    } else assert.doesNotMatch(JSON.stringify(stripUrls(e)), BETA, id);
  }
  for (const id of LOT2_REVISED_IDS) {
    const e = byId.get(id);
    assert.ok(e.history.some(h => h.note.startsWith('revise:') && h.note.includes('t341u')), id);
    assert.ok(e.history.some(h => h.actor === 'Mathieu' && h.note.startsWith('approve:') && h.at < '2026-11-09'), `${id}: earlier approval by Mathieu kept`);
  }
});

test('lot 2 pages: accessible (lang, viewport, noindex, one h1, no heading jump, captions, no inline script/style), no beta, no third-party names', async () => {
  const records = await runtime(); if (lot2NewPublished(records) === 0) return;
  const categories = (await readJSON(join(root, 'public/wiki/catalog.json'))).categories;
  const all = (await siteEntries()).filter(e => e.status === 'published');
  setCategoryNames(categories); setVisualLinks(all); setV2Catalog(all);
  for (const lang of ['fr', 'en']) for (const id of LOT2_IDS) {
    const html = renderEntry(all.find(e => e.id === id), lang);
    assert.match(html, new RegExp(`<html lang="${lang}"`), id);
    assert.match(html, /<meta name="viewport" content="width=device-width,initial-scale=1">/, id);
    assert.match(html, /<meta name="robots" content="noindex,nofollow">/, id);
    assert.equal((html.match(/<h1[\s>]/g) ?? []).length, 1, id);
    const levels = [...html.matchAll(/<h([1-6])[\s>]/g)].map(m => +m[1]);
    for (let i = 1; i < levels.length; i++) assert.ok(levels[i] <= levels[i - 1] + 1, `${id} ${lang}: h${levels[i - 1]} -> h${levels[i]}`);
    assert.equal((html.match(/<caption[\s>]/g) ?? []).length, (html.match(/<table[\s>]/g) ?? []).length, `${id} ${lang}: table without caption`);
    assert.doesNotMatch(html, /<script(?![^>]*\bsrc=)[^>]*>/, id);
    assert.doesNotMatch(html, /<style[\s>]|\sstyle="/, id);
    const main = html.slice(html.indexOf('<main'));   // contenu de la fiche (hors menu commun)
    assert.doesNotMatch(visibleHtml(main), THIRD, `${id} ${lang}`);
    const body = main.replace(/<aside class="v2-rail">[\s\S]*?<\/aside>/, '');
    if (T391_BETA_QUESTS.has(id)) {
      // t391u (Oui de Mathieu) : ces 4 fiches reçoivent la liste des quêtes de l'index bêta (révision t388u), autorisée
      // uniquement si chaque mention « bêta » est marquée à confirmer ; la liste des sources n'est pas concernée.
      const noSrc = body.replace(/<section class="article-section sources-block"[\s\S]*?<\/section>/, '');
      const noQuests = noSrc.replace(/<section class="article-section" id="quetes-liste"[\s\S]*?<\/section>/, '');
      for (const m of noSrc.matchAll(/<(li|p|td|th|h2|h3|caption|dd|dt)[\s>][\s\S]*?<\/\1>/g)) {
        const t = visibleHtml(m[0]);
        if (/b[êe]ta\b/i.test(t)) assert.match(t, /à confirmer|to be confirmed/i, `${id} ${lang}: ${t.slice(0, 120)}`);
      }
      assert.doesNotMatch(visibleHtml(noQuests), BETA_NO_WORD, `${id} ${lang}`);
    } else assert.doesNotMatch(visibleHtml(body), BETA, `${id} ${lang}`);
    if (id === 'forever-reputations-confirmed') assert.doesNotMatch(main.replace(/<aside class="v2-rail">[\s\S]*?<\/aside>/, ''), BG_REP, lang);
  }
});

test('lot 2 exploration: 14 places, no coordinates published (model ready for a future Cartographe)', async () => {
  const e = (await batch()).find(x => x.id === 'forever-exploration-named-places');
  const table = e.article.sections.find(s => s.id === 'index').blocks[0];
  assert.equal(table.rows.length, 14);
  assert.ok(table.rows.every(r => r.at(-1).fr === 'Non publiées' && /^[a-z0-9-]+$/.test(r[0].fr)));
  assert.doesNotMatch(JSON.stringify(e.article), /\b\d{1,2}[.,]\d\s*[,;/]\s*\d{1,2}[.,]\d\b/, 'no x,y coordinate pair');
});

test('no sitemap in the built wiki', async () => {
  for (const d of ['dist-v2', '../site/wiki']) for (const f of ['sitemap.xml', 'fr/sitemap.xml', 'en/sitemap.xml']) assert.equal(await exists(join(root, d, f)), false, `${d}/${f}`);
});

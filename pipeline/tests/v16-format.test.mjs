// v16 (format-v16) — extension du format d'article approuvée par Mathieu le 01/11/2026 05:04 (« 1 oui ») ; SEO inchangé (« 2 non »).
// Garde-fous : seul le bloc « Analyse de la rédaction IA WoW4ever » peut être sans source ; tout bloc factuel reste sourcé ;
// les pages existantes (format 1, sans tags ni eventDate) sont rendues à l'octet près comme avant ; aucune fiche publiée en plus.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, writeFile, mkdtemp} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ANALYSIS_LABEL, validateArticle, articlePlainText} from '../lib/articles.mjs';
import {validate, auditDataset} from '../lib/documentary.mjs';
import {draftToEntry, parseFrontMatterYAML} from '../lib/v16/draft.mjs';
import {main as checkData} from '../scripts/check-data.mjs';
import {main as draftCli} from '../scripts/draft-to-entry.mjs';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks} from '../lib/pages.mjs';
import {setV2Catalog, renderEntry, renderCategory, renderHome, renderIndex} from '../lib/v2/render.mjs';
import {entryPath} from '../lib/articles.mjs';
import {isLot1, lot1Published} from './lot1-ids.mjs';
import {isLot2, isLot2New, lot2NewPublished} from './lot2-ids.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const EXAMPLE = join(root, '../ops/v16/exemple-lancement.md');
const example = () => readFile(EXAMPLE, 'utf8').then(md => draftToEntry(md, {file: 'exemple-lancement.md'}));
const clone = value => structuredClone(value);
const analysisSection = entry => entry.article.sections.find(section => section.blocks.every(block => block.type === 'analysis'));

test('v16 example draft converts to a valid format 2 DRAFT entry (official sources only, never published)', async () => {
  const {entry, errors} = await example();
  assert.deepEqual(errors, []);
  assert.equal(entry.status, 'draft'); assert.equal(entry.identityConfirmed, false); assert.equal(entry.review, undefined);
  assert.equal(entry.article.format, 2);
  assert.deepEqual(validate(entry), []);
  assert.ok(entry.sources.every(source => new URL(source.url).hostname === 'news.blizzard.com'));
  assert.deepEqual(entry.tags.map(tag => tag.en), ['Launch', 'Schedule', 'Rulesets']);
  assert.equal(entry.eventDate, '2026-11-04');
  const block = analysisSection(entry).blocks[0];
  assert.deepEqual(block.label, ANALYSIS_LABEL); assert.equal(block.src, undefined);
  assert.deepEqual(entry.article.sections.map(s => s.title.fr), ['Les détails', 'Conséquences pour les joueurs', 'L\'analyse WoW4ever']);
  assert.ok(articlePlainText(entry, 'fr').includes('À notre avis'));
});

test('v16 validation: the analysis block is the ONLY block allowed without sources', async () => {
  const {entry} = await example();
  // a factual paragraph without sources is still rejected
  const p = clone(entry); delete p.article.sections[0].blocks[0].src;
  assert.ok(validate(p).some(error => /sections\[0\]\.blocks\[0\]: at least one source required/.test(error)));
  const kp = clone(entry); kp.article.keyPoints[0].src = [];
  assert.ok(validate(kp).some(error => /keyPoints\[0\]: at least one source required/.test(error)));
  const conf = clone(entry); delete conf.article.confirmed[0].src;
  assert.ok(validate(conf).some(error => /confirmed\[0\]: at least one source required/.test(error)));
  const lead = clone(entry); delete lead.article.lead.src;
  assert.ok(validate(lead).some(error => /lead: at least one source required/.test(error)));
  // an unknown source key on an analysis block is rejected too
  const unknown = clone(entry); analysisSection(unknown).blocks[0].src = ['inconnue'];
  assert.ok(validate(unknown).some(error => /unknown source inconnue/.test(error)));
});

test('v16 validation: an analysis block must be labelled exactly, sit alone in its section and use format 2', async () => {
  const {entry} = await example();
  const LABEL = /analysis block must be labelled exactly « Analyse de la rédaction IA WoW4ever » \/ « WoW4ever AI editorial analysis »/;
  for (const label of [undefined, {fr: 'Analyse de la rédaction', en: ANALYSIS_LABEL.en}, {fr: ANALYSIS_LABEL.fr, en: 'AI analysis'}, {fr: 'analyse de la rédaction ia wow4ever', en: ANALYSIS_LABEL.en}, 'Analyse de la rédaction IA WoW4ever']) {
    const bad = clone(entry); const block = analysisSection(bad).blocks[0];
    if (label === undefined) delete block.label; else block.label = label;
    assert.ok(validate(bad).some(error => LABEL.test(error)), JSON.stringify(label));
  }
  const mixed = clone(entry); analysisSection(mixed).blocks.push({type: 'p', fr: 'Fait.', en: 'Fact.', src: ['bz-golive']});
  assert.ok(validate(mixed).some(error => /analysis block must sit in a section without factual blocks/.test(error)));
  const f1 = clone(entry); f1.article.format = 1;
  assert.ok(validate(f1).some(error => /analysis blocks require article.format 2/.test(error)));
  const reserved = clone(entry); reserved.article.sections[0].id = 'discussion';
  assert.ok(validate(reserved).some(error => /reserved by the article layout/.test(error)));
  const f3 = clone(entry); f3.article.format = 3;
  assert.ok(validateArticle(f3).includes('article.format must be 1 or 2'));
});

test('v16 validation: optional tags and eventDate', async () => {
  const {entry} = await example();
  const cases = [[{tags: []}, /tags: 1 to 8/], [{tags: [{fr: 'Lancement'}]}, /each tag needs fr\/en/], [{tags: [{fr: 'A', en: 'B'}, {fr: 'a', en: 'C'}]}, /duplicate tag/],
    [{tags: Array.from({length: 9}, (_, i) => ({fr: `t${i}`, en: `t${i}`}))}, /tags: 1 to 8/], [{tags: [{fr: 'x'.repeat(41), en: 'y'}]}, /40 characters/],
    [{eventDate: '2026-02-30'}, /eventDate/], [{eventDate: '4 novembre'}, /eventDate/], [{eventDate: '2026-11-04T00:00:00Z'}, /eventDate/]];
  for (const [patch, pattern] of cases) assert.ok(validate({...clone(entry), ...patch}).some(error => pattern.test(error)), JSON.stringify(patch));
  const none = clone(entry); delete none.tags; delete none.eventDate;
  assert.deepEqual(validate(none), []);
});

test('v16 check-data: rejects a wrongly labelled analysis block and a sourceless factual block, accepts the real dataset', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'v16-check-'));
  const records = JSON.parse(await readFile(join(root, 'runtime/entries.json'), 'utf8'));
  const run = async data => { const path = join(dir, `${Math.random()}.json`); await writeFile(path, JSON.stringify(data)); let code = 0, out = ''; await checkData([path], {log: text => { out += text; }, setExitCode: c => { code = c; }}); return {code, report: JSON.parse(out)}; };
  const ok = await run(records);
  const v17 = records.filter(e => e.id.startsWith('guide-debutant-') && e.status === 'published').length; // v17 beginner guides
  assert.equal(ok.code, 0); assert.equal(ok.report.published, 89 + v17 + lot1Published(records) + lot2NewPublished(records) + 26 + 48 + 26); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ; // v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; v33: + lot 2 ; lot 1 ; assert.deepEqual(ok.report.errors, []); // v31: +2 ; v30: +2
  const {entry} = await example();
  assert.equal((await run([...records, entry])).code, 0);
  const badLabel = clone(entry); analysisSection(badLabel).blocks[0].label = {fr: 'Notre avis', en: 'Our opinion'};
  const r1 = await run([...records, badLabel]);
  assert.equal(r1.code, 1); assert.ok(r1.report.errors[0].errors.some(e => /labelled exactly/.test(e)));
  const noSrc = clone(entry); delete noSrc.article.sections[1].blocks[0].src;
  const r2 = await run([...records, noSrc]);
  assert.equal(r2.code, 1); assert.ok(r2.report.errors[0].errors.some(e => /at least one source required/.test(e)));
});

test('v16 converter: front matter rules (draft only, official sources, FR/EN symmetry, tags) and CLI writes nothing on error', async () => {
  const md = await readFile(EXAMPLE, 'utf8');
  const errs = text => draftToEntry(text).errors.join(' | ');
  assert.match(errs(md.replace('status: draft', 'status: published')), /status must be "draft"/);
  assert.match(errs(md.replace('https://news.blizzard.com/fr-fr/article/24315820', 'https://www.wowhead.com/news/24315820')), /official Blizzard source required/);
  assert.match(errs(md.replace('https://news.blizzard.com/fr-fr/', 'http://news.blizzard.com/fr-fr/')), /official Blizzard source required/);
  assert.match(errs(md.replace('  - "Calendrier | Schedule"', '  - "Calendrier"')), /write "Français \| English"/);
  assert.match(errs(md.replace('- De nouvelles combinaisons race-classe sont proposées. [src: bz-golive]\n', '')), /FR has 2 items but EN has 3/);
  assert.match(errs(md.replace('## Les détails', '## Les détails\n\n## En plus\nTexte. [src: bz-golive]')), /must match one to one/);
  assert.match(errs(md.replace('Les Éolides arrivent comme nouvelle race jouable. [src: bz-golive]', 'Les Éolides arrivent comme nouvelle race jouable.').replace('The Skyborne arrive as a new playable race. [src: bz-golive]', 'The Skyborne arrive as a new playable race.')), /sections\[0\]\.blocks\[1\]\.items\[0\]: at least one source required/);
  assert.match(errs(md.replace('2026-09-13 : annonce', '13/09 : annonce')), /same YYYY-MM-DD date/);
  assert.match(errs(md.replace('### To be confirmed', '### Confirmed')), /do not match/);
  assert.deepEqual(draftToEntry(await readFile(join(root, '../ops/v16/modele-article.md'), 'utf8')).errors, [], 'the blank template converts');
  assert.deepEqual(parseFrontMatterYAML('a: 1\nb:\n  c: "x: y"\nl:\n- p\n- [q, r]\nm:\n  - k: v\n    w: z'), {a: 1, b: {c: 'x: y'}, l: ['p', ['q', 'r']], m: [{k: 'v', w: 'z'}]});
  assert.throws(() => parseFrontMatterYAML('a: 1\na: 2'), /duplicate key/);
  const dir = await mkdtemp(join(tmpdir(), 'v16-cli-'));
  const bad = join(dir, 'bad.md'); await writeFile(bad, md.replace('status: draft', 'status: published'));
  let code = 0; const out = join(dir, 'batch.json');
  await draftCli([EXAMPLE, bad, '--out', out], {log: () => {}, error: () => {}, setExitCode: c => { code = c; }});
  assert.equal(code, 1);
  await assert.rejects(readFile(out), /ENOENT/);
  await draftCli([EXAMPLE, '--out', out], {log: () => {}, error: () => {}, setExitCode: c => { code = c; }});
  const batch = JSON.parse(await readFile(out, 'utf8'));
  assert.equal(batch.length, 1); assert.equal(batch[0].status, 'draft');
});

test('v16 rendering: format 2 layout, distinct "Avis · IA" box, tags, event date, Discussion link to /community/ (no script, no auto-post)', async () => {
  const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
  const published = (await siteEntries()).filter(e => e.status === 'published');
  setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published);
  const {entry} = await example();
  for (const lang of ['fr', 'en']) {
    const html = renderEntry(entry, lang);
    const order = (lang === 'fr' ? ['id="introduction-title">Introduction', 'id="a-retenir-title">Ce qu’il faut retenir', '-title">Les détails<', '-title">Conséquences pour les joueurs<', '-title">L\'analyse WoW4ever<', 'id="et-maintenant-title">Et maintenant ?', 'id="sources-title">Sources', 'id="discussion-title">Discussion']
      : ['id="introduction-title">Introduction', 'id="a-retenir-title">Key takeaways', '-title">The details<', '-title">What it means for players<', '-title">The WoW4ever analysis<', 'id="et-maintenant-title">What’s next?', 'id="sources-title">Sources', 'id="discussion-title">Discussion']);
    let at = -1;
    for (const marker of order) { const i = html.indexOf(marker); assert.ok(i > at, `${lang}: ${marker}`); at = i; }
    assert.match(html, new RegExp(`<aside class="v16-analysis" aria-label="${ANALYSIS_LABEL[lang]}"><p class="v16-analysis-head"><span class="v16-analysis-badge">${lang === 'fr' ? 'Avis · IA' : 'Opinion · AI'}</span><strong>${ANALYSIS_LABEL[lang]}</strong>`));
    assert.equal((html.match(/class="v16-analysis"/g) ?? []).length, 1);
    assert.match(html, /<ul class="v16-tags"[^>]*><li class="v16-tag">(Lancement|Launch)<\/li>/);
    assert.match(html, new RegExp(`<dt>${lang === 'fr' ? 'Date de l’événement' : 'Event date'}</dt><dd><time datetime="2026-11-04">`));
    assert.ok(html.indexOf(lang === 'fr' ? '<dt>Mis à jour</dt>' : '<dt>Updated</dt>') < html.indexOf(lang === 'fr' ? '<dt>Date de l’événement</dt>' : '<dt>Event date</dt>'));
    assert.match(html, /<section class="article-section v16-discussion" id="discussion"[^>]*>.*<a class="v2-btn is-gold-outline" href="\/community\/" data-community-link>/s);
    assert.doesNotMatch(html, /<script(?! type="module" src="\.\.\/\.\.\/\.\.\/wk-header\.js")(?! src="\.\.\/\.\.\/\.\.\/theme\.js"><\/script>)|style=|<style/);
    assert.match(html, /<meta name="robots" content="noindex,nofollow">/);
    assert.doesNotMatch(html, /rel="canonical"/);
  }
});

test('v16 opt-in only: every published entry page renders exactly as the deployed site (site/wiki), no new published entry', async () => {
  const categories = JSON.parse(await readFile(join(root, 'public/wiki/catalog.json'), 'utf8')).categories;
  // v33 (lot 2, Mathieu t341u, 2026-11-09): site/wiki is the v33 wiki built from this dataset, so EVERY published entry
  // (lot 1 and lot 2 included) must render byte-for-byte as site/wiki — no exclusion, no normalisation.
  const published = (await siteEntries()).filter(e => e.status === 'published');
  // v17: the 9 beginner guides (format 2, tags) are the only additions; every other entry stays format 1 without tags.
  const older = published.filter(e => !e.id.startsWith('guide-debutant-'));
  const V22_FORMAT2 = ['forever-news-golive-nov4', 'article-forever-launch-notes', 'guide-forever-gamepad-support', 'article-forever-familiar', 'forever-news-violet-dust-drops', 'forever-news-forging-forever-taldramir', 'forever-news-class-tuning-nov10', 'forever-news-hotfixes-nov5-6', 'forever-news-pvp-faction-balance', 'forever-news-story-unbowed'];
  const lot2 = lot2NewPublished(published);
  assert.equal(older.filter(e => !isLot1(e) && !isLot2New(e)).length, 189); assert.equal(older.length, 196 + lot2); assert.equal(published.length, 205 + lot2); // v39 (t391u, Oui de Mathieu) : +26 fiches de complétion ; // v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; v33: + 4 lot 2
  assert.ok(older.filter(e => !V22_FORMAT2.includes(e.id)).every(e => e.article === undefined || e.article.format === 1), 'v16 publishes no format 2 article');
  assert.ok(older.filter(e => !V22_FORMAT2.includes(e.id)).every(e => e.tags === undefined && e.eventDate === undefined));
  assert.ok(!published.some(e => ['forever-news-beta'].includes(e.id)), 'AC2 stays a draft');
  setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published);
  const wiki = join(root, '../site/wiki');
  for (const lang of ['fr', 'en']) {
    for (const entry of published) assert.equal(renderEntry(entry, lang), await readFile(join(wiki, entryPath(entry, lang), 'index.html'), 'utf8'), entryPath(entry, lang));
    assert.equal(renderIndex(lang), await readFile(join(wiki, lang, 'wiki/index.html'), 'utf8'));
    assert.equal(renderCategory('news', lang), await readFile(join(wiki, lang, lang === 'fr' ? 'actualites' : 'news', 'index.html'), 'utf8'));
  }
  setVisualLinks([]);
});

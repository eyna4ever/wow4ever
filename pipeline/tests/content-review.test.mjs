import {test} from 'node:test';
import assert from 'node:assert/strict';
import {link, mkdir, mkdtemp, readFile, readdir, rm, stat, symlink, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {contentDigest, transitionRecord} from '../lib/documentary.mjs';
import {createContentReview, main} from '../scripts/content-review.mjs';

// Synthetic fixtures only. None are imported into the documentary store.
const now = '2026-10-19T12:00:00.000Z';
const fixture = (id = 'review-test') => ({id, title: {fr: 'Titre de contrôle', en: 'Review title'},
  description: {fr: 'Description française', en: 'English description'}, category: 'guides', subcategory: 'test',
  status: 'draft', identityConfirmed: false, gameVersion: 'test-version', version: 1, updatedAt: now,
  sources: [{url: 'https://example.org/reference', accessedAt: now, license: 'test-only'}],
  relations: [], steps: [{fr: 'Étape française', en: 'English step'}],
  history: [{at: now, actor: 'PRIVATE-ACTOR', note: 'PRIVATE-NOTE', version: 1}], secret: 'PRIVATE-SECRET'});
const quiet = {log: () => {}};

test('relecture FR/EN explicite des brouillons, traductions, sources et relations sans mutation', () => {
  const first = fixture(), second = fixture('review-related');
  first.relations = [second.id];
  const records = [first, second], before = structuredClone(records), fingerprint = contentDigest(first);
  const review = createContentReview(records);
  assert.equal(review.valid, true);
  assert.equal(review.records, 2);
  assert.match(review.html, /Brouillon/);
  assert.match(review.html, /Identité non confirmée/);
  assert.match(review.html, /Traductions non validées/);
  for (const value of ['Description française', 'English description', 'Étape française', 'English step', 'test-version', now, 'test-only']) assert.ok(review.html.includes(value));
  assert.match(review.html, /href="#entry-1">review-related/);
  assert.match(review.html, /href="https:\/\/example.org\/reference" target="_blank" rel="noopener noreferrer"/);
  assert.doesNotMatch(review.html, /PRIVATE-|<form\b|<button\b/);
  assert.deepEqual(records, before);
  assert.equal(contentDigest(first), fingerprint);
});

test('les champs hostiles sont du texte échappé, jamais des éléments ou attributs actifs', () => {
  const attack = '<img src=x onerror="globalThis.pwned=1"><script>alert(1)</script>\'&';
  const entry = fixture();
  entry.id = attack; entry.title.fr = attack; entry.title.en = attack;
  entry.description.fr = attack; entry.description.en = attack;
  entry.subcategory = attack; entry.gameVersion = attack; entry.updatedAt = attack;
  entry.sources = [{url: 'https://example.org/?q=%22%3E%3Cscript%3E', title: attack, accessedAt: attack, license: attack}];
  entry.steps = [{fr: attack, en: attack}]; entry.relations = [attack];
  const review = createContentReview([entry]);
  assert.equal(review.valid, false);
  assert.doesNotMatch(review.html, /<img\b|<script>alert|<script[^>]+src|href="javascript:|onerror="globalThis/);
  assert.match(review.html, /&lt;img src=x onerror=&quot;globalThis/);
  assert.match(review.html, /&lt;script&gt;alert/);
  assert.match(review.html, /&#39;&amp;/);
  assert.equal((review.html.match(/<script>/g) ?? []).length, 1);
  assert.match(review.html, /Content-Security-Policy/);
  assert.match(review.html, /connect-src 'none'/);
});

test('les références non HTTPS, identifiants de connexion et paramètres secrets ne sont jamais exportés', () => {
  const entry = fixture();
  entry.sources = ['javascript:alert(1)', 'http://example.org/', 'https://user:PRIVATE-PASSWORD@example.org/',
    'https://example.org/?token=PRIVATE-TOKEN', 'https://example.org/?api_key=PRIVATE-APIKEY'].map(url => ({url, accessedAt: now, license: 'test-only'}));
  const review = createContentReview([entry]);
  assert.match(review.html, /Référence HTTPS refusée/);
  assert.doesNotMatch(review.html, /PRIVATE-|href="(?:javascript|http):/);
});

test('le document signale données invalides et relations orphelines tout en restant lisible', () => {
  const entry = fixture(); entry.relations = ['review-missing'];
  const review = createContentReview([null, entry]);
  assert.equal(review.valid, false);
  assert.match(review.html, /entry must be an object/);
  assert.match(review.html, /dangling relation: review-missing/);
  assert.match(review.html, /cible absente/);
  assert.match(review.html, /Erreurs d’intégrité/);
  assert.match(createContentReview({}).html, /dataset must be an array/);
});

test('une validation courante est distinguée de données approuvées modifiées depuis', () => {
  const approval = {actor: 'PRIVATE-REVIEWER', note: 'PRIVATE-REVIEW', now,
    humanReview: true, identity: true, rights: true, translations: true};
  let records = transitionRecord([fixture()], 'review-test', 'submit', approval).records;
  records = transitionRecord(records, 'review-test', 'approve', approval).records;
  const review = createContentReview(records);
  assert.equal(review.valid, true);
  assert.match(review.html, /Traductions validées dans la révision courante/);
  assert.doesNotMatch(review.html, /PRIVATE-/);
  records[0].description.en = 'Changed';
  assert.match(createContentReview(records).html, /Traductions non validées/);
});

test('une base vide présente les douze catégories et ne prétend jamais à la complétude', () => {
  const review = createContentReview([]);
  assert.equal(review.valid, true);
  assert.equal(review.records, 0);
  assert.equal((review.html.match(/<option value="(?:classes|races|zones|instances|professions|items|quests|pvp|creatures|guides|news|glossary)">/g) ?? []).length, 12);
  assert.match(review.html, /Aucune fiche disponible/);
  assert.match(review.html, /complétude.*inconnue/);
});

test('les étapes invalides et identifiants dupliqués ne masquent pas un défaut de validation', () => {
  for (const steps of [{}, [null], [{fr: 'Étape', en: ''}]]) {
    const review = createContentReview([{...fixture(), steps}]);
    assert.equal(review.valid, false);
    assert.match(review.html, /steps must contain/);
  }
  const review = createContentReview([fixture(), fixture()]);
  assert.equal(review.valid, false);
  assert.match(review.html, /duplicate ID/);
  assert.equal((review.html.match(/Erreurs d’intégrité \/ Integrity errors/g) ?? []).length, 2);
});

test('la CLI écrit seulement le HTML privé et conserve les octets et permissions de la base', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-review-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'seed.json'), runtime = join(root, 'runtime'), output = join(root, 'private', 'review.html');
  const body = JSON.stringify([fixture()]);
  await writeFile(seed, body, {mode: 0o640});
  const before = await stat(seed);
  await assert.rejects(main([], quiet), /--output/);
  const result = await main(['--output', output, '--seed', seed, '--runtime-dir', runtime], quiet);
  assert.equal(result.valid, true);
  assert.equal(await readFile(seed, 'utf8'), body);
  assert.equal((await stat(seed)).mode, before.mode);
  assert.equal((await stat(seed)).mtimeMs, before.mtimeMs);
  assert.equal((await stat(output)).mode & 0o777, 0o600);
  assert.deepEqual((await readdir(root)).sort(), ['private', 'seed.json']);
  assert.deepEqual(await readdir(join(root, 'private')), ['review.html']);
  assert.match(await readFile(output, 'utf8'), /Titre de contrôle/);
});

test('la CLI respecte le runtime prioritaire et signale code 1 avec audit sur données invalides', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-review-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'seed.json'), runtime = join(root, 'runtime'), output = join(root, 'review.html');
  await writeFile(seed, '[]\n'); await mkdir(runtime);
  const body = JSON.stringify([{id: 'invalid-runtime', status: 'published'}]);
  await writeFile(join(runtime, 'entries.json'), body);
  let code = 0;
  const result = await main(['--output', output, '--seed', seed, '--runtime-dir', runtime], {...quiet, setExitCode: value => { code = value; }});
  assert.equal(code, 1);
  assert.equal(result.records, 1);
  assert.match(await readFile(output, 'utf8'), /current human review/);
  assert.equal(await readFile(join(runtime, 'entries.json'), 'utf8'), body);
  assert.deepEqual(await readdir(runtime), ['entries.json']);
});

test('la CLI refuse chemins publics, symlinks et collisions directes ou hardlinks avec les sources', async t => {
  const root = await mkdtemp(join(tmpdir(), 'wiki-review-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const seed = join(root, 'seed.html'), runtime = join(root, 'runtime');
  await writeFile(seed, '[]\n'); await mkdir(join(root, 'private'));
  await symlink(join(root, 'private'), join(root, 'alias'));
  await symlink(seed, join(root, 'review.html'));
  await link(seed, join(root, 'hardlink.html'));
  for (const path of [join(root, 'public', 'review.html'), join(root, 'dist', 'review.html')]) {
    await assert.rejects(main(['--output', path, '--seed', seed, '--runtime-dir', runtime], quiet), /public\/ ou dist\//);
  }
  for (const path of [join(root, 'alias', 'review.html'), join(root, 'review.html')]) {
    await assert.rejects(main(['--output', path, '--seed', seed, '--runtime-dir', runtime], quiet), /lien symbolique/);
  }
  for (const path of [seed, join(root, 'hardlink.html')]) {
    await assert.rejects(main(['--output', path, '--seed', seed, '--runtime-dir', runtime], quiet), /remplacer une source/);
  }
  const absentOutput = join(root, 'not-created.html'), aliasSeed = join(root, 'dangling-seed.json');
  await symlink(absentOutput, aliasSeed);
  await assert.rejects(main(['--output', absentOutput, '--seed', aliasSeed, '--runtime-dir', runtime], quiet), /remplacer une source/);
  assert.equal(await readFile(seed, 'utf8'), '[]\n');
});

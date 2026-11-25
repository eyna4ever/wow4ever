import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeQuery, normalizeLanguage, searchEntries, searchSuggestions, safeSourceURL, isDisplayableEntry, readPersonalState, savePersonalState, STORAGE_KEY, toggleValue, progressKey, guideProgress, relatedEntries} from '../lib/ui-core.mjs';

// These isolated synthetic fixtures test UI behavior. They are never copied into the public catalog.
function fixture(id = 'test-ui-alpha', overrides = {}) {
  return {id, status: 'published', publicationValidated: true, title: {fr: 'Test Épée', en: 'Test Sword'}, description: {fr: 'Document synthétique pour tester la recherche.', en: 'Synthetic document for search testing.'}, category: 'items', subcategory: 'test', version: 1, sources: [{url: 'https://example.invalid/ui-test', license: 'Synthetic fixture', accessedAt: '2026-10-18'}], relations: [], ...overrides};
}

test('search normalizes accents, spaces and case without changing source text', () => {
  assert.equal(normalizeQuery('  ÉPÉE   test  '), 'epee test');
  assert.equal(normalizeQuery(null), '');
  const entry = fixture();
  assert.deepEqual(searchEntries([entry], {query: 'epee TEST', lang: 'fr'}), [entry]);
  assert.equal(entry.title.fr, 'Test Épée');
  assert.equal(searchEntries([entry], {query: 'sword', lang: 'fr'}).length, 0);
  assert.equal(searchEntries([entry], {query: 'sword', lang: 'en'}).length, 1);
  assert.equal(normalizeLanguage('de'), 'fr');
});

test('search combines category, favorites and all query words', () => {
  const first = fixture();
  const second = fixture('test-ui-beta', {category: 'guides'});
  assert.deepEqual(searchEntries([first, second], {query: 'epee document', category: 'guides', favoritesOnly: true, favorites: [second.id]}), [second]);
  assert.equal(searchEntries([first, second], {category: 'items', favoritesOnly: true, favorites: [second.id]}).length, 0);
  assert.equal(searchEntries([first], {query: 'epee absent'}).length, 0);
});

test('suggestions use filtered data, require a query and respect limits', () => {
  const entries = [fixture(), fixture('test-ui-beta')];
  assert.deepEqual(searchSuggestions(entries, {query: ''}), []);
  assert.equal(searchSuggestions(entries, {query: 'test'}, 1).length, 1);
  assert.equal(searchSuggestions(entries, {query: 'test'}, -1).length, 0);
  assert.equal(searchSuggestions([], {query: 'classe'}).length, 0);
});

test('browser gate hides drafts and entries without required reviewed provenance', () => {
  assert.equal(isDisplayableEntry(fixture()), true);
  for (const changes of [{status: 'draft'}, {status: 'verified'}, {publicationValidated: false}, {publicationValidated: undefined}, {sources: []}, {title: {fr: 'Test'}}, {sources: [{url: 'javascript:alert(1)', license: 'x', accessedAt: '2026-10-18'}]}]) {
    assert.equal(searchEntries([fixture('test-ui-alpha', changes)]).length, 0);
  }
});

test('source links accept only HTTPS references without credentials', () => {
  assert.equal(safeSourceURL('https://example.invalid/reference'), 'https://example.invalid/reference');
  for (const value of ['javascript:alert(1)', 'data:text/plain,x', 'http://example.invalid', 'https://user:password@example.invalid', '/relative', null]) assert.equal(safeSourceURL(value), null);
});

test('storage supports persistence and safely handles corruption, denial or unknown format', () => {
  const data = new Map();
  const storage = {getItem: key => data.get(key) ?? null, setItem: (key, value) => data.set(key, value)};
  assert.equal(savePersonalState(storage, {lang: 'en', favorites: ['test-ui-alpha', 'test-ui-alpha', 5], progress: ['one']}), true);
  assert.deepEqual(readPersonalState(storage), {version: 1, lang: 'en', favorites: ['test-ui-alpha'], progress: ['one']});
  data.set(STORAGE_KEY, '{');
  assert.deepEqual(readPersonalState(storage).favorites, []);
  data.set(STORAGE_KEY, JSON.stringify({version: 99, favorites: ['test-ui-alpha']}));
  assert.deepEqual(readPersonalState(storage).favorites, []);
  const denied = {getItem() {throw new Error('Denied');}, setItem() {throw new Error('Denied');}};
  assert.deepEqual(readPersonalState(denied).progress, []);
  assert.equal(savePersonalState(denied, {}), false);
  assert.equal(savePersonalState(undefined, {}), false);
});

test('guide progress is scoped to entry revision and toggles preserve unique values', () => {
  const entry = fixture('test-ui-guide', {steps: [{fr: 'Étape test', en: 'Test step'}, {fr: 'Autre étape', en: 'Other step'}]});
  const key = progressKey(entry, 0);
  assert.equal(key, 'test-ui-guide:v1:step:0');
  assert.deepEqual(guideProgress(entry, [key]), {done: 1, total: 2, percent: 50});
  assert.deepEqual(guideProgress({...entry, version: 2}, [key]), {done: 0, total: 2, percent: 0});
  assert.deepEqual(guideProgress(fixture(), [key]), {done: 0, total: 0, percent: 0});
  assert.deepEqual(toggleValue(['a', 'a', 'b'], 'a'), ['b']);
  assert.deepEqual(toggleValue(['a'], 'b'), ['a', 'b']);
  assert.equal(progressKey(entry, -1), null);
});

test('related entries only expose published reviewed documents and exclude self', () => {
  const first = fixture('test-ui-first', {relations: ['test-ui-first', 'test-ui-second', 'test-ui-third', 'absent-entry']});
  const second = fixture('test-ui-second');
  const third = fixture('test-ui-third', {status: 'draft'});
  assert.deepEqual(relatedEntries(first, [first, second, third]), [second]);
});

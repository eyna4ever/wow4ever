import {test} from 'node:test';
import assert from 'node:assert/strict';
import {selectPublicEntries} from '../lib/public-catalog.mjs';
import {transitionRecord, contentDigest} from '../lib/documentary.mjs';

// These records are synthetic fixtures, never catalog data or export content.
const now = '2026-10-18T00:00:00.000Z';
const approval = {actor: 'PRIVATE-REVIEWER', note: 'Reviewed synthetic fixture', now, humanReview: true, identity: true, rights: true, translations: true};
const fixture = (id = 'test-public') => ({id, title: {fr: 'Test', en: 'Test'}, description: {fr: 'Test', en: 'Test'}, category: 'guides', subcategory: 'test', status: 'draft', gameVersion: 'test', version: 1, updatedAt: now, sources: [{url: 'https://example.org/reference', accessedAt: now, license: 'test-only', internal: 'PRIVATE-SOURCE'}], relations: [], history: [{at: now, actor: 'PRIVATE-AUTHOR', note: 'Synthetic test fixture', version: 1}]});
function published(entry = fixture()) {
  let records = transitionRecord([entry], entry.id, 'submit', approval).records;
  records = transitionRecord(records, entry.id, 'approve', approval).records;
  return transitionRecord(records, entry.id, 'publish', {...approval, publish: true}).records[0];
}

test('public selector rejects malformed roots and unpublished states', () => {
  for (const root of [null, {}, false, 'test', 0]) assert.deepEqual(selectPublicEntries(root), []);
  const entry = published();
  for (const status of ['draft', 'review', 'verified']) assert.deepEqual(selectPublicEntries([{...entry, status}]), []);
});

test('public selector requires current complete publication approval', () => {
  const entry = published();
  for (const invalid of [
    {...entry, review: undefined},
    {...entry, identityConfirmed: false},
    {...entry, review: {...entry.review, approved: false}},
    {...entry, review: {...entry.review, rightsConfirmed: false}},
    {...entry, review: {...entry.review, translationsConfirmed: false}},
    {...entry, review: {...entry.review, contentDigest: '0'.repeat(64)}},
    {...entry, description: {...entry.description, fr: 'Unreviewed change'}},
    {...entry, sources: []},
    {...entry, title: {fr: 'Test', en: ''}}
  ]) assert.deepEqual(selectPublicEntries([invalid]), []);
});

test('valid publication yields an explicit public DTO without private metadata', () => {
  const entry = published({...fixture(), confidential: 'PRIVATE-ROOT'});
  const result = selectPublicEntries([entry]);
  assert.equal(result.length, 1);
  assert.equal(result[0].publicationValidated, true);
  assert.equal(result[0].status, 'published');
  assert.equal(result[0].id, entry.id);
  assert.equal('identityConfirmed' in result[0], false);
  assert.equal('review' in result[0], false);
  assert.equal('importMeta' in result[0], false);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE-/);
});

test('public projection never mutates or aliases source records', () => {
  const entry = published({...fixture(), steps: [{fr: 'Étape', en: 'Step'}]});
  const original = structuredClone(entry);
  const [result] = selectPublicEntries([entry]);
  result.title.fr = 'Changed DTO';
  result.sources[0].license = 'Changed DTO';
  result.history[0].note = 'Changed DTO';
  result.steps[0].fr = 'Changed DTO';
  assert.deepEqual(entry, original);
});

test('relations reveal only unambiguous valid public identifiers', () => {
  const draft = fixture('test-private');
  const second = published(fixture('test-second'));
  const first = published(fixture('test-first'));
  first.relations = [draft.id, second.id];
  first.review.contentDigest = contentDigest(first);
  const result = selectPublicEntries([first, second, draft]);
  assert.deepEqual(result[0].relations, [second.id]);
  assert.doesNotMatch(JSON.stringify(result), /test-private/);
});

test('duplicate identifiers exclude all ambiguous publications', () => {
  const entry = published();
  assert.deepEqual(selectPublicEntries([entry, structuredClone(entry)]), []);
  assert.deepEqual(selectPublicEntries([entry, {...fixture(), id: entry.id}]), []);
});

test('optional guide steps must be bounded bilingual data', () => {
  for (const steps of [null, {}, [null], [{fr: 'Étape', en: ''}], [{fr: 'x'.repeat(10_001), en: 'Step'}], Array(201).fill({fr: 'Étape', en: 'Step'})]) {
    // Review protects this exact content, but does not make a malformed UI shape valid.
    const entry = published({...fixture(), steps});
    assert.deepEqual(selectPublicEntries([entry]), []);
  }
  const [entry] = selectPublicEntries([published({...fixture(), steps: [{fr: 'Étape', en: 'Step', private: 'PRIVATE-STEP'}]})]);
  assert.deepEqual(entry.steps, [{fr: 'Étape', en: 'Step'}]);
});

test('one malformed record does not expose it or block an unrelated publication', () => {
  const entry = published();
  const result = selectPublicEntries([null, false, {id: 'test-invalid', status: 'published'}, entry]);
  assert.deepEqual(result.map(record => record.id), [entry.id]);
});

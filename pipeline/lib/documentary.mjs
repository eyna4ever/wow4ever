import {createHash, randomUUID} from 'node:crypto';
import {mkdir, open, readFile, rename, rm, writeFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {applySourcePolicy, policyErrors} from './source-policy.mjs';
import {validateArticle} from './articles.mjs';

export const categories = new Set(['classes', 'races', 'zones', 'instances', 'professions', 'items', 'quests', 'pvp', 'creatures', 'guides', 'news', 'glossary']);
export const limits = Object.freeze({maxRecords: 100, maxBytes: 2_000_000, maxTotalRecords: 10_000, maxSources: 20, staleDays: 180});
const statuses = new Set(['draft', 'review', 'verified', 'published']);
const stableId = /^[a-z0-9][a-z0-9-]{2,99}$/;
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const hasText = (value, max = 100_000) => typeof value === 'string' && value.trim().length > 0 && value.length <= max;
const isDate = value => {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2}))?$/.test(value)) return false;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return false;
  // Date.parse otherwise accepts impossible dates such as February 30.
  const [year, month, day] = value.slice(0, 10).split('-').map(Number);
  return day > 0 && month > 0 && month <= 12 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate();
};
const httpsURL = value => {
  if (!hasText(value, 4096)) return false;
  try { const url = new URL(value); return url.protocol === 'https:' && Boolean(url.hostname) && !url.username && !url.password; } catch { return false; }
};

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (isObject(value)) return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  return value;
}
export function digest(value) { return createHash('sha256').update(JSON.stringify(canonical(value))).digest('hex'); }

/** Normalize JSON only; never coerce IDs, numbers, booleans, or missing translations. */
export function normalizeEntry(value) {
  function clean(item, depth = 0) {
    if (depth > 30) throw new Error('JSON nesting limit exceeded');
    if (typeof item === 'string') return item.trim().normalize('NFC');
    if (item === null || typeof item === 'boolean' || (typeof item === 'number' && Number.isFinite(item))) return item;
    if (Array.isArray(item)) return item.map(value => clean(value, depth + 1));
    if (!isObject(item) || ![Object.prototype, null].includes(Object.getPrototypeOf(item))) throw new Error('JSON values required');
    const entries = Object.entries(item);
    if (entries.some(([key]) => ['__proto__', 'constructor', 'prototype'].includes(key))) throw new Error('unsafe JSON key');
    return Object.fromEntries(entries.map(([key, value]) => [key, clean(value, depth + 1)]));
  }
  const entry = clean(value);
  if (!isObject(entry)) return entry;
  if (Array.isArray(entry.relations)) entry.relations = [...new Set(entry.relations)];
  if (Array.isArray(entry.sources)) {
    const seen = new Set();
    entry.sources = entry.sources.filter(source => {
      if (!isObject(source)) return true;
      if (httpsURL(source.url)) source.url = new URL(source.url).href;
      if (!('gameVersion' in source) && hasText(entry.gameVersion)) source.gameVersion = entry.gameVersion;
      const key = digest(source);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }
  return entry;
}

/** A human approval is tied to the actual document, not its workflow timestamps. */
export function contentDigest(entry) {
  const content = Object.fromEntries(Object.entries(entry).filter(([key]) => !['status', 'updatedAt', 'version', 'history', 'review', 'importMeta', 'identityConfirmed'].includes(key)));
  return digest(content);
}

export function validate(entry, {maxSources = limits.maxSources} = {}) {
  const errors = [];
  if (!isObject(entry)) return ['entry must be an object'];
  try { normalizeEntry(entry); } catch (error) { return [`invalid JSON entry: ${error.message}`]; }
  if (typeof entry.id !== 'string' || !stableId.test(entry.id)) errors.push('invalid stable id');
  for (const key of ['title', 'description']) {
    if (!isObject(entry[key])) { errors.push(`${key} must be an object`); continue; }
    for (const locale of ['fr', 'en']) if (!hasText(entry[key][locale], key === 'title' ? 300 : 100_000)) errors.push(`${key}.${locale} required or too long`);
  }
  if (!categories.has(entry.category)) errors.push('unknown category');
  for (const key of ['subcategory', 'gameVersion']) if (!hasText(entry[key], 300)) errors.push(`${key} required or too long`);
  if (!Number.isSafeInteger(entry.version) || entry.version < 1) errors.push('invalid version');
  if (!statuses.has(entry.status)) errors.push('invalid status');
  if (!isDate(entry.updatedAt)) errors.push('invalid update date');
  if ('identityConfirmed' in entry && typeof entry.identityConfirmed !== 'boolean') errors.push('identityConfirmed must be boolean');
  if (!Array.isArray(entry.sources) || !entry.sources.length || entry.sources.length > maxSources) errors.push(`1 to ${maxSources} sources required`);
  for (const [index, source] of (Array.isArray(entry.sources) ? entry.sources : []).entries()) {
    if (!isObject(source)) { errors.push(`source ${index} must be an object`); continue; }
    if (!httpsURL(source.url)) errors.push(`source ${index}: https reference without credentials required`);
    if (!hasText(source.license, 2000) || !isDate(source.accessedAt)) errors.push(`source ${index}: license/date required`);
    if ('gameVersion' in source && !hasText(source.gameVersion, 300)) errors.push(`source ${index}: invalid gameVersion`);
    if (source.gameVersion && source.gameVersion !== entry.gameVersion) errors.push(`source ${index}: version differs from entry`);
    if ('title' in source && !hasText(source.title, 1000)) errors.push(`source ${index}: invalid title`);
  }
  if (!Array.isArray(entry.relations) || entry.relations.some(id => typeof id !== 'string' || !stableId.test(id)) || new Set(entry.relations).size !== entry.relations.length) errors.push('unique stable relation IDs required');
  if (Array.isArray(entry.relations) && entry.relations.includes(entry.id)) errors.push('self relation is not allowed');
  if (!Array.isArray(entry.history) || !entry.history.length) errors.push('history required');
  for (const [index, change] of (Array.isArray(entry.history) ? entry.history : []).entries()) {
    if (!isObject(change) || !hasText(change.actor, 300) || !hasText(change.note, 4000) || !isDate(change.at)) errors.push(`history ${index}: actor, note and valid date required`);
    if (isObject(change) && 'version' in change && (!Number.isSafeInteger(change.version) || change.version < 1 || change.version > entry.version)) errors.push(`history ${index}: invalid revision version`);
  }
  if ('article' in entry) errors.push(...validateArticle(entry));
  // v16 optional metadata: tags (bilingual chips) and the date of the event an entry is about.
  if ('tags' in entry) {
    const tags = entry.tags;
    if (!Array.isArray(tags) || !tags.length || tags.length > 8) errors.push('tags: 1 to 8 tags required when present');
    else {
      if (!tags.every(tag => isObject(tag) && ['fr', 'en'].every(lang => hasText(tag[lang], 40)) && Object.keys(tag).length === 2)) errors.push('tags: each tag needs fr/en text (40 characters max)');
      else if (new Set(tags.map(tag => tag.fr.toLowerCase())).size !== tags.length || new Set(tags.map(tag => tag.en.toLowerCase())).size !== tags.length) errors.push('tags: duplicate tag');
    }
  }
  if ('eventDate' in entry && !(typeof entry.eventDate === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(entry.eventDate) && isDate(entry.eventDate))) errors.push('eventDate must be a valid YYYY-MM-DD date');
  if ('importMeta' in entry && (!isObject(entry.importMeta) || !/^[a-f0-9]{64}$/.test(entry.importMeta.fingerprint ?? '') || !isDate(entry.importMeta.importedAt) || !statuses.has(entry.importMeta.sourceStatus))) errors.push('invalid import receipt');
  if (['verified', 'published'].includes(entry.status)) {
    const review = entry.review;
    if (!entry.identityConfirmed || !isObject(review) || review.approved !== true || !hasText(review.reviewer, 300) || !isDate(review.at) || review.rightsConfirmed !== true || review.translationsConfirmed !== true || review.contentDigest !== contentDigest(entry)) errors.push('current human review, confirmed identity, rights and translations required');
  }
  // V2.1 étape 03: source policy (wiki.gg refused; non-official sources can never carry an official status).
  errors.push(...policyErrors(entry));
  return errors;
}

export function auditDataset(records, options = {}) {
  if (!Array.isArray(records)) return {entries: 0, published: 0, errors: [{id: null, errors: ['dataset must be an array']}], stale: []};
  const invalid = [], ids = new Set(), now = options.now ? new Date(options.now).getTime() : Date.now();
  for (const [index, entry] of records.entries()) {
    const errors = validate(entry, options);
    const id = isObject(entry) && typeof entry.id === 'string' ? entry.id : null;
    if (id && ids.has(id)) errors.push('duplicate ID');
    if (id) ids.add(id);
    if (errors.length) invalid.push({index, id, errors});
  }
  for (const [index, entry] of records.entries()) {
    if (!isObject(entry) || !Array.isArray(entry.relations)) continue;
    const missing = entry.relations.filter(id => typeof id === 'string' && !ids.has(id));
    if (missing.length) invalid.push({index, id: entry.id ?? null, errors: missing.map(id => `dangling relation: ${id}`)});
  }
  const stale = records.filter(entry => isObject(entry) && [entry.updatedAt, ...(Array.isArray(entry.sources) ? entry.sources.map(source => source?.accessedAt) : [])].some(value => isDate(value) && now - Date.parse(value) > (options.staleDays ?? limits.staleDays) * 86_400_000)).map(entry => entry.id);
  return {entries: records.length, published: records.filter(entry => entry?.status === 'published').length, errors: invalid, stale};
}

function quota(value, label, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) throw new Error(`${label} must be a non-negative safe integer`);
  return value;
}

/** Import never trusts a foreign publication status or human-approval claim. */
export function merge(current, incoming, options = {}) {
  if (!Array.isArray(current) || !Array.isArray(incoming)) throw new Error('current dataset and incoming batch must be arrays');
  const settings = {...limits, ...options};
  for (const key of ['maxRecords', 'maxBytes', 'maxTotalRecords', 'maxSources', 'staleDays']) quota(settings[key], key);
  if (incoming.length > settings.maxRecords) throw new Error('batch quota exceeded');
  let byteLength;
  try { byteLength = Buffer.byteLength(JSON.stringify(incoming)); } catch { throw new Error('incoming batch must contain JSON values'); }
  if (byteLength > settings.maxBytes) throw new Error('byte quota exceeded');
  const currentAudit = auditDataset(current, settings);
  if (currentAudit.errors.length) throw new Error('current dataset is invalid; repair or restore it before importing');
  const now = options.now ? new Date(options.now).toISOString() : new Date().toISOString();
  const records = structuredClone(current), byId = new Map(records.map(entry => [entry.id, entry]));
  const report = {format: 1, operation: 'import', at: now, inputRecords: incoming.length, inputBytes: byteLength, inserted: [], duplicates: [], conflicts: [], invalid: [], quarantined: [], downgraded: [], stale: [], cost: {currency: 'EUR', actual: 0, ceiling: 0}, stages: {normalization: 'complete', deduplication: 'complete', verification: 'structural-only', translation: 'human-required', publication: 'human-required'}};
  // Build candidates before resolving references so forward references in one batch work.
  let candidates = [];
  const candidateById = new Map(), blockedIds = new Set();
  for (const [index, raw] of incoming.entries()) {
    let entry;
    try { entry = normalizeEntry(raw); } catch (error) { report.invalid.push({index, id: raw?.id ?? null, errors: [error.message]}); continue; }
    if (!isObject(entry)) { report.invalid.push({index, id: null, errors: ['entry must be an object']}); continue; }
    const fingerprint = digest(Object.fromEntries(Object.entries(entry).filter(([key]) => key !== 'importMeta')));
    const originalStatus = entry.status;
    // Preserve validation of the incoming status, but drop every imported approval.
    entry.status = statuses.has(originalStatus) ? 'draft' : originalStatus;
    entry.identityConfirmed = false;
    delete entry.review;
    delete entry.importMeta;
    // V2.1 étape 03 / t359u: refused hosts (wiki.gg) are quarantined; non-official claims are forced to « à confirmer », except stamped 70862 extracts already marked « données du jeu ».
    const policy = applySourcePolicy(entry);
    if (policy.refused.length) { report.quarantined.push({index, id: typeof entry.id === 'string' ? entry.id : null, reason: 'source refusée (wiki.gg exclu)', urls: policy.refused}); continue; }
    entry = policy.entry;
    if (policy.downgraded.length) report.downgraded.push({index, id: entry.id, changes: policy.downgraded});
    const errors = validate(entry, settings);
    if (errors.length) { report.invalid.push({index, id: typeof entry.id === 'string' ? entry.id : null, errors}); continue; }
    const existing = byId.get(entry.id);
    if (existing) {
      const comparable = normalizeEntry(existing);
      delete comparable.importMeta;
      const existingFingerprint = existing.importMeta?.fingerprint ?? digest(comparable);
      if (existingFingerprint === fingerprint || digest(comparable) === fingerprint) report.duplicates.push(entry.id);
      else report.conflicts.push({id: entry.id, existingVersion: existing.version, incomingVersion: entry.version, reason: 'same ID with different content; explicit human resolution required'});
      continue;
    }
    if (blockedIds.has(entry.id)) { report.conflicts.push({id: entry.id, reason: 'conflicting ID within incoming batch'}); continue; }
    if (candidateById.has(entry.id)) {
      if (candidateById.get(entry.id) === fingerprint) report.duplicates.push(entry.id);
      else {
        report.conflicts.push({id: entry.id, reason: 'same ID with different content within incoming batch; neither candidate imported'});
        candidates = candidates.filter(candidate => candidate.entry.id !== entry.id);
        blockedIds.add(entry.id);
      }
      continue;
    }
    candidateById.set(entry.id, fingerprint);
    entry.importMeta = {fingerprint, importedAt: now, sourceStatus: originalStatus};
    entry.history.push({at: now, actor: 'local-import', note: 'Imported to draft; external approval is not trusted.', version: entry.version});
    candidates.push({entry, index});
  }
  // Repeatedly remove dangling candidates; a rejected reference cannot leave a dependent record behind.
  let accepted = candidates;
  while (true) {
    const available = new Set([...byId.keys(), ...accepted.map(candidate => candidate.entry.id)]);
    const rejected = accepted.filter(({entry}) => entry.relations.some(id => !available.has(id)));
    if (!rejected.length) break;
    for (const {entry, index} of rejected) report.invalid.push({index, id: entry.id, errors: entry.relations.filter(id => !available.has(id)).map(id => `dangling relation: ${id}`)});
    const rejectedIds = new Set(rejected.map(candidate => candidate.entry.id));
    accepted = accepted.filter(candidate => !rejectedIds.has(candidate.entry.id));
  }
  if (records.length + accepted.length > settings.maxTotalRecords) throw new Error('total dataset quota exceeded');
  for (const {entry} of accepted) { records.push(entry); report.inserted.push(entry.id); }
  report.stale = auditDataset(records, {...settings, now}).stale;
  return {records, report};
}

export function transitionRecord(records, id, action, options = {}) {
  const audit = auditDataset(records);
  if (audit.errors.length) throw new Error('dataset is invalid; repair it before review');
  if (!hasText(options.actor, 300) || !hasText(options.note, 4000)) throw new Error('actor and review note are required');
  const result = structuredClone(records), entry = result.find(record => record.id === id);
  if (!entry) throw new Error('entry not found');
  const now = options.now ? new Date(options.now).toISOString() : new Date().toISOString();
  if (action === 'submit') {
    if (entry.status !== 'draft') throw new Error('only a draft can be submitted');
    entry.status = 'review';
    delete entry.review;
  } else if (action === 'approve') {
    if (entry.status !== 'review') throw new Error('only a submitted entry can be approved');
    if (![options.humanReview, options.identity, options.rights, options.translations].every(value => value === true)) throw new Error('explicit human, identity, rights and translation attestations are required');
    entry.identityConfirmed = true;
    entry.status = 'verified';
    entry.review = {approved: true, reviewer: options.actor.trim(), at: now, rightsConfirmed: true, translationsConfirmed: true, contentDigest: contentDigest(entry)};
  } else if (action === 'publish') {
    if (entry.status !== 'verified' || options.publish !== true) throw new Error('publication requires a verified entry and --confirm-publish');
    entry.status = 'published';
  } else if (action === 'reject') {
    if (!['review', 'verified', 'published'].includes(entry.status)) throw new Error('entry must be in review, verified or published');
    entry.status = 'draft';
    entry.identityConfirmed = false;
    delete entry.review;
  } else throw new Error('unknown review action');
  entry.version += 1;
  entry.updatedAt = now;
  entry.history.push({at: now, actor: options.actor.trim(), note: `${action}: ${options.note.trim()}`, version: entry.version});
  const errors = validate(entry);
  if (errors.length) throw new Error(`review failed: ${errors.join('; ')}`);
  return {records: result, report: {format: 1, operation: action, at: now, id, actor: options.actor.trim(), status: entry.status, version: entry.version, cost: {currency: 'EUR', actual: 0, ceiling: 0}}};
}

/** Explicit local correction replaces content, withdraws approval, and preserves local history. */
export function reviseRecord(records, id, incoming, options = {}) {
  if (auditDataset(records).errors.length) throw new Error('dataset is invalid; repair it before revision');
  if (!hasText(options.actor, 300) || !hasText(options.note, 4000)) throw new Error('actor and revision note are required');
  const previous = records.find(entry => entry.id === id);
  if (!previous) throw new Error('entry not found');
  const entry = normalizeEntry(incoming);
  if (!isObject(entry) || entry.id !== id) throw new Error('revision must preserve the stable entry ID');
  if (!statuses.has(entry.status)) throw new Error('revision has an invalid status');
  const importedContent = Object.fromEntries(Object.entries(entry).filter(([key]) => key !== 'importMeta'));
  const now = options.now ? new Date(options.now).toISOString() : new Date().toISOString();
  entry.status = 'draft';
  entry.identityConfirmed = false;
  delete entry.review;
  entry.version = previous.version + 1;
  entry.updatedAt = now;
  entry.importMeta = {fingerprint: digest(importedContent), importedAt: now, sourceStatus: incoming.status};
  entry.history = [...structuredClone(previous.history), {at: now, actor: options.actor.trim(), note: `revise: ${options.note.trim()}`, version: entry.version}];
  const result = records.map(record => record.id === id ? entry : structuredClone(record));
  const audit = auditDataset(result);
  if (audit.errors.length) throw new Error(`revision failed: ${audit.errors.flatMap(item => item.errors).join('; ')}`);
  return {records: result, report: {format: 1, operation: 'revise', at: now, id, actor: options.actor.trim(), status: 'draft', version: entry.version, previousContentDigest: contentDigest(previous), contentDigest: contentDigest(entry), cost: {currency: 'EUR', actual: 0, ceiling: 0}}};
}

export function parseArgs(argv, {values = [], flags = []} = {}) {
  const options = {}, positional = [];
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith('--')) { positional.push(arg); continue; }
    const name = arg.slice(2);
    if (name in options) throw new Error(`duplicate option: ${arg}`);
    if (flags.includes(name)) options[name] = true;
    else if (values.includes(name)) {
      const value = argv[++index];
      if (!value || value.startsWith('--')) throw new Error(`value required for ${arg}`);
      options[name] = value;
    } else throw new Error(`unknown option: ${arg}`);
  }
  return {options, positional};
}

export async function readJSON(path, {maxBytes = 50_000_000} = {}) {
  const handle = await open(path, 'r');
  try {
    if ((await handle.stat()).size > maxBytes) throw new Error('file byte quota exceeded');
    const content = await handle.readFile('utf8');
    if (Buffer.byteLength(content) > maxBytes) throw new Error('file byte quota exceeded');
    return JSON.parse(content);
  } finally { await handle.close(); }
}

export async function loadDataset({runtimeDir = resolve('runtime'), seedPath = resolve('data/entries.json')} = {}) {
  try { return await readJSON(join(runtimeDir, 'entries.json')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; return readJSON(seedPath); }
}

export async function withDatasetLock(runtimeDir, task) {
  await mkdir(runtimeDir, {recursive: true, mode: 0o700});
  const lock = join(runtimeDir, '.documentary-lock');
  try { await mkdir(lock, {mode: 0o700}); }
  catch (error) { if (error.code === 'EEXIST') throw new Error('documentary store is locked; verify the other process before removing its lock'); throw error; }
  try {
    await writeFile(join(lock, 'owner.json'), JSON.stringify({pid: process.pid, at: new Date().toISOString()}), {mode: 0o600});
    return await task();
  } finally { await rm(lock, {recursive: true, force: true}); }
}

async function atomicJSON(path, value) {
  const temporary = `${path}.${randomUUID()}.tmp`;
  const handle = await open(temporary, 'wx', 0o600);
  try { await handle.writeFile(`${JSON.stringify(value, null, 2)}\n`); await handle.sync(); }
  finally { await handle.close(); }
  try { await rename(temporary, path); }
  catch (error) { await rm(temporary, {force: true}); throw error; }
}

/** Retain rejected/no-change import reports too, without rewriting the dataset. */
export async function persistReport(runtimeDir, report) {
  const reports = join(runtimeDir, 'reports');
  await mkdir(reports, {recursive: true, mode: 0o700});
  const reportPath = join(reports, `${new Date().toISOString().replaceAll(':', '-')}-${randomUUID()}.json`);
  const receipt = {...report, reportPath};
  await atomicJSON(reportPath, receipt);
  return receipt;
}

/** Caller holds the store lock. The checksum-protected backup is durable before replacement. */
export async function commitDataset(runtimeDir, before, after, report) {
  const audit = auditDataset(after);
  if (audit.errors.length) throw new Error('refusing to persist invalid records');
  const token = `${new Date().toISOString().replaceAll(':', '-')}-${randomUUID()}`;
  const backups = join(runtimeDir, 'backups'), reports = join(runtimeDir, 'reports');
  await mkdir(backups, {recursive: true, mode: 0o700});
  await mkdir(reports, {recursive: true, mode: 0o700});
  const backup = join(backups, `${token}.json`);
  const backupBody = {format: 1, at: new Date().toISOString(), operation: report.operation, checksum: digest(before), records: before};
  const backupHandle = await open(backup, 'wx', 0o600);
  try { await backupHandle.writeFile(`${JSON.stringify(backupBody, null, 2)}\n`); await backupHandle.sync(); }
  finally { await backupHandle.close(); }
  const reportPath = join(reports, `${token}.json`);
  const receipt = {...report, backup, beforeChecksum: digest(before), afterChecksum: digest(after), committed: false};
  await atomicJSON(reportPath, receipt);
  await atomicJSON(join(runtimeDir, 'entries.json'), after);
  receipt.committed = true;
  await atomicJSON(reportPath, receipt);
  return {...receipt, reportPath};
}

export function decodeBackup(backup) {
  if (!isObject(backup) || backup.format !== 1 || !Array.isArray(backup.records) || backup.checksum !== digest(backup.records)) throw new Error('invalid backup or checksum mismatch');
  const audit = auditDataset(backup.records);
  if (audit.errors.length) throw new Error('backup records do not pass integrity checks');
  return backup.records;
}

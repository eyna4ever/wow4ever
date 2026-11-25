import {validate} from './documentary.mjs';
import {entryPath, articlePlainText} from './articles.mjs';
import {classifySource, entryVerification, isGameDataSource, VERIFICATION} from './source-policy.mjs';

const bilingual = value => value !== null && typeof value === 'object' && !Array.isArray(value)
  && ['fr', 'en'].every(lang => typeof value[lang] === 'string' && value[lang].trim().length > 0 && value[lang].length <= 10_000);

function toDTO(entry, visibleIds, status) {
  // V2.1 étape 03: the computed verification and the non-official source tiers travel with the DTO only when they
  // differ from the official default, so fully official pages render byte-for-byte as before.
  const verification = entryVerification(entry);
  return {
    id: entry.id,
    title: {fr: entry.title.fr, en: entry.title.en},
    description: {fr: entry.description.fr, en: entry.description.en},
    category: entry.category,
    subcategory: entry.subcategory,
    status,
    publicationValidated: status === 'published',
    gameVersion: entry.gameVersion,
    version: entry.version,
    updatedAt: entry.updatedAt,
    ...(verification === VERIFICATION.official ? {} : {verification}),
    url: {fr: entryPath(entry, 'fr'), en: entryPath(entry, 'en')},
    sources: entry.sources.map(source => ({
      ...(source.key === undefined ? {} : {key: source.key}),
      ...(source.language === undefined ? {} : {language: source.language}),
      ...(source.publishedAt === undefined ? {} : {publishedAt: source.publishedAt}),
      ...(source.undated === true && source.publishedAt === undefined ? {undated: true} : {}),   // v17: official page without a shown date
      url: source.url,
      accessedAt: source.accessedAt,
      license: source.license,
      ...(source.title === undefined ? {} : {title: source.title}),
      ...(source.gameVersion === undefined ? {} : {gameVersion: source.gameVersion}),
      ...(classifySource(source.url) === 'officiel' ? {} : {tier: classifySource(source.url), verification: isGameDataSource(source) ? VERIFICATION.gameData : VERIFICATION.unconfirmed})
    })),
    relations: entry.relations.filter(id => visibleIds.has(id)),
    history: entry.history.map(change => ({
      at: change.at,
      note: change.note,
      ...(change.version === undefined ? {} : {version: change.version})
    })),
    ...(entry.steps === undefined ? {} : {steps: entry.steps.map(step => ({fr: step.fr, en: step.en}))}),
    ...(entry.article === undefined ? {} : {article: structuredClone(entry.article)}),
    ...(entry.tags === undefined ? {} : {tags: entry.tags.map(tag => ({fr: tag.fr, en: tag.en}))}),
    ...(entry.eventDate === undefined ? {} : {eventDate: entry.eventDate})
  };
}

function uniqueValid(records, accept) {
  if (!Array.isArray(records)) return [];
  const frequencies = new Map();
  for (const entry of records) {
    if (entry && typeof entry.id === 'string') frequencies.set(entry.id, (frequencies.get(entry.id) ?? 0) + 1);
  }
  return records.filter(entry => {
    if (!entry || !accept(entry) || frequencies.get(entry.id) !== 1) return false;
    if (validate(entry).length !== 0) return false;
    if ('steps' in entry && (!Array.isArray(entry.steps) || entry.steps.length > 200 || !entry.steps.every(bilingual))) return false;
    return true;
  });
}

/**
 * Server/build boundary. Only complete, currently reviewed publications become
 * public DTOs. The source records, editorial attestations and private fields are
 * never serialized. This module depends on Node and must not enter client code.
 */
export function selectPublicEntries(records) {
  const publications = uniqueValid(records, entry => entry.status === 'published');
  const publicIds = new Set(publications.map(entry => entry.id));
  return publications.map(entry => toDTO(entry, publicIds, 'published'));
}

/**
 * Preview boundary — LOCAL REVIEW ONLY, never packaged or deployed: every
 * structurally valid entry, drafts included, each carrying its real status.
 */
export function selectPreviewEntries(records) {
  const entries = uniqueValid(records, () => true);
  const ids = new Set(entries.map(entry => entry.id));
  return entries.map(entry => toDTO(entry, ids, entry.status));
}

/** Home catalogue DTO: long article bodies are replaced by plain search text. */
export function homeEntries(entries) {
  return (Array.isArray(entries) ? entries : []).map(entry => {
    if (entry.article === undefined) return entry;
    const {article, ...rest} = entry;
    return {...rest, hasArticle: true, searchText: {fr: articlePlainText(entry, 'fr'), en: articlePlainText(entry, 'en')}};
  });
}

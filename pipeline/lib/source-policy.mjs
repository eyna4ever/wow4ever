/**
 * V2.1 étape 03 — politique de sources (décisions de Mathieu du 09/11/2026).
 * Pure functions, no I/O. Used by documentary.mjs (validate/merge), public-catalog.mjs and the renderers.
 *
 *  - officiel     : pages Blizzard (news, site du jeu, forums officiels, comptes X Blizzard). Seul niveau qui peut porter
 *                   « officiel confirmé ».
 *  - extrait_client : bases de fans sans licence ou extraites du client (Eternadex, Wowhead, wago.tools, wow.tools).
 *                   Par défaut « à confirmer ». Exception t359u (13/11/2026) : un extrait tamponné du client
 *                   WoW Forever build 1.60.1.70862 peut porter « données du jeu » (ce n’est pas « officiel confirmé »).
 *  - communautaire : toute autre source tierce. Publiable uniquement avec « à confirmer ».
 *  - refuse       : *.wiki.gg (warcraft.wiki.gg exclu par décision du 09/11/2026). Jamais importé, jamais publié.
 * A claim (entry, article block, fact) is official only when at least ONE of ITS OWN sources is official: mixing an
 * official source into an entry never upgrades a block that cites only non-official sources.
 */
export const TIERS = Object.freeze(['officiel', 'extrait_client', 'communautaire', 'refuse']);
export const VERIFICATION = Object.freeze({official: 'officiel confirmé', inGame: 'vérifié en jeu', unconfirmed: 'à confirmer', obsolete: 'obsolète', gameData: 'données du jeu'});
export const OFFICIAL_CLAIMS = Object.freeze(['officiel confirmé', 'vérifié en jeu']);
export const FOREVER_CLIENT_BUILD = '1.60.1.70862';
export const UNCONFIRMED_LABEL = Object.freeze({fr: 'À confirmer', en: 'Unconfirmed — to be confirmed'});
export const GAME_DATA_LABEL = Object.freeze({fr: 'Données du jeu (client 1.60.1.70862)', en: 'Game data (client 1.60.1.70862)'});

/** True when an extrait_client source is stamped with the Forever client build 1.60.1.70862. */
export function isStampedClientExtract(source) {
  if (classifySource(source?.url) !== 'extrait_client') return false;
  if (source?.clientBuild === FOREVER_CLIENT_BUILD || source?.build === FOREVER_CLIENT_BUILD) return true;
  const text = `${source?.title ?? ''} ${source?.gameVersion ?? ''}`;
  return text.includes(FOREVER_CLIENT_BUILD);
}

/** Unofficial source whose verification may stay « données du jeu » (stamped 70862 extract). */
export function isGameDataSource(source) {
  return source?.verification === VERIFICATION.gameData && isStampedClientExtract(source);
}

const OFFICIAL_HOSTS = /^(news\.blizzard\.com|worldofwarcraft\.blizzard\.com|(us|eu)\.forums\.blizzard\.com|www\.blizzard\.com|blizzard\.com|eu\.support\.blizzard\.com|us\.support\.blizzard\.com)$/;
const OFFICIAL_X = /^\/(blizzard[a-z0-9_]*|warcraft[a-z0-9_]*|wow_?forever[a-z0-9_]*)(\/|$)/i;
const CLIENT_EXTRACT_HOSTS = /(^|\.)(eternadex\.com|wowhead\.com|wago\.tools|wow\.tools|wowdb\.com)$/;
const REFUSED_HOSTS = /(^|\.)wiki\.gg$/;

export function classifySource(url) {
  let parsed;
  try { parsed = new URL(String(url ?? '')); } catch { return 'communautaire'; }
  const host = parsed.hostname.toLowerCase().replace(/\.$/, '');
  if (REFUSED_HOSTS.test(host)) return 'refuse';
  if (parsed.protocol === 'https:' && OFFICIAL_HOSTS.test(host)) return 'officiel';
  if (parsed.protocol === 'https:' && (host === 'x.com' || host === 'twitter.com') && OFFICIAL_X.test(parsed.pathname)) return 'officiel';
  if (CLIENT_EXTRACT_HOSTS.test(host)) return 'extrait_client';
  return 'communautaire';
}
export const isOfficial = source => classifySource(source?.url) === 'officiel';

/** Sources matching a block `src` key (keys may omit the -fr/-en suffix, as in articles.mjs). */
export function sourcesForKeys(entry, keys) {
  const all = Array.isArray(entry?.sources) ? entry.sources : [];
  return all.filter(source => (keys ?? []).some(key => source?.key === key || String(source?.key ?? '').startsWith(`${key}-`)));
}
export const blockIsOfficial = (entry, src) => sourcesForKeys(entry, src).some(isOfficial);

/** Computed verification for a whole entry: official only if at least one official source. */
export function entryVerification(entry) {
  const sources = Array.isArray(entry?.sources) ? entry.sources : [];
  if (entry?.verification === VERIFICATION.obsolete) return VERIFICATION.obsolete;
  if (sources.some(isOfficial)) return VERIFICATION.official;
  if (entry?.verification === VERIFICATION.gameData && sources.some(isStampedClientExtract)) return VERIFICATION.gameData;
  return VERIFICATION.unconfirmed;
}

/** Group keys (source key minus -fr/-en) whose every version is non-official — used to tag citations. */
export function unofficialGroupKeys(entry) {
  const byGroup = new Map();
  for (const source of entry?.sources ?? []) {
    const key = String(source?.key ?? source?.url ?? '').replace(/-(fr|en)$/, '');
    byGroup.set(key, (byGroup.get(key) ?? false) || isOfficial(source));
  }
  return new Set([...byGroup].filter(([, official]) => !official).map(([key]) => key));
}

/** Group keys whose every version is a stamped 70862 client extract marked « données du jeu ». */
export function gameDataGroupKeys(entry) {
  const byGroup = new Map();
  for (const source of entry?.sources ?? []) {
    const key = String(source?.key ?? source?.url ?? '').replace(/-(fr|en)$/, '');
    const cur = byGroup.get(key) ?? {ok: true, any: false};
    cur.any = true;
    cur.ok = cur.ok && isGameDataSource(source);
    byGroup.set(key, cur);
  }
  return new Set([...byGroup].filter(([, g]) => g.any && g.ok).map(([key]) => key));
}

function* claimBlocks(entry) {
  const article = entry?.article;
  if (!article || typeof article !== 'object') return;
  if (article.lead) yield {where: 'article.lead', block: article.lead};
  for (const [i, p] of (article.keyPoints ?? []).entries()) yield {where: `article.keyPoints[${i}]`, block: p};
  for (const [s, section] of (article.sections ?? []).entries()) for (const [b, block] of (section?.blocks ?? []).entries()) {
    if (block?.type === 'analysis') continue;
    yield {where: `article.sections[${s}].blocks[${b}]`, block};
    for (const [k, item] of (block?.type === 'list' ? block.items ?? [] : []).entries()) yield {where: `article.sections[${s}].blocks[${b}].items[${k}]`, block: item};
  }
  for (const [i, item] of (article.confirmed ?? []).entries()) yield {where: `article.confirmed[${i}]`, block: item, confirmed: true};
}

/**
 * Validation errors (never mutates). Called by documentary.validate(), so a hand edit of entries.json cannot
 * bypass the policy either.
 */
export function policyErrors(entry) {
  const errors = [];
  const sources = Array.isArray(entry?.sources) ? entry.sources : [];
  for (const [i, source] of sources.entries()) {
    const tier = classifySource(source?.url);
    if (tier === 'refuse') errors.push(`sources[${i}]: source refusée par la politique (wiki.gg exclu) — ${source?.url}`);
    if (tier !== 'officiel' && OFFICIAL_CLAIMS.includes(source?.verification)) errors.push(`sources[${i}]: une source ${tier} ne peut pas être « ${source.verification} »`);
    if (source?.verification === VERIFICATION.gameData && !isStampedClientExtract(source)) errors.push(`sources[${i}]: « données du jeu » réservé à un extrait du client tamponné ${FOREVER_CLIENT_BUILD}`);
    if (source?.verification === VERIFICATION.inGame && !(source?.proofType === 'constat en jeu' && source?.observedBy && source?.build)) errors.push(`sources[${i}]: « vérifié en jeu » exige proofType, observedBy et build`);
  }
  if (OFFICIAL_CLAIMS.includes(entry?.verification) && !sources.some(isOfficial)) errors.push(`verification « ${entry.verification} » interdite : aucune source officielle Blizzard`);
  if (entry?.verification === VERIFICATION.gameData && !sources.some(isStampedClientExtract)) errors.push(`verification « données du jeu » interdite : aucun extrait du client tamponné ${FOREVER_CLIENT_BUILD}`);
  for (const [i, fact] of (Array.isArray(entry?.facts) ? entry.facts : []).entries()) {
    if (OFFICIAL_CLAIMS.includes(fact?.status) && !sourcesForKeys(entry, fact?.src).some(isOfficial)) errors.push(`facts[${i}]: « ${fact.status} » interdit sans source officielle propre au fait`);
  }
  for (const {where, block, confirmed} of claimBlocks(entry)) {
    if (!Array.isArray(block?.src)) continue;
    const official = blockIsOfficial(entry, block.src);
    if (confirmed && !official) errors.push(`${where}: rangé dans « confirmé par les sources officielles » sans source officielle`);
    if (!official && OFFICIAL_CLAIMS.includes(block?.status)) errors.push(`${where}: « ${block.status} » interdit sans source officielle`);
  }
  return errors;
}

/**
 * Import-time normalisation (returns {entry, downgraded[], refused[]}). Never upgrades anything:
 *  - refused sources → the whole record is quarantined by the caller;
 *  - non-official sources, facts, blocks and the entry itself are forced to « à confirmer »,
 *    except a stamped 1.60.1.70862 client extract already marked « données du jeu » (never auto-upgraded);
 *  - article.confirmed items without an official source move to article.pending.
 */
export function applySourcePolicy(input) {
  const entry = structuredClone(input);
  const downgraded = [], refused = [];
  const sources = Array.isArray(entry.sources) ? entry.sources : [];
  for (const [i, source] of sources.entries()) {
    if (!source || typeof source !== 'object') continue;
    const tier = classifySource(source.url);
    if (tier === 'refuse') { refused.push(source.url); continue; }
    if (tier !== 'officiel' && !isGameDataSource(source) && source.verification !== VERIFICATION.unconfirmed) {
      if (source.verification !== undefined) downgraded.push({where: `sources[${i}]`, from: source.verification, to: VERIFICATION.unconfirmed});
      source.verification = VERIFICATION.unconfirmed;
    }
  }
  const computed = entryVerification(entry);
  if (OFFICIAL_CLAIMS.includes(entry.verification) && computed !== VERIFICATION.official) downgraded.push({where: 'verification', from: entry.verification, to: computed});
  if (computed === VERIFICATION.unconfirmed) {
    if (entry.verification === VERIFICATION.gameData && sources.some(isStampedClientExtract)) {
      // keep « données du jeu » on a client-only page sourced by a stamped 70862 extract
    } else {
      entry.verification = VERIFICATION.unconfirmed;
    }
  }
  const keepFactStatus = (status, src) => {
    if (status === VERIFICATION.unconfirmed) return true;
    if (sourcesForKeys(entry, src).some(isOfficial)) return true;
    return status === VERIFICATION.gameData && sourcesForKeys(entry, src).length && sourcesForKeys(entry, src).every(isGameDataSource);
  };
  for (const [i, fact] of (Array.isArray(entry.facts) ? entry.facts : []).entries()) {
    if (fact && typeof fact === 'object' && !keepFactStatus(fact.status, fact.src)) {
      downgraded.push({where: `facts[${i}]`, from: fact.status, to: VERIFICATION.unconfirmed});
      fact.status = VERIFICATION.unconfirmed;
    }
  }
  for (const {where, block, confirmed} of claimBlocks(entry)) {
    if (!confirmed && block && typeof block === 'object' && OFFICIAL_CLAIMS.includes(block.status) && !blockIsOfficial(entry, block.src)) {
      downgraded.push({where, from: block.status, to: VERIFICATION.unconfirmed});
      block.status = VERIFICATION.unconfirmed;
    }
  }
  const article = entry.article;
  if (article && typeof article === 'object' && Array.isArray(article.confirmed)) {
    const keep = [];
    for (const [i, item] of article.confirmed.entries()) {
      if (blockIsOfficial(entry, item?.src)) keep.push(item);
      else { downgraded.push({where: `article.confirmed[${i}]`, from: 'confirmé', to: 'pending (à confirmer)'}); (article.pending ??= []).push(item); }
    }
    article.confirmed = keep;
  }
  return {entry, downgraded, refused};
}

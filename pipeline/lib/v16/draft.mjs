/**
 * v16 — converts a routine draft (Markdown + front matter, /workspace/wow4ever-chatgpt/veille/articles/*.md)
 * into a pipeline DRAFT entry (article.format 2). Pure functions: no file system, no network.
 *
 * The result is always a draft (status draft, identityConfirmed false, no review): publication still goes
 * through scripts/import.mjs (forced to draft) and scripts/review.mjs (human attestations). Only official
 * Blizzard sources (https, *.blizzard.com) are accepted. See ops/v16/README.md for the file format.
 */
import {ANALYSIS_LABEL} from '../articles.mjs';
import {validate} from '../documentary.mjs';

const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
export const DEFAULT_LICENSE = 'Droits réservés Blizzard ; référence et synthèse originale, réutilisation à vérifier lors de la revue humaine.';
export const OFFICIAL_HOST = /^(?:[a-z0-9-]+\.)*blizzard\.com$/;
const DEFAULT_SUBCATEGORY = {news: 'annonces'};

/* ---------- front matter: a small, strict YAML subset (maps, lists, scalars, inline [a, b]) ---------- */
function scalar(raw) {
  const value = raw.trim();
  if (value === '') return '';
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.startsWith('"') ? JSON.parse(value) : value.slice(1, -1).replace(/''/g, "'");
  }
  if (value.startsWith('[') && value.endsWith(']')) return value.slice(1, -1).split(',').map(item => scalar(item)).filter(item => item !== '');
  if (/^-?\d+$/.test(value)) return Number(value);
  if (value === 'true' || value === 'false') return value === 'true';
  return value;
}
const stripComment = line => line.replace(/\s+#(?=(?:[^"']|"[^"]*"|'[^']*')*$).*$/, '');
export function parseFrontMatterYAML(text) {
  const lines = text.split('\n').map((raw, index) => ({raw: stripComment(raw).replace(/\s+$/, ''), n: index + 1}))
    .filter(line => line.raw.trim() && !line.raw.trim().startsWith('#'))
    .map(line => ({...line, indent: line.raw.match(/^ */)[0].length, text: line.raw.trim()}));
  if (lines.some(line => /\t/.test(line.raw))) throw new Error('front matter: tabs are not allowed, use spaces');
  let i = 0;
  function block(indent) {
    if (i >= lines.length || lines[i].indent < indent) return null;
    return lines[i].text.startsWith('- ') || lines[i].text === '-' ? list(lines[i].indent) : map(lines[i].indent);
  }
  function map(indent) {
    const out = {};
    while (i < lines.length && lines[i].indent === indent && !lines[i].text.startsWith('- ')) {
      const line = lines[i];
      const m = line.text.match(/^([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$/);
      if (!m) throw new Error(`front matter line ${line.n}: "key: value" expected`);
      if (m[1] in out) throw new Error(`front matter line ${line.n}: duplicate key ${m[1]}`);
      i += 1;
      if (m[2] !== undefined && m[2] !== '') out[m[1]] = scalar(m[2]);
      else if (i < lines.length && lines[i].indent > indent) out[m[1]] = block(lines[i].indent);
      else if (i < lines.length && lines[i].indent === indent && lines[i].text.startsWith('- ')) out[m[1]] = list(indent);
      else out[m[1]] = '';
    }
    if (i < lines.length && lines[i].indent > indent) throw new Error(`front matter line ${lines[i].n}: unexpected indentation`);
    return out;
  }
  function list(indent) {
    const out = [];
    while (i < lines.length && lines[i].indent === indent && (lines[i].text.startsWith('- ') || lines[i].text === '-')) {
      const line = lines[i], rest = line.text.slice(1).trim();
      if (/^[A-Za-z_][\w-]*\s*:(\s|$)/.test(rest)) {
        // "- key: value" starts a map whose other keys are aligned with "key"
        lines[i] = {...line, indent: indent + 2, text: rest};
        out.push(map(indent + 2));
      } else {
        i += 1;
        out.push(rest === '' ? block(indent + 1) : scalar(rest));
      }
    }
    return out;
  }
  const result = block(0) ?? {};
  if (i < lines.length) throw new Error(`front matter line ${lines[i].n}: could not be read`);
  if (!isObject(result)) throw new Error('front matter must be a map of keys');
  return result;
}

export function splitDraft(markdown) {
  const text = markdown.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n');
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) throw new Error('the draft must start with a front matter block between two "---" lines');
  return {meta: parseFrontMatterYAML(m[1]), body: m[2]};
}

/* ---------- body: "# FR" and "# EN" halves with the same "##" parts in the same order ---------- */
const SRC = /\s*\[src:\s*([a-z0-9][a-z0-9-, ]*)\]\s*$/i;
function sourced(text, where) {
  const m = text.match(SRC);
  const clean = text.replace(SRC, '').trim();
  if (!clean) throw new Error(`${where}: empty text`);
  return {text: clean, src: m ? m[1].split(',').map(key => key.trim()).filter(Boolean) : []};
}
function parseHalf(lines, lang) {
  const parts = [];
  let part = null, sub = null, para = [];
  const flush = () => {
    if (para.length && part) (sub ?? part).items.push({kind: 'p', text: para.join(' ').trim()});
    para = [];
  };
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.startsWith('### ')) { flush(); if (!part) throw new Error(`${lang}: "###" before any "##" part`); sub = {title: line.slice(4).trim(), items: []}; part.subs.push(sub); continue; }
    if (line.startsWith('## ')) { flush(); part = {title: line.slice(3).trim(), items: [], subs: []}; sub = null; parts.push(part); continue; }
    if (/^\s*[-*] /.test(line)) { flush(); if (!part) throw new Error(`${lang}: text before any "##" part`); (sub ?? part).items.push({kind: 'li', text: line.replace(/^\s*[-*] /, '').trim()}); continue; }
    if (!line.trim()) { flush(); continue; }
    if (!part) throw new Error(`${lang}: text before any "##" part`);
    para.push(line.trim());
  }
  flush();
  return parts;
}
export function splitLanguages(body) {
  const halves = {fr: null, en: null};
  let current = null;
  for (const line of body.split('\n')) {
    const m = line.match(/^#\s+(FR|EN)\s*$/i);
    if (m) {
      current = m[1].toLowerCase();
      if (halves[current]) throw new Error(`"# ${m[1]}" appears twice`);
      halves[current] = []; continue;
    }
    if (current) halves[current].push(line);
    else if (line.trim()) throw new Error('the body must start with "# FR" (then "# EN")');
  }
  if (!halves.fr || !halves.en) throw new Error('both "# FR" and "# EN" halves are required');
  return {fr: parseHalf(halves.fr, 'FR'), en: parseHalf(halves.en, 'EN')};
}

const norm = title => title.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[’']/g, "'").replace(/\s+/g, ' ').replace(/\s*\?$/, ' ?').trim();
const ROLE = {
  introduction: 'lead', "ce qu'il faut retenir": 'keyPoints', 'et maintenant ?': 'next', sources: 'ignore', discussion: 'ignore',
  "l'analyse wow4ever": 'analysis', "l'analyse de la redaction ia wow4ever": 'analysis', 'analyse de la redaction ia wow4ever': 'analysis'
};
const SUBROLE = {dates: 'dates', 'dates cles': 'dates', confirme: 'confirmed', 'a confirmer': 'pending', 'reste a confirmer': 'pending', 'ecarts entre sources': 'notes',
  'key dates': 'dates', confirmed: 'confirmed', 'to be confirmed': 'pending', 'still to be confirmed': 'pending', 'source discrepancies': 'notes'};
const slugId = title => norm(title).replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60).replace(/-+$/, '') || 'partie';

/** Pair the FR and EN halves part by part (roles come from the French headings). */
function buildArticle(halves, meta) {
  const {fr, en} = halves;
  if (fr.length !== en.length) throw new Error(`FR has ${fr.length} "##" parts but EN has ${en.length}: they must match one to one`);
  const article = {format: 2, slug: meta.slug, illustration: meta.illustration ?? meta.category, keyPoints: [], sections: [], confirmed: [], pending: []};
  const pair = (a, b, where) => {
    if (a.length !== b.length) throw new Error(`${where}: FR has ${a.length} items but EN has ${b.length}`);
    return a.map((item, index) => {
      const f = sourced(item.text, `${where} FR #${index + 1}`), e = sourced(b[index].text, `${where} EN #${index + 1}`);
      if (item.kind !== b[index].kind) throw new Error(`${where} #${index + 1}: FR and EN differ (paragraph vs list item)`);
      const src = [...new Set([...f.src, ...e.src])];
      return {kind: item.kind, fr: f.text, en: e.text, ...(src.length ? {src} : {})};
    });
  };
  const usedIds = new Set();
  fr.forEach((part, index) => {
    const other = en[index], where = `part "${part.title}"`;
    const role = ROLE[norm(part.title)] ?? 'section';
    if (role === 'ignore') return;
    if (role === 'next') {
      if (part.items.length || other.items.length) throw new Error(`${where}: use the "###" sub-parts (Dates, Confirmé, À confirmer)`);
      if (part.subs.length !== other.subs.length) throw new Error(`${where}: FR and EN sub-parts differ`);
      part.subs.forEach((sub, s) => {
        const kind = SUBROLE[norm(sub.title)];
        if (!kind) throw new Error(`${where}: unknown sub-part "${sub.title}" (Dates, Confirmé, À confirmer, Écarts entre sources)`);
        if (SUBROLE[norm(other.subs[s].title)] !== kind) throw new Error(`${where}: FR sub-part "${sub.title}" and EN sub-part "${other.subs[s].title}" do not match`);
        const items = pair(sub.items, other.subs[s].items, `${where} / ${sub.title}`);
        if (kind === 'dates') article.dates = items.map(({kind: _k, ...item}) => {
          const d = /^(\d{4}-\d{2}-\d{2})\s*[:—–-]\s*/;
          if (!d.test(item.fr) || !d.test(item.en) || item.fr.match(d)[1] !== item.en.match(d)[1]) throw new Error(`${where} / Dates: each line must start with the same YYYY-MM-DD date in FR and EN`);
          return {date: item.fr.match(d)[1], ...item, fr: item.fr.replace(d, ''), en: item.en.replace(d, '')};
        });
        else article[kind] = items.map(({kind: _k, ...item}) => item);
      });
      return;
    }
    const items = pair(part.items, other.items, where);
    if (role === 'lead') {
      if (items.length !== 1 || items[0].kind !== 'p') throw new Error(`${where}: exactly one paragraph expected`);
      const {kind: _k, ...lead} = items[0]; article.lead = lead; return;
    }
    if (role === 'keyPoints') { article.keyPoints = items.map(({kind: _k, ...item}) => item); return; }
    let id = slugId(part.title);
    while (usedIds.has(id) || ['introduction', 'a-retenir', 'et-maintenant', 'sources', 'discussion'].includes(id)) id = `${id}-2`;
    usedIds.add(id);
    const title = {fr: part.title, en: other.title};
    if (role === 'analysis') {
      if (items.some(item => item.kind !== 'p')) throw new Error(`${where}: the analysis is written as paragraphs`);
      article.sections.push({id, title, blocks: items.map(({kind: _k, ...item}) => ({type: 'analysis', label: {...ANALYSIS_LABEL}, ...item}))});
      return;
    }
    const blocks = [];
    for (const item of items) {
      const {kind, ...block} = item;
      if (kind === 'li') { const last = blocks.at(-1); if (last?.type === 'list') last.items.push(block); else blocks.push({type: 'list', items: [block]}); }
      else blocks.push({type: 'p', ...block});
    }
    article.sections.push({id, title, blocks});
  });
  return article;
}

const bilingualMeta = (meta, key) => isObject(meta[key]) ? meta[key] : (meta[`${key}_fr`] !== undefined || meta[`${key}_en`] !== undefined ? {fr: meta[`${key}_fr`], en: meta[`${key}_en`]} : undefined);
const asDate = value => String(value ?? '').trim();

/**
 * @returns {{entry: object, errors: string[]}} errors = front matter/format problems + documentary validation (validate()).
 */
export function draftToEntry(markdown, {file = 'brouillon.md', now = new Date().toISOString().slice(0, 10)} = {}) {
  const {meta, body} = splitDraft(markdown);
  const errors = [];
  const title = bilingualMeta(meta, 'title'), slug = bilingualMeta(meta, 'slug');
  if (String(meta.status ?? '').trim() !== 'draft') errors.push('front matter: status must be "draft" (a draft never arrives published)');
  const publication = asDate(meta.publicationDate ?? meta.publication_date ?? meta.date ?? now);
  const eventDate = meta.eventDate ?? meta.event_date;
  const category = meta.category;
  const tags = meta.tags === undefined ? undefined : (Array.isArray(meta.tags) ? meta.tags : [meta.tags]).map(tag => {
    if (isObject(tag)) return {fr: String(tag.fr ?? ''), en: String(tag.en ?? '')};
    const [fr, en] = String(tag).split('|').map(part => part.trim());
    if (!en) errors.push(`tag "${tag}": write "Français | English" or fr:/en:`);
    return {fr: fr ?? '', en: en ?? ''};
  });
  const sources = (Array.isArray(meta.sources) ? meta.sources : []).map((source, index) => {
    if (!isObject(source)) { errors.push(`sources[${index}] must be a map (key, language, url, title, publishedAt)`); return {}; }
    let host = '';
    try { host = new URL(String(source.url)).hostname; } catch { /* reported by validate() */ }
    if (!OFFICIAL_HOST.test(host) || !String(source.url).startsWith('https://')) errors.push(`sources[${index}]: official Blizzard source required (https://…blizzard.com), got ${source.url}`);
    const out = {key: source.key, language: source.language, url: source.url, title: source.title, publishedAt: asDate(source.publishedAt ?? source.published_at),
      accessedAt: asDate(source.accessedAt ?? source.accessed_at ?? publication), license: source.license ?? DEFAULT_LICENSE};
    // v17: official page with no publication date shown → `undated: true`, no invented date (see validateArticle).
    if (source.undated === true && !out.publishedAt) { delete out.publishedAt; out.undated = true; }
    return out;
  });
  if (!sources.length) errors.push('front matter: at least one official source is required');
  let article;
  try { article = buildArticle(splitLanguages(body), {...meta, slug}); } catch (error) { errors.push(`body: ${error.message}`); }
  const gameVersion = meta.gameVersion ?? `World of Warcraft: Forever — ${category === 'news' ? 'annonces' : String(category ?? '')}, état documentaire ${publication}`;
  for (const source of sources) source.gameVersion = gameVersion;
  const plain = text => String(text ?? '');
  const description = bilingualMeta(meta, 'description') ?? (article?.lead ? {fr: plain(article.lead.fr), en: plain(article.lead.en)} : undefined);
  const id = meta.id ?? `article-${String(slug?.en ?? 'sans-slug')}`.slice(0, 100);
  const priority = meta.priority ?? meta.priorite;
  const entry = {
    id, title, description, category, subcategory: meta.subcategory ?? DEFAULT_SUBCATEGORY[category] ?? String(category ?? ''),
    gameVersion, version: 1, status: 'draft', identityConfirmed: false, updatedAt: publication,
    ...(tags ? {tags} : {}), ...(eventDate !== undefined ? {eventDate: asDate(eventDate)} : {}),
    sources, relations: Array.isArray(meta.relations) ? meta.relations : [],
    ...(article ? {article} : {}),
    history: [{at: publication, actor: 'AI-documentary-draft', version: 1,
      note: `Brouillon converti depuis ${file} (format d’article v16${priority ? `, priorité ${priority}` : ''}) ; à relire et valider par Mathieu avant toute publication.`}]
  };
  if (article) errors.push(...validate(entry));
  return {entry, errors: [...new Set(errors)]};
}

/**
 * Compile content/articles/*.mjs + content/sources-*.json into a draft batch JSON
 * ready for `node scripts/import.mjs`. Never marks anything published or reviewed.
 *
 * Usage: node scripts/compile-articles.mjs [--output data/batches/forever-articles.json]
 */
import {readdir, readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve, dirname, join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {validate} from '../lib/documentary.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const outFlag = argv.indexOf('--output');
const output = resolve(outFlag !== -1 ? argv[outFlag + 1] : join(root, 'data/batches/forever-articles.json'));
const LICENSE = 'Droits réservés Blizzard ; référence et synthèse originale, réutilisation à vérifier lors de la revue humaine.';
const GAME = 'World of Warcraft: Forever — annonces et bêta, état documentaire 2026-10-27';
const NOW = new Date().toISOString();

const sourcesCatalog = JSON.parse(await readFile(join(root, 'content/sources-2026-10-24.json'), 'utf8'));

function resolveKeys(keys) {
  const out = [];
  const seen = new Set();
  for (const key of keys) {
    const matches = Object.entries(sourcesCatalog).filter(([k]) => k === key || k.startsWith(`${key}-`));
    if (!matches.length) throw new Error(`unknown source key: ${key}`);
    for (const [full, meta] of matches) {
      if (seen.has(full)) continue;
      seen.add(full);
      out.push({
        key: full,
        url: meta.url,
        title: meta.title,
        language: meta.language,
        publishedAt: meta.publishedAt,
        accessedAt: meta.accessedAt,
        license: LICENSE,
        gameVersion: GAME
      });
    }
  }
  return out;
}

function collectKeys(article) {
  const keys = new Set();
  const add = src => { for (const k of src ?? []) keys.add(k); };
  add(article.lead?.src);
  for (const p of article.keyPoints ?? []) add(p.src);
  for (const s of article.sections ?? []) for (const b of s.blocks ?? []) {
    if (b.type === 'list') for (const i of b.items ?? []) add(i.src);
    else add(b.src);
  }
  for (const p of article.confirmed ?? []) add(p.src);
  for (const p of article.notes ?? []) add(p.src);
  for (const p of article.dates ?? []) add(p.src);
  return [...keys];
}

function toEntry(raw) {
  const {
    id, code, category, subcategory, title, description, slug, illustration,
    relations = [], lead, keyPoints, sections, confirmed, pending, notes, dates
  } = raw;
  if (!id || !category || !title || !description || !slug || !illustration) {
    throw new Error(`incomplete article authoring for ${id ?? '?'}`);
  }
  const article = {
    format: 1,
    slug,
    illustration,
    lead,
    keyPoints,
    sections,
    confirmed,
    pending,
    ...(notes?.length ? {notes} : {}),
    ...(dates?.length ? {dates} : {})
  };
  const sources = resolveKeys(collectKeys({lead, keyPoints, sections, confirmed, notes, dates}));
  if (sources.length > 20) throw new Error(`${id}: ${sources.length} sources exceeds maxSources=20; narrow citations`);
  const entry = {
    id,
    title,
    description,
    category,
    subcategory: subcategory ?? 'article',
    sources,
    status: 'draft',
    updatedAt: NOW,
    version: 1,
    gameVersion: GAME,
    relations,
    history: [{
      at: NOW,
      actor: 'compile-articles',
      note: `Brouillon d’article long${code ? ` (${code})` : ''} compilé depuis content/articles — aucune attestation humaine.`,
      version: 1
    }],
    article
  };
  const errors = validate(entry);
  if (errors.length) throw new Error(`${id}: ${errors.join('; ')}`);
  return entry;
}

const dir = join(root, 'content/articles');
const files = (await readdir(dir)).filter(name => name.endsWith('.mjs')).sort();
const entries = [];
for (const name of files) {
  const mod = await import(pathToFileURL(join(dir, name)).href);
  const list = Array.isArray(mod.default) ? mod.default : [mod.default];
  for (const raw of list) entries.push(toEntry(raw));
}
const ids = new Set();
for (const entry of entries) {
  if (ids.has(entry.id)) throw new Error(`duplicate article id ${entry.id}`);
  ids.add(entry.id);
}
await mkdir(dirname(output), {recursive: true});
await writeFile(output, `${JSON.stringify(entries, null, 2)}\n`);
const digest = createHash('sha256').update(JSON.stringify(entries)).digest('hex');
console.log(JSON.stringify({
  output,
  articles: entries.length,
  categories: [...new Set(entries.map(e => e.category))].sort(),
  ids: entries.map(e => e.id),
  sha256: digest,
  status: 'all draft'
}, null, 2));

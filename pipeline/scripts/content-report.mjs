import {randomUUID} from 'node:crypto';
import {mkdir, realpath, rename, rm, writeFile} from 'node:fs/promises';
import {basename, dirname, join, parse, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditDataset, categories, digest, loadDataset, parseArgs} from '../lib/documentary.mjs';
import {selectPublicEntries} from '../lib/public-catalog.mjs';

const labels = Object.freeze({
  classes: 'Classes et spécialisations', races: 'Races et factions', zones: 'Zones et exploration',
  instances: 'Donjons et raids', professions: 'Métiers et artisanat', items: 'Objets et équipements',
  quests: 'Quêtes et progression', pvp: 'PvP et activités', creatures: 'Créatures et boss',
  guides: 'Guides débutants et avancés', news: 'Actualités et annonces', glossary: 'Glossaire et références'
});
const statuses = ['draft', 'review', 'verified', 'published'];
const emptyCounts = () => ({draft: 0, review: 0, verified: 0, published: 0, unknown: 0});
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const warning = 'La complétude est inconnue sans référentiel exhaustif de la version exacte de WoW Forever. Aucune proportion de complétude ne peut être déduite de ces compteurs.';

function referenceURL(value) {
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || !url.hostname || url.username || url.password) return null;
    // Deux ancres d’une même page constituent une référence documentaire unique.
    url.hash = '';
    return url.href;
  } catch { return null; }
}

function dateOnly(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)
    || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0, 10) !== value) {
    throw new Error('--as-of attend une date réelle au format AAAA-MM-JJ');
  }
  return value;
}

/** Rapport interne agrégé : ne contient ni texte de fiche ni attestations humaines. */
export function createContentReport(records, {asOf = new Date().toISOString().slice(0, 10)} = {}) {
  dateOnly(asOf);
  const audit = auditDataset(records, {now: `${asOf}T23:59:59.999Z`});
  const entries = Array.isArray(records) ? records : [];
  const invalidIndices = new Set(audit.errors.map(error => error.index).filter(Number.isInteger));
  const publicEntries = selectPublicEntries(entries).filter(entry =>
    !audit.errors.some(error => error.id === entry.id));
  const publicIds = new Set(publicEntries.map(entry => entry.id));
  const references = new Set();
  const scopes = new Map();
  const totals = {records: entries.length, statuses: emptyCounts(), invalidRecords: invalidIndices.size,
    uncategorized: 0, publicEligible: publicEntries.length};
  const rows = [...categories].map(category => ({category, label: labels[category], records: 0,
    statuses: emptyCounts(), invalidRecords: 0, publicEligible: 0, uniqueSources: 0}));
  const byCategory = new Map(rows.map(row => [row.category, row]));
  const sourcesByCategory = new Map(rows.map(row => [row.category, new Set()]));
  for (const [index, entry] of entries.entries()) {
    const row = object(entry) ? byCategory.get(entry.category) : undefined;
    const status = statuses.includes(entry?.status) ? entry.status : 'unknown';
    totals.statuses[status] += 1;
    if (row) {
      row.records += 1;
      row.statuses[status] += 1;
      if (invalidIndices.has(index)) row.invalidRecords += 1;
      if (publicIds.has(entry.id)) row.publicEligible += 1;
    } else totals.uncategorized += 1;
    if (typeof entry?.gameVersion === 'string' && entry.gameVersion.trim()) {
      const version = entry.gameVersion.trim();
      const scope = scopes.get(version) ?? {gameVersion: version, records: 0, statuses: emptyCounts(), publicEligible: 0};
      scope.records += 1;
      scope.statuses[status] += 1;
      if (publicIds.has(entry.id)) scope.publicEligible += 1;
      scopes.set(version, scope);
    }
    for (const source of Array.isArray(entry?.sources) ? entry.sources : []) {
      const url = typeof source?.url === 'string' ? referenceURL(source.url) : null;
      if (!url) continue;
      references.add(url);
      if (row) sourcesByCategory.get(row.category).add(url);
    }
  }
  for (const row of rows) row.uniqueSources = sourcesByCategory.get(row.category).size;
  return {
    format: 1, locale: 'fr', asOf, datasetChecksum: digest(records),
    confidentiality: 'Rapport interne ; ne pas publier dans public/ ou dist/.',
    completeness: {known: false, warning},
    methodology: {
      statuses: 'Statuts déclarés dans les données, y compris les fiches invalides ; ils ne prouvent pas une publication.',
      publicEligible: 'Fiches publiées admissibles après contrôle de structure, de validation humaine, de traduction, de droits, de relations et d’identifiants uniques.',
      uniqueSources: 'Nombre de références HTTPS distinctes sans identifiants de connexion, après normalisation de l’URL et retrait des ancres ; une URL présente ne constitue pas une vérification factuelle.',
      snapshot: 'Lecture seule, sans recherche réseau. À données et date de référence identiques, le rapport est identique.'
    },
    totals, categories: rows, uniqueSources: references.size,
    versionScopes: [...scopes.values()].sort((a, b) => a.gameVersion < b.gameVersion ? -1 : a.gameVersion > b.gameVersion ? 1 : 0),
    missingVersionScope: entries.filter(entry => typeof entry?.gameVersion !== 'string' || !entry.gameVersion.trim()).length,
    validation: {valid: audit.errors.length === 0, errors: audit.errors, staleRecords: audit.stale.length},
    nextCategories: rows.filter(row => row.publicEligible === 0).map(row => row.category)
  };
}

const cell = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('|', '&#124;').replaceAll('`', '&#96;').replace(/[\r\n]+/g, ' ');

export function renderContentReport(report) {
  const lines = [
    '# Couverture documentaire — WoW Forever Wiki', '', report.confidentiality, '',
    `Date de référence : ${report.asOf}. Empreinte des données : \`${report.datasetChecksum}\`.`, '',
    report.completeness.warning, '',
    `Fiches : **${report.totals.records}**. Publications admissibles : **${report.totals.publicEligible}**. Références HTTPS uniques : **${report.uniqueSources}**.`, '',
    '| Catégorie | Total | Brouillon | En revue | Vérifiée | Publiée (déclarée) | Invalide | Publication admissible | Sources uniques |',
    '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'
  ];
  for (const row of report.categories) lines.push(`| ${cell(row.label)} | ${row.records} | ${row.statuses.draft} | ${row.statuses.review} | ${row.statuses.verified} | ${row.statuses.published} | ${row.invalidRecords} | ${row.publicEligible} | ${row.uniqueSources} |`);
  lines.push('', `Hors catégorie : ${report.totals.uncategorized}. Statut inconnu : ${report.totals.statuses.unknown}.`, '',
    '## Périmètres de version', '', '| Version déclarée | Fiches | Publications admissibles |', '| --- | ---: | ---: |');
  for (const scope of report.versionScopes) lines.push(`| ${cell(scope.gameVersion)} | ${scope.records} | ${scope.publicEligible} |`);
  if (!report.versionScopes.length) lines.push('| Aucun périmètre renseigné | 0 | 0 |');
  lines.push('', `Version absente : ${report.missingVersionScope}.`, '', '## Contrôles', '',
    `Intégrité : **${report.validation.valid ? 'valide' : 'erreurs présentes'}**. Fiches potentiellement obsolètes : ${report.validation.staleRecords}.`, '');
  if (report.validation.errors.length) {
    lines.push('| Position | Identifiant | Diagnostic technique |', '| --- | --- | --- |');
    for (const error of report.validation.errors) {
      for (const detail of error.errors) lines.push(`| ${error.index ?? 'ensemble'} | ${cell(error.id ?? 'absent')} | ${cell(detail)} |`);
    }
  } else lines.push('Aucune erreur de validation détectée. Cela ne remplace pas la vérification documentaire humaine.');
  lines.push('', '## Méthode', '');
  for (const description of Object.values(report.methodology)) lines.push(`- ${description}`);
  lines.push('', 'Rubriques sans publication admissible : ' + (report.nextCategories.map(category => labels[category]).join(', ') || 'aucune') + '.', '');
  return lines.join('\n');
}

async function physicalPath(path) {
  let parent = resolve(path);
  const suffix = [];
  while (true) {
    try { return join(await realpath(parent), ...suffix); }
    catch (error) {
      if (error.code !== 'ENOENT' || dirname(parent) === parent) throw error;
      suffix.unshift(basename(parent));
      parent = dirname(parent);
    }
  }
}

async function safeOutputDirectory(outputDir, inputs) {
  const destination = resolve(outputDir);
  const physical = await physicalPath(destination);
  for (const path of [destination, physical]) {
    if (path.slice(parse(path).root.length).split(sep).some(part => ['public', 'dist'].includes(part))) {
      throw new Error('Le rapport interne ne peut pas être écrit dans public/ ou dist/.');
    }
  }
  for (const input of inputs) {
    const source = await physicalPath(input);
    for (const filename of ['content-report.json', 'content-report.md']) {
      if (await physicalPath(join(destination, filename)) === source) throw new Error('La sortie ne doit pas remplacer une source de données.');
    }
  }
  return destination;
}

async function atomicWrite(path, body) {
  const temporary = `${path}.${randomUUID()}.tmp`;
  try {
    await writeFile(temporary, body, {flag: 'wx', mode: 0o600});
    await rename(temporary, path);
  } finally { await rm(temporary, {force: true}); }
}

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['output-dir', 'runtime-dir', 'seed', 'as-of'], flags: ['help']});
  if (options.help) {
    log('Usage : node scripts/content-report.mjs --output-dir DOSSIER_PRIVE [--runtime-dir runtime] [--seed data/entries.json] [--as-of AAAA-MM-JJ]\nLecture seule ; runtime/entries.json est prioritaire, sinon la base initiale est utilisée.');
    return;
  }
  if (positional.length || !options['output-dir']) throw new Error('--output-dir explicite est obligatoire ; utiliser --help');
  const runtimeDir = resolve(options['runtime-dir'] ?? 'runtime');
  const seedPath = resolve(options.seed ?? 'data/entries.json');
  const outputDir = await safeOutputDirectory(options['output-dir'], [seedPath, join(runtimeDir, 'entries.json')]);
  const records = await loadDataset({runtimeDir, seedPath});
  const report = createContentReport(records, {asOf: options['as-of']});
  await mkdir(outputDir, {recursive: true, mode: 0o700});
  const jsonPath = join(outputDir, 'content-report.json');
  const markdownPath = join(outputDir, 'content-report.md');
  await atomicWrite(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
  await atomicWrite(markdownPath, renderContentReport(report));
  log(JSON.stringify({jsonPath, markdownPath, records: report.totals.records, publicEligible: report.totals.publicEligible,
    categories: report.categories.length, valid: report.validation.valid}, null, 2));
  if (!report.validation.valid) setExitCode(2);
  return report;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Rapport documentaire impossible : ${error.message}`); process.exitCode = 1; });
}

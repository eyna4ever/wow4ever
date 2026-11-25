import {createHash, randomUUID} from 'node:crypto';
import {lstat, mkdir, readlink, realpath, rename, rm, stat, writeFile} from 'node:fs/promises';
import {basename, dirname, join, parse, resolve, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditDataset, categories, loadDataset, parseArgs} from '../lib/documentary.mjs';

const labels = Object.freeze({classes: 'Classes et spécialisations', races: 'Races et factions', zones: 'Zones et exploration',
  instances: 'Donjons et raids', professions: 'Métiers et artisanat', items: 'Objets et équipements',
  quests: 'Quêtes et progression', pvp: 'PvP et activités', creatures: 'Créatures et boss',
  guides: 'Guides débutants et avancés', news: 'Actualités et annonces', glossary: 'Glossaire et références'});
const statuses = Object.freeze({draft: 'Brouillon', review: 'En relecture', verified: 'Vérifiée', published: 'Publiée (statut déclaré)'});
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value, fallback = 'Non renseigné') => typeof value === 'string' && value.trim() ? value : fallback;
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;').replaceAll("'", '&#39;');

// Never serialize source credentials, unsafe schemes or common secret-bearing parameters.
function safeReference(value) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || !url.hostname || url.username || url.password) return null;
    if ([...url.searchParams.keys()].some(key => /^(?:access[_-]?token|token|api[_-]?key|key|secret|password|authorization|signature)$/i.test(key))) return null;
    return url.href;
  } catch { return null; }
}

const filterScript = `(() => {
  const search = document.getElementById('search');
  const category = document.getElementById('category');
  const entries = [...document.querySelectorAll('[data-entry]')];
  const fold = value => value.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLocaleLowerCase('fr');
  function filter() {
    const query = fold(search.value.trim());
    let count = 0;
    for (const entry of entries) {
      entry.hidden = Boolean(category.value && entry.dataset.category !== category.value) || !fold(entry.textContent).includes(query);
      if (!entry.hidden) count += 1;
    }
    document.getElementById('results').textContent = count + ' fiche(s) affichée(s)';
  }
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);
  filter();
})();`;
const style = `:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#10151c;color:#eee9df;line-height:1.6}*{box-sizing:border-box}body{max-width:1180px;margin:auto;padding:20px}a{color:#e9c679;overflow-wrap:anywhere}h1,h2,h3{line-height:1.25}header,.notice,article,.audit{border:1px solid #897044;border-radius:8px;padding:20px;margin-bottom:20px;background:#18212b}header p{max-width:85ch}.notice{background:#302a1b}.controls{display:flex;flex-wrap:wrap;gap:16px;margin:20px 0}.controls label{display:flex;flex-direction:column;flex:1;min-width:210px}input,select{font:inherit;color:inherit;background:#10151c;border:1px solid #b99a60;padding:10px;min-height:44px}input:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #ffdc86;outline-offset:3px}.bilingual{display:grid;grid-template-columns:1fr 1fr;gap:24px}.description,li{white-space:pre-wrap;overflow-wrap:anywhere}.metadata{display:grid;grid-template-columns:max-content 1fr;gap:5px 15px;font-size:.95rem}.metadata dt{color:#d1bd95}.metadata dd{margin:0;overflow-wrap:anywhere}.badges{display:flex;flex-wrap:wrap;gap:8px}.badge{padding:4px 10px;background:#302a1b;border:1px solid #897044;border-radius:4px}.error{border-color:#de8d80;color:#ffcdc3}.sources li{margin:16px 0}.sources p{margin:4px 0;font-size:.9rem}nav ul{display:flex;flex-wrap:wrap;gap:8px 20px;padding-left:20px}summary{cursor:pointer;padding:8px 0}[hidden]{display:none!important}footer{font-size:.9rem;color:#c6baa4}@media(max-width:640px){body{padding:12px}header,article,.notice,.audit{padding:16px}.bilingual{grid-template-columns:1fr;gap:12px}.metadata{grid-template-columns:1fr;gap:0}.metadata dd{margin-bottom:8px}h1{font-size:1.6rem}}`;

function bilingual(entry, field, heading) {
  return `<div class="bilingual">${['fr', 'en'].map(locale => `<section lang="${locale}" aria-label="${heading} ${locale.toUpperCase()}"><h3>${heading} · ${locale.toUpperCase()}</h3><p class="description">${escape(text(entry[field]?.[locale], 'Traduction absente / Missing translation'))}</p></section>`).join('')}</div>`;
}

function renderEntry(raw, index, records, invalidIndices) {
  const entry = object(raw) ? raw : {};
  const category = categories.has(entry.category) ? entry.category : 'other';
  const reviewValid = !invalidIndices.has(index) && ['verified', 'published'].includes(entry.status);
  const sources = Array.isArray(entry.sources) ? entry.sources : [];
  const relations = Array.isArray(entry.relations) ? entry.relations : [];
  const steps = Array.isArray(entry.steps) ? entry.steps : [];
  const metadata = [['Identifiant stable', text(entry.id)], ['Catégorie', category === 'other' ? 'Catégorie inconnue' : labels[category]],
    ['Sous-catégorie', text(entry.subcategory)], ['Version du jeu / Game version', text(entry.gameVersion)],
    ['Version de la fiche / Revision', Number.isSafeInteger(entry.version) ? entry.version : 'Non renseignée'],
    ['Mise à jour / Updated', text(entry.updatedAt)]];
  return `<article id="entry-${index}" data-entry data-category="${category}">
<h2>${escape(text(entry.title?.fr, 'Sans titre français'))} / <span lang="en">${escape(text(entry.title?.en, 'Missing English title'))}</span></h2>
<div class="badges"><span class="badge">${escape(Object.hasOwn(statuses, entry.status) ? statuses[entry.status] : 'Statut inconnu')}</span>
<span class="badge">${entry.identityConfirmed === true ? 'Identité déclarée confirmée' : 'Identité non confirmée / Identity unconfirmed'}</span>
<span class="badge">${reviewValid ? 'Traductions validées dans la révision courante' : 'Traductions non validées / Translations unapproved'}</span>
${invalidIndices.has(index) ? '<span class="badge error">Erreurs d’intégrité / Integrity errors</span>' : ''}</div>
<dl class="metadata">${metadata.map(([key, value]) => `<dt>${escape(key)}</dt><dd>${escape(value)}</dd>`).join('')}</dl>
${bilingual(entry, 'description', 'Description')}
${steps.length ? `<h3>Étapes / Steps</h3><ol>${steps.map(step => `<li><div class="bilingual"><p lang="fr">${escape(text(step?.fr, 'Étape française absente'))}</p><p lang="en">${escape(text(step?.en, 'English step missing'))}</p></div></li>`).join('')}</ol>` : ''}
<h3>Sources et droits / Sources and rights</h3>
${sources.length ? `<ol class="sources">${sources.map(source => {
    const url = safeReference(source?.url);
    return `<li>${url ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(text(source?.title, url))}</a>` : '<strong class="error">Référence HTTPS refusée ou absente / Reference rejected</strong>'}
<p>Consultée le / Accessed: ${escape(text(source?.accessedAt))} · Version: ${escape(text(source?.gameVersion, text(entry.gameVersion)))}</p>
<p>Droits / License: ${escape(text(source?.license))}</p></li>`;
  }).join('')}</ol>` : '<p>Aucune source renseignée / No source supplied.</p>'}
<h3>Relations / Related entries</h3>${relations.length ? `<ul>${relations.map(id => {
    const target = records.findIndex(record => object(record) && record.id === id);
    return `<li>${target >= 0 ? `<a href="#entry-${target}">${escape(text(id))}</a>` : `${escape(text(id))} — cible absente / missing target`}</li>`;
  }).join('')}</ul>` : '<p>Aucune relation / No related entry.</p>'}
</article>`;
}

/** Local review only: allowlisted fields, no approval controls, no dataset mutation. */
export function createContentReview(records) {
  const audit = auditDataset(records);
  const entries = Array.isArray(records) ? records : [];
  for (const [index, entry] of entries.entries()) {
    if (object(entry) && 'steps' in entry && (!Array.isArray(entry.steps) || entry.steps.length > 200
      || !entry.steps.every(step => object(step) && ['fr', 'en'].every(locale => typeof step[locale] === 'string' && step[locale].trim() && step[locale].length <= 10_000)))) {
      audit.errors.push({index, id: typeof entry.id === 'string' ? entry.id : null, errors: ['steps must contain at most 200 bilingual text steps']});
    }
  }
  const invalidIndices = new Set(audit.errors.map(error => error.index).filter(Number.isInteger));
  const invalidIds = new Set(audit.errors.map(error => error.id).filter(id => typeof id === 'string'));
  entries.forEach((entry, index) => { if (invalidIds.has(entry?.id)) invalidIndices.add(index); });
  const scriptHash = createHash('sha256').update(filterScript).digest('base64');
  const coverage = [...categories].map(category => ({category, count: entries.filter(entry => entry?.category === category).length}));
  const html = `<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'sha256-${scriptHash}'; base-uri 'none'; form-action 'none'; connect-src 'none'">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Relecture privée FR/EN — WoW Forever Wiki</title><style>${style}</style></head>
<body><header><h1>Dossier de relecture FR/EN</h1><p>WoW Forever Wiki · Document interne hors ligne. Ne pas déposer ce fichier dans public/ ou dist/.</p>
<p>Ces fiches sont des documents candidats. Une référence présente ne prouve pas le fait cité. Les textes FR/EN restent soumis à vérification humaine de l’identité du jeu, des faits, des droits et des traductions.</p>
<p>Lecture seule : aucun statut, empreinte ou droit n’est modifié. Ce dossier ne permet ni d’approuver ni de publier.</p></header>
<aside class="notice"><strong>${entries.length} fiche(s) · ${audit.errors.length ? 'Erreurs d’intégrité présentes' : 'Contrôles structurels sans erreur'}</strong><p>La complétude de chaque catégorie reste inconnue sans référentiel exhaustif du jeu et de sa version exacte. Les 12 catégories ne sont pas nécessairement documentées.</p></aside>
<section class="audit" aria-labelledby="audit-title"><h2 id="audit-title">Audit de structure / Integrity audit</h2>
${audit.errors.length ? `<ul>${audit.errors.flatMap(error => error.errors.map(detail => `<li>${Number.isInteger(error.index) ? `<a href="#entry-${error.index}">Fiche ${error.index + 1}</a>` : 'Ensemble de données'} · ${escape(text(error.id, 'Identifiant absent'))} : ${escape(detail)}</li>`)).join('')}</ul>` : '<p>Aucune erreur structurelle détectée. Cela ne constitue pas une validation documentaire.</p>'}
<p>${audit.stale.length} fiche(s) potentiellement obsolète(s) selon la date des données ou de leurs références.</p></section>
<nav aria-label="Couverture des catégories"><h2>Catégories / Categories</h2><ul>${coverage.map(({category, count}) => `<li>${escape(labels[category])} : ${count}</li>`).join('')}</ul></nav>
<div class="controls"><label for="search">Rechercher dans ce dossier / Search<input type="search" id="search" autocomplete="off"></label>
<label for="category">Catégorie / Category<select id="category"><option value="">Toutes / All</option>${[...categories].map(category => `<option value="${category}">${escape(labels[category])}</option>`).join('')}<option value="other">Catégorie inconnue</option></select></label></div>
<p id="results" role="status" aria-live="polite">${entries.length} fiche(s) affichée(s)</p>
<main>${entries.length ? entries.map((entry, index) => renderEntry(entry, index, entries, invalidIndices)).join('\n') : '<p>Aucune fiche disponible / No entry available.</p>'}</main>
<footer>Les données sources, les statuts et les autorisations restent inchangés. Les noms des auteurs, l’historique privé et les attestations détaillées ne sont pas exportés.</footer>
<script>${filterScript}</script></body></html>\n`;
  return {html, audit, valid: audit.errors.length === 0, records: entries.length};
}

async function sourceLocation(path, depth = 0) {
  if (depth > 32) throw new Error('Trop de liens symboliques dans une source de données.');
  try {
    if ((await lstat(path)).isSymbolicLink()) return sourceLocation(resolve(dirname(path), await readlink(path)), depth + 1);
    return await realpath(path);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    const parent = dirname(path);
    return parent === path ? path : join(await sourceLocation(parent, depth + 1), basename(path));
  }
}

async function assertPrivateOutput(destination, inputs) {
  const parts = destination.slice(parse(destination).root.length).split(sep);
  if (parts.some(part => ['public', 'dist'].includes(part.toLowerCase()))) throw new Error('La relecture privée ne peut pas être écrite dans public/ ou dist/.');
  // Reject every symlink in the output path, including directory aliases.
  let current = parse(destination).root;
  for (const part of parts) {
    current = join(current, part);
    try {
      const info = await lstat(current);
      if (info.isSymbolicLink()) throw new Error('La destination de relecture ne doit contenir aucun lien symbolique.');
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
  for (const input of inputs) {
    if (destination === resolve(input) || destination === await sourceLocation(resolve(input))) throw new Error('La sortie ne doit pas remplacer une source de données.');
    try {
      const [target, source] = await Promise.all([stat(destination), stat(input)]);
      if (target.dev === source.dev && target.ino === source.ino) throw new Error('La sortie ne doit pas remplacer une source de données.');
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
}

export async function main(argv = process.argv.slice(2), {log = console.log, setExitCode = code => { process.exitCode = code; }} = {}) {
  const {options, positional} = parseArgs(argv, {values: ['output', 'runtime-dir', 'seed'], flags: ['help']});
  if (options.help) {
    log('Usage : node scripts/content-review.mjs --output /chemin-prive/relecture.html [--runtime-dir runtime] [--seed data/entries.json]\nLecture seule et sans réseau ; runtime/entries.json est prioritaire, sinon la base initiale est utilisée.');
    return;
  }
  if (positional.length || !options.output) throw new Error('--output explicite est obligatoire ; utiliser --help');
  const destination = resolve(options.output), runtimeDir = resolve(options['runtime-dir'] ?? 'runtime'), seedPath = resolve(options.seed ?? 'data/entries.json');
  const inputs = [seedPath, join(runtimeDir, 'entries.json')];
  await assertPrivateOutput(destination, inputs);
  if (!destination.toLowerCase().endsWith('.html')) throw new Error('--output doit désigner un fichier .html privé');
  const review = createContentReview(await loadDataset({runtimeDir, seedPath}));
  await mkdir(dirname(destination), {recursive: true, mode: 0o700});
  await assertPrivateOutput(destination, inputs);
  const temporary = join(dirname(destination), `.review-${randomUUID()}.tmp`);
  try {
    await writeFile(temporary, review.html, {flag: 'wx', mode: 0o600});
    await assertPrivateOutput(destination, inputs);
    await rename(temporary, destination);
  } finally { await rm(temporary, {force: true}); }
  log(JSON.stringify({output: destination, records: review.records, valid: review.valid, auditErrors: review.audit.errors.length}, null, 2));
  if (!review.valid) setExitCode(1);
  return review;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Relecture documentaire impossible : ${error.message}`); process.exitCode = 1; });
}

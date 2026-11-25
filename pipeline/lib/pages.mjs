/**
 * Static page renderer: one HTML page per entry (/fr/<category>/<slug>/), one landing
 * page per category (/fr/<category>/). No inline script, no inline style, no data: URL,
 * so pages run under the strict CSP of deploy/Caddyfile.example.
 */
import {ANALYSIS_LABEL, CATEGORY_SLUGS, categoryPath, entryPath, readingMinutes, sourceGroups} from './articles.mjs';
import {visualFor, VISUAL_SIZE} from './visuals.mjs';
import {GAME_DATA_LABEL, UNCONFIRMED_LABEL, gameDataGroupKeys, unofficialGroupKeys, VERIFICATION} from './source-policy.mjs';
import {SITE_NAME, siteHeader, groupOf} from './site-chrome.mjs';

export const UNOFFICIAL = {fr: 'Site indépendant et non officiel de Blizzard Entertainment.', en: 'Independent, unofficial site, not affiliated with Blizzard Entertainment.'};
export const ART_LABEL = {fr: 'Illustration d’ambiance — ne constitue pas une source', en: 'Ambiance illustration — not a source'};
const esc = value => String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const T = (lang, fr, en) => lang === 'en' ? en : fr;
const other = lang => lang === 'fr' ? 'en' : 'fr';

export function formatDate(iso, lang) {
  const [y, m, d] = String(iso).slice(0, 10).split('-').map(Number);
  if (!y || !m || !d) return esc(iso);
  return new Intl.DateTimeFormat(lang === 'en' ? 'en-GB' : 'fr-FR', {day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'}).format(new Date(Date.UTC(y, m - 1, d)));
}
const time = (iso, lang) => `<time datetime="${esc(String(iso).slice(0, 10))}">${formatDate(iso, lang)}</time>`;

/** V2.1 étape 03: visible « À confirmer » / "Unconfirmed" mark (existing pill style, CSP-safe, no new CSS). */
export const unconfirmedPill = (lang, text = UNCONFIRMED_LABEL[lang]) => `<span class="status-pill is-draft">${text}</span>`;
export const gameDataPill = (lang, text = GAME_DATA_LABEL[lang]) => `<span class="status-pill">${text}</span>`;
export function statusBadge(status, lang, verification) {
  if (verification === VERIFICATION.unconfirmed) return `${statusBadge(status, lang)} ${unconfirmedPill(lang)}`;
  if (verification === VERIFICATION.gameData) return `${statusBadge(status, lang)} ${gameDataPill(lang)}`;
  if (status === 'published') return `<span class="status-pill is-published">${T(lang, 'Publié · validé', 'Published · reviewed')}</span>`;
  return `<span class="status-pill is-draft">${T(lang, 'Brouillon — à valider', 'Draft — pending review')}</span>`;
}

function picture(category, prefix, lang, {sizes = '(min-width: 1100px) 1024px, 100vw', eager = false, avif = false} = {}) {
  const base = `${prefix}assets/art-${category}`;
  // v11 (v2 site only): AVIF first, WebP img as fallback; the v1 markup is unchanged when avif is false.
  if (avif) return `<picture><source type="image/avif" srcset="${base}-480.avif 480w, ${base}-1024.avif 1024w" sizes="${sizes}"><img class="art-image" src="${base}-1024.webp" srcset="${base}-640.webp 640w, ${base}-1024.webp 1024w" sizes="${sizes}" width="1024" height="576" alt="${esc(ART_LABEL[lang])}"${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async"></picture>`;
  return `<img class="art-image" src="${base}-1024.webp" srcset="${base}-640.webp 640w, ${base}-1024.webp 1024w" sizes="${sizes}" width="1024" height="576" alt="${esc(ART_LABEL[lang])}"${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async">`;
}

/** Entry artwork: the article's own illustration (webp 640/1280 + jpg fallback), else the category art. */
let LINKED_VISUALS = new Map();
/** Short entries borrow the artwork of a related elite article (same catalogue only), else the category art. */
export function setVisualLinks(entries) {
  LINKED_VISUALS = new Map();
  const articles = entries.filter(entry => visualFor(entry));
  for (const entry of entries) {
    if (visualFor(entry)) continue;
    const viaOwn = (entry.relations ?? []).map(id => articles.find(article => article.id === id)).find(Boolean);
    const viaArticle = articles.find(article => article.category === entry.category && (article.relations ?? []).includes(entry.id)) ?? articles.find(article => (article.relations ?? []).includes(entry.id));
    const match = viaArticle ?? viaOwn;
    if (match) LINKED_VISUALS.set(entry.id, visualFor(match));
  }
}
export function entryPicture(entry, prefix, lang, {sizes = '(min-width: 1100px) 1180px, 100vw', eager = false, cls = 'art-image', avif = false} = {}) {
  const visual = visualFor(entry) ?? LINKED_VISUALS.get(entry.id);
  if (!visual) return picture(entry.category, prefix, lang, {sizes, eager, avif}).replace('class="art-image"', `class="${cls}"`);
  const base = `${prefix}assets/art-${visual.file}`;
  const modern = avif ? `<source type="image/avif" srcset="${base}-480.avif 480w, ${base}-960.avif 960w, ${base}-1280.avif 1280w" sizes="${sizes}">` : '';
  return `<picture>${modern}<source type="image/webp" srcset="${base}-640.webp 640w, ${base}-1280.webp 1280w" sizes="${sizes}"><img class="${cls}" src="${base}-1280.jpg" width="${VISUAL_SIZE.width}" height="${VISUAL_SIZE.height}" alt="${esc(visual.alt[lang])}"${eager ? ' fetchpriority="high"' : ' loading="lazy"'} decoding="async"></picture>`;
}
const THUMB_SIZES = '(min-width: 1100px) 360px, (min-width: 700px) 50vw, 100vw';

function head({lang, title, description, prefix, alternate, preview}) {
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#0b141b">${preview ? '<meta name="wow4ever-build" content="preview-local-only">' : ''}<link rel="icon" href="${prefix}assets/favicon.svg" type="image/svg+xml"><title>${esc(title)} — ${SITE_NAME}</title><meta name="description" content="${esc(description)}">${alternate ? `<link rel="alternate" hreflang="${other(lang)}" href="${esc(alternate)}">` : ''}<link rel="stylesheet" href="${prefix}site.css"></head>`;
}

function header({lang, prefix, switchHref, preview, current = ''}) {
  const home = preview ? `${prefix}${lang}/index.html` : `${prefix}${lang}/`;
  return `<a href="#main-content" class="skip-link">${T(lang, 'Aller au contenu', 'Skip to content')}</a>
${preview ? `<p class="preview-banner" role="note">${T(lang, 'APERÇU LOCAL — contient des brouillons non validés. Ne pas déployer.', 'LOCAL PREVIEW — contains unreviewed drafts. Do not deploy.')}</p>` : ''}
<div class="site-shell">
${siteHeader({lang, prefix, switchHref, home, current, preview})}
<main id="main-content" tabindex="-1">`;
}

function footer(lang, prefix = '') {
  return `</main>
<footer class="site-footer"><div class="footer-main"><span class="footer-ornament" aria-hidden="true">──── ✧ ────</span><p>${SITE_NAME} <span aria-hidden="true">·</span> ${T(lang, 'Projet communautaire indépendant', 'Independent community project')}</p></div><p class="independence">${UNOFFICIAL.fr}${lang === 'en' ? ` ${UNOFFICIAL.en}` : ''} ${T(lang, 'Les illustrations sont des créations d’ambiance originales, sans valeur documentaire.', 'Illustrations are original ambiance artwork with no documentary value.')}</p></footer>
</div>${prefix ? `<script type="module" src="${prefix}wk-header.js"></script>` : ''}</body></html>`;
}

function breadcrumbs(lang, prefix, items, preview) {
  const home = preview ? `${prefix}${lang}/index.html` : `${prefix}${lang}/`;
  const all = [[T(lang, 'Accueil', 'Home'), home], ...items];
  return `<nav class="breadcrumbs" aria-label="${T(lang, 'Fil d’Ariane', 'Breadcrumb')}"><ol>${all.map(([label, href], i) => i === all.length - 1 ? `<li><span aria-current="page">${esc(label)}</span></li>` : `<li><a href="${href}">${esc(label)}</a></li>`).join('')}</ol></nav>`;
}

function citations(src, numbers) {
  const unique = [...new Set(src.map(key => numbers.get(key.replace(/-(fr|en)$/, ''))).filter(Boolean))];
  const marks = unique.map(n => `<sup class="cite"><a href="#source-${n}" aria-label="Source ${n}">[${n}]</a></sup>`).join('');
  // V2.1 étape 03 / t359u: unofficial-only claims are marked « À confirmer », unless every cited
  // unofficial source is a stamped 70862 extract marked « données du jeu ».
  const unofficial = numbers.unofficial;
  const keys = src.map(key => key.replace(/-(fr|en)$/, ''));
  if (unofficial?.size && src.length && keys.every(key => unofficial.has(key))) {
    const gameData = numbers.gameData;
    if (gameData?.size && keys.every(key => gameData.has(key))) return `${marks} ${gameDataPill(numbers.lang)}`;
    return `${marks} ${unconfirmedPill(numbers.lang)}`;
  }
  return marks;
}
// v23: *name* → <em>name</em> (English spell names without an official French name). Escaped first, so no HTML injection.
export const emph = text => esc(text).replace(/\*([^*<>\n]{1,80})\*/g, '<em>$1</em>');
/** v38 / t361u: CSP-safe internal wiki links only — [label](/fr/path/) or a bare /fr/path/ or /en/path/. No external URLs, no javascript:. */
const WIKI_HREF = /^\/(?:fr|en)(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)+\/$/;
const WIKI_MD = /\[([^\]]{1,200})\]\((\/(?:fr|en)(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)+\/)\)/g;
const WIKI_BARE = /(?<!\]\()(\/(?:fr|en)(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)+\/)/g;
const linkBare = escaped => escaped.replace(WIKI_BARE, '<a href="$1">$1</a>');
export function wikiText(text) {
  const s = String(text ?? '');
  let out = '', last = 0;
  for (const match of s.matchAll(WIKI_MD)) {
    if (!WIKI_HREF.test(match[2])) continue;
    out += linkBare(emph(s.slice(last, match.index)));
    out += `<a href="${match[2]}">${emph(match[1])}</a>`;
    last = match.index + match[0].length;
  }
  out += linkBare(emph(s.slice(last)));
  return out;
}
const sourcedText = (block, lang, numbers) => `${wikiText(block[lang])}${citations(block.src ?? [], numbers)}`;
const cellText = (cell, lang) => wikiText(cell[lang]);

function relatedCards(entry, all, lang, prefix, preview) {
  const byId = new Map(all.map(item => [item.id, item]));
  const picked = [];
  for (const id of entry.relations) if (byId.has(id)) picked.push(byId.get(id));
  for (const item of all) if (picked.length < 6 && item.id !== entry.id && item.category === entry.category && item.article && !picked.includes(item)) picked.push(item);
  if (!picked.length) return '';
  return `<section class="related" aria-labelledby="related-title"><h2 id="related-title">${T(lang, 'Articles liés', 'Related articles')}</h2><p class="art-note">${THUMBS_NOTE[lang]}</p><ul class="related-grid">${picked.slice(0, 6).map(item => `<li><a class="related-card has-thumb${item.article ? '' : ' is-notice'}" href="${prefix}${entryPath(item, lang)}${preview ? 'index.html' : ''}"><span class="card-thumb">${entryPicture(item, prefix, lang, {sizes: '(min-width: 1100px) 260px, (min-width: 700px) 50vw, 100vw', cls: 'thumb-image'})}</span><span class="eyebrow">${esc(categoryName(item.category, lang))}</span><strong>${esc(item.title[lang])}</strong><span class="related-meta">${item.article ? `${readingMinutes(item, lang)} min · ` : ''}${statusText(item.status, lang)}</span></a></li>`).join('')}</ul></section>`;
}
const statusText = (status, lang) => status === 'published' ? T(lang, 'Publié', 'Published') : T(lang, 'Brouillon', 'Draft');

let CATEGORY_NAMES = {};
export function setCategoryNames(categories) { CATEGORY_NAMES = Object.fromEntries(categories.map(([id, fr, en]) => [id, {fr, en}])); }
export const categoryName = (id, lang) => CATEGORY_NAMES[id]?.[lang] ?? id;

function sourcesBlock(entry, lang) {
  const groups = sourceGroups(entry);
  const unofficial = unofficialGroupKeys(entry);
  const items = groups.map(group => {
    const versions = [...group.versions].sort((a, b) => (a.language === lang ? -1 : 0) - (b.language === lang ? -1 : 0));
    const lines = versions.map(source => `<a href="${esc(source.url)}" rel="noopener noreferrer"${source.language ? ` hreflang="${esc(source.language)}"` : ''}>${esc(source.title ?? source.url)}</a>${source.language ? ` <span class="source-lang">(${esc(source.language.toUpperCase())})</span>` : ''}${source.publishedAt ? ` · ${T(lang, 'publié le', 'published')} ${time(source.publishedAt, lang)}` : source.undated ? ` · ${T(lang, 'date de publication non indiquée', 'no publication date shown')}` : ''} · ${T(lang, 'consulté le', 'accessed')} ${time(source.accessedAt, lang)}`);
    const gameData = gameDataGroupKeys(entry);
    let mark = '';
    if (gameData.has(group.key)) mark = ` ${gameDataPill(lang, T(lang, 'Données du jeu — client 1.60.1.70862', 'Game data — client 1.60.1.70862'))}`;
    else if (unofficial.has(group.key)) mark = ` ${unconfirmedPill(lang, T(lang, 'Source non officielle — à confirmer', 'Non-official source — unconfirmed'))}`;
    return `<li id="source-${group.number}"><span class="source-number">[${group.number}]</span> <span class="source-lines">${lines.join('<br>')}${mark}</span></li>`;
  });
  const gameData = gameDataGroupKeys(entry);
  const stillUnconfirmed = [...unofficial].some(key => !gameData.has(key));
  const extras = [];
  if (gameData.size) extras.push(T(lang, 'Les sources marquées « données du jeu » viennent des fichiers du client WoW Forever (build 1.60.1.70862). Ce n’est pas une confirmation officielle de Blizzard.', 'Sources marked “game data” come from the WoW Forever client files (build 1.60.1.70862). This is not an official Blizzard confirmation.'));
  if (stillUnconfirmed) extras.push(T(lang, 'Les sources marquées « à confirmer » ne sont pas des sources officielles Blizzard (base de fans ou extrait sans tampon de build) : les informations qui ne reposent que sur elles restent à confirmer.', 'Sources marked “unconfirmed” are not official Blizzard sources (fan database or extract without a build stamp): information resting only on them remains unconfirmed.'));
  const extra = extras.length ? ` ${extras.join(' ')}` : '';
  const onlyGameData = unofficial.size === groups.length && unofficial.size && [...unofficial].every(key => gameData.has(key));
  const noOfficial = unofficial.size === groups.length
    ? (onlyGameData
      ? T(lang, 'Aucune source officielle Blizzard pour cette fiche : le contenu repose sur des données du jeu (client 1.60.1.70862), ce qui n’est pas une confirmation officielle. Ce wiki en propose une synthèse originale ; seules de courtes citations sont reproduites.', 'No official Blizzard source for this entry: its content rests on game data (client 1.60.1.70862), which is not an official confirmation. This wiki offers an original synthesis; only short quotes are reproduced.')
      : T(lang, 'Aucune source officielle Blizzard pour cette fiche : tout son contenu reste à confirmer. Ce wiki en propose une synthèse originale ; seules de courtes citations sont reproduites.', 'No official Blizzard source for this entry: all of its content remains unconfirmed. This wiki offers an original synthesis; only short quotes are reproduced.'))
    : T(lang, 'Sources officielles Blizzard Entertainment (droits réservés). Ce wiki en propose une synthèse originale ; seules de courtes citations sont reproduites. Les informations annoncées peuvent évoluer avant ou après le lancement.', 'Official Blizzard Entertainment sources (all rights reserved). This wiki offers an original synthesis; only short quotes are reproduced. Announced information may change before or after launch.');
  return `<section class="article-section sources-block" id="sources" aria-labelledby="sources-title"><h2 id="sources-title">${T(lang, 'Sources', 'Sources')}</h2><ol class="source-list">${items.join('')}</ol><p class="rights-note">${noOfficial}${extra}</p></section>`;
}

function metaLine(entry, lang) {
  const parts = [statusBadge(entry.status, lang, entry.verification)];
  if (entry.article) parts.push(`<span>${readingMinutes(entry, lang)} ${T(lang, 'min de lecture', 'min read')}</span>`);
  parts.push(`<span>${T(lang, 'Mis à jour le', 'Updated')} ${time(entry.updatedAt, lang)}</span>`);
  parts.push(`<span>${sourceGroups(entry).length} ${T(lang, sourceGroups(entry).length > 1 ? 'sources' : 'source', sourceGroups(entry).length > 1 ? 'sources' : 'source')}</span>`);
  return `<p class="article-meta">${parts.join('<span aria-hidden="true"> · </span>')}</p>`;
}

/** Article/notice body (sections, sourced statements) and its table of contents; shared by the v8 and v2 templates. */
export function entryContent(entry, lang) {
  const article = entry.article;
  const groups = sourceGroups(entry);
  const numbers = new Map(groups.map(group => [group.key, group.number]));
  numbers.unofficial = unofficialGroupKeys(entry);
  numbers.gameData = gameDataGroupKeys(entry);
  numbers.lang = lang;
  const toc = [];
  let body = '';
  if (article?.format === 2) return entryContentV16(entry, lang, numbers);
  if (article) {
    toc.push(['en-bref', T(lang, 'En bref', 'In brief')]);
    body += `<section class="article-section lead-box" id="en-bref" aria-labelledby="en-bref-title"><h2 id="en-bref-title">${T(lang, 'En bref', 'In brief')}</h2><p>${sourcedText(article.lead, lang, numbers)}</p></section>`;
    toc.push(['points-cles', T(lang, 'Points clés', 'Key points')]);
    body += `<section class="article-section" id="points-cles" aria-labelledby="points-cles-title"><h2 id="points-cles-title">${T(lang, 'Points clés', 'Key points')}</h2><ul class="key-points">${article.keyPoints.map(point => `<li>${sourcedText(point, lang, numbers)}</li>`).join('')}</ul></section>`;
    for (const section of article.sections) {
      toc.push([section.id, section.title[lang]]);
      const blocks = section.blocks.map(block => {
        if (block.type === 'list') return `<ul>${block.items.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul>`;
        if (block.type === 'table') return `<div class="table-wrap" role="region" aria-label="${esc(block.caption[lang])}" tabindex="0"><table><caption>${wikiText(block.caption[lang])}${citations(block.src, numbers)}</caption><thead><tr>${block.head.map(cell => `<th scope="col">${cellText(cell, lang)}</th>`).join('')}</tr></thead><tbody>${block.rows.map(row => `<tr>${row.map((cell, i) => i === 0 ? `<th scope="row">${cellText(cell, lang)}</th>` : `<td>${cellText(cell, lang)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
        return `<p>${sourcedText(block, lang, numbers)}</p>`;
      }).join('');
      body += `<section class="article-section" id="${section.id}" aria-labelledby="${section.id}-title"><h2 id="${section.id}-title">${esc(section.title[lang])}</h2>${blocks}</section>`;
    }
    toc.push(['confirme', T(lang, 'Confirmé / à confirmer', 'Confirmed / to be confirmed')]);
    body += `<section class="article-section status-grid" id="confirme" aria-labelledby="confirme-title"><h2 id="confirme-title">${T(lang, 'Ce qui est confirmé / ce qui reste à confirmer', 'What is confirmed / what remains to be confirmed')}</h2><div class="status-columns"><div class="status-col is-confirmed"><h3>${T(lang, 'Confirmé par les sources officielles', 'Confirmed by official sources')}</h3><ul>${article.confirmed.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></div><div class="status-col is-pending"><h3>${T(lang, 'Reste à confirmer', 'Still to be confirmed')}</h3><ul>${article.pending.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></div></div></section>`;
    if (article.notes?.length) {
      toc.push(['remarques', T(lang, 'Écarts entre sources', 'Source discrepancies')]);
      body += `<section class="article-section notes-box" id="remarques" aria-labelledby="remarques-title"><h2 id="remarques-title">${T(lang, 'Écarts entre sources', 'Source discrepancies')}</h2><ul>${article.notes.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></section>`;
    }
    if (article.dates?.length) {
      toc.push(['dates', T(lang, 'Dates clés', 'Key dates')]);
      body += `<section class="article-section" id="dates" aria-labelledby="dates-title"><h2 id="dates-title">${T(lang, 'Dates clés', 'Key dates')}</h2><ol class="timeline">${[...article.dates].sort((a, b) => a.date.localeCompare(b.date)).map(item => `<li>${time(item.date, lang)}<span>${sourcedText(item, lang, numbers)}</span></li>`).join('')}</ol></section>`;
    }
  } else {
    body += `<section class="article-section lead-box" id="en-bref" aria-labelledby="en-bref-title"><h2 id="en-bref-title">${T(lang, 'En bref', 'In brief')}</h2><p>${wikiText(entry.description[lang])}${groups.map(group => `<sup class="cite"><a href="#source-${group.number}" aria-label="Source ${group.number}">[${group.number}]</a></sup>`).join('')}${entry.verification === VERIFICATION.unconfirmed ? ` ${unconfirmedPill(lang)}` : entry.verification === VERIFICATION.gameData ? ` ${gameDataPill(lang)}` : ''}</p><p class="panel-note">${T(lang, 'Fiche courte validée. Un article détaillé peut la compléter (voir les articles liés).', 'Short reviewed entry. A detailed article may complement it (see related articles).')}</p></section>`;
    toc.push(['en-bref', T(lang, 'En bref', 'In brief')]);
  }
  return {body, toc, sources: sourcesBlock(entry, lang)};
}

/**
 * v16 — article.format 2 (opt-in): Introduction, Ce qu'il faut retenir, authored sections (e.g. Les détails,
 * Conséquences pour les joueurs, L'analyse WoW4ever), Et maintenant ?, then Sources and Discussion (render.mjs).
 * Analysis blocks are boxed and labelled "Avis · IA" so they can never be read as facts.
 */
export function analysisBox(block, lang, numbers) {
  return `<aside class="v16-analysis" aria-label="${esc(ANALYSIS_LABEL[lang])}"><p class="v16-analysis-head"><span class="v16-analysis-badge">${T(lang, 'Avis · IA', 'Opinion · AI')}</span><strong>${esc(ANALYSIS_LABEL[lang])}</strong></p><p>${esc(block[lang])}${citations(block.src ?? [], numbers)}</p><p class="v16-analysis-note">${T(lang, 'Point de vue de la rédaction, rédigé par l’IA de WoW4ever et relu avant publication. Ce n’est pas une information officielle : les faits sont dans les autres parties, avec leurs sources.', 'Editorial opinion written by the WoW4ever AI and reviewed before publication. This is not official information: the facts are in the other parts, with their sources.')}</p></aside>`;
}
function entryContentV16(entry, lang, numbers) {
  const article = entry.article;
  const toc = [];
  let body = '';
  const add = (id, title, inner, cls = '') => { toc.push([id, title]); body += `<section class="article-section${cls ? ` ${cls}` : ''}" id="${id}" aria-labelledby="${id}-title"><h2 id="${id}-title">${esc(title)}</h2>${inner}</section>`; };
  add('introduction', T(lang, 'Introduction', 'Introduction'), `<p>${sourcedText(article.lead, lang, numbers)}</p>`, 'lead-box');
  add('a-retenir', T(lang, 'Ce qu’il faut retenir', 'Key takeaways'), `<ul class="key-points">${article.keyPoints.map(point => `<li>${sourcedText(point, lang, numbers)}</li>`).join('')}</ul>`);
  for (const section of article.sections) {
    const isAnalysis = section.blocks.every(block => block.type === 'analysis');
    const blocks = section.blocks.map(block => {
      if (block.type === 'analysis') return analysisBox(block, lang, numbers);
      if (block.type === 'list') return `<ul>${block.items.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul>`;
      if (block.type === 'table') return `<div class="table-wrap" role="region" aria-label="${esc(block.caption[lang])}" tabindex="0"><table><caption>${wikiText(block.caption[lang])}${citations(block.src, numbers)}</caption><thead><tr>${block.head.map(cell => `<th scope="col">${cellText(cell, lang)}</th>`).join('')}</tr></thead><tbody>${block.rows.map(row => `<tr>${row.map((cell, i) => i === 0 ? `<th scope="row">${cellText(cell, lang)}</th>` : `<td>${cellText(cell, lang)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
      return `<p>${sourcedText(block, lang, numbers)}</p>`;
    }).join('');
    add(section.id, section.title[lang], blocks, isAnalysis ? 'is-analysis' : '');
  }
  const dates = article.dates?.length ? `<h3>${T(lang, 'Dates clés', 'Key dates')}</h3><ol class="timeline">${[...article.dates].sort((a, b) => a.date.localeCompare(b.date)).map(item => `<li>${time(item.date, lang)}<span>${sourcedText(item, lang, numbers)}</span></li>`).join('')}</ol>` : '';
  const notes = article.notes?.length ? `<div class="notes-box"><h3>${T(lang, 'Écarts entre sources', 'Source discrepancies')}</h3><ul>${article.notes.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></div>` : '';
  add('et-maintenant', T(lang, 'Et maintenant ?', 'What’s next?'), `${dates}<div class="status-columns"><div class="status-col is-confirmed"><h3>${T(lang, 'Confirmé par les sources officielles', 'Confirmed by official sources')}</h3><ul>${article.confirmed.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></div><div class="status-col is-pending"><h3>${T(lang, 'Reste à confirmer', 'Still to be confirmed')}</h3><ul>${article.pending.map(item => `<li>${sourcedText(item, lang, numbers)}</li>`).join('')}</ul></div></div>${notes}`, 'status-grid');
  return {body, toc, sources: sourcesBlock(entry, lang)};
}
/** v16 — closing "Discussion" part of a format 2 article: an invitation to the existing forums (no automatic post). */
export function discussionBlock(lang, category) {
  const guide = category === 'guides'; // v18 — guides are not news: adapt the invitation wording
  return `<section class="article-section v16-discussion" id="discussion" aria-labelledby="discussion-title"><h2 id="discussion-title">${T(lang, 'Discussion', 'Discussion')}</h2><p>${guide ? T(lang, 'Une question, un conseil à partager sur ce guide ? Parlez-en avec les autres joueurs sur les forums du wiki.', 'A question or a tip to share about this guide? Talk about it with other players on the wiki forums.') : T(lang, 'Une question, un avis sur cette actualité ? Parlez-en avec les autres joueurs sur les forums du wiki.', 'A question or an opinion about this news? Talk about it with other players on the wiki forums.')}</p><p><a class="v2-btn is-gold-outline" href="/community/" data-community-link>${T(lang, 'Ouvrir les forums', 'Open the forums')} <span aria-hidden="true">→</span></a></p></section>`;
}

export function renderEntryPage(entry, {lang, all, preview = false}) {
  const prefix = '../../../';
  const title = entry.title[lang];
  const {body, toc} = entryContent(entry, lang);
  toc.push(['sources', T(lang, 'Sources', 'Sources')]);
  const related = relatedCards(entry, all, lang, prefix, preview);
  if (related) toc.push(['related-title', T(lang, 'Articles liés', 'Related articles')]);
  const catHref = `${prefix}${categoryPath(entry.category, lang)}${preview ? 'index.html' : ''}`;
  const switchHref = `${prefix}${entryPath(entry, other(lang))}${preview ? 'index.html' : ''}`;
  return head({lang, title, description: entry.description[lang], prefix, alternate: switchHref, preview})
    + header({lang, prefix, switchHref, preview, current: groupOf(entry.category)})
    + breadcrumbs(lang, prefix, [[categoryName(entry.category, lang), catHref], [title, '']], preview)
    + `<article class="article-page ornate" aria-labelledby="article-title"><header class="article-hero"><figure class="article-figure">${entryPicture(entry, prefix, lang, {eager: true, sizes: '(min-width: 1320px) 1320px, 100vw'})}<figcaption>${esc(ART_LABEL[lang])}.</figcaption></figure><div class="article-heading"><p class="eyebrow">${esc(categoryName(entry.category, lang))}</p><h1 id="article-title">${esc(title)}</h1><p class="article-dek">${esc(entry.description[lang])}</p>${metaLine(entry, lang)}</div></header>`
    + `<div class="article-layout"><aside class="article-toc" aria-labelledby="toc-title"><details open><summary id="toc-title">${T(lang, 'Sommaire', 'Contents')}</summary><ol>${toc.map(([id, label]) => `<li><a href="#${id === 'related-title' ? 'related-title' : id}">${esc(label)}</a></li>`).join('')}</ol></details></aside><div class="article-body">${body}${sourcesBlock(entry, lang)}<p class="article-version">${T(lang, 'Version documentaire', 'Documentary version')} : ${esc(entry.gameVersion)} · ${T(lang, 'révision', 'revision')} ${entry.version}</p></div>${related ? `<aside class="article-rail">${related}</aside>` : ''}</div></article>`
    + footer(lang, prefix);
}

export const CATEGORY_INTROS = {
  classes: {fr: 'Les classes jouables de World of Warcraft: Forever, d’après les présentations détaillées publiées par Blizzard.', en: 'The playable classes of World of Warcraft: Forever, based on Blizzard’s published deep dives.'},
  races: {fr: 'Les Éolides et les évolutions raciales annoncées.', en: 'The Skyborne and the announced racial changes.'},
  zones: {fr: 'Régions nouvelles ou réinventées de l’Azeroth d’origine.', en: 'New or reimagined regions of original Azeroth.'},
  instances: {fr: 'Les neuf donjons du lancement et les trois raids prévus le 9 décembre 2026.', en: 'The nine launch dungeons and the three raids planned for December 9, 2026.'},
  professions: {fr: 'Métiers, campement et plans d’artisanat.', en: 'Professions, camping and crafting blueprints.'},
  items: {fr: 'Itemisation et apparences, dans la limite de ce que Blizzard a détaillé.', en: 'Itemization and appearances, within what Blizzard has detailed.'},
  quests: {fr: 'Progression, héritage et suites de quêtes documentées.', en: 'Progression, legacy and documented questlines.'},
  pvp: {fr: 'Honneur, rangs, saisons et champ de bataille des îles des Sombrelances.', en: 'Honor, ranks, seasons and the Darkspear Islands battleground.'},
  creatures: {fr: 'Rubrique encore peu documentée par les sources officielles.', en: 'A category still thinly covered by official sources.'},
  guides: {fr: 'Préparer son arrivée : ensembles de règles, noms, installation.', en: 'Getting ready: rulesets, names, installation.'},
  news: {fr: 'Calendrier, bêta et annonces officielles.', en: 'Schedule, beta and official announcements.'},
  glossary: {fr: 'Les termes propres à World of Warcraft: Forever.', en: 'Terms specific to World of Warcraft: Forever.'}
};

export function renderCategoryPage(category, {lang, entries, preview = false}) {
  const prefix = '../../';
  const title = categoryName(category, lang);
  const items = entries.filter(entry => entry.category === category);
  const articles = items.filter(entry => entry.article).sort((a, b) => a.title[lang].localeCompare(b.title[lang], lang));
  const notices = items.filter(entry => !entry.article).sort((a, b) => a.title[lang].localeCompare(b.title[lang], lang));
  const card = entry => `<li><a class="entry-card has-thumb${entry.article ? '' : ' is-notice'}" href="${prefix}${entryPath(entry, lang)}${preview ? 'index.html' : ''}"><span class="card-thumb">${entryPicture(entry, prefix, lang, {sizes: THUMB_SIZES, cls: 'thumb-image'})}</span><span class="entry-card-top">${statusBadge(entry.status, lang)}${entry.article ? `<span>${readingMinutes(entry, lang)} min</span>` : ''}<span>${time(entry.updatedAt, lang)}</span></span><strong>${esc(entry.title[lang])}</strong><span class="entry-card-text">${esc(entry.description[lang])}</span></a></li>`;
  const switchHref = `${prefix}${categoryPath(category, other(lang))}${preview ? 'index.html' : ''}`;
  return head({lang, title, description: CATEGORY_INTROS[category][lang], prefix, alternate: switchHref, preview})
    + header({lang, prefix, switchHref, preview, current: groupOf(category)})
    + breadcrumbs(lang, prefix, [[title, '']], preview)
    + `<section class="category-hero ornate" aria-labelledby="category-title"><figure class="category-figure">${picture(category, prefix, lang, {eager: true})}<figcaption>${esc(ART_LABEL[lang])}.</figcaption></figure><div class="category-heading"><p class="eyebrow">${T(lang, 'Rubrique', 'Category')}</p><h1 id="category-title">${esc(title)}</h1><p>${esc(CATEGORY_INTROS[category][lang])}</p><p class="article-meta">${articles.length} ${T(lang, articles.length > 1 ? 'articles' : 'article', articles.length === 1 ? 'article' : 'articles')} · ${notices.length} ${T(lang, notices.length > 1 ? 'fiches courtes' : 'fiche courte', notices.length === 1 ? 'short entry' : 'short entries')}</p></div></section>`
    + `<section class="category-list" aria-labelledby="articles-title"><h2 id="articles-title">${T(lang, 'Articles', 'Articles')}</h2>${articles.length ? `<ul class="entry-grid${articles.length === 1 ? ' single' : ''}">${articles.map(card).join('')}</ul><p class="art-note">${THUMBS_NOTE[lang]}</p>` : `<p class="panel-note">${T(lang, 'Aucun article publié dans cette rubrique pour l’instant.', 'No article published in this category yet.')}</p>`}</section>`
    + `<section class="category-list" aria-labelledby="notices-title"><h2 id="notices-title">${T(lang, 'Fiches courtes', 'Short entries')}</h2>${notices.length ? `<ul class="entry-grid compact">${notices.map(card).join('')}</ul><p class="art-note">${THUMBS_NOTE[lang]}</p>` : `<p class="panel-note">${T(lang, 'Aucune fiche courte publiée dans cette rubrique.', 'No short entry published in this category.')}</p>`}</section>`
    + footer(lang, prefix);
}

/** Preview hub: static index of every category (no SPA), local review only. */
export function renderPreviewHub({lang, entries, categories, prefix = '../'}) {
  const rows = categories.map(([id]) => {
    const items = entries.filter(entry => entry.category === id);
    const drafts = items.filter(entry => entry.status !== 'published').length;
    return `<li><a class="entry-card" href="${prefix}${categoryPath(id, lang)}index.html"><strong>${esc(categoryName(id, lang))}</strong><span class="entry-card-text">${items.filter(e => e.article).length} ${T(lang, 'articles', 'articles')} · ${items.filter(e => !e.article).length} ${T(lang, 'fiches', 'entries')} · ${drafts} ${T(lang, 'brouillons', 'drafts')}</span></a></li>`;
  }).join('');
  return head({lang, title: T(lang, 'Aperçu local des articles', 'Local article preview'), description: T(lang, 'Aperçu local, brouillons inclus.', 'Local preview, drafts included.'), prefix, alternate: `${prefix}${other(lang)}/index.html`, preview: true})
    + header({lang, prefix, switchHref: `${prefix}${other(lang)}/index.html`, preview: true})
    + `<section class="category-list preview-hub" aria-labelledby="hub-title"><h1 id="hub-title">${T(lang, 'Aperçu local des articles', 'Local article preview')}</h1><p class="panel-note">${T(lang, 'Cet aperçu contient des brouillons non validés. Il n’est jamais empaqueté ni déployé.', 'This preview contains unreviewed drafts. It is never packaged or deployed.')}</p><ul class="entry-grid">${rows}</ul></section>`
    + footer(lang, prefix);
}

export {CATEGORY_SLUGS};

/** Thumbnail caption for card grids (each grid carries the ambiance-art notice once). */
export const THUMBS_NOTE = {fr: 'Vignettes : illustrations d’ambiance — ne constituent pas une source.', en: 'Thumbnails: ambiance illustrations — not a source.'};

/**
 * Home « À la une / Articles »: one large featured card then a grid. Published articles only (callers pass
 * the public catalogue). Text carries data-fr/data-en and links data-href-fr/en so the SPA language switch
 * keeps working without inline script.
 */
export function renderFeatured({lang, entries, prefix = '../'}) {
  const byId = new Map(entries.filter(entry => entry.article && entry.status === 'published').map(entry => [entry.id, entry]));
  const ordered = [...byId.values()].sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)) || a.title[lang].localeCompare(b.title[lang], lang));   // v22: automatic, newest first
  if (!ordered.length) return '';
  const both = (fr, en) => `data-fr="${esc(fr)}" data-en="${esc(en)}"`;
  const hrefs = entry => `href="${prefix}${entryPath(entry, lang)}" data-href-fr="${prefix}${entryPath(entry, 'fr')}" data-href-en="${prefix}${entryPath(entry, 'en')}"`;
  const alts = entry => { const v = visualFor(entry); return v ? ` data-alt-fr="${esc(v.alt.fr)}" data-alt-en="${esc(v.alt.en)}"` : ''; };
  const meta = entry => `<span class="feature-meta"><span class="eyebrow" ${both(categoryName(entry.category, 'fr'), categoryName(entry.category, 'en'))}>${esc(categoryName(entry.category, lang))}</span><time datetime="${esc(entry.updatedAt.slice(0, 10))}" ${both(formatDate(entry.updatedAt, 'fr'), formatDate(entry.updatedAt, 'en'))}>${formatDate(entry.updatedAt, lang)}</time></span>`;
  const [main, ...rest] = ordered;
  const grid = rest.slice(0, 6), more = rest.slice(6);
  const withAlt = (html, entry) => html.replace('<img ', `<img${alts(entry)} `);
  return `<section id="a-la-une" class="featured-section" aria-labelledby="featured-title"><div class="section-heading"><div class="heading-line" aria-hidden="true">✧</div><div><h2 id="featured-title" ${both('À la une', 'Featured')}>${T(lang, 'À la une', 'Featured')}</h2><p ${both('Les articles de fond, vérifiés et sourcés', 'In-depth articles, reviewed and sourced')}>${T(lang, 'Les articles de fond, vérifiés et sourcés', 'In-depth articles, reviewed and sourced')}</p></div><div class="heading-line" aria-hidden="true">✧</div></div>`
    + `<a class="featured-main ornate" ${hrefs(main)}><span class="featured-art">${withAlt(entryPicture(main, prefix, lang, {sizes: '(min-width: 1100px) 760px, 100vw', cls: 'thumb-image'}), main)}</span><span class="featured-copy">${meta(main)}<strong ${both(main.title.fr, main.title.en)}>${esc(main.title[lang])}</strong><span class="featured-dek" ${both(main.description.fr, main.description.en)}>${esc(main.description[lang])}</span><span class="featured-cta"><span ${both('Lire l’article', 'Read the article')}>${T(lang, 'Lire l’article', 'Read the article')}</span> <span aria-hidden="true">→</span></span></span></a>`
    + `<ul class="featured-grid">${grid.map(entry => `<li><a class="featured-card" ${hrefs(entry)}><span class="card-thumb">${withAlt(entryPicture(entry, prefix, lang, {sizes: '(min-width: 1100px) 360px, (min-width: 700px) 50vw, 100vw', cls: 'thumb-image'}), entry)}</span>${meta(entry)}<strong ${both(entry.title.fr, entry.title.en)}>${esc(entry.title[lang])}</strong></a></li>`).join('')}</ul>`
    + (more.length ? `<div class="featured-more"><h3 ${both('Tous les articles', 'All articles')}>${T(lang, 'Tous les articles', 'All articles')}</h3><ul>${more.map(entry => `<li><a ${hrefs(entry)}><span class="card-thumb mini">${withAlt(entryPicture(entry, prefix, lang, {sizes: '120px', cls: 'thumb-image'}), entry)}</span><span><span class="eyebrow" ${both(categoryName(entry.category, 'fr'), categoryName(entry.category, 'en'))}>${esc(categoryName(entry.category, lang))}</span><strong ${both(entry.title.fr, entry.title.en)}>${esc(entry.title[lang])}</strong></span></a></li>`).join('')}</ul></div>` : '')
    + `<p class="art-note" ${both(THUMBS_NOTE.fr, THUMBS_NOTE.en)}>${THUMBS_NOTE[lang]}</p></section>`;
}

import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectPublicEntries, selectPreviewEntries, homeEntries} from './public-catalog.mjs';
import {setNavCatalog, siteHeader} from './site-chrome.mjs';

// Bundlers such as Next.js do not always provide import.meta.dirname; fall back to the URL,
// then to an explicit WOW_FOREVER_ROOT, then to the working directory (Next runs from the project root).
function projectDirectory(){
  if(process.env.WOW_FOREVER_ROOT)return resolve(process.env.WOW_FOREVER_ROOT);
  if(typeof import.meta.dirname==='string')return resolve(import.meta.dirname,'..');
  try{if(String(import.meta.url).startsWith('file:'))return resolve(dirname(fileURLToPath(import.meta.url)),'..');}catch{}
  return process.cwd();
}
export const root=projectDirectory();
export function scriptJSON(value){return JSON.stringify(value).replaceAll('<','\\u003c').replaceAll('>','\\u003e').replaceAll('&','\\u0026').replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029');}
export async function loadRecords({projectRoot=root}={}){
  let records;
  try{records=JSON.parse(await readFile(resolve(projectRoot,'runtime/entries.json'),'utf8'));}
  catch(error){if(error.code!=='ENOENT')throw error;records=JSON.parse(await readFile(resolve(projectRoot,'data/entries.json'),'utf8'));}
  if(!Array.isArray(records))throw new Error('Documentary dataset must be an array');
  return records;
}
export async function loadCategories({projectRoot=root}={}){
  return JSON.parse(await readFile(resolve(projectRoot,'public/wiki/catalog.json'),'utf8')).categories;
}
/** Full DTOs for static pages. preview=true includes drafts and is for local review only. */
export async function siteEntries({projectRoot=root,preview=false}={}){
  const records=await loadRecords({projectRoot});
  return preview?selectPreviewEntries(records):selectPublicEntries(records);
}
/** Home catalogue payload: always published entries only (drafts are never embedded in the SPA). */
export async function sitePayload({projectRoot=root}={}){
  const records=await loadRecords({projectRoot});
  const categories=await loadCategories({projectRoot});
  return {categories,entries:homeEntries(selectPublicEntries(records))};
}
/** Inject the shared Wowkipedia header (lib/site-chrome.mjs) at the <!--wk-site-header--> marker of the home template. */
// navEntries: full published DTOs (article slugs) for the menu's entry links; the home payload strips article bodies,
// so falling back to it would derive slugs from titles and break links to articles.
export function withSiteHeader(template,{lang='fr',prefix='../',payload,page='home',navEntries}={}){
  if(payload)setNavCatalog({categories:payload.categories,entries:navEntries??payload.entries});
  const other=lang==='fr'?'en':'fr';
  const path=page==='wiki'?'wiki/':'';
  return template.replace('<!--wk-site-header-->',()=>siteHeader({lang,prefix,home:`${prefix}${lang}/`,switchHref:`${prefix}${other}/${path}`,current:page}));
}
const english=template=>template.replace(/<([a-z][\w:-]*)\b([^<>]*\bdata-fr="[^"]*"[^<>]*\bdata-en="([^"]*)"[^<>]*)>[^<]*<\/\1>/g,(_all,tag,attributes,en)=>`<${tag}${attributes}>${en}</${tag}>`);

/**
 * L1b "Tout le wiki" (/fr/wiki/, /en/wiki/): the home registry (search form, category filters, registry with
 * favourites, entry panel, dialogs, footer) without the home hero, featured articles and tool cards. Same
 * template and same app.js, so ?q= and ?cat= work as on the home page (which keeps its registry until L2).
 */
export function wikiTemplate(template){
  const at=marker=>{const i=template.indexOf(marker);if(i<0)throw new Error(`wiki page: marker not found: ${marker}`);return i;};
  const hero=at('<section class="hero ornate"'),archives=at('<section id="archives"'),tools=at('<section class="feature-grid"'),catalog=at('<section id="catalog-section"');
  if(!(hero<archives&&archives<tools&&tools<catalog))throw new Error('wiki page: unexpected template order');
  const form=template.slice(hero,archives).match(/<form id="search-form"[\s\S]*?<\/form>/)?.[0];
  if(!form)throw new Error('wiki page: search form not found');
  const intro=`<section class="wiki-intro ornate" aria-labelledby="wiki-title"><p class="eyebrow" data-fr="LE REGISTRE COMPLET" data-en="THE FULL REGISTRY">LE REGISTRE COMPLET</p><h1 id="wiki-title" data-fr="Tout le wiki" data-en="The whole wiki">Tout le wiki</h1><p class="wiki-intro-text" data-fr="Toutes les fiches et tous les articles publiés, vérifiés et sourcés. Cherchez un mot-clé ou filtrez par rubrique." data-en="Every published, reviewed and sourced entry and article. Search a keyword or filter by category.">Toutes les fiches et tous les articles publiés, vérifiés et sourcés. Cherchez un mot-clé ou filtrez par rubrique.</p>${form}</section>\n`;
  return template.slice(0,hero)+intro+template.slice(archives,tools)+template.slice(catalog);
}
export async function siteMarkup({projectRoot=root,payload,lang='fr',prefix='../',page='home',navEntries}={}){
  const data=payload??await sitePayload({projectRoot});
  navEntries??=await siteEntries({projectRoot});
  let template=await readFile(resolve(projectRoot,'public/wiki/template.html'),'utf8');
  if(page==='wiki')template=wikiTemplate(template);
  if(lang==='en')template=english(template);
  template=withSiteHeader(template,{lang,prefix,payload:data,page,navEntries});
  return template+'\n<script id="wiki-data" type="application/json">'+scriptJSON(data)+'</script>';
}

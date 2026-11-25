import {readFile,writeFile,mkdir,cp,copyFile,rm} from 'node:fs/promises';
import {resolve} from 'node:path';
import {root,sitePayload,siteMarkup,siteEntries,loadCategories} from '../lib/site.mjs';
import {setNavCatalog,searchIndex,SITE_NAME} from '../lib/site-chrome.mjs';
import {renderEntryPage,renderCategoryPage,renderPreviewHub,setCategoryNames,renderFeatured,setVisualLinks} from '../lib/pages.mjs';
import {entryPath,categoryPath,CATEGORY_SLUGS} from '../lib/articles.mjs';

// --preview builds a LOCAL review site including drafts into dist-preview/ (never packaged, never deployed).
const preview=process.argv.includes('--preview');
const base=resolve(root,'public/wiki');
async function writePages(outDir,entries,{preview=false}={}){
  const categories=await loadCategories();
  setCategoryNames(categories);
  setVisualLinks(entries);
  setNavCatalog({categories,entries});
  let pages=0;
  for(const lang of ['fr','en']){
    for(const category of Object.keys(CATEGORY_SLUGS)){
      await mkdir(resolve(outDir,categoryPath(category,lang)),{recursive:true});
      await writeFile(resolve(outDir,categoryPath(category,lang),'index.html'),renderCategoryPage(category,{lang,entries,preview}));pages+=1;
    }
    for(const entry of entries){
      await mkdir(resolve(outDir,entryPath(entry,lang)),{recursive:true});
      await writeFile(resolve(outDir,entryPath(entry,lang),'index.html'),renderEntryPage(entry,{lang,all:entries,preview}));pages+=1;
    }
  }
  return pages;
}
if(preview){
  const outDir=resolve(root,'dist-preview');
  await rm(outDir,{recursive:true,force:true});await mkdir(outDir,{recursive:true});
  await cp(resolve(base,'assets'),resolve(outDir,'assets'),{recursive:true,filter:source=>!source.endsWith('.png')});
  await copyFile(resolve(base,'site.css'),resolve(outDir,'site.css'));
  await copyFile(resolve(base,'wk-header.js'),resolve(outDir,'wk-header.js'));await copyFile(resolve(root,'lib/ui-core.mjs'),resolve(outDir,'ui-core.mjs'));
  const entries=await siteEntries({preview:true});
  const categories=await loadCategories();
  const pages=await writePages(outDir,entries,{preview:true});
  for(const lang of ['fr','en']){await mkdir(resolve(outDir,lang),{recursive:true});await writeFile(resolve(outDir,lang,'index.html'),renderPreviewHub({lang,entries,categories}));}
  await writeFile(resolve(outDir,'index.html'),renderPreviewHub({lang:'fr',entries,categories,prefix:'./'}));
  await writeFile(resolve(outDir,'PREVIEW-LOCAL-ONLY.txt'),'Aperçu local avec brouillons. Ne jamais déployer ni empaqueter. / Local preview with drafts. Never deploy or package.\n');
  console.log(`Preview built (LOCAL ONLY): ${entries.length} entries (${entries.filter(e=>e.status!=='published').length} non-published), ${pages} pages in dist-preview/.`);
  process.exit(0);
}

const out=resolve(root,'dist'), artifacts=resolve(root,'artifacts');
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});await mkdir(artifacts,{recursive:true});
const payload=await sitePayload();
// One home markup per language and depth: the shared header carries relative links (./ at the root, ../ under /fr/ and /en/).
const markups={};
const navEntries=await siteEntries();
for(const lang of ['fr','en'])for(const prefix of ['./','../'])markups[lang+prefix]=await siteMarkup({payload,lang,prefix,navEntries});
// L1b: "Tout le wiki" registry page, one level deeper (/fr/wiki/, /en/wiki/).
for(const lang of ['fr','en'])markups[lang+'wiki']=await siteMarkup({payload,lang,prefix:'../../',page:'wiki',navEntries});
const [css,app,core,headerJS]=await Promise.all([readFile(resolve(base,'site.css'),'utf8'),readFile(resolve(base,'app.js'),'utf8'),readFile(resolve(root,'lib/ui-core.mjs'),'utf8'),readFile(resolve(base,'wk-header.js'),'utf8')]);
await copyFile(resolve(root,'lib/ui-core.mjs'),resolve(base,'ui-core.mjs'));
await cp(resolve(base,'assets'),resolve(out,'assets'),{recursive:true,filter:source=>!source.endsWith('.png')});
await Promise.all([writeFile(resolve(out,'site.css'),css),writeFile(resolve(out,'app.js'),app),writeFile(resolve(out,'ui-core.mjs'),core),writeFile(resolve(out,'wk-header.js'),headerJS)]);
// Search overlay index (published DTO fields only), fetched by wk-header.js when the overlay opens.
await writeFile(resolve(out,'search-index.json'),JSON.stringify(searchIndex(payload)));
function html({lang='fr',prefix='./',standalone=false,inlineCSS='',inlineJS='',page='home'}={}){
  const wiki=page==='wiki';
  const title=wiki?(lang==='fr'?`Tout le wiki — ${SITE_NAME}`:`The whole wiki — ${SITE_NAME}`):lang==='fr'?`${SITE_NAME} — Archives & aventures`:`${SITE_NAME} — Archives & adventures`;
  const head=`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#0b141b">${standalone?'':`<link rel="icon" href="${prefix}assets/favicon.svg" type="image/svg+xml">`}<title>${title}</title><meta name="description" content="${lang==='fr'?'Encyclopédie fantasy bilingue indépendante, en construction. Site indépendant et non officiel de Blizzard Entertainment.':'Independent bilingual fantasy encyclopedia, under construction. Independent, unofficial site, not affiliated with Blizzard Entertainment.'}">${standalone?`<style>${inlineCSS}</style>`:`${wiki?'':`<link rel="preload" href="${prefix}assets/hero.webp" as="image">`}<link rel="stylesheet" href="${prefix}site.css">`}</head>`;
  const body=wiki?markups[lang+'wiki']:markups[lang+(prefix==='./'?'./':'../')];
  const withFeatured=standalone||wiki?body:body.replace('<section id="archives"',renderFeatured({lang,entries:publicEntries,prefix:prefix==='./'?'./':prefix})+'<section id="archives"');
  return head+`<body><div id="wiki-app" data-language="${lang}"${standalone?'':` data-root="${prefix}"`}${wiki?' data-page="wiki"':''}>${withFeatured}</div>`+(standalone?`<script>\n(()=>{\n${inlineJS}\n})();\n</script>`:`<script type="module" src="${prefix}app.js"></script><script type="module" src="${prefix}wk-header.js"></script>`)+`<noscript><p>Activez JavaScript pour la recherche, les filtres et la navigation interactive. / Enable JavaScript for search, filters and interactive navigation.</p></noscript></body></html>`;
}
const publicEntries=await siteEntries();
if(publicEntries.some(entry=>entry.status!=='published'))throw new Error('refusing to render a non-published entry in the public build');
setCategoryNames(await loadCategories());
setVisualLinks(publicEntries);
setNavCatalog({categories:payload.categories,entries:publicEntries});
await writeFile(resolve(out,'index.html'),html());
for(const lang of ['fr','en']){await mkdir(resolve(out,lang),{recursive:true});await writeFile(resolve(out,lang,'index.html'),html({lang,prefix:'../'}));}
for(const lang of ['fr','en']){await mkdir(resolve(out,lang,'wiki'),{recursive:true});await writeFile(resolve(out,lang,'wiki','index.html'),html({lang,prefix:'../../',page:'wiki'}));}
const pageCount=await writePages(out,publicEntries);
// A separate self-contained file supports file:// on Android and desktop without module CORS.
let inlineCSS=css;const embedded=new Map();let variables='';
for(const match of [...css.matchAll(/url\(['"]?(\.\/assets\/[^)'"\s]+)['"]?\)/g)]){
  const filename=match[1];
  if(!embedded.has(filename)){
    const data=await readFile(resolve(base,filename));
    const type=filename.endsWith('.svg')?'image/svg+xml':filename.endsWith('.webp')?'image/webp':'image/png';
    const name=`--embedded-asset-${embedded.size}`;
    embedded.set(filename,name);
    variables+=`${name}:url("data:${type};base64,${data.toString('base64')}");`;
  }
  inlineCSS=inlineCSS.replaceAll(match[0],`var(${embedded.get(filename)})`);
}
inlineCSS=':root{'+variables+'}\n'+inlineCSS;
const inlineJS=(core.replace(/^export /gm,'')+'\n'+app.replace(/^import[^\n]*\n/,'').replace(/^export /gm,'')).replace(/<\/script/gi,'<\\/script');
const standalone=html({standalone:true,inlineCSS,inlineJS});
await writeFile(resolve(artifacts,'wow-forever-integre.html'),standalone);
await writeFile(resolve(artifacts,'public-report.json'),JSON.stringify({categories:payload.categories.length,published:payload.entries.length,standaloneBytes:Buffer.byteLength(standalone),publicFiles:['index.html','fr/index.html','en/index.html','fr/wiki/','en/wiki/','fr/<category>/','fr/<category>/<slug>/','en/<category>/','en/<category>/<slug>/','site.css','app.js','ui-core.mjs','wk-header.js','search-index.json','assets/*'],pages:pageCount,deployment:'not deployed'},null,2));
console.log(`Static integration built: ${payload.categories.length} categories, ${payload.entries.length} published entries, ${pageCount} static pages. Standalone ${Math.round(Buffer.byteLength(standalone)/1024)} KiB.`);

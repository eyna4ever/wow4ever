// WoWki4ever v2 — PROPOSAL build (branch refonte-v2). Writes a local review site to dist-v2/ (never packaged, never deployed).
// Published entries only: refuses to run if a draft would be rendered.
import {writeFile,mkdir,cp,copyFile,rm} from 'node:fs/promises';
import {resolve} from 'node:path';
import {root,sitePayload,siteEntries,loadCategories,loadRecords} from '../lib/site.mjs';
import {searchIndex} from '../lib/site-chrome.mjs';
import {setCategoryNames,setVisualLinks} from '../lib/pages.mjs';
import {entryPath,categoryPath} from '../lib/articles.mjs';
import {setV2Catalog,renderHome,renderGame,renderCategory,renderEntry,renderIndex,renderMoved,gamePath,wikiIndexPath} from '../lib/v2/render.mjs';
import {loadMerges,mergeStubs} from '../lib/v2/merges.mjs';
import {SECTIONS,inListing} from '../lib/v2/structure.mjs';

const out=resolve(root,'dist-v2'), base=resolve(root,'public/wiki');
const entries=(await siteEntries()).filter(entry=>entry.status==='published');
const all=await siteEntries();
if(all.some(entry=>entry.status!=='published'))throw new Error('siteEntries() returned a non-published entry — refusing to build v2.');
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
await cp(resolve(base,'assets'),resolve(out,'assets'),{recursive:true,filter:source=>!source.endsWith('.png')});
await copyFile(resolve(base,'wk-header.js'),resolve(out,'wk-header.js'));
await copyFile(resolve(root,'lib/ui-core.mjs'),resolve(out,'ui-core.mjs'));
await copyFile(resolve(root,'public/v2/v2.css'),resolve(out,'v2.css'));
for (const f of ['theme.js','theme-wow.css']) await copyFile(resolve(root,'public/v2',f),resolve(out,f)); // v20 theme switcher
await cp(resolve(root,'public/v2/assets'),resolve(out,'assets'),{recursive:true}); // V2c illustrations (v2-*.webp/.jpg)
// v39 test UI: the scoped v39 rules / script are APPENDED to v2.css and wk-header.js (the only names the Flask wiki allowlist
// serves). Every v39 rule is scoped to body.v39 and the script returns at once without it, so the forum (same files) is unchanged.
{ const {readFile}=await import('node:fs/promises');
  await writeFile(resolve(out,'v2.css'),(await readFile(resolve(out,'v2.css'),'utf8'))+'\n'+await readFile(resolve(root,'public/v39/v39.css'),'utf8'));
  await writeFile(resolve(out,'wk-header.js'),(await readFile(resolve(out,'wk-header.js'),'utf8'))+'\n'+await readFile(resolve(root,'public/v39/v39-nav.js'),'utf8')); }
await writeFile(resolve(out,'search-index.json'),JSON.stringify(searchIndex(await sitePayload())));
setCategoryNames(await loadCategories());
setVisualLinks(entries);
setV2Catalog(entries);
const write=async(path,html)=>{await mkdir(resolve(out,path),{recursive:true});await writeFile(resolve(out,path,'index.html'),html);pages+=1;};
let pages=0;
const cats=SECTIONS.flatMap(section=>section.categories).filter(cat=>inListing(entries,cat).length);
for(const lang of ['fr','en']){
  await write(`${lang}/`,renderHome(lang));
  await write(gamePath(lang),renderGame(lang));
  await write(wikiIndexPath(lang),renderIndex(lang));
  for(const cat of cats)await write(categoryPath(cat,lang),renderCategory(cat,lang));
  for(const entry of entries)await write(entryPath(entry,lang),renderEntry(entry,lang));
}
// v15: addresses of merged entries keep working (static page -> kept entry); see lib/v2/merges.mjs.
const {stubs,pending}=mergeStubs(await loadRecords(),entries,await loadMerges(root));
for(const stub of stubs)await write(stub.path,renderMoved(stub.retired,stub.target,stub.lang,stub.at));
if(pending.length)console.log(`merges not applied yet (still published): ${pending.join(', ')}`);
await writeFile(resolve(out,'index.html'),renderHome('fr','./'));pages+=1; // site root = French home (relative links from /)
await writeFile(resolve(out,'PROPOSITION-V2-LOCALE.txt'),'Proposition v2 (branche refonte-v2). Revue locale uniquement — ne pas déployer.\n');
console.log(`v2 proposal built: ${entries.length} published entries, ${pages} pages in dist-v2/ (${stubs.length} merged-page redirects).`);

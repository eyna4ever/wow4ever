/** Optional real browser check. No network downloads. Synthetic game data is never injected. */
const {existsSync,mkdirSync}=require('node:fs');
const {resolve}=require('node:path');
const {pathToFileURL}=require('node:url');
const assert=require('node:assert/strict');
// Portable lookup: WIKI_PLAYWRIGHT_MODULE (path to playwright or playwright-core), then local packages.
let playwright;
for(const name of [process.env.WIKI_PLAYWRIGHT_MODULE,'playwright','playwright-core'].filter(Boolean)){
 try{playwright=require(name);break;}catch{}
}
if(!playwright){console.error('Playwright not found: install playwright or playwright-core, or set WIKI_PLAYWRIGHT_MODULE. Browser check not executed.');process.exit(2);}
(async()=>{
 const root=resolve(__dirname,'..');
 mkdirSync(resolve(root,'artifacts'),{recursive:true});
 const executable=process.env.WIKI_BROWSER_EXECUTABLE??(['/usr/bin/chromium','/usr/bin/chromium-browser','/usr/bin/google-chrome'].find(path=>existsSync(path)));
 const browser=await playwright.chromium.launch({executablePath:executable,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(resolve(root,'artifacts/wow-forever-integre.html')).href);
 assert.equal(await page.locator('[data-category]').count(),12);
 await page.locator('[data-category="classes"]').click();
 assert.equal(await page.locator('[data-category="classes"]').getAttribute('aria-pressed'),'true');
 await page.locator('#search-input').fill('<script>alert(1)</script>');
 assert.match(await page.locator('#empty-title').innerText(),/<script>/);
 assert.equal(await page.locator('#empty-title script').count(),0);
 await page.locator('#reset-filters').click();
 assert.equal(await page.locator('#search-input').inputValue(),'');
 await page.locator('#favorites-only').check();
 assert.match(await page.locator('#empty-title').innerText(),/favori/);
 // L1 (2026-10-30): the shared WoWki4ever header replaces the in-page FR/EN toggle and the local account button:
 // FR/EN is a link to the other-language page, sign-in is /account/ (Discord). The standalone file keeps no-JS header links.
 assert.equal(await page.locator('.wk-lang').getAttribute('href'),'./en/');
 assert.equal(await page.locator('.wk-discord').first().getAttribute('href'),'/account/');
 assert.equal(await page.locator('#wk-search').isHidden(),true);
 await page.locator('[data-view="maps"]').first().click();
 assert.equal(await page.locator('#feature-panel').isVisible(),true);
 assert.match(await page.locator('#feature-body').innerText(),/Aucune carte|No reviewed map/);
 await page.locator('#reset-filters').click();
 await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:resolve(root,'artifacts/desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
 // Standalone file: wk-header.js is not inlined, so the header stays in its no-JS form (menu links visible, no drawer button).
 assert.equal(await page.locator('#wk-nav').isVisible(),true);
 assert.equal(await page.locator('#wk-menu-toggle').isHidden(),true);
 await page.locator('#reset-filters').click();await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:resolve(root,'artifacts/mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 await browser.close();console.log('PASS browser: categories, literal search, reset, shared header links (FR/EN, Discord), map panel, no-JS mobile header, horizontal overflow, zero page errors.');
})().catch(e=>{console.error(e.message);process.exitCode=1});

// v11 (mobile-first, 31/10/2026): guards for the phone-first stylesheet and the responsive image markup of the v2 site.
import {test, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, access} from 'node:fs/promises';
import {siteEntries} from '../lib/site.mjs';
import {setCategoryNames, setVisualLinks, UNOFFICIAL} from '../lib/pages.mjs';
import {SECTIONS, inListing} from '../lib/v2/structure.mjs';
import {setV2Catalog, renderHome, renderGame, renderCategory, renderEntry, renderIndex} from '../lib/v2/render.mjs';

const categories = JSON.parse(await readFile(new URL('../public/wiki/catalog.json', import.meta.url), 'utf8')).categories;
const published = (await siteEntries()).filter(entry => entry.status === 'published');
const setup = () => { setCategoryNames(categories); setVisualLinks(published); setV2Catalog(published); };
afterEach(() => setVisualLinks([]));
const css = await readFile(new URL('../public/v2/v2.css', import.meta.url), 'utf8');
const exists = async rel => { try { await access(new URL(`../public/${rel}`, import.meta.url)); return true; } catch { return false; } };

test('v11 stylesheet is mobile-first: larger screens via min-width, small-screen-only rules stay narrow', () => {
  const queries = [...css.matchAll(/@media\s*([^{]+)\{/g)].map(m => m[1].replace(/\s+/g, ''));
  const mins = queries.filter(q => /^\(min-width:\d+px\)$/.test(q));
  assert.ok(mins.length >= 4, 'min-width blocks for tablets and desktops');
  // the header base (phones) is the compact bar; desktop restores its larger shadow
  assert.match(css, /\.wk-header\{position:sticky;top:0;z-index:60;box-shadow:0 1px 0 #0008;/);
  assert.match(css, /@media\(min-width:1101px\)\{[^@]*\.wk-header\{box-shadow:0 8px 30px #0008\}/);
  // no expensive scroll-time effects anywhere
  assert.doesNotMatch(css, /backdrop-filter|background-attachment:\s*fixed/);
  // never a remote resource
  assert.doesNotMatch(css, /@import|https?:|url\(\s*["']?\/\//i);
});

test('v11 drawer opens with opacity/transform only, compact before JavaScript, still usable without it', () => {
  assert.match(css, /\.wk-header\.is-enhanced \.wk-nav\{display:flex;visibility:hidden;opacity:0;transform:translateY\(-10px\);transition:opacity \.2s ease,transform \.2s ease,visibility 0s linear \.2s;/);
  assert.match(css, /\.wk-header\.is-enhanced \.wk-nav\.is-open\{visibility:visible;opacity:1;transform:none;transition-delay:0s\}/);
  assert.doesNotMatch(css, /\.wk-nav\.is-open\{display:/, 'no display toggle (not animatable, causes reflow)');
  assert.match(css, /@media\(max-width:1220px\) and \(scripting:enabled\)\{[^@]*\.wk-header:not\(\.is-enhanced\) \.wk-nav\{display:flex;visibility:hidden/, 'no layout shift before wk-header.js');
  assert.match(css, /@media\(scripting:none\)\{\.wk-burger\{display:none!important\}\}/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)\{[^@]*\.wk-header \.wk-nav\{transition:none!important\}|@media\(prefers-reduced-motion:reduce\)\{[^@]*\.wk-header \.wk-nav\{?[^}]*transition:none!important/);
});

test('v11 pages: AVIF+WebP pictures with existing files, explicit sizes, one high-priority image, no hidden burger, JS preloaded', async () => {
  setup();
  const pages = [];
  for (const lang of ['fr', 'en']) {
    pages.push(renderHome(lang), renderGame(lang), renderIndex(lang));
    for (const cat of SECTIONS.flatMap(s => s.categories)) if (inListing(published, cat).length) pages.push(renderCategory(cat, lang));
    for (const entry of published) pages.push(renderEntry(entry, lang));
  }
  const files = new Set();
  for (const html of pages) {
    assert.ok(html.includes(UNOFFICIAL.fr));
    for (const pic of html.match(/<picture>.*?<\/picture>/g) ?? []) {
      assert.match(pic, /^<picture><source type="image\/avif" srcset="[^"]+" sizes="[^"]+">/, pic.slice(0, 120));
      assert.match(pic, /<img [^>]*width="\d+" height="\d+"/);
      for (const m of pic.matchAll(/(?:\.\.\/)*assets\/([a-z0-9-]+\.(?:avif|webp|jpg))/g)) files.add(m[1]);
    }
    for (const img of html.match(/<img [^>]*>/g) ?? []) assert.match(img, /width="\d+" height="\d+"/, img);
    assert.ok((html.match(/fetchpriority="high"/g) ?? []).length <= 1, 'at most one high-priority image (hero or banner)');
    assert.doesNotMatch(html, /id="wk-menu-toggle"[^>]*\shidden/);
    assert.match(html, /<link rel="modulepreload" href="(\.\.\/)*wk-header\.js"><link rel="modulepreload" href="(\.\.\/)*ui-core\.mjs">/);
    // v20: v2.css + the opt-in theme-wow.css (all its rules are scoped to html[data-theme=wow]).
    assert.deepEqual(html.match(/<link rel="stylesheet" href="[^"]+"/g)?.map(l => l.replace(/.*\//, '')), ['v2.css"', 'theme-wow.css"']);
  }
  for (const f of files) assert.ok(await exists(`v2/assets/${f}`) || await exists(`wiki/assets/${f}`), f);
  assert.ok([...files].filter(f => f.endsWith('.avif')).length >= 60);
});

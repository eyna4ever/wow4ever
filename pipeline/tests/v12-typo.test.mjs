// v12 (31/10/2026, "pas de correspondance entre les bordures gauche et droite de l'écran", police un peu plus petite et
// plus lisible sur tous les téléphones): guards for the phone block of v2.css. The browser test is ops/v12/symmetry.py.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const css = await readFile(new URL('../public/v2/v2.css', import.meta.url), 'utf8');
const block = q => { const i = css.lastIndexOf(`@media(${q}){`); assert.ok(i >= 0, `block ${q}`); let d = 0, j = css.indexOf('{', i);
  for (let k = j; k < css.length; k++) { if (css[k] === '{') d++; else if (css[k] === '}' && --d === 0) return css.slice(j + 1, k); } };
const phone = block('max-width:640px');

test('v12 phones: one symmetric gutter (safe areas included) for header, hero, content, menu and footer', () => {
  assert.match(phone, /--g:max\(16px,env\(safe-area-inset-left\),env\(safe-area-inset-right\)\)/);
  assert.match(phone, /\.v2-hero-copy,\.v2-featured,\.v2-home-grid,\.v2-banner-copy,\.v2-wrap,\.v2-footer-inner,\.v2-footer \.independence\{padding-left:var\(--g\);padding-right:var\(--g\)\}/);
  assert.match(phone, /\.wk-header \.wk-nav\{padding-left:var\(--g\)!important;padding-right:var\(--g\)!important\}/);
  assert.match(block('max-width:480px'), /\.wk-bar\{padding-left:var\(--g\);padding-right:var\(--g\);gap:8px\}/);
  assert.match(block('max-width:480px'), /\.wk-brand\{flex:0 1 auto;min-width:0;gap:8px;min-height:44px\}/, 'the logo shrinks instead of pushing the buttons out');
  // grids never grow wider than the phone (min-content of a card or a nowrap list)
  assert.match(css, /\.v2-cards\.is-2\{grid-template-columns:repeat\(auto-fill,minmax\(min\(260px,100%\),1fr\)\)\}/);
  assert.match(css, /\.v2-cat-grid\{[^}]*minmax\(min\(270px,100%\),1fr\)/);
  assert.match(css, /\.v2-index-grid\{[^}]*minmax\(min\(280px,100%\),1fr\)/);
  assert.match(phone, /\.v2-cards,\.v2-lead,\.v2-layout\{grid-template-columns:minmax\(0,1fr\)\}/);
  assert.doesNotMatch(css, /100vw/, 'no 100vw box (scrollbar makes it wider than the page)');
});

test('v12 phones: smaller fluid type, 1.6 line height, no text inflation, long words wrap, tables scroll', () => {
  assert.match(css, /html\{[^}]*-webkit-text-size-adjust:100%;text-size-adjust:100%/);
  assert.match(css, /--sans:system-ui,-apple-system,Roboto,'Segoe UI','Noto Sans','Helvetica Neue',Arial,sans-serif/);
  assert.match(phone, /body\.v2\{font-size:clamp\(14\.5px,13\.5px \+ \.3125vw,15\.5px\);line-height:1\.6;letter-spacing:normal\}/);
  assert.match(phone, /\.v2-article p,\.v2-article li\{font-size:clamp\(15px,13\.5px \+ \.47vw,16\.5px\);line-height:1\.62\}/);
  assert.match(phone, /\.v2-banner-copy h1\{font-size:clamp\(23px,17\.5px \+ 1\.72vw,30px\)/);
  assert.match(phone, /\.v2-hero-title\{font-size:clamp\(32px,11\.4vw,52px\)/, 'the hero title fits the phone width');
  assert.match(phone, /overflow-wrap:break-word;hyphens:auto/);
  assert.match(css, /\.table-wrap\{overflow-x:auto/);
  // desktop and tablet keep their sizes
  assert.match(css, /@media\(min-width:641px\)\{\nbody\.v2\{font-size:16px\}/);
  assert.match(css, /\.v2-article p,\.v2-article li\{color:#dde3ef;font-size:16\.5px;line-height:1\.72\}/);
  assert.doesNotMatch(css, /@font-face|\.woff/, 'system fonts only');
});

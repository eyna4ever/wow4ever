import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {Script} from 'node:vm';
import {inflateRawSync} from 'node:zlib';
import {selectPublicEntries, homeEntries} from '../lib/public-catalog.mjs';

const attributes = tag => Object.fromEntries([...tag.matchAll(/([\w:-]+)\s*=\s*["']([^"']*)["']/g)].map(match => [match[1], match[2]]));

/** Structural checks only: these do not replace a rendered accessibility audit. */
export function inspectTemplate(html) {
  const tags = [...html.matchAll(/<[a-z][^>]*>/gi)].map(match => match[0]);
  const ids = tags.map(tag => attributes(tag).id).filter(Boolean);
  assert.equal(new Set(ids).size, ids.length, 'duplicate HTML IDs');
  assert.equal((html.match(/<h1\b/g) ?? []).length, 1, 'one main heading required');
  // L1 (2026-10-30): the shared WoWki4ever header replaces the home-only main-nav/menu-toggle/language-toggle controls.
  for (const id of ['main-content', 'search-form', 'search-input', 'wk-nav', 'wk-menu-toggle', 'wk-search', 'wk-search-input', 'categories', 'results', 'result-summary', 'entry-panel', 'feature-panel', 'account-dialog', 'info-dialog']) assert.ok(ids.includes(id), `missing ${id}`);
  assert.match(html, /<label\b[^>]*for=["']search-input["']/i, 'visible or hidden search label required');
  assert.match(html, /class=["'][^"']*skip-link/, 'skip link required');
  assert.ok(html.includes('Site indépendant et non officiel de Blizzard Entertainment.') || html.includes('Independent, unofficial site, not affiliated with Blizzard Entertainment.'), 'unofficial-site notice required');
  const categories = tags.map(tag => attributes(tag)['data-category']).filter(Boolean);
  assert.equal(categories.length, 12, 'twelve category controls required');
  assert.equal(new Set(categories).size, 12, 'unique category controls required');
  for (const tag of tags) {
    const attr = attributes(tag);
    for (const key of ['for', 'aria-controls', 'aria-labelledby']) {
      for (const id of (attr[key] ?? '').split(/\s+/).filter(Boolean)) assert.ok(ids.includes(id), `${key} refers to missing ${id}`);
    }
    if (attr.href?.startsWith('#') && attr.href.length > 1) assert.ok(ids.includes(attr.href.slice(1)), `broken fragment ${attr.href}`);
    if (attr['data-category']) assert.ok(['true', 'false'].includes(attr['aria-pressed']), 'category selected state required');
  }
  return {ids: ids.length, categories: categories.length};
}

export function inspectStandalone(html, sourceRecords) {
  const structure = inspectTemplate(html);
  assert.match(html, /^<!doctype html>/i, 'HTML document required');
  assert.match(html, /<meta\b[^>]*name=["']viewport["']/i, 'mobile viewport required');
  assert.match(html, /<html\b[^>]*lang=["'](?:fr|en)["']/i, 'document language required');
  assert.doesNotMatch(html, /(?:file:\/\/|\/workspace\/|https?:\/\/[^\s"']+\.(?:js|css)(?:[?"']))/i, 'development paths or remote dependencies found');
  const dataMatch = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)].find(match => attributes(match[1]).id === 'wiki-data');
  assert.ok(dataMatch, 'embedded public catalog required');
  const data = JSON.parse(dataMatch[2]);
  assert.equal(data.categories.length, 12, 'embedded twelve-category catalog required');
  assert.deepEqual(data.entries, homeEntries(selectPublicEntries(sourceRecords)), 'export differs from strictly selected publications');
  let executableScripts = 0;
  for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    const attr = attributes(match[1]);
    assert.equal(attr.src, undefined, 'standalone scripts must be embedded');
    if (attr.type === 'application/json' || attr.type === 'application/ld+json') continue;
    assert.notEqual(attr.type, 'module', 'standalone JavaScript must work on file://');
    new Script(match[2], {filename: 'standalone-inline.js'});
    executableScripts += 1;
  }
  assert.ok(executableScripts > 0, 'interactive script required');
  for (const match of html.matchAll(/<(?:img|source|link)\b[^>]*>/gi)) {
    const attr = attributes(match[0]);
    const url = attr.src ?? attr.href;
    if (url) assert.ok(url.startsWith('data:') || url.startsWith('#'), `non-embedded resource ${url}`);
  }
  for (const style of html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) {
    for (const match of style[1].matchAll(/url\(\s*["']?([^)'"\s]+)/gi)) assert.ok(match[1].startsWith('data:'), `non-embedded CSS asset ${match[1]}`);
  }
  return {...structure, entries: data.entries.length, executableScripts};
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

export function inspectArchive(buffer, standalone) {
  assert.ok(Buffer.isBuffer(buffer), 'ZIP buffer required');
  let end = -1;
  for (let offset = buffer.length - 22; offset >= Math.max(0, buffer.length - 65_557); offset -= 1) {
    if (buffer.readUInt32LE(offset) === 0x06054b50 && offset + 22 + buffer.readUInt16LE(offset + 20) === buffer.length) { end = offset; break; }
  }
  assert.ok(end >= 0, 'ZIP end directory missing');
  assert.equal(buffer.readUInt16LE(end + 4), 0, 'multi-disk ZIP unsupported');
  const count = buffer.readUInt16LE(end + 10);
  assert.ok(count > 0 && count < 10_000, 'reasonable archive entry count required');
  let cursor = buffer.readUInt32LE(end + 16), bytes = 0, matchingHTML = false;
  const names = new Set();
  for (let index = 0; index < count; index += 1) {
    assert.equal(buffer.readUInt32LE(cursor), 0x02014b50, 'invalid ZIP central entry');
    const flags = buffer.readUInt16LE(cursor + 8), method = buffer.readUInt16LE(cursor + 10);
    const checksum = buffer.readUInt32LE(cursor + 16), compressedSize = buffer.readUInt32LE(cursor + 20), size = buffer.readUInt32LE(cursor + 24);
    const length = buffer.readUInt16LE(cursor + 28), extra = buffer.readUInt16LE(cursor + 30), comment = buffer.readUInt16LE(cursor + 32);
    const mode = buffer.readUInt32LE(cursor + 38) >>> 16, local = buffer.readUInt32LE(cursor + 42);
    const name = buffer.subarray(cursor + 46, cursor + 46 + length).toString('utf8');
    assert.ok(name && !name.startsWith('/') && !name.includes('\\') && !name.includes('\0') && !name.split('/').includes('..') && !/^[a-z]:/i.test(name), `unsafe ZIP path ${name}`);
    assert.equal(names.has(name), false, `duplicate ZIP path ${name}`);
    names.add(name);
    assert.doesNotMatch(name, /(?:^|\/)(?:runtime|node_modules|\.next|\.git|\.aws|\.codex|\.agents)(?:\/|$)|(?:^|\/)\.env(?!\.example$)|\.(?:pem|key)$/i, `private or generated tree in archive ${name}`);
    assert.notEqual(mode & 0xf000, 0xa000, `symbolic link in archive ${name}`);
    assert.equal(flags & 1, 0, 'encrypted ZIP unsupported');
    assert.ok(method === 0 || method === 8, 'unsupported compression');
    assert.ok(size <= 64_000_000 && (bytes += size) <= 128_000_000, 'archive size bound exceeded');
    assert.equal(buffer.readUInt32LE(local), 0x04034b50, 'missing ZIP local header');
    const start = local + 30 + buffer.readUInt16LE(local + 26) + buffer.readUInt16LE(local + 28);
    const compressed = buffer.subarray(start, start + compressedSize);
    const content = method === 8 ? inflateRawSync(compressed, {maxOutputLength: 64_000_000}) : compressed;
    assert.equal(content.length, size, `size mismatch ${name}`);
    assert.equal(crc32(content), checksum, `checksum mismatch ${name}`);
    if (name.endsWith('wow-forever-integre.html')) matchingHTML = content.equals(Buffer.from(standalone));
    cursor += 46 + length + extra + comment;
  }
  assert.equal(matchingHTML, true, 'current standalone HTML missing from ZIP');
  assert.ok([...names].some(name => name === 'site/index.html'), 'static site entry missing');
  assert.ok([...names].some(name => name === 'sources/README.md'), 'source README missing');
  return {entries: names.size, uncompressedBytes: bytes};
}

export async function main(argv = process.argv.slice(2)) {
  const htmlPath = resolve(argv[0] ?? 'artifacts/wow-forever-integre.html');
  const sourcePath = resolve(argv[1] ?? 'data/entries.json');
  const html = await readFile(htmlPath, 'utf8');
  const sourceRecords = JSON.parse(await readFile(sourcePath, 'utf8'));
  const report = {html: htmlPath, ...inspectStandalone(html, sourceRecords), browser: 'not-tested', archive: null};
  if (argv[2]) report.archive = inspectArchive(await readFile(resolve(argv[2])), html);
  console.log(JSON.stringify(report, null, 2));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main().catch(error => { console.error(`Release integrity failed: ${error.message}`); process.exitCode = 1; });
}

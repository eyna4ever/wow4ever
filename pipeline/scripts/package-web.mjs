/**
 * Package ONLY the public static web folder (dist/) as a tar.gz whose root is the web root
 * (index.html, fr/, en/, assets/...). Extract with: tar -xzf wow4ever-web.tar.gz -C /srv/wow4ever
 * Local only: no network, no deployment. Refuses drafts, SQLite, review files, sources or research.
 * Usage: node scripts/package-web.mjs [--output artifacts/deliveries/wow4ever-web.tar.gz]
 */
import {execFileSync} from 'node:child_process';
import {readFile, mkdir, writeFile} from 'node:fs/promises';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {inventoryStatic, inspectPublicHTML, sha256} from './prepare-demo.mjs';
import {loadDataset} from '../lib/documentary.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const flag = argv.indexOf('--output');
if (flag !== -1 && !argv[flag + 1]) throw new Error('--output requires a path');
const output = resolve(flag !== -1 ? argv[flag + 1] : join(root, 'artifacts/deliveries/wow4ever-web.tar.gz'));
if (/dist-preview/.test(output)) throw new Error('refusing to package next to the local preview');
const dist = join(root, 'dist');
const records = await loadDataset({runtimeDir: join(root, 'runtime'), seedPath: join(root, 'data/entries.json')});
const files = await inventoryStatic(dist); // allow-list: index.html, fr/, en/, site.css, app.js, ui-core.mjs, assets/*.svg|webp|jpg|woff2
let published = 0;
for (const path of ['index.html', 'fr/index.html', 'en/index.html', 'fr/wiki/index.html', 'en/wiki/index.html']) published = inspectPublicHTML(await readFile(join(dist, path), 'utf8'), records);
const draftIds = records.filter(entry => entry.status !== 'published').map(entry => entry.id);
// Article drafts must leave no trace: neither ID, page slug, nor title in any public file.
const {entryPath} = await import('../lib/articles.mjs');
const publishedTitles = new Set(records.filter(entry => entry.status === 'published').flatMap(entry => [entry.title?.fr, entry.title?.en]));
const draftMarkers = records.filter(entry => entry.status !== 'published' && entry.article).flatMap(entry => {
  const markers = [entryPath(entry, 'fr'), entryPath(entry, 'en'), entry.id];
  const slugs = [entry.article?.slug?.fr, entry.article?.slug?.en].filter(Boolean);
  // Titles are not used: category intros can legitimately share wording with a draft title.
  return markers.filter(Boolean);
});
for (const file of files) {
  if (!/\.(html|js|mjs|css|json)$/.test(file.path)) continue;
  const text = await readFile(join(dist, file.path), 'utf8');
  const leak = draftIds.find(id => text.includes(`"${id}"`));
  if (leak) throw new Error(`Unpublished entry ${leak} found in ${file.path}`);
  const marker = draftMarkers.find(value => text.includes(value));
  if (marker) throw new Error(`Unpublished article marker "${marker}" found in ${file.path}`);
  if (/wow4ever-build" content="preview/.test(text)) throw new Error(`Local preview page found in ${file.path}`);
}
// L1: the search-overlay index may only contain published, validated entries that exist in the dataset.
if (files.some(file => file.path === 'search-index.json')) {
  const index = JSON.parse(await readFile(join(dist, 'search-index.json'), 'utf8'));
  const publishedIds = new Set(records.filter(entry => entry.status === 'published').map(entry => entry.id));
  for (const entry of index.entries ?? []) {
    if (!publishedIds.has(entry.id) || entry.status !== 'published' || entry.publicationValidated !== true) throw new Error(`search-index.json: unpublished entry ${entry.id}`);
    for (const key of Object.keys(entry)) if (!['id', 'status', 'publicationValidated', 'category', 'subcategory', 'title', 'description', 'url', 'searchText', 'hasArticle', 'sources'].includes(key)) throw new Error(`search-index.json: unexpected field ${key}`);
  }
}
await mkdir(dirname(output), {recursive: true});
execFileSync('python3', ['-c', `
import sys, tarfile, gzip, io, json, os
src, out, names = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
import time
# Real timestamps keep HTTP Last-Modified meaningful; set SOURCE_DATE_EPOCH for a reproducible archive.
stamp = int(os.environ.get('SOURCE_DATE_EPOCH') or time.time())
tmp = out + '.tmp'
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as tar:
    dirs = sorted({'/'.join(n.split('/')[:i]) for n in names for i in range(1, n.count('/') + 1)})
    for d in dirs:
        info = tarfile.TarInfo(d); info.type = tarfile.DIRTYPE; info.mode = 0o755; info.mtime = stamp
        tar.addfile(info)
    for n in sorted(names):
        data = open(os.path.join(src, n), 'rb').read()
        info = tarfile.TarInfo(n); info.size = len(data); info.mode = 0o644; info.mtime = stamp
        tar.addfile(info, io.BytesIO(data))
with open(tmp, 'wb') as fh:
    with gzip.GzipFile(fileobj=fh, mode='wb', mtime=stamp, filename='') as gz:
        gz.write(raw.getvalue())
os.replace(tmp, out)
`, dist, output, JSON.stringify(files.map(file => file.path))], {stdio: ['ignore', 'inherit', 'inherit']});
const bytes = await readFile(output);
const report = {archive: output, bytes: bytes.length, sha256: sha256(bytes), files: files.length, published, root: 'web root (index.html at top level)', deployment: 'not deployed'};
await writeFile(output + '.sha256', `${report.sha256}  ${output.split('/').pop()}\n`);
console.log(JSON.stringify(report, null, 2));

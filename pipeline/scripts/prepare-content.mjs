import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile, copyFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {loadDataset, auditDataset, digest} from '../lib/documentary.mjs';

const root = resolve(import.meta.dirname, '..');
const out = join(root, 'artifacts/content-package');
// Portable delivery folder: --output-dir <dir> or WOW_FOREVER_OUTPUT_DIR, else artifacts/deliveries inside the project.
const outputFlag = process.argv.indexOf('--output-dir');
if (outputFlag !== -1 && !process.argv[outputFlag + 1]) throw new Error('--output-dir requires a path');
const downloads = resolve(outputFlag !== -1 ? process.argv[outputFlag + 1] : (process.env.WOW_FOREVER_OUTPUT_DIR || join(root, 'artifacts/deliveries')));
await mkdir(out, {recursive: true, mode: 0o700});
await mkdir(downloads, {recursive: true, mode: 0o700});
function run(script, args = []) {
  const stdout = execFileSync(process.execPath, [join(root, script), ...args], {cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 8_000_000});
  console.log(JSON.stringify({step: script, status: 'completed'}));
  return stdout;
}
run('scripts/import-library.mjs');
const records = await loadDataset({runtimeDir: join(root, 'runtime'), seedPath: join(root, 'data/entries.json')});
const audit = auditDataset(records);
if (audit.errors.length) throw new Error('Invalid documentary dataset; no review package produced.');
run('scripts/content-report.mjs', ['--output-dir', out]);
run('scripts/content-review.mjs', ['--output', join(out, 'relecture.html')]);
run('scripts/export-content-sqlite.mjs', ['--output', join(out, 'wiki.sqlite')]);
await writeFile(join(out, 'entries.json'), JSON.stringify(records, null, 2) + '\n', {mode: 0o600});
const sourceFiles = ['forever-classes-sources.json', 'forever-world-sources.json', 'forever-systems-sources.json'];
for (const name of sourceFiles) await copyFile(join(root, 'data/research', name), join(out, name));
await writeFile(join(out, 'LIRE-MOI.txt'), [
  'WoW Forever Wiki — dossier privé de relecture',
  '',
  `${records.length} fiches FR/EN ; ${audit.published} publications déclarées.`,
  'Périmètre candidat : jeu Blizzard World of Warcraft: Forever, annonces et bêta consultées le 19 octobre 2026.',
  'Le propriétaire du wiki doit confirmer ce périmètre et faire vérifier faits, droits et traductions.',
  'Ouvrir relecture.html sur téléphone ou ordinateur. Ce document ne publie ni ne valide les fiches.',
  'wiki.sqlite est une base relationnelle locale exportée, pas une base hébergée ou connectée au site.',
  'entries.json conserve les statuts et l’historique réel du magasin local.',
  'Les fichiers sources recensent les références consultées et les limites, sans copie intégrale des pages.',
  'Les traductions FR/EN d’un même article ne sont pas des confirmations indépendantes.',
  'Complétude inconnue sans inventaire exhaustif de la version exacte du jeu.',
  'Ne pas placer ce paquet, la base ou les brouillons dans public/ ou dist/.',
  ''
].join('\n'), {mode: 0o600});
const names = ['LIRE-MOI.txt', 'relecture.html', 'wiki.sqlite', 'entries.json', 'content-report.json', 'content-report.md', ...sourceFiles];
const manifest = {format: 1, datasetChecksum: digest(records), records: records.length, published: audit.published, files: []};
for (const name of names) {
  const bytes = await readFile(join(out, name));
  manifest.files.push({name, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
}
await writeFile(join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', {mode: 0o600});
names.push('manifest.json');
const archive = join(downloads, 'wow-forever-base-documentaire.zip');
execFileSync('python3', ['-c', `
import json, os, pathlib, sys, zipfile
folder, archive, names = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), json.loads(sys.argv[3])
temporary = archive.with_suffix('.zip.tmp')
try:
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in names:
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100600 << 16
            output.writestr(info, (folder / name).read_bytes())
    with zipfile.ZipFile(temporary) as check:
        if check.testzip() is not None: raise RuntimeError('Invalid ZIP')
    os.replace(temporary, archive)
finally:
    if temporary.exists(): temporary.unlink()
`, out, archive, JSON.stringify(names)], {cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe']});
await copyFile(join(out, 'relecture.html'), join(downloads, 'wow-forever-relecture.html'));
console.log(JSON.stringify({archive, review: join(downloads, 'wow-forever-relecture.html'), sqlite: join(out, 'wiki.sqlite'), records: records.length, published: audit.published}, null, 2));

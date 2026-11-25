#!/usr/bin/env python3
"""v9 (refonte v2c, 30/10/2026): replace wiki/ by the v2c static build and record the new test baselines.

Input : pipeline/artifacts/wow4ever-wiki-v2.tar.gz (ops/v2/package.sh, reproducible), verified by SHA-256.
Steps : 1) BEFORE replacing, fingerprint the documentary content of the current v8 wiki/ (article sections + sources
           blocks of every entry page) -> tests/v8-content-fingerprint.json;
        2) replace wiki/ by the archive content (allow-listed names only, no links/special files, no '..');
        3) write tests/wiki-baseline.json = SHA-256 of every file of the v2c build (no edit, nothing added).
Usage: python3 tools/integrate_v2.py TARBALL --expected-sha SHA [--source LABEL]
(v10: same tool, new build of contenu-v10 91c9048; the v8 reference fingerprint is kept as is.)
"""
import argparse, hashlib, io, json, re, shutil, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = re.compile(r'(index\.html|v2\.css|ui-core\.mjs|wk-header\.js|search-index\.json|assets/[a-z0-9-]+\.(avif|webp|jpg|svg)|(fr|en)/([a-z0-9-]+/)*index\.html)')
sys.path.insert(0, str(ROOT / 'tools'))
from content_blocks import article_blocks  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tarball', type=Path)
    ap.add_argument('--expected-sha', required=True)
    ap.add_argument('--source', default='wow4ever-wiki-v2.tar.gz (static build v2c, wowki4ever-source refonte-v2 c05707b, ops/v2/package.sh)')
    args = ap.parse_args()
    raw = args.tarball.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.expected_sha:
        raise SystemExit(f'SHA-256 inattendu pour {args.tarball}')
    wiki = ROOT / 'wiki'
    if (ROOT / 'tests/v8-content-fingerprint.json').exists():
        reference = json.loads((ROOT / 'tests/v8-content-fingerprint.json').read_text())
    else:
        if not (wiki / 'wk-header.js').is_file() or (wiki / 'v2.css').exists():
            raise SystemExit('wiki/ actuel : la build v8 est attendue pour l’empreinte de référence.')
        pages = {}
        for p in sorted(wiki.rglob('index.html')):
            blocks = article_blocks(p.read_text('utf-8'))
            if blocks:
                pages[str(p.relative_to(wiki))] = hashlib.sha256('\n'.join(blocks).encode()).hexdigest()
        reference = {'source': 'wiki v8 (release 20261030T172843, wowki4ever-source 4b0ad76, build 771326700019ddecc57e5ea14f6380b6f7451f0447b5c5fcf0d7574a359d915f)', 'pages': pages}
        (ROOT / 'tests/v8-content-fingerprint.json').write_text(json.dumps(reference, ensure_ascii=False, indent=1) + '\n')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        members = tar.getmembers()
        for m in members:
            name = m.name[2:] if m.name.startswith('./') else m.name
            if m.isdir():
                continue
            if not m.isfile() or '..' in Path(name).parts or name.startswith('/') or not ALLOWED.fullmatch(name):
                raise SystemExit(f'entrée refusée dans l’archive : {m.name}')
            files[name] = tar.extractfile(m).read()
    shutil.rmtree(wiki, ignore_errors=True)
    for name, data in sorted(files.items()):
        (wiki / name).parent.mkdir(parents=True, exist_ok=True)
        (wiki / name).write_bytes(data)
    baseline = {'source': args.source,
                'tarball_sha256': args.expected_sha,
                'files': {k: hashlib.sha256(v).hexdigest() for k, v in sorted(files.items())}}
    (ROOT / 'tests/wiki-baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=1) + '\n')
    print(f'Wiki v2c intégré : {len(files)} fichiers, {sum(1 for f in files if f.endswith(".html"))} pages HTML ; '
          f'référence v8 : {len(reference["pages"])} pages documentaires.')


if __name__ == '__main__':
    main()

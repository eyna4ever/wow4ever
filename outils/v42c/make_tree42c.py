#!/usr/bin/env python3
"""v42c (t412u/t413u) : v42c-test/tree = v42b en ligne (v42b-test/tree) + recherche dans la page « Tout le wiki » + adresses
versionnées (?v=42c) de wk-header.js, ui-core.mjs et v2.css sur toutes les pages (un module en cache ne peut plus rester ancien)."""
import re, shutil, subprocess
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42b-test/tree'; B = R / 'v42c-test/tree'; P = Path('/tmp/v42c-pipeline')
subprocess.run(['node', 'scripts/build-v2.mjs'], cwd=P, check=True, capture_output=True)
if B.exists(): shutil.rmtree(B)
shutil.copytree(A, B, symlinks=True)
W = B / 'wiki'
shutil.copyfile(P / 'dist-v2/wk-header.js', W / 'wk-header.js')
assert (P / 'dist-v2/ui-core.mjs').read_bytes() == (A / 'wiki/ui-core.mjs').read_bytes()
with open(W / 'v2.css', 'a', encoding='utf-8') as fh: fh.write((R / 'v42c-test/css/v42c-recherche.css').read_text('utf-8'))
RX = re.compile(r'((?:href|src)="(?:\.\./|\./)*(?:wk-header\.js|ui-core\.mjs|v2\.css))"')
n = 0
for f in sorted(W.rglob('*.html')):
    t = f.read_text('utf-8'); nt, k = RX.subn(r'\1?v=42c"', t)
    if 'http-equiv="refresh"' not in t:
        assert k == 4, (f, k)  # stylesheet v2.css + 2 modulepreload + script module
    if k: f.write_text(nt, 'utf-8'); n += 1
print('pages versionnées', n)

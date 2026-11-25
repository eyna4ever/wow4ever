#!/usr/bin/env python3
"""v42c : compare v42c-test/tree à v42b (en ligne). Seules différences permises : ?v=42c sur 3 adresses dans les pages,
wk-header.js (mode « dans la page »), v2.css (règles ajoutées à la fin), tests/. Contenu, chemins, CSP, Caddy inchangés."""
import filecmp, re, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42b-test/tree'; B = R / 'v42c-test/tree'
bad = []; changed = []
def walk(p):
    return {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
fa, fb = walk(A), walk(B)
if fa != fb: bad.append(('fichiers ajoutés/retirés', sorted(fa ^ fb)[:10]))
for f in sorted(fa & fb):
    if filecmp.cmp(A / f, B / f, shallow=False): continue
    changed.append(f)
    if f.startswith('tests/') or f == 'wiki/wk-header.js': continue
    if f == 'wiki/v2.css':
        a, b = (A / f).read_text(), (B / f).read_text()
        if not (b.startswith(a) and 'wk-search-inline' in b[len(a):]): bad.append(f)
        continue
    if f.endswith('.html'):
        a, b = (A / f).read_text(), (B / f).read_text()
        if b.replace('?v=42c"', '"') != a or b.count('?v=42c"') != 4: bad.append(f)
        continue
    bad.append(f)
js = (B / 'wiki/wk-header.js').read_text()
for need in ["from './ui-core.mjs?v=42c'", 'wk-search-inline', 'overlay.hidden && !inline']:
    if need not in js: bad.append(('js', need))
if js.count('fetch(') != 1 or re.search(r'innerHTML|eval\(|https://', js): bad.append('js interdits')
html = sum(1 for f in changed if f.endswith('.html'))
print('modifiés', len(changed), 'dont html', html, '; problèmes', bad if bad else 0)
sys.exit(1 if bad or html != 473 else 0)

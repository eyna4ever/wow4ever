#!/usr/bin/env python3
"""v42b (t409u/t410u) : contrôles de la recherche détaillée sur v42b-test/tree, base = v42 en ligne (v42-test/tree, 4c9a4378…)."""
import json, re, hashlib, gzip, subprocess, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42-test/tree'; B = R / 'v42b-test/tree'
ERR = []; INFO = {}
E = ERR.append
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
if base != '4c9a437871db7bc1efe24d56206944fdb4f6f1260f65555e66909c170ac682ed': E(f'base v42 inattendue {base}')
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B)
if fa - fb: E(f'fichiers disparus {sorted(fa - fb)[:5]}')
if fb - fa != {'wiki/search-detail-fr.json', 'wiki/search-detail-en.json'}: E(f'nouveaux fichiers inattendus {sorted(fb - fa)}')
ch = sorted(k for k in fa & fb if H(A / k) != H(B / k))
other = [k for k in ch if not k.endswith('.html') and k not in ('community/app.py', 'tests/test_community.py', 'tests/wiki-baseline.json', 'wiki/ui-core.mjs', 'wiki/v2.css', 'wiki/wk-header.js')]
if other: E(f'fichiers modifiés hors périmètre {other}')
INFO['html_with_anchors_added'] = sum(k.endswith('.html') for k in ch)
for k in ch:
    if not k.endswith('.html'): continue
    a = (A / k).read_text('utf-8'); b = (B / k).read_text('utf-8')
    b2 = re.sub(r'<(tr|li|p) id="r-[a-z0-9-]+">', r'<\1>', b); b2 = re.sub(r'<details class="v42-vendor" id="r-[a-z0-9-]+">', '<details class="v42-vendor">', b2)
    if a != b2: E(f'{k} : autre changement que des ancres')
    ids = re.findall(r'\sid="([^"]+)"', b)
    if len(ids) != len(set(ids)): E(f'{k} : id en double')
ao, an = (A / 'community/app.py').read_text(), (B / 'community/app.py').read_text()
if an.replace("'search-index.json','search-detail-fr.json','search-detail-en.json',", "'search-index.json',") != ao: E('app.py : autre changement que la liste blanche')
co, cn = (A / 'wiki/v2.css').read_text(), (B / 'wiki/v2.css').read_text()
if not cn.startswith(co) or '.wk-dfilter' not in cn[len(co):] or re.search(r'@import|url\(|https?:', cn[len(co):]): E('v2.css : ajout inattendu')
js = (B / 'wiki/wk-header.js').read_text()
if js.count('fetch(') != 1 or re.search(r'innerHTML|outerHTML|insertAdjacentHTML|eval\(|new Function|https?://|document\.cookie|localStorage', js): E('wk-header.js : règle de sécurité')
if "new URL('search-index.json', import.meta.url)" not in js or 'search-detail-${lang}.json' not in js: E('wk-header.js : index attendus absents')
ui = (B / 'wiki/ui-core.mjs').read_text(); uo = (A / 'wiki/ui-core.mjs').read_text()
if not ui.startswith(uo.rstrip('\n')): E('ui-core.mjs : fonctions existantes modifiées')
# index détaillés : chaque ancre existe sur sa page ; tailles
sys.path.insert(0, str(R / 'v42b-test/outils'))
def slug(s):
    import unicodedata
    s = unicodedata.normalize('NFD', s); s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'x'
names_all = []
THIRD = re.compile(r'eternadex|wowhead|wiki\.gg|\bwago\b|curseforge', re.I)
for lang in ('fr', 'en'):
    p = B / f'wiki/search-detail-{lang}.json'; raw = p.read_bytes(); d = json.loads(raw)
    INFO[f'detail_{lang}'] = dict(records=len(d['r']), bytes=len(raw), gzip=len(gzip.compress(raw, 9)))
    ids_cache = {}; missing = 0
    for r in d['r']:
        page = d['pages'][r[2]][0]; anchor = r[3] or 'r-' + slug(r[0]); names_all.append(r[0])
        if page not in ids_cache: ids_cache[page] = set(re.findall(r'\sid="([^"]+)"', (B / 'wiki' / page / 'index.html').read_text('utf-8')))
        if anchor not in ids_cache[page]: missing += 1
        if THIRD.search(r[0]) or (len(r) > 4 and isinstance(r[4], str) and THIRD.search(r[4])): E(f'nom de site tiers dans l’index : {r[:3]}')
    if any(THIRD.search(x) for x in d['d']) or any(THIRD.search(x[1]) for x in d['pages']): E('nom de site tiers dans l’index (tables)')
    INFO[f'missing_anchor_{lang}'] = missing
    if missing: E(f'{missing} ancres introuvables ({lang})')
# même calcul d'ancre en JavaScript (ui-core.detailAnchor) qu'en Python
Path('/tmp/v42b-names.json').write_text(json.dumps(names_all, ensure_ascii=False))
js_out = subprocess.run(['node', '-e', "import('" + str(B / 'wiki/ui-core.mjs') + "').then(m=>{const n=JSON.parse(require('fs').readFileSync('/tmp/v42b-names.json','utf8'));console.log(JSON.stringify(n.map(x=>m.detailAnchor(x))))})"], capture_output=True, text=True, check=True).stdout
js_anchors = json.loads(js_out); diff = sum(1 for n, a in zip(names_all, js_anchors) if a != 'r-' + slug(n))
INFO['anchor_js_python_mismatch'] = diff
if diff: E(f'{diff} ancres calculées différemment en JS')
if any('sitemap' in str(p) for p in (B / 'wiki').rglob('*')): E('sitemap présent')
# validateur v42 : seules les différences attendues (ancres dans les blocs, liste blanche app.py)
out = subprocess.run(['python3', str(R / 'v42b-test/outils/validate_v42b_base.py')], capture_output=True, text=True).stdout
errs = [l[3:] for l in out.splitlines() if l.startswith(' - ')]
unexpected = [e for e in errs if not (e.startswith('blocs modifiés hors périmètre') or e == 'forum modifié : community/app.py')]
INFO['v42_validator_errors_expected'] = len(errs) - len(unexpected)
for e in unexpected: E('validateur v42 : ' + e)
print(json.dumps(INFO, ensure_ascii=False, indent=1)); print('ERREURS', len(ERR)); [print(' -', e) for e in ERR]
sys.exit(1 if ERR else 0)

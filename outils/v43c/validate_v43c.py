#!/usr/bin/env python3
"""v43c : compare v43c-test/tree avec la v43b en ligne (v43b-test/tree). Changements permis : pages HTML du wiki, search-index.json,
search-detail-fr/en.json, 2 fichiers de test ; ajouts permis : les 2 pages de l'article Blackmaw. Application, CSS, JS, images : inchangés."""
import filecmp, json, re, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v43b-test/tree'; B = R / 'v43c-test/tree'
walk = lambda p: {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
fa, fb = walk(A), walk(B); bad = []
NEW = {'wiki/fr/actualites/sanctions-abus-blackmaw-hold/index.html', 'wiki/en/news/blackmaw-hold-abuse-actions/index.html'}
if fa - fb: bad.append(('fichiers retirés', sorted(fa - fb)))
if fb - fa != NEW: bad.append(('fichiers ajoutés', sorted(fb - fa)))
ch = sorted(f for f in fa & fb if not filecmp.cmp(A / f, B / f, shallow=False))
html = [f for f in ch if re.fullmatch(r'wiki/[a-z0-9/_-]+/index\.html|wiki/index\.html', f)]
other = sorted(set(ch) - set(html))
if other != ['tests/test_community.py', 'tests/wiki-baseline.json', 'wiki/search-detail-en.json', 'wiki/search-detail-fr.json', 'wiki/search-index.json']:
    bad.append(('autres changements', other))
TITLES = [('Correctifs Forever du 5 au 20 novembre', 'Correctifs Forever du 5 au 16 novembre'), ('Forever hotfixes, November 5–20', 'Forever hotfixes, November 5–16')]
inline = lambda s: (len(re.findall(r'<style', s)), len(re.findall(r'<script(?![^>]*\bsrc=)', s)), len(re.findall(r'\son[a-z]+=', s)))
hosts = lambda s: set(re.findall(r'(?:href|src)="https?://([^/"]+)', s))
kinds = {'titre_seul': [], 'contenu': []}
for f in html:
    o, n = (A / f).read_text('utf-8'), (B / f).read_text('utf-8')
    if inline(o) != inline(n): bad.append((f, 'style/script en ligne'))
    if hosts(n) - hosts(o) - {'news.blizzard.com', 'us.forums.blizzard.com', 'eu.forums.blizzard.com'}: bad.append((f, 'hôte externe', hosts(n) - hosts(o)))
    if ('noindex' in o) != ('noindex' in n): bad.append((f, 'noindex'))
    n2 = n
    for a, b in TITLES: n2 = n2.replace(a, b)
    n2 = re.sub(r'(<span class="wk-label">(?:Actualités|News)</span><span class="wk-count">)16<', r'\g<1>15<', n2)  # menu : +1 actualité
    kinds['titre_seul' if n2 == o else 'contenu'].append(f)
kinds['contenu'] = [f for f in kinds['contenu']]
print('\n'.join(kinds['contenu']), file=sys.stderr)
for f in NEW:
    s = (B / f).read_text('utf-8')
    if '<meta name="robots" content="noindex,nofollow">' not in s: bad.append((f, 'noindex absent'))
    if inline(s) != (0, 0, 0): bad.append((f, 'style/script en ligne'))
    if 'v2.css?v=42c' not in s or 'wk-header.js?v=42c' not in s: bad.append((f, '?v=42c absent'))
    if '[src:' in s: bad.append((f, 'marqueur [src: brut'))
for L in ('fr', 'en'):
    d = json.loads((B / f'wiki/search-detail-{L}.json').read_text('utf-8'))
    if len(d['pages']) != 221 or len(d['r']) <= 15000: bad.append((L, 'search-detail', len(d['pages']), len(d['r'])))
si = json.loads((B / 'wiki/search-index.json').read_text('utf-8')); si0 = json.loads((A / 'wiki/search-index.json').read_text('utf-8'))
cnt = lambda x: len(x) if isinstance(x, list) else {k: len(v) for k, v in x.items() if isinstance(v, list)}
stale = [f for f in fb if f.endswith('.html') and ('du 5 au 16 novembre' in (B / f).read_text('utf-8') or 'November 5–16' in (B / f).read_text('utf-8'))]
if stale: bad.append(('ancien titre restant', stale[:5]))
print(json.dumps({'added': sorted(fb - fa), 'html_changed': len(html), 'title_only': len(kinds['titre_seul']), 'content_changed': len(kinds['contenu']),
                  'other': other, 'search_index': [cnt(si0), cnt(si)], 'problems': bad[:20]}, ensure_ascii=False, indent=1))
sys.exit(1 if bad else 0)

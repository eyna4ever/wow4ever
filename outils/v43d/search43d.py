#!/usr/bin/env python3
"""v43d : étend search-detail-fr/en.json à partir de la v43c (221 pages).
On lance search42b.py sur une copie jetable, puis on ne reprend que les enregistrements
de l'article Correctifs (nouvelles sections details-nov23 et problemes-en-cours, titre mis à jour).
Les autres enregistrements v43c, y compris Blackmaw, sont conservés. Les pages HTML ne sont pas réécrites."""
import json, re, shutil, subprocess, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); W = R / 'v43d-test/tree/wiki'; OLD = R / 'v43c-test/tree/wiki'; S = Path('/tmp/v43d-sd')
SRC42 = R / 'v42b-test/outils/search42b.py'
src = SRC42.read_text(); slug_src = src[src.index('def slug(s):'):src.index('CARD_TYPE')]
ns = {}; exec('import unicodedata, re\n' + slug_src, ns); slug = ns['slug']
HOTP = {'fr': 'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en': 'en/news/forever-hotfixes-november-5-6/'}
if S.exists(): shutil.rmtree(S)
shutil.copytree(W, S)
subprocess.run([sys.executable, str(SRC42), str(S)], check=True, capture_output=True)
for L in ('fr', 'en'):
    a, b = (W / HOTP[L] / 'index.html').read_text('utf-8'), (S / HOTP[L] / 'index.html').read_text('utf-8')
    assert a == b, L  # page figée : search42b n'ajoute pas d'ancres
def decomp(d):
    out = []
    for r in d['r']:
        name, ti, pi, a = r[:4]; rest = list(r[4:])
        if rest and isinstance(rest[0], int): rest[0] = d['d'][rest[0]]
        out.append([name, ti, d['pages'][pi][0], a or 'r-' + slug(name)] + rest)
    return out
def comp(d0, pages, recs):
    pi = {p[0]: i for i, p in enumerate(pages)}
    dcount = {}
    for r in recs:
        if len(r) > 4: dcount[r[4]] = dcount.get(r[4], 0) + 1
    dl = sorted([x for x, n in dcount.items() if n > 1], key=lambda x: -dcount[x]); di = {x: i for i, x in enumerate(dl)}
    rr = []
    for r in recs:
        x = [r[0], r[1], pi[r[2]], '' if r[3] == 'r-' + slug(r[0]) else r[3]]
        if len(r) > 4: x.append(di[r[4]] if r[4] in di else r[4])
        if len(r) > 5: x.append(r[5])
        rr.append(x)
    out = {'v': d0['v'], 'lang': d0['lang'], 'types': d0['types'], 'pages': pages, 'd': dl, 'r': rr}
    if 'syn' in d0: out['syn'] = d0['syn']
    return out
summary = {}
for L in ('fr', 'en'):
    raw = (OLD / f'search-detail-{L}.json').read_text('utf-8'); old = json.loads(raw)
    ro = decomp(old)
    assert json.dumps(comp(old, old['pages'], ro), ensure_ascii=False, separators=(',', ':')) == raw, 'aller-retour v43c inexact'
    sc = json.loads((S / f'search-detail-{L}.json').read_text('utf-8')); rs = decomp(sc)
    bypage = {}
    for r in ro: bypage.setdefault(r[2], []).append(r)
    recs_hot = [r for r in rs if r[2] == HOTP[L]]
    assert any(r[3] == 'details-nov23' for r in recs_hot), L
    # notes-box n'est pas indexé par search42b : on ajoute la section à la main, juste après le lot du 23 novembre
    if not any(r[3] == 'problemes-en-cours' for r in recs_hot):
        i = next(i for i, r in enumerate(recs_hot) if r[3] == 'details-nov23')
        recs_hot.insert(i + 1, ['Problèmes en cours' if L == 'fr' else 'Known issues in progress', 17, HOTP[L], 'problemes-en-cours'])
    bypage[HOTP[L]] = recs_hot
    titles = {p[0]: p[1] for p in old['pages']}; titles[HOTP[L]] = next(p[1] for p in sc['pages'] if p[0] == HOTP[L])
    pages = [[p, titles[p]] for p, _ in old['pages']]
    recs = [r for p, _ in pages for r in bypage.get(p, [])]
    out = comp(old, pages, recs)
    (W / f'search-detail-{L}.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    summary[L] = {'pages': len(pages), 'records': len(recs), 'old_records': len(ro), 'hotfix_records': len(bypage[HOTP[L]]), 'hot_title': titles[HOTP[L]]}
print(json.dumps(summary, ensure_ascii=False, indent=1))

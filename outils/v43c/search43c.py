#!/usr/bin/env python3
"""v43c : index détaillé (search-detail-fr/en.json). search42b.py n'est pas idempotent (il n'indexe que les lignes sans ancre),
donc on ne régénère PAS tout : on le lance sur une copie jetable de l'arbre v43c, puis on reprend uniquement
  - les 2 nouvelles pages Blackmaw (ancres de passages ajoutées comme sur les autres actualités + leurs enregistrements),
  - les sections de l'article correctifs (page figée : seules les sections existantes sont indexées) et son nouveau titre ;
tous les autres enregistrements v43b sont conservés tels quels. Usage : search43c.py (arbre v43c-test/tree)."""
import json, re, shutil, subprocess, sys, importlib.util
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); W = R / 'v43c-test/tree/wiki'; OLD = R / 'v43b-test/tree/wiki'; S = Path('/tmp/v43c-sd')
SRC42 = R / 'v42b-test/outils/search42b.py'
src = SRC42.read_text(); slug_src = src[src.index('def slug(s):'):src.index('CARD_TYPE')]
ns = {}; exec('import unicodedata, re\n' + slug_src, ns); slug = ns['slug']
NEWP = {'fr': 'fr/actualites/sanctions-abus-blackmaw-hold/', 'en': 'en/news/blackmaw-hold-abuse-actions/'}
HOTP = {'fr': 'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en': 'en/news/forever-hotfixes-november-5-6/'}
if S.exists(): shutil.rmtree(S)
shutil.copytree(W, S)
subprocess.run([sys.executable, str(SRC42), str(S)], check=True, capture_output=True)
for L in ('fr', 'en'):
    p = NEWP[L] + 'index.html'; a, b = (W / p).read_text('utf-8'), (S / p).read_text('utf-8')
    assert re.sub(r' id="r-[^"]*"', '', b) == a and b != a, p
    (W / p).write_text(b, 'utf-8')
    assert (S / HOTP[L] / 'index.html').read_text('utf-8') == (W / HOTP[L] / 'index.html').read_text('utf-8')  # page figée : inchangée
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
    assert list(old.keys())[:6] == ['v', 'lang', 'types', 'pages', 'd', 'r']
    ro = decomp(old)
    assert json.dumps(comp(old, old['pages'], ro), ensure_ascii=False, separators=(',', ':')) == raw, 'aller-retour v43b inexact'
    sc = json.loads((S / f'search-detail-{L}.json').read_text('utf-8')); rs = decomp(sc)
    bypage = {}
    for r in ro: bypage.setdefault(r[2], []).append(r)
    order = [p[0] for p in old['pages']]
    for p in (HOTP[L], NEWP[L]): bypage[p] = [r for r in rs if r[2] == p]; assert bypage[p], p
    titles = {p[0]: p[1] for p in old['pages']}; titles.update({p[0]: p[1] for p in sc['pages'] if p[0] in (HOTP[L], NEWP[L])})
    pages_new = sorted(set(order) | {NEWP[L]}, key=lambda x: [p[0] for p in sc['pages']].index(x))
    assert [p[0] for p in sc['pages']] == pages_new, 'ordre des pages'
    pages = [[p, titles[p]] for p in pages_new]
    recs = [r for p in pages_new for r in bypage.get(p, [])]
    assert [r for r in recs if r[2] not in (HOTP[L], NEWP[L])] == [r for r in ro if r[2] != HOTP[L]]
    out = comp(old, pages, recs)
    (W / f'search-detail-{L}.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    summary[L] = {'pages': len(pages), 'records': len(recs), 'old_records': len(ro), 'new_page_records': len(bypage[NEWP[L]]), 'hotfix_records': len(bypage[HOTP[L]]),
                  'hot_title': titles[HOTP[L]]}
print(json.dumps(summary, ensure_ascii=False, indent=1))

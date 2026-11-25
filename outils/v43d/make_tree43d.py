#!/usr/bin/env python3
"""v43d (Oui de Mathieu t423u, 25/11/2026, Europe/Paris) : construit v43d-test/tree = v43c-test/tree
(contenu v43c jamais déployé : lots des 17, 19 et 20 novembre, article Blackmaw, podcast épisode 8)
+ lot officiel du 23 novembre et encadré « problèmes en cours » (lockboxes, monte épique)
+ description de l'article Correctifs couvrant toute la série, lien de l'article Blackmaw vers la fiche du donjon.
Base en ligne : v43b (releases/20261118T005337). Build de TEST : aucun envoi, aucun déploiement."""
import json, re, shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import data43d as D
R = Path('/workspace/wowkipedia-v21-elite'); C = R / 'v43c-test/tree'; T = R / 'v43d-test/tree'; W = T / 'wiki'
V43C = 'b2f35655cad35ec602dfa214b9a67a2219ae4f29ec77ec9921494e9c0bf50bc8'
assert json.loads((C / 'tests/wiki-baseline.json').read_text())['tarball_sha256'] == V43C
def once(t, old, new, what):
    c = t.count(old); assert c == 1, (what, c, old[:80]); return t.replace(old, new)
D25 = {'fr': '<time datetime="2026-11-25">25 novembre 2026</time>', 'en': '<time datetime="2026-11-25">25 November 2026</time>'}
D24 = {'fr': '<time datetime="2026-11-24">24 novembre 2026</time>', 'en': '<time datetime="2026-11-24">24 November 2026</time>'}
HOT = {'fr': 'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en': 'en/news/forever-hotfixes-november-5-6/'}
BM = {'fr': 'fr/actualites/sanctions-abus-blackmaw-hold/', 'en': 'en/news/blackmaw-hold-abuse-actions/'}
DUN = {'fr': 'fr/donjons-raids/repaire-des-noiregueules/', 'en': 'en/dungeons-raids/blackmaw-hold/'}
T20 = {'fr': 'Correctifs Forever du 5 au 20 novembre : XP en donjon, classes, objets et quêtes', 'en': 'Forever hotfixes, November 5–20: dungeon XP, classes, items and quests'}
T23 = {'fr': 'Correctifs Forever du 5 au 23 novembre : XP en donjon, classes, objets et quêtes', 'en': 'Forever hotfixes, November 5–23: dungeon XP, classes, items and quests'}
if T.exists(): shutil.rmtree(T)
shutil.copytree(C, T, symlinks=True, ignore=shutil.ignore_patterns('__pycache__'))

def cite(*n): return ''.join(f'<sup class="cite"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>' for i in n)
def words(t):
    a = t[t.find('<article'):t.find('</article>')]
    return len(re.sub(r'<[^>]+>', ' ', a).split())
def fdate(iso, L):
    y, m, d = iso.split('-'); M = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'] if L == 'fr' else \
        ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return f'<time datetime="{iso}">{int(d)} {M[int(m) - 1]} {y}</time>'

def hotfix(path, L):
    t = path.read_text('utf-8')
    assert 'id="details-nov23"' not in t and 'id="details-nov20"' in t, 'déjà appliqué ?'
    w0 = words(t)
    title, para, items = D.SEC['nov23'][L]; c = D.CITES['nov23']
    lis = []
    for i, item in enumerate(items):
        cites = D.CONSEQ_CITE if i == len(items) - 1 else (c[0],)
        lis.append(f'<li>{item}{cite(*cites)}</li>')
    sec = (f'<section class="article-section" id="details-nov23" aria-labelledby="details-nov23-title"><h2 id="details-nov23-title">{title}</h2>'
           f'<p>{para}{cite(*c)}</p><ul>' + ''.join(lis) + '</ul></section>')
    bt, bitems = D.BOX[L]
    box = (f'<section class="article-section notes-box" id="problemes-en-cours" aria-labelledby="problemes-en-cours-title"><h2 id="problemes-en-cours-title">{bt}</h2><ul>'
           + ''.join(f'<li>{x}{cite(*ci)}</li>' for x, ci in zip(bitems, D.BOX_CITE)) + '</ul></section>')
    t = once(t, '<section class="article-section" id="details-nov20"', sec + box + '<section class="article-section" id="details-nov20"', 'section')
    toc = f'<li><a href="#details-nov23"><span>{title}</span></a></li><li><a href="#problemes-en-cours"><span>{bt}</span></a></li>'
    t = once(t, '<li><a href="#details-nov20"><span>', toc + '<li><a href="#details-nov20"><span>', 'toc')
    assert len(re.findall(r'<li><a href="#details-nov20">(?!<span>)', t)) == 1
    tabs = f'<li><a href="#details-nov23">{title}</a></li><li><a href="#problemes-en-cours">{bt}</a></li>'
    t = re.sub(r'<li><a href="#details-nov20">(?!<span>)', tabs + '<li><a href="#details-nov20">', t, count=1)
    keys = f'<li>{D.KEY["nov23"][L]}{cite(c[0])}</li><li>{D.KEY["issues"][L]}{cite(27, 29)}</li>'
    t = once(t, '<ul class="key-points"><li>', '<ul class="key-points">' + keys + '<li>', 'keypoint')
    for o, n in D.INTRO[L]: t = once(t, o, n, 'intro')
    i = t.find('id="introduction-title"'); j = t.find('</p></section>', i); assert 0 < i < j
    t = t[:j] + cite(24) + t[j:]
    k = t.find('<p class="v16-analysis-note">'); assert k > 0 and t[k - 4:k] == '</p>'
    t = t[:k - 4] + D.ANAL[L] + t[k - 4:]
    tl = ''.join(f'<li><time datetime="{iso}">{lab}</time><span>{txt}{cite(*D.CITES[b])}</span></li>' for iso, lab, txt, b in D.TL[L])
    t = once(t, '</ol><div class="status-columns">', tl + '</ol><div class="status-columns">', 'timeline')
    pub, acc = ('publié le', 'consulté le') if L == 'fr' else ('published', 'accessed')
    assert 'id="source-24"' not in t and 'id="source-23"' in t
    lis = ''.join(f'<li id="source-{24 + i}"><span class="source-number">[{24 + i}]</span> <span class="source-lines"><a href="{u}" rel="noopener noreferrer" hreflang="en">{tt[L]}</a> <span class="source-lang">(EN)</span> · {pub} {fdate(p_, L)} · {acc} {fdate(a_, L)}</span></li>'
                  for i, (u, tt, p_, a_) in enumerate(D.SRC))
    t = once(t, '</li></ol><p class="rights-note">', '</li>' + lis + '</ol><p class="rights-note">', 'sources')
    if L == 'fr':
        t = once(t, '<dt>Mis à jour</dt><dd>' + D24[L], '<dt>Mis à jour</dt><dd>' + D25[L], 'maj')
        t = once(t, '<dt>Date de l’événement</dt><dd><time datetime="2026-11-20">20 novembre 2026</time>', '<dt>Date de l’événement</dt><dd><time datetime="2026-11-23">23 novembre 2026</time>', 'event')
        t = once(t, '23 sources officielles', '30 sources officielles', 'nsrc'); t = once(t, ' · révision 22</p>', ' · révision 23</p>', 'rev')
    else:
        t = once(t, '<dt>Updated</dt><dd>' + D24[L], '<dt>Updated</dt><dd>' + D25[L], 'maj')
        t = once(t, '<dt>Event date</dt><dd><time datetime="2026-11-20">20 November 2026</time>', '<dt>Event date</dt><dd><time datetime="2026-11-23">23 November 2026</time>', 'event')
        t = once(t, '23 official sources', '30 official sources', 'nsrc'); t = once(t, ' · revision 22</p>', ' · revision 23</p>', 'rev')
    assert t.count('état documentaire 2026-11-24') == 2; t = t.replace('état documentaire 2026-11-24', 'état documentaire 2026-11-25')
    n = t.count(D.META_OLD[L]); assert n == 2, n  # meta + encadré « En résumé »
    t = t.replace(D.META_OLD[L], D.META[L])
    lab = '<dt>Lecture</dt><dd>' if L == 'fr' else '<dt>Reading time</dt><dd>'
    m = re.search(re.escape(lab) + r'(\d+) min</dd>', t); assert m
    newmin = round(int(m.group(1)) * words(t) / w0); t = t.replace(m.group(0), f'{lab}{newmin} min</dd>')
    path.write_text(t, 'utf-8'); return int(m.group(1)), newmin

mins = {}
for L in ('fr', 'en'): mins[L] = hotfix(W / HOT[L] / 'index.html', L)

changed_hot = set()
for f in sorted(W.rglob('*.html')):
    t = f.read_text('utf-8'); n = t
    for L in ('fr', 'en'): n = n.replace(T20[L], T23[L])
    for L in ('fr', 'en'):
        def fix(m, L=L):
            s = m.group(0).replace(D24[L], D25[L]).replace(D.META_OLD[L], D.META[L])
            return re.sub(r'Article · \d+ min · ', f'Article · {mins[L][1]} min · ', s)
        n = re.sub(r'<a [^>]*href="[^"]*' + re.escape(HOT[L]) + r'"[^>]*>.*?</a>', fix, n, flags=re.S)
    if n != t: f.write_text(n, 'utf-8'); changed_hot.add(str(f.relative_to(W)))
# descriptions hors cartes (déjà traitées sur les deux pages de l'article)
stale_desc = []
for f in sorted(W.rglob('*.html')):
    t = f.read_text('utf-8')
    if D.META_OLD['fr'] in t or D.META_OLD['en'] in t:
        stale_desc.append(str(f.relative_to(W)))
assert not stale_desc, stale_desc

# Blackmaw : lien vers la fiche donjon (premier mention + pages liées)
ICON = '<svg class="v2-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 4h11a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V8"/><path d="M9 8h7M9 12h7M9 16h4"/></svg>'
for L, old, new, label in (
    ('fr', 'dans le donjon Repaire des Noiregueules (Blackmaw Hold)',
     'dans le donjon <a href="../../../fr/donjons-raids/repaire-des-noiregueules/">Repaire des Noiregueules</a> (Blackmaw Hold)',
     'Repaire des Noiregueules'),
    ('en', 'in the Blackmaw Hold dungeon',
     'in the <a href="../../../en/dungeons-raids/blackmaw-hold/">Blackmaw Hold</a> dungeon',
     'Blackmaw Hold'),
):
    p = W / BM[L] / 'index.html'; t = p.read_text('utf-8')
    i = t.find('id="introduction"'); j = t.find('</section>', i); assert 0 < i < j and t[i:j].count(old) == 1
    t = t[:i] + t[i:j].replace(old, new, 1) + t[j:]
    rel = f'<li><a href="../../../{DUN[L]}">{ICON}<span>{label}</span></a></li>'
    t = once(t, '<ul class="v39-linklist"><li>', '<ul class="v39-linklist">' + rel + '<li>', 'bm-related')
    p.write_text(t, 'utf-8')

si = json.loads((W / 'search-index.json').read_text('utf-8'))
e = next(x for x in si['entries'] if x['id'] == 'forever-news-hotfixes-nov5-6')
for L in ('fr', 'en'):
    e['title'][L] = T23[L]
    e['description'][L] = D.META[L]
    st = e['searchText'][L]
    st2 = st.replace('du 5 au 20 novembre' if L == 'fr' else 'november 5–20', 'du 5 au 23 novembre' if L == 'fr' else 'november 5–23', 1)
    assert st2 != st, L
    e['searchText'][L] = st2 + D.SEARCH[L]
lic = e['sources'][-1]['license']
for u, _, _, acc in D.SRC: e['sources'].append({'url': u, 'license': lic, 'accessedAt': acc})
assert D.META_OLD['fr'] not in json.dumps(si, ensure_ascii=False) or True
js = json.dumps(si, ensure_ascii=False, separators=(',', ':'))
assert D.META_OLD['fr'] not in js and D.META_OLD['en'] not in js
(W / 'search-index.json').write_text(js, 'utf-8')

report = {'hotfix_minutes': mins, 'title_pages': len(changed_hot)}
json.dump(report, open(R / 'v43d-test/tree-report.json', 'w'), indent=1)
print(json.dumps(report))

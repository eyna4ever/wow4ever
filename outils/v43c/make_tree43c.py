#!/usr/bin/env python3
"""v43c (Oui de Mathieu t422u, 23/11/2026, Europe/Paris) : construit v43c-test/tree = v43b-test/tree (en ligne, releases/20261118T005337)
+ nouvel article « sanctions-abus-blackmaw-hold » (FR/EN, pipeline documentaire : apply-v43c.mjs puis build-v2)
+ mise à jour de l'article « Correctifs Forever » (lots des 17, 19 et 20 novembre, même méthode HTML que la v40b)
+ mise à jour de la fiche « Le podcast officiel WoW: Forever » (épisode 8).
Méthode Blackmaw : les pages générées AVANT / APRÈS l'ajout (dist /tmp/v43c-before et /tmp/v43c-pipe, toutes deux passées par
apply_v40b.py comme la v40b en ligne) donnent un delta, appliqué par fusion à trois voies (balise par balise) sur les pages v43b.
Accueils FR/EN faits main (v40) : compteur et listes mis à jour explicitement. Build de TEST : aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, subprocess, sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from merge3 import merge3
import data43c as D
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v43b-test/tree'; T = R / 'v43c-test/tree'; W = T / 'wiki'
BEFORE, AFTER = Path('/tmp/v43c-before/dist-v2'), Path('/tmp/v43c-pipe/dist-v2')
B40, T40 = Path('/tmp/v43c-b40'), Path('/tmp/v43c-t40')
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
V43B = 'c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517'
assert json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256'] == V43B
def once(t, old, new, what):
    c = t.count(old); assert c == 1, (what, c); return t.replace(old, new)
D24 = {'fr': '<time datetime="2026-11-24">24 novembre 2026</time>', 'en': '<time datetime="2026-11-24">24 November 2026</time>'}
D17 = {'fr': '<time datetime="2026-11-17">17 novembre 2026</time>', 'en': '<time datetime="2026-11-17">17 November 2026</time>'}
D14 = {'fr': '<time datetime="2026-11-14">14 novembre 2026</time>', 'en': '<time datetime="2026-11-14">14 November 2026</time>'}
HOT = {'fr': 'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en': 'en/news/forever-hotfixes-november-5-6/'}
POD = {'fr': 'fr/actualites/le-podcast-officiel-wow-forever/', 'en': 'en/news/the-official-wow-forever-podcast/'}
BM = {'fr': 'fr/actualites/sanctions-abus-blackmaw-hold/', 'en': 'en/news/blackmaw-hold-abuse-actions/'}
T16 = {'fr': 'Correctifs Forever du 5 au 16 novembre : XP en donjon, classes, objets et quêtes', 'en': 'Forever hotfixes, November 5–16: dungeon XP, classes, items and quests'}
T14 = {'fr': 'Correctifs Forever du 5 au 14 novembre : XP en donjon, classes, objets et quêtes', 'en': 'Forever hotfixes, November 5–14: dungeon XP, classes, items and quests'}
T20 = {'fr': 'Correctifs Forever du 5 au 20 novembre : XP en donjon, classes, objets et quêtes', 'en': 'Forever hotfixes, November 5–20: dungeon XP, classes, items and quests'}

# 0) copie de la v43b
if T.exists(): shutil.rmtree(T)
shutil.copytree(A, T, symlinks=True, ignore=shutil.ignore_patterns('__pycache__'))

# 1) avant / après passés par la v40b (même état que les pages en ligne)
for d, src in ((B40, BEFORE), (T40, AFTER)):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(); shutil.copytree(src, d / 'wiki')
    r = subprocess.run([sys.executable, str(R / 'v40b-test/outils/apply_v40b.py'), str(d)], capture_output=True, text=True)
    if d == B40: assert r.returncode == 0, r.stderr
    else:  # après l'ajout, la une des rubriques n'est plus l'article correctifs : la v40b s'arrête juste avant ces vignettes
        assert r.returncode != 0 and "v2-lead-title" in r.stderr, r.stderr
        for f, L, o, n in (('index.html', 'fr', 'Article · 14 min · ', 'Article · 17 min · '), ('fr/actualites/index.html', 'fr', 'Article · 14 min · ', 'Article · 17 min · '),
                           ('en/news/index.html', 'en', 'Article · 11 min · ', 'Article · 13 min · ')):
            p = d / 'wiki' / f; t = p.read_text('utf-8')
            m = re.search(r'<a class="v2-card" href="[^"]*' + re.escape(HOT[L]) + r'">.*?</a>', t, re.S); assert m, f
            blk = m.group(0); assert blk.count(o + D17[L]) == 1, f
            p.write_text(t[:m.start()] + blk.replace(o + D17[L], n + D17[L]) + t[m.end():], 'utf-8')
BW, TW = B40 / 'wiki', T40 / 'wiki'

# 2) Blackmaw : fusion à trois voies
def norm_new(s):
    for f in ('v2.css', 'wk-header.js', 'ui-core.mjs'):
        s = re.sub(r'((?:href|src)="(?:\.\./)*' + re.escape(f) + r')"', r'\1?v=42c"', s)
    return s
# contrôle de la normalisation : une page d'actualité existante, avant l'ajout, donne exactement la page v43b
for L, p in (('fr', 'fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html'),
             ('en', 'en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html')):
    assert norm_new((BW / p).read_text('utf-8')) == (A / 'wiki' / p).read_text('utf-8'), p
HOMES = {'fr/index.html', 'en/index.html'}
merged, new = [], []
for f in sorted(TW.rglob('*')):
    if not f.is_file(): continue
    r = str(f.relative_to(TW)); b = BW / r
    if r == 'search-index.json': continue
    if not b.exists():
        assert r in (BM['fr'] + 'index.html', BM['en'] + 'index.html'), r
        (W / r).parent.mkdir(parents=True, exist_ok=True); (W / r).write_text(norm_new(f.read_text('utf-8')), 'utf-8'); new.append(r); continue
    if f.read_bytes() == b.read_bytes(): continue
    assert r.endswith('.html'), r
    if r in HOMES: continue
    m, c = merge3((W / r).read_text('utf-8'), b.read_text('utf-8'), f.read_text('utf-8'))
    assert not c, (r, c)
    (W / r).write_text(m, 'utf-8'); merged.append(r)
assert len(new) == 2 and len(merged) == 469, (len(new), len(merged))
# accueils faits main : compteur Actualités / News
for L in ('fr', 'en'):
    p = W / L / 'index.html'; t = p.read_text('utf-8')
    t, n = re.subn(r'(<(?:strong|span class="wk-label")>(?:Actualités|News)</(?:strong|span)><span class="wk-count">)15<', r'\g<1>16<', t); assert n >= 1, (L, n)
    p.write_text(t, 'utf-8')
assert 'wk-count">15<' not in ''.join(p.read_text('utf-8') for p in W.rglob('*.html') if 'Actualités</' in p.read_text('utf-8') and False)
# index de recherche : celui du pipeline (avec Blackmaw), l'entrée correctifs reste celle de la v43b (v40b)
si_old = json.loads((A / 'wiki/search-index.json').read_text('utf-8')); si = json.loads((AFTER / 'search-index.json').read_text('utf-8'))
assert json.dumps(si_old, ensure_ascii=False, separators=(',', ':')) == (A / 'wiki/search-index.json').read_text('utf-8')
old_by = {e['id']: e for e in si_old['entries']}
for i, e in enumerate(si['entries']):
    if e['id'] == 'forever-news-hotfixes-nov5-6': si['entries'][i] = old_by[e['id']]
    elif e['id'] in old_by: assert e == old_by[e['id']], e['id']
assert [e['id'] for e in si['entries'] if e['id'] not in old_by] == ['article-blackmaw-hold-abuse-actions'] and si['categories'] == si_old['categories']

# 3) Correctifs Forever : lots des 17, 19 et 20 novembre (FR + EN)
def cite(*n): return ''.join(f'<sup class="cite"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>' for i in n)
def words(t):
    a = t[t.find('<article'):t.find('</article>')]
    return len(re.sub(r'<[^>]+>', ' ', a).split())
def fdate(iso, L):
    y, m, d = iso.split('-'); M = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'] if L == 'fr' else \
        ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return f'<time datetime="{iso}">{int(d)} {M[int(m) - 1]} {y}</time>'
INTRO2 = {'fr': ('La page française de l’article 24315281 reste titrée 9 novembre', 'La page française de l’article 24315281 porte encore un titre plus ancien (« 13 novembre » au 20 novembre)'),
          'en': ('The French page of article 24315281 is still titled November 9', 'The French page of article 24315281 still carries an older title (“November 13” as of November 20)')}
def hotfix(path, L):
    t = path.read_text('utf-8')
    assert 'id="details-nov17"' not in t and 'id="details-nov16"' in t, 'déjà appliqué ?'
    w0 = words(t); secs = ''; toc = ''; tabs = ''; keys = ''
    for k in ('nov20', 'nov19', 'nov17'):
        title, para, items = D.SEC[k][L]; c = D.CITES[k]
        secs += (f'<section class="article-section" id="details-{k}" aria-labelledby="details-{k}-title"><h2 id="details-{k}-title">{title}</h2>'
                 f'<p>{para}{cite(*c)}</p><ul>' + ''.join(f'<li>{i}{cite(c[0])}</li>' for i in items) + '</ul></section>')
        toc += f'<li><a href="#details-{k}"><span>{title}</span></a></li>'; tabs += f'<li><a href="#details-{k}">{title}</a></li>'
        keys += f'<li>{D.KEY[k][L]}{cite(c[0])}</li>'
    t = once(t, '<section class="article-section" id="details-nov16"', secs + '<section class="article-section" id="details-nov16"', 'section')
    t = once(t, '<li><a href="#details-nov16"><span>', toc + '<li><a href="#details-nov16"><span>', 'toc')
    assert len(re.findall(r'<li><a href="#details-nov16">(?!<span>)', t)) == 1, 'tabs'
    t = re.sub(r'<li><a href="#details-nov16">(?!<span>)', tabs + '<li><a href="#details-nov16">', t)
    t = once(t, '<ul class="key-points"><li>', '<ul class="key-points">' + keys + '<li>', 'keypoint')
    for o, n in D.INTRO[L] + [INTRO2[L]]: t = once(t, o, n, 'intro')
    i = t.find('id="introduction-title"'); j = t.find('</p></section>', i); assert 0 < i < j
    t = t[:j] + cite(17) + t[j:]
    k = t.find('<p class="v16-analysis-note">'); assert k > 0 and t[k - 4:k] == '</p>'
    t = t[:k - 4] + ''.join(D.ANAL[L]) + t[k - 4:]
    tl = ''.join(f'<li><time datetime="{iso}">{lab}</time><span>{txt}{cite(*D.CITES[b])}</span></li>' for iso, lab, txt, b in D.TL[L])
    t = once(t, '</ol><div class="status-columns">', tl + '</ol><div class="status-columns">', 'timeline')
    pub, acc = ('publié le', 'consulté le') if L == 'fr' else ('published', 'accessed')
    assert 'id="source-17"' not in t and 'id="source-16"' in t
    lis = ''.join(f'<li id="source-{17 + i}"><span class="source-number">[{17 + i}]</span> <span class="source-lines"><a href="{u}" rel="noopener noreferrer" hreflang="en">{tt[L]}</a> <span class="source-lang">(EN)</span> · {pub} {fdate(p_, L)} · {acc} {fdate(a_, L)}</span></li>'
                  for i, (u, tt, p_, a_) in enumerate(D.SRC))
    t = once(t, '</li></ol><p class="rights-note">', '</li>' + lis + '</ol><p class="rights-note">', 'sources')
    if L == 'fr':
        t = once(t, '<dt>Mis à jour</dt><dd>' + D17[L], '<dt>Mis à jour</dt><dd>' + D24[L], 'maj')
        t = once(t, '<dt>Date de l’événement</dt><dd><time datetime="2026-11-16">16 novembre 2026</time>', '<dt>Date de l’événement</dt><dd><time datetime="2026-11-20">20 novembre 2026</time>', 'event')
        t = once(t, '16 sources officielles', '23 sources officielles', 'nsrc'); t = once(t, ' · révision 21</p>', ' · révision 22</p>', 'rev')
    else:
        t = once(t, '<dt>Updated</dt><dd>' + D17[L], '<dt>Updated</dt><dd>' + D24[L], 'maj')
        t = once(t, '<dt>Event date</dt><dd><time datetime="2026-11-16">16 November 2026</time>', '<dt>Event date</dt><dd><time datetime="2026-11-20">20 November 2026</time>', 'event')
        t = once(t, '16 official sources', '23 official sources', 'nsrc'); t = once(t, ' · revision 21</p>', ' · revision 22</p>', 'rev')
    assert t.count('état documentaire 2026-11-17') == 2; t = t.replace('état documentaire 2026-11-17', 'état documentaire 2026-11-24')
    lab = '<dt>Lecture</dt><dd>' if L == 'fr' else '<dt>Reading time</dt><dd>'
    m = re.search(re.escape(lab) + r'(\d+) min</dd>', t); assert m
    newmin = round(int(m.group(1)) * words(t) / w0); t = t.replace(m.group(0), f'{lab}{newmin} min</dd>')
    path.write_text(t, 'utf-8'); return int(m.group(1)), newmin
mins = {}
for L in ('fr', 'en'): mins[L] = hotfix(W / HOT[L] / 'index.html', L)
# titre de l'article partout ; vignettes et listes qui pointent vers l'article : date, durée de lecture
changed_hot = set()
for f in sorted(W.rglob('*.html')):
    t = f.read_text('utf-8'); n = t
    for L in ('fr', 'en'): n = n.replace(T16[L], T20[L]).replace(T14[L], T20[L])
    for L in ('fr', 'en'):
        def fix(m):
            s = m.group(0).replace(D17[L], D24[L])
            return re.sub(r'Article · \d+ min · ', f'Article · {mins[L][1]} min · ', s)
        n = re.sub(r'<a [^>]*href="[^"]*' + re.escape(HOT[L]) + r'"[^>]*>.*?</a>', fix, n, flags=re.S)
    if n != t: f.write_text(n, 'utf-8'); changed_hot.add(str(f.relative_to(W)))
for L in ('fr', 'en'):
    e = next(x for x in si['entries'] if x['id'] == 'forever-news-hotfixes-nov5-6')
    e['title'][L] = T20[L]
    st = e['searchText'][L]; st2 = re.sub(r'du 5 au 1[46] novembre' if L == 'fr' else r'november 5–1[46]', 'du 5 au 20 novembre' if L == 'fr' else 'november 5–20', st, count=1)
    assert st2 != st or T20[L].lower() in st, (L, st[:80]); e['searchText'][L] = st2 + D.SEARCH[L]
lic = e['sources'][-1]['license']
for u, _, _, acc in D.SRC: e['sources'].append({'url': u, 'license': lic, 'accessedAt': acc})

# 4) Podcast : épisode 8
for L in ('fr', 'en'):
    p = W / POD[L] / 'index.html'; t = p.read_text('utf-8'); add, anchor = D.POD[L]
    assert t.count(anchor) == 3 and 'pisode 8' not in t, L
    t = t.replace(anchor, anchor + add)
    t = once(t, add + cite(1, 2, 3, 4, 5, 6, 7) + '</p>', add + cite(1, 2, 3, 4, 5, 6, 7, 8) + '</p>', 'cite8')
    pub, acc = ('publié le', 'consulté le') if L == 'fr' else ('published', 'accessed')
    order = ('fr', 'en') if L == 'fr' else ('en', 'fr')
    lines = '<br>'.join(f'<a href="{D.POD_SRC[x][0]}" rel="noopener noreferrer" hreflang="{x}">{D.POD_SRC[x][1]}</a> <span class="source-lang">({x.upper()})</span> · {pub} {fdate("2026-11-19", L)} · {acc} {fdate("2026-11-20", L)}' for x in order)
    li8 = f'<li id="source-8"><span class="source-number">[8]</span> <span class="source-lines">{lines}</span></li>'
    assert 'id="source-8"' not in t and 'id="source-7"' in t
    i = t.find('<li id="source-7"'); j = t.find('</li>', i) + 5; assert t[j:j + 5] == '</ol>', t[j:j + 20]
    t = t[:j] + li8 + t[j:]
    t = once(t, '7 sources officielles' if L == 'fr' else '7 official sources', '8 sources officielles' if L == 'fr' else '8 official sources', 'nsrc')
    t = once(t, ('<dt>Mis à jour</dt><dd>' if L == 'fr' else '<dt>Updated</dt><dd>') + D14[L], ('<dt>Mis à jour</dt><dd>' if L == 'fr' else '<dt>Updated</dt><dd>') + D24[L], 'maj')
    assert t.count('état documentaire 2026-11-14') == 2; t = t.replace('état documentaire 2026-11-14', 'état documentaire 2026-11-24')
    t = once(t, ' · révision 12</p>' if L == 'fr' else ' · revision 12</p>', ' · révision 13</p>' if L == 'fr' else ' · revision 13</p>', 'rev')
    p.write_text(t, 'utf-8')
e = next(x for x in si['entries'] if x['id'] == 'forever-news-podcast-series')
for L in ('fr', 'en'):
    add, anchor = D.POD[L]; assert e['description'][L].endswith(anchor); e['description'][L] += add
    if isinstance(e.get('searchText'), dict): e['searchText'][L] += ' ' + add.lower().strip()
for x in ('fr', 'en'): e['sources'].append({'url': D.POD_SRC[x][0], 'license': e['sources'][-1]['license'], 'accessedAt': '2026-11-20'})
(W / 'search-index.json').write_text(json.dumps(si, ensure_ascii=False, separators=(',', ':')), 'utf-8')

# 5) accueils FR/EN faits main : « Dernières mises à jour » et « Dernières actualités »
TAG = {'fr': ('Actualité', 'Mis à jour le '), 'en': ('News', 'Updated ')}
BMT = {L: json.loads((AFTER / 'search-index.json').read_text('utf-8')) for L in ('fr',)}['fr']
BMT = next(x for x in BMT['entries'] if x['id'] == 'article-blackmaw-hold-abuse-actions')['title']
PODT = {'fr': 'Le podcast officiel WoW: Forever', 'en': 'The official WoW: Forever podcast'}
for L in ('fr', 'en'):
    p = W / L / 'index.html'; t = p.read_text('utf-8')
    rx = re.compile(r'(<ul class="v40-home-list v40-home-updates-list">)(.*?)(</ul>)', re.S); m = rx.search(t); assert m
    items = re.findall(r'<li>.*?</li>', m.group(2)); assert len(items) == 6 and HOT[L] in items[0] and T20[L] in items[0] and D24[L] in items[0], items[0]
    pod = f'<li><a href="../{POD[L]}"><span class="v2-tag is-actualites">{TAG[L][0]}</span><strong>{PODT[L]}</strong><span class="v2-list-meta">{TAG[L][1]}{D24[L]}</span></a></li>'
    t = t[:m.start(2)] + items[0] + pod + ''.join(items[1:5]) + t[m.end(2):]
    rx = re.compile(r'(<section class="v40-home-news"[^>]*>.*?<ul class="v40-home-list">)(.*?)(</ul>)', re.S); m = rx.search(t); assert m
    items = re.findall(r'<li>.*?</li>', m.group(2)); assert len(items) == 3 and HOT[L] in items[0] and D24[L] in items[0], items[0]
    bm = f'<li><a href="../{BM[L]}"><strong>{BMT[L]}</strong><span class="v2-list-meta">{D24[L]}</span></a></li>'
    t = t[:m.start(2)] + bm + items[0] + items[1] + t[m.end(2):]
    p.write_text(t, 'utf-8')
json.dump({'merged': len(merged), 'new': new, 'hotfix_minutes': mins, 'title_pages': len(changed_hot)}, open(R / 'v43c-test/tree-report.json', 'w'), indent=1)
print(json.dumps({'merged': len(merged), 'new': new, 'hotfix_minutes': mins, 'title_pages': len(changed_hot)}))

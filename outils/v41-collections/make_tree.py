#!/usr/bin/env python3
"""v41 (t403u) : construit v41-test/tree = v40-test/tree + wiki reconstruit (pipeline /tmp/v41-pipeline/dist-v2),
accueils v40 faits main restaurés puis patchés (compteur Objets, tuile Collections, accès rapide, dernières mises à jour),
v2.css v40 + feuille v41. Aucun déploiement."""
import json, os, re, shutil, sys
R = '/workspace/wowkipedia-v21-elite'
V40 = f'{R}/v40b-test/tree'; DST = f'{R}/v41-test/tree'; DIST = '/tmp/v41-pipeline/dist-v2'  # base : v40b (en ligne, releases/20261117T201412)
C = json.load(open(f'{R}/collections-v41/out/counts.json'))
TOTAL = C['mounts'] + C['pets'] + C['toys']
if os.path.exists(DST): shutil.rmtree(DST)
shutil.copytree(V40, DST, symlinks=True)
shutil.rmtree(f'{DST}/wiki'); shutil.copytree(DIST, f'{DST}/wiki')
os.remove(f'{DST}/wiki/PROPOSITION-V2-LOCALE.txt')
gen = {l: open(f'{DIST}/{l}/index.html', encoding='utf-8').read() for l in ('fr', 'en')}
ICON = '<svg class="v2-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3.5 14.6 9l5.9.6-4.4 4 1.3 5.9L12 16.6l-5.4 2.9 1.3-5.9-4.4-4 5.9-.6z"/></svg>'
T = {'fr': dict(items='Objets', tile='Collections', sub='montures, mascottes, jouets', hidden=' objets', coll='../fr/objets/collections/',
                quick_old='<li><a href="../fr/objets/montures/">Montures</a></li>', quick_new='<li><a href="../fr/objets/collections/">Montures, mascottes et jouets</a></li>'),
     'en': dict(items='Items', tile='Collections', sub='mounts, pets, toys', hidden=' items', coll='../en/items/collections/',
                quick_old='<li><a href="../en/items/mounts/">Mounts</a></li>', quick_new='<li><a href="../en/items/collections/">Mounts, pets and toys</a></li>')}
for l, t in T.items():
    p = f'{DST}/wiki/{l}/index.html'
    s = open(f'{V40}/wiki/{l}/index.html', encoding='utf-8').read()
    old = f'<strong>{t["items"]}</strong><span class="wk-count">8<'
    assert s.count(old) == 1, (l, 'objets'); s = s.replace(old, f'<strong>{t["items"]}</strong><span class="wk-count">9<')
    m = re.search(r'(<li><a href="\.\./' + l + r'/(?:objets|items)/">.*?</a></li>)', s); assert m, (l, 'tile')
    tile = (f'<li><a href="{t["coll"]}">{ICON}<strong>{t["tile"]}</strong><span class="wk-count">{TOTAL}<span class="visually-hidden">{t["hidden"]}</span></span></a></li>')
    s = s.replace(m.group(1), m.group(1) + tile, 1)
    assert s.count(t['quick_old']) == 1, (l, 'quick'); s = s.replace(t['quick_old'], t['quick_new'])
    # « Dernières mises à jour » : la liste générée par le pipeline (5 fiches v41 du 17 novembre)
    rx = re.compile(r'(<ul class="v40-home-list v40-home-updates-list">)(.*?)(</ul>)', re.S)
    items = re.findall(r'<li><a href="[^"]*"><span class="v2-tag[^"]*">[^<]*</span><strong>[^<]*</strong><span class="v2-list-meta">.*?</time></span></a></li>', gen[l])[:5]
    assert len(items) == 5 and all('2026-11-17' in i for i in items), (l, 'updates')
    assert rx.search(s); s = rx.sub(lambda mm: mm.group(1) + ''.join(items) + mm.group(3), s, count=1)
    open(p, 'w', encoding='utf-8').write(s)
css = open(f'{V40}/wiki/v2.css', encoding='utf-8').read() + open(f'{R}/collections-v41/css/v41-collections.css', encoding='utf-8').read()
open(f'{DST}/wiki/v2.css', 'w', encoding='utf-8').write(css)
# en-tête du forum : seul le compteur Objets change (8 -> 9)
hp = f'{DST}/community/templates/_v2_header.html'
h = open(hp, encoding='utf-8').read()
n_old = len(re.findall(r'(Objets|Items)</span><span class="wk-count">8<', h)) or len(re.findall(r'(Objets|Items)(</strong>|</span>)?<span class="wk-count">8<', h))
h2, k = re.subn(r'((?:Objets|Items)(?:</strong>|</span>)?<span class="wk-count">)8<', r'\g<1>9<', h)
print('forum header replacements', k)
open(hp, 'w', encoding='utf-8').write(h2)
# v40b : mêmes modifications rejouées sur l'arbre v41 (article Correctifs du 16 novembre, titres, index de recherche, vignettes).
import subprocess
subprocess.run(['python3', f'{R}/v40b-test/outils/apply_v40b.py', DST], check=True)
# Accueil « Dernières mises à jour » : l'article Correctifs (mis à jour le 17 novembre par la v40b) + les 5 fiches v41.
HOT = {'fr': ('../fr/actualites/correctifs-forever-5-et-6-novembre/', 'Actualité', 'Correctifs Forever du 5 au 16 novembre : XP en donjon, classes, objets et quêtes', 'Mis à jour le <time datetime="2026-11-17">17 novembre 2026</time>'),
       'en': ('../en/news/forever-hotfixes-november-5-6/', 'News', 'Forever hotfixes, November 5–16: dungeon XP, classes, items and quests', 'Updated <time datetime="2026-11-17">17 November 2026</time>')}
for l, (href, tag, title, meta) in HOT.items():
    p = f'{DST}/wiki/{l}/index.html'; s2 = open(p, encoding='utf-8').read()
    k = '<ul class="v40-home-list v40-home-updates-list">'; assert s2.count(k) == 1
    s2 = s2.replace(k, k + f'<li><a href="{href}"><span class="v2-tag is-actualites">{tag}</span><strong>{title}</strong><span class="v2-list-meta">{meta}</span></a></li>')
    open(p, 'w', encoding='utf-8').write(s2)
print('tree ok', TOTAL)

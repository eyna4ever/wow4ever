#!/usr/bin/env python3
"""v42 (t407u) : construit v42-test/tree — même chaîne que la v41 (Collections incluses), plus Métiers 18 -> 28, accès rapide Matériaux, feuille v42.
Origine v41 : construit v41-test/tree = v40-test/tree + wiki reconstruit (pipeline /tmp/v41-pipeline/dist-v2),
accueils v40 faits main restaurés puis patchés (compteur Objets, tuile Collections, accès rapide, dernières mises à jour),
v2.css v40 + feuille v41. Aucun déploiement."""
import json, os, re, shutil, sys
R = '/workspace/wowkipedia-v21-elite'
V40 = f'{R}/v40b-test/tree'; DST = f'{R}/v42-test/tree'; DIST = '/tmp/v42-pipeline/dist-v2'  # base : v40b (en ligne, releases/20261117T201412)
C = json.load(open(f'{R}/collections-v41/out/counts.json'))
TOTAL = C['mounts'] + C['pets'] + C['toys']
if os.path.exists(DST): shutil.rmtree(DST)
shutil.copytree(V40, DST, symlinks=True)
shutil.rmtree(f'{DST}/wiki'); shutil.copytree(DIST, f'{DST}/wiki')
os.remove(f'{DST}/wiki/PROPOSITION-V2-LOCALE.txt')
gen = {l: open(f'{DIST}/{l}/index.html', encoding='utf-8').read() for l in ('fr', 'en')}
ICON = '<svg class="v2-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 3.5 14.6 9l5.9.6-4.4 4 1.3 5.9L12 16.6l-5.4 2.9 1.3-5.9-4.4-4 5.9-.6z"/></svg>'
ENT42 = json.load(open('/tmp/v42-pipeline/runtime/entries.json'))
PROF_N = sum(1 for e in ENT42 if e['category'] == 'professions' and e['status'] == 'published')
assert PROF_N == 28, PROF_N
T = {'fr': dict(prof='Métiers', quick_rec='<li><a href="../fr/metiers/#fiches-recipes">Recettes</a></li>', quick_mat='<li><a href="../fr/metiers/materiaux/">Matériaux : où les trouver</a></li>', items='Objets', tile='Collections', sub='montures, mascottes, jouets', hidden=' objets', coll='../fr/objets/collections/',
                quick_old='<li><a href="../fr/objets/montures/">Montures</a></li>', quick_new='<li><a href="../fr/objets/collections/">Montures, mascottes et jouets</a></li>'),
     'en': dict(prof='Professions', quick_rec='<li><a href="../en/professions/#fiches-recipes">Recipes</a></li>', quick_mat='<li><a href="../en/professions/materials/">Materials: where to find them</a></li>', items='Items', tile='Collections', sub='mounts, pets, toys', hidden=' items', coll='../en/items/collections/',
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
    # v42 : compteur Métiers 18 -> 28 et accès rapide « Matériaux : où les trouver »
    mo = f'<strong>{t["prof"]}</strong><span class="wk-count">18<'; assert s.count(mo) == 1, (l, 'metiers'); s = s.replace(mo, f'<strong>{t["prof"]}</strong><span class="wk-count">{PROF_N}<')
    assert s.count(t['quick_rec']) == 1, (l, 'quick rec'); s = s.replace(t['quick_rec'], t['quick_rec'] + t['quick_mat'])
    # « Dernières mises à jour » : la liste générée par le pipeline (5 fiches v41 du 17 novembre)
    rx = re.compile(r'(<ul class="v40-home-list v40-home-updates-list">)(.*?)(</ul>)', re.S)
    items = re.findall(r'<li><a href="[^"]*"><span class="v2-tag[^"]*">[^<]*</span><strong>[^<]*</strong><span class="v2-list-meta">.*?</time></span></a></li>', gen[l])[:5]
    assert len(items) == 5 and all('2026-11-17' in i for i in items), (l, 'updates')
    assert all(('metiers/materiaux' in i or 'professions/materials' in i or 'zones/' in i or 'recettes-' in i or '-recipes' in i or 'objets/' in i or 'items/' in i) for i in items), items
    assert rx.search(s); s = rx.sub(lambda mm: mm.group(1) + ''.join(items) + mm.group(3), s, count=1)
    open(p, 'w', encoding='utf-8').write(s)
css = open(f'{V40}/wiki/v2.css', encoding='utf-8').read() + open(f'{R}/collections-v41/css/v41-collections.css', encoding='utf-8').read() + open(f'{R}/v42-test/css/v42-ou-trouver.css', encoding='utf-8').read()
open(f'{DST}/wiki/v2.css', 'w', encoding='utf-8').write(css)
# en-tête du forum : seul le compteur Objets change (8 -> 9)
hp = f'{DST}/community/templates/_v2_header.html'
h = open(hp, encoding='utf-8').read()
n_old = len(re.findall(r'(Objets|Items)</span><span class="wk-count">8<', h)) or len(re.findall(r'(Objets|Items)(</strong>|</span>)?<span class="wk-count">8<', h))
h2, k = re.subn(r'((?:Objets|Items)(?:</strong>|</span>)?<span class="wk-count">)8<', r'\g<1>9<', h)
print('forum header replacements', k)
h2, k2 = re.subn(r'((?:Métiers|Professions)(?:</strong>|</span>)?<span class="wk-count">)18<', r'\g<1>' + str(PROF_N) + '<', h2)
print('forum header Métiers replacements', k2); assert k2 >= 1
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
print('tree ok', TOTAL, 'metiers', PROF_N)

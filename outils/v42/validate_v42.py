#!/usr/bin/env python3
"""v42 (t407u) : contrôles du build de test v42-test/tree (base en ligne v40b ; v41 Collections incluse).
Liens internes + ancres #mat-, CSP/self-host (pas de script/style inline, pas de ressource externe), noindex, pas de sitemap,
blocs d'article modifiés uniquement dans le périmètre v41+v42, Discord = compteurs seulement, compteurs accueil/en-tête forum,
aucun nom de site tiers visible, étiquette « fichiers du jeu » retirée de la liste de PNJ des zones, noms étranges exclus/signalés,
589 matériaux présents une seule fois, icônes 64x64 WebP en lazy, v2.css = v40b + v41 + v42."""
import hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
R = Path('/workspace/wowkipedia-v21-elite'); NEW = R / 'v42-test/tree'; OLD = R / 'v40b-test/tree'; V41 = R / 'v41-test/tree'
w, ow, w41 = NEW / 'wiki', OLD / 'wiki', V41 / 'wiki'
sys.path.insert(0, str(OLD / 'tools')); from content_blocks import article_blocks
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
errs = []; info = {}
def E(m): errs.append(m)
html = sorted(str(p.relative_to(w)) for p in w.rglob('*.html'))
info['pages'] = len(html)
def visible(t):
    t = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', t); t = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', t); return re.sub(r'<[^>]+>', ' ', t)
broken = []; nlinks = 0; anchors_checked = 0; ids_cache = {}
def ids_of(p):
    if p not in ids_cache: ids_cache[p] = set(re.findall(r'\sid="([^"]+)"', p.read_text('utf-8')))
    return ids_cache[p]
for f in html:
    t = (w / f).read_text('utf-8')
    if 'name="robots" content="noindex' not in t: E(f'noindex manquant {f}')
    if re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="', t): E(f'script/style inline {f}')
    if re.search(r'(src|srcset)="https?:', t): E(f'ressource externe {f}')
    if re.search(r'Eternadex|Wowhead|wiki\.gg|\bwago\b|Materialbot', visible(t), re.I): E(f'nom de site tiers / nom exclu visible {f}')
    if 'http-equiv="refresh"' in t: continue
    if 'Site indépendant et non officiel de Blizzard Entertainment.' not in t: E(f'mention manquante {f}')
    base = (w / f).parent
    for attr, u in re.findall(r'\s(href|src)="([^"]+)"', t):
        if re.match(r'(?i)(https?:|mailto:|#|data:|javascript:)', u) or u.split('?')[0].split('#')[0] in ('/community/', '/account/', '/privacy/'): continue
        nlinks += 1
        path = unquote(urlsplit(u).path)
        tgt = ((w / path.lstrip('/')) if path.startswith('/') else (base / path)).resolve()
        if tgt.is_dir(): tgt = tgt / 'index.html'
        if not tgt.exists(): broken.append((f, u)); continue
        frag = urlsplit(u).fragment
        if frag.startswith('mat-') or frag.startswith('fiches-'):
            anchors_checked += 1
            if frag not in ids_of(tgt): broken.append((f, u))
    for u in re.findall(r'srcset="([^"]+)"', t):
        for part in u.split(','):
            p = part.strip().split(' ')[0]
            if not (base / p).resolve().exists(): broken.append((f, p))
info['internal_links_checked'] = nlinks; info['anchors_checked'] = anchors_checked; info['broken'] = broken[:10]
if broken: E(f'{len(broken)} liens internes cassés')
# périmètre : pages attendues d'après les fiches nouvelles / révisées
ENT = {e['id']: e for e in json.load(open('/tmp/v42-pipeline/runtime/entries.json'))}
CATS = {'zones': ('zones', 'zones'), 'professions': ('metiers', 'professions'), 'items': ('objets', 'items'), 'quests': ('quetes', 'quests'), 'creatures': ('creatures', 'creatures'), 'instances': ('donjons-raids', 'dungeons-raids'), 'classes': ('classes', 'classes')}
outd = R / 'v42-test/out/entries'
rev_ids = [json.loads(p.read_text())['id'] for p in sorted(outd.glob('rev-*.json'))]; new_ids = [json.loads(p.read_text())['id'] for p in sorted(outd.glob('new-*.json'))]
def page_of(i, l): e = ENT[i]; return f'{l}/{CATS[e["category"]][0 if l == "fr" else 1]}/{e["article"]["slug"][l]}/index.html'
SCOPE41 = {'fr/objets/montures/index.html', 'fr/objets/mascottes/index.html', 'fr/objets/jouets/index.html', 'fr/quetes/recompenses-heritage/index.html',
           'en/items/mounts/index.html', 'en/items/companion-pets/index.html', 'en/items/toys/index.html', 'en/quests/legacy-rewards/index.html'}
SCOPE42 = {page_of(i, l) for i in rev_ids for l in ('fr', 'en')}
for p in SCOPE42:
    if not (w / p).exists(): E(f'page attendue absente {p}')
changed = []
for f in sorted(str(p.relative_to(ow)) for p in ow.rglob('index.html')):
    o, n = (ow / f).read_text('utf-8'), (w / f).read_text('utf-8')
    if article_blocks(o) != article_blocks(n): changed.append(f)
info['article_blocks_changed_vs_v40b'] = len(changed)
if set(changed) - SCOPE41 - SCOPE42: E(f'blocs modifiés hors périmètre (vs v40b) : {sorted(set(changed) - SCOPE41 - SCOPE42)[:10]}')
ch41 = []
for f in sorted(str(p.relative_to(w41)) for p in w41.rglob('index.html')):
    if not (w / f).exists(): E(f'page v41 disparue {f}'); continue
    if article_blocks((w41 / f).read_text('utf-8')) != article_blocks((w / f).read_text('utf-8')): ch41.append(f)
info['article_blocks_changed_vs_v41'] = len(ch41)
if set(ch41) - SCOPE42: E(f'blocs modifiés hors périmètre (vs v41) : {sorted(set(ch41) - SCOPE42)[:10]}')
info['scope42_pages'] = len(SCOPE42); info['scope42_unchanged'] = sorted(SCOPE42 - set(ch41))
old_pages = {str(p.relative_to(ow)) for p in ow.rglob('*.html')}
new_pages = sorted(set(html) - old_pages); info['new_pages_vs_v40b'] = len(new_pages)
new41 = sorted(set(html) - {str(p.relative_to(w41)) for p in w41.rglob('*.html')}); info['new_pages_vs_v41'] = new41
exp_new = {page_of(i, l) for i in new_ids for l in ('fr', 'en')}
if set(new41) != exp_new: E(f'nouvelles pages inattendues {sorted(set(new41) ^ exp_new)}')
if set(old_pages) - set(html): E(f'pages supprimées {sorted(set(old_pages) - set(html))[:5]}')
# doublons : un titre = une page
titles = {}
for e in ENT.values():
    if e['status'] != 'published': continue
    for l in ('fr', 'en'): titles.setdefault((l, e['title'][l].strip().lower()), []).append(e['id'])
dups = {k: v for k, v in titles.items() if len(v) > 1}; info['duplicate_titles'] = dups
if any(i in new_ids for v in dups.values() for i in v): E(f'titre en double {dups}')
# Discord / correctifs : seuls les compteurs changent (Objets 8 -> 9 en v41, Métiers 18 -> 28 en v42)
for f in ('fr/actualites/correctifs-forever-5-et-6-novembre/index.html', 'en/news/forever-hotfixes-november-5-6/index.html', 'fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html', 'en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html'):
    o, n = (ow / f).read_text('utf-8'), (w / f).read_text('utf-8')
    o2 = re.sub(r'((?:Objets|Items)</span><span class="wk-count">)8<', r'\g<1>9<', o)
    o2 = re.sub(r'((?:Métiers|Professions)</span><span class="wk-count">)18<', r'\g<1>28<', o2)
    if o2 != n: E(f'Discord modifié au-delà des compteurs : {f}')
for f, labs in (('fr/index.html', (('Zones', 54), ('Donjons et raids', 26), ('Créatures', 14), ('Métiers', 28), ('Objets', 9), ('Quêtes et progression', 23), ('JcJ', 6), ('Actualités', 15), ('Classes', 11), ('Races', 11), ('Bien débuter', 18), ('Glossaire', 3), ('Collections', 238))),
                ('en/index.html', (('Zones', 54), ('Dungeons and raids', 26), ('Creatures', 14), ('Professions', 28), ('Items', 9), ('Quests and progression', 23), ('PvP', 6), ('News', 15), ('Classes', 11), ('Races', 11), ('Getting started', 18), ('Glossary', 3), ('Collections', 238)))):
    t = (w / f).read_text('utf-8')
    for lab, c in labs:
        if f'<strong>{lab}</strong><span class="wk-count">{c}<' not in t: E(f'compteur {f} {lab} {c}')
    if 'class="v40-home"' not in t or 'v2-hero' in t or 'v25-map' in t: E(f'structure accueil {f}')
    if ('../fr/metiers/materiaux/' if f.startswith('fr') else '../en/professions/materials/') not in t: E(f'accès rapide Matériaux {f}')
for l, href in (('fr', 'metiers/'), ('en', 'professions/')):
    t = (w / l / href / 'index.html').read_text('utf-8')
    for i in new_ids:
        if ENT[i]['article']['slug'][l] + '/' not in t: E(f'index Métiers sans lien vers {i} ({l})')
    if 'id="fiches-materials"' not in t: E(f'index Métiers : groupe Matériaux absent ({l})')
fh = (NEW / 'community/templates/_v2_header.html').read_text('utf-8')
for lab, c in (('Zones', 54), ('Créatures', 14), ('Quêtes et progression', 23), ('Objets', 9), ('Métiers', 28), ('Classes', 11), ('Donjons et raids', 26)):
    if f'<span class="wk-label">{lab}</span><span class="wk-count">{c}<' not in fh: E(f'en-tête forum {lab}')
for p in (OLD / 'community').rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:
        k = p.relative_to(OLD); q = NEW / k
        if H(p) != H(q) and str(k) != 'community/templates/_v2_header.html': E(f'forum modifié : {k}')
idx = json.loads((w / 'search-index.json').read_text('utf-8')); ids = {e['id'] for e in idx['entries']}
info['search_ids'] = len(ids)
if len(ids) != 220 or any(e.get('verification') is not None for e in idx['entries']) or not set(new_ids) <= ids: E('search-index')
alltext = ' '.join(visible((w / f).read_text('utf-8')) for f in html)
if re.search(r'Stone Key|Clé de pierre|sleeping bag|sac de couchage', alltext, re.I): E('élément non publié visible')
CF = re.compile(r'feu de camp|campfire', re.I)
for f in html:
    n_new = len(CF.findall(visible((w / f).read_text('utf-8'))))
    n_old = len(CF.findall(visible((ow / f).read_text('utf-8')))) if (ow / f).exists() else 0
    if n_new > n_old: E(f'feu de camp : nouvelle occurrence {f} ({n_old} -> {n_new})')
if any('sitemap' in str(p) for p in w.rglob('*')): E('sitemap présent')
# décision (c) : la liste de PNJ des zones n'est plus présentée comme « fichiers du jeu »
zone_pages = sorted({page_of(i, l) for i in rev_ids if ENT[i]['category'] == 'zones' for l in ('fr', 'en')}); info['zone_pages'] = len(zone_pages)
BAD = re.compile(r'liste des fichiers du jeu|liste de PNJ des fichiers du jeu|données des fichiers du jeu|game-file list|game-file NPC list|game-file data|PNJ \(données du jeu\)|NPCs \(game data\)', re.I)
for f in zone_pages:
    t = (w / f).read_text('utf-8'); v = visible(t)
    if BAD.search(v): E(f'étiquette « fichiers du jeu » restante {f} : {BAD.search(v).group(0)}')
    src = re.search(r'<ol class="source-list">.*?</ol>', t, re.S).group(0)
    for li in re.findall(r'<li id="source-\d+".*?</li>', src, re.S):
        if 'npc-liste.json' in li and 'Données du jeu' in li or ('npc-liste.json' in li and 'Game data' in li): E(f'liste de PNJ encore étiquetée données du jeu {f}')
# décision 1 (v42) : bestiaire, donjons, maîtres de classe : la base tierce n'est plus présentée comme « données du jeu »
d1_pages = sorted({page_of(i, l) for i in rev_ids if ENT[i]['category'] in ('creatures', 'instances', 'classes') for l in ('fr', 'en')}); info['d1_pages'] = len(d1_pages)
BAD1 = re.compile(r'données du jeu|fichiers du jeu|game data|game files|game-file|extrait Forever|Forever extract|NPC extract', re.I)
def no_hist(t): return re.sub(r'(?is)<section[^>]*id="historique-des-corrections".*?</section>', ' ', t)
for f in d1_pages:
    t = (w / f).read_text('utf-8'); v = visible(no_hist(re.sub(r'(?is)<ol class="source-list">.*?</ol>', ' ', t)))
    if BAD1.search(v): E(f'décision 1 : « données du jeu » restant {f} : {v[max(0, BAD1.search(v).start() - 60):BAD1.search(v).end() + 30]!r}')
    src = re.search(r'<ol class="source-list">.*?</ol>', t, re.S)
    for li in re.findall(r'<li id="source-\d+".*?</li>', src.group(0) if src else '', re.S):
        if 'eternadex' in li and not re.search(r'à confirmer|to be confirmed|unconfirmed', li): E(f'décision 1 : source tierce encore « données du jeu » {f}')
# décision (d) : noms allemands toujours signalés dans les annuaires de zone
sys.path.insert(0, str(R / 'v42-test/outils'))
GER = re.compile(r'[äöüßÄÖÜ]|\b(der|von|des)\b')
unflag = 0
F42 = json.load(open('/tmp/v42-pipeline/data/collections-v42.json'))
for k, v in F42.items():
    if not k.startswith('pnj-'): continue
    for l in ('fr', 'en'):
        for nm, rest in re.findall(r'<strong>([^<]+)</strong>(.{0,90})', v[l]) + re.findall(r'<th scope="row">([^<]+)</th>()', v[l]):
            if re.search(r'[äöüß]', nm) and 'nom allemand' not in rest and 'German name' not in rest: unflag += 1
info['german_names_unflagged_with_umlaut'] = unflag
if unflag: E(f'{unflag} noms allemands non signalés')
# 589 matériaux : chacun une seule fois (FR et EN)
M = json.load(open(R / 'v42-research/materials.json'))
for l, d in (('fr', 'metiers'), ('en', 'professions')):
    seen = {}
    for p in (w / l / d).glob('materia*/index.html'):
        for i in re.findall(r'<article class="v41-card v42-card[^"]*" id="mat-(\d+)"', p.read_text('utf-8')): seen[i] = seen.get(i, 0) + 1
    info[f'materials_{l}'] = len(seen)
    if set(seen) != set(M) or any(c != 1 for c in seen.values()): E(f'matériaux {l} : {len(seen)} / {len(M)}')
icons = sorted(w.glob('assets/icone-jeu-*.webp')); info['icons'] = len(icons); info['icons_bytes'] = sum(p.stat().st_size for p in icons)
imgs = 0
for f in sorted(SCOPE41 | SCOPE42 | set(new_pages)):
    t = (w / f).read_text('utf-8')
    for tag in re.findall(r'<img [^>]*>', t):
        if 'icone-jeu-' in tag:
            imgs += 1
            if 'loading="lazy"' not in tag or not ('width="56"' in tag or ('v42-chip-ic' in tag and 'width="28"' in tag)) or 'alt="' not in tag: E(f'img {f}')
info['img_tags_in_scope'] = imgs
from PIL import Image
bad = [p.name for p in icons if Image.open(p).size != (64, 64) or Image.open(p).format != 'WEBP']
if bad: E(f'icônes non conformes {bad[:5]}')
css = (w / 'v2.css').read_bytes(); ocss = (ow / 'v2.css').read_bytes(); css41 = (w41 / 'v2.css').read_bytes()
if not css.startswith(ocss) or not css.startswith(css41) or b'.v41-card' not in css or b'.v42-chip' not in css or b'@import' in css: E('v2.css')
sizes = sorted(((w / f).stat().st_size, f) for f in html)[-5:]; info['largest_pages'] = [(f, round(s / 1024)) for s, f in sizes]
print(json.dumps(info, ensure_ascii=False, indent=1)); print('ERREURS', len(errs)); [print(' -', e) for e in errs]
sys.exit(1 if errs else 0)

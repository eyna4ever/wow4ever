#!/usr/bin/env python3
"""v41 : contrôles du build de test (liens internes, CSP/self-host, noindex, contenu préservé hors fiches v41, compteurs)."""
import hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
R = Path('/workspace/wowkipedia-v21-elite'); NEW = R / 'v41-test/tree'; OLD = R / 'v40b-test/tree'
w, ow = NEW / 'wiki', OLD / 'wiki'
sys.path.insert(0, str(OLD / 'tools')); from content_blocks import article_blocks
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
errs = []; info = {}
def E(m): errs.append(m)
html = sorted(str(p.relative_to(w)) for p in w.rglob('*.html'))
info['pages'] = len(html)
def visible(t):
    t = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', t); t = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', t); return re.sub(r'<[^>]+>', ' ', t)
broken = []; nlinks = 0
for f in html:
    t = (w / f).read_text('utf-8')
    if 'name="robots" content="noindex' not in t: E(f'noindex manquant {f}')
    if re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="', t): E(f'script/style inline {f}')
    if re.search(r'(src|srcset)="https?:', t): E(f'ressource externe {f}')
    if re.search(r'Eternadex|Wowhead|wiki\.gg', visible(t), re.I): E(f'nom de site tiers visible {f}')
    if 'http-equiv="refresh"' in t: continue
    if 'Site indépendant et non officiel de Blizzard Entertainment.' not in t: E(f'mention manquante {f}')
    base = (w / f).parent
    for attr, u in re.findall(r'\s(href|src)="([^"]+)"', t):
        if re.match(r'(?i)(https?:|mailto:|#|data:|javascript:)', u) or u.split('?')[0].split('#')[0] in ('/community/', '/account/', '/privacy/'): continue  # servis par l'application Flask, pas par le wiki statique
        nlinks += 1
        path = unquote(urlsplit(u).path)
        tgt = (w / path.lstrip('/')) if path.startswith('/') else (base / path)
        tgt = tgt.resolve()
        if tgt.is_dir(): tgt = tgt / 'index.html'
        if not tgt.exists(): broken.append((f, u))
    for u in re.findall(r'srcset="([^"]+)"', t):
        for part in u.split(','):
            p = part.strip().split(' ')[0]
            if not (base / p).resolve().exists(): broken.append((f, p))
info['internal_links_checked'] = nlinks; info['broken'] = broken[:10]
if broken: E(f'{len(broken)} liens internes cassés')
# contenu préservé : blocs d'article identiques à la v40 sauf fiches v41
V41 = {'fr/objets/montures/index.html', 'fr/objets/mascottes/index.html', 'fr/objets/jouets/index.html', 'fr/quetes/recompenses-heritage/index.html',
       'en/items/mounts/index.html', 'en/items/companion-pets/index.html', 'en/items/toys/index.html', 'en/quests/legacy-rewards/index.html'}
changed = []
for f in sorted(str(p.relative_to(ow)) for p in ow.rglob('index.html')):
    o, n = (ow / f).read_text('utf-8'), (w / f).read_text('utf-8')
    if article_blocks(o) != article_blocks(n): changed.append(f)
info['article_blocks_changed'] = changed
if set(changed) - V41: E(f'blocs modifiés hors périmètre : {sorted(set(changed) - V41)}')
new_pages = sorted(set(html) - {str(p.relative_to(ow)) for p in ow.rglob('*.html')}); info['new_pages'] = new_pages
# Discord : seuls les compteurs changent
for f in ('fr/actualites/correctifs-forever-5-et-6-novembre/index.html', 'en/news/forever-hotfixes-november-5-6/index.html', 'fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html', 'en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html'):
    o, n = (ow / f).read_text('utf-8'), (w / f).read_text('utf-8')
    o2 = re.sub(r'((?:Objets|Items)</span><span class="wk-count">)8<', r'\g<1>9<', o)
    if o2 != n: E(f'Discord modifié au-delà du compteur : {f}')
# compteurs accueil
for f, labs in (('fr/index.html', (('Zones', 54), ('Donjons et raids', 26), ('Créatures', 14), ('Métiers', 18), ('Objets', 9), ('Quêtes et progression', 23), ('JcJ', 6), ('Actualités', 15), ('Classes', 11), ('Races', 11), ('Bien débuter', 18), ('Glossaire', 3), ('Collections', 238))),
                ('en/index.html', (('Zones', 54), ('Dungeons and raids', 26), ('Creatures', 14), ('Professions', 18), ('Items', 9), ('Quests and progression', 23), ('PvP', 6), ('News', 15), ('Classes', 11), ('Races', 11), ('Getting started', 18), ('Glossary', 3), ('Collections', 238)))):
    t = (w / f).read_text('utf-8')
    for lab, c in labs:
        if f'<strong>{lab}</strong><span class="wk-count">{c}<' not in t: E(f'compteur {f} {lab} {c}')
    if 'class="v40-home"' not in t or 'v2-hero' in t or 'v25-map' in t: E(f'structure accueil {f}')
fh = (NEW / 'community/templates/_v2_header.html').read_text('utf-8')
for lab, c in (('Zones', 54), ('Créatures', 14), ('Quêtes et progression', 23), ('Objets', 9), ('Métiers', 18), ('Classes', 11), ('Donjons et raids', 26)):
    if f'<span class="wk-label">{lab}</span><span class="wk-count">{c}<' not in fh: E(f'en-tête forum {lab}')
# forum : seul l'en-tête diffère
for p in (OLD / 'community').rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:
        k = p.relative_to(OLD); q = NEW / k
        if H(p) != H(q) and str(k) != 'community/templates/_v2_header.html': E(f'forum modifié : {k}')
idx = json.loads((w / 'search-index.json').read_text('utf-8')); ids = {e['id'] for e in idx['entries']}
info['search_ids'] = len(ids)
if len(ids) != 210 or any(e.get('verification') is not None for e in idx['entries']): E('search-index')
alltext = ' '.join(visible((w / f).read_text('utf-8')) for f in html)
if re.search(r'Stone Key|Clé de pierre|sleeping bag|sac de couchage', alltext, re.I): E('élément non publié visible')
# « feu de camp / campfire » existe déjà dans 80 pages v40 (menu/recettes) : aucune occurrence nouvelle n'est tolérée.
CF = re.compile(r'feu de camp|campfire', re.I)
for f in html:
    n_new = len(CF.findall(visible((w / f).read_text('utf-8'))))
    n_old = len(CF.findall(visible((ow / f).read_text('utf-8')))) if (ow / f).exists() else 0
    if n_new > n_old: E(f'feu de camp : nouvelle occurrence {f}')
if any('sitemap' in str(p) for p in w.rglob('*')): E('sitemap présent')
# images des collections
icons = sorted(w.glob('assets/icone-jeu-*.webp')); info['icons'] = len(icons); info['icons_bytes'] = sum(p.stat().st_size for p in icons)
imgs = 0
for f in sorted(V41 | set(new_pages)):
    t = (w / f).read_text('utf-8')
    for tag in re.findall(r'<img [^>]*>', t):
        if 'icone-jeu-' in tag:
            imgs += 1
            if 'loading="lazy"' not in tag or 'width="56"' not in tag or 'alt="' not in tag: E(f'img {f}')
info['img_tags_on_collection_pages'] = imgs
from PIL import Image
bad = [p.name for p in icons if Image.open(p).size != (64, 64) or Image.open(p).format != 'WEBP']
if bad: E(f'icônes non conformes {bad[:5]}')
css = (w / 'v2.css').read_bytes(); ocss = (ow / 'v2.css').read_bytes()
if not css.startswith(ocss) or b'.v41-card' not in css or b'@import' in css: E('v2.css')
game = [f for f in html if 'v39-figure is-game' in (w / f).read_text('utf-8')]; info['zone_game_figures'] = len(game)
print(json.dumps(info, ensure_ascii=False, indent=1)); print('ERREURS', len(errs)); [print(' -', e) for e in errs]
sys.exit(1 if errs else 0)

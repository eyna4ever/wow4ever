#!/usr/bin/env python3
"""v41 : prépare v41-test/v41-deploy (archive delta + update-v41.sh adapté de update-v40.sh). Aucun envoi, aucun déploiement."""
import hashlib, json, os, re, shutil, subprocess, tarfile, io
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v40b-test/tree'; B = R / 'v41-test/tree'; D = R / 'v41-test/v41-deploy'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B); assert fa <= fb
new = sorted(fb - fa); ch = sorted(k for k in fa if H(A / k) != H(B / k))
assert all(re.fullmatch(r'wiki/assets/icone-jeu-\d+\.webp|wiki/(fr/objets|en/items)/collections/index\.html', k) for k in new), new
assert all(k.startswith('wiki/') or k in ('tests/test_community.py', 'tests/wiki-baseline.json', 'community/templates/_v2_header.html') for k in ch)
members = sorted(new + ch)
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v41.tar.gz'
# archive reproductible : fichiers réguliers seulement, propriétaire 0, mtime fixe
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in members:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = 1795449600; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
import gzip
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
base = json.loads((B / 'tests/wiki-baseline.json').read_text()); V41TAR = base['tarball_sha256']
V40TAR = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
V40CSS, V40JS, HDR40, HDR41 = H(A / 'wiki/v2.css'), H(A / 'wiki/wk-header.js'), H(A / 'community/templates/_v2_header.html'), H(B / 'community/templates/_v2_header.html')
NNEW, NALL = len(new), len(members)
s = (R / 'v40-test/v40-deploy/update-v40.sh').read_text()
head_end = s.index('set -eEuo pipefail')
HEAD = f"""#!/bin/bash
# update-v41.sh : Wowkipedia v40b -> v41 (préparé pour t403u, 17 novembre 2026, Europe/Paris). PAQUET DE TEST PRÉPARÉ, NON PUBLIÉ.
#   Production : wowkipedia.com. CE SCRIPT NE DOIT ÊTRE LANCÉ qu'après un Oui EXPLICITE de publication de Mathieu.
#   v41 : catégorie Collections (montures, mascottes, jouets, héritage) illustrée par les icônes du jeu (fichiers du client
#   WoW Forever 1.60.1.70862, CDN officiel Blizzard), WebP 64 px auto-hébergées, chargement différé. 1 nouvelle fiche
#   (FR+EN) + 4 fiches révisées ; 453 pages, 210 fiches. Compteur « Objets » 8 -> 9 dans le menu de toutes les pages,
#   dans l'en-tête du forum (seul changement du forum) et sur l'accueil (+ tuile « Collections » 238).
#   Inchangés : adresses et slugs existants, CSP, Caddyfile (blocs raveforge compris), /opt/raveforge, noindex (pas de
#   sitemap), .env (jamais lu), code du forum (app.py, schéma, CSS, base.html, pied), page Discord (hors compteur),
#   wk-header.js, theme-wow.css, article « Correctifs Forever » FR/EN de la v40b (compteur Objets mis à 9).
# A lancer en root : bash update-v41.sh   (sortie courte ; journal détaillé dans /root/wow4ever-v41-*.log)
# Exige la v40b en ligne (release connue : releases/20261117T201412 ; empreinte wiki {V40TAR}),
#   même application, CSS, JS et en-tête du forum. La v41 rejoue les modifications v40b (article Correctifs du 16 novembre).
# Sauvegarde : /root/wow4ever-v41-backup-<horodatage>. Retour arrière automatique en cas d'échec ; manuel :
#   bash /root/wow4ever-rollback-v41.sh (-> releases/20261117T201412, v40b). N'écrase aucun rollback-v40.sh … rollback-v30.sh.
# Archive : /root/wow4ever-wiki-v41.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W41_URL.
"""
s = HEAD + s[head_end:]
# variables
s = re.sub(r'(?m)^SUM=.*$', f'SUM={SUM}', s)
s = re.sub(r'(?m)^V39REL=.*$', 'V40REL="(release v40 : chemin non connu au moment de la préparation)"', s)
s = re.sub(r'(?m)^V39TAR=.*$', f'V40TAR_={V40TAR}', s)
s = re.sub(r'(?m)^V40TAR=.*$', f'V41TAR={V41TAR}', s)
s = re.sub(r'(?m)^V39CSS=.*$', f'V40CSS={V40CSS}', s)
s = re.sub(r'(?m)^V39JS=.*$', f'V40JS={V40JS}', s)
s = re.sub(r'(?m)^HDR39=.*$', f'HDR40={HDR40}\nHDR41={HDR41}', s)
s = re.sub(r'(?m)^CHANGED=.*$', 'CHANGED=   # rempli depuis la liste de l\'archive (étape 2)', s)
s = re.sub(r'(?m)^COUNTS=.*$', "COUNTS='Zones|54;Créatures|14;Quêtes et progression|23;Objets|9;Collections|238;Métiers|18;Classes|11;Donjons et raids|26'", s)
s = re.sub(r'(?m)^RBLIST=.*$', 'RBLIST="40b 40 39 38 37 36 35 34 33 32 31 30"', s)
# usages
s = s.replace('"$BASE" != "$V40TAR"', '"$BASE" != "$V41TAR"').replace('"$BASE" = "$V39TAR"', '"$BASE" = "$V40TAR_"')
s = s.replace('$V39CSS', '$V40CSS').replace('$V39JS', '$V40JS').replace('$HDR39', '$HDR40').replace('$V39REL', '$V40REL').replace('$V39TAR', '$V40TAR_')
s = s.replace('"$V40TAR" "$CHANGED" "$HDR40"', '"$V41TAR" "$CHANGED" "$HDR40 $HDR41"')
# archive checks
s = s.replace(r"grep -vqE '^(wiki/(v2\.css|fr/index\.html|en/index\.html)|tests/(test_community\.py|wiki-baseline\.json))$'", r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json)|community/templates/_v2_header\.html)$'"); assert 'community/templates/_v2_header\\.html)$' in s
s = s.replace('[ "$(wc -l <<<"$LIST")" = 5 ] || die "archive : 5 fichiers attendus."', f'[ "$(wc -l <<<"$LIST")" = {NALL} ] || die "archive : {NALL} fichiers attendus."\nCHANGED=$(tr \'\\n\' \' \' <<<"$LIST")')
# bloc python de vérification : remplacé
i = s.index("import hashlib,json,re,sys\nfrom pathlib import Path\nnew,old,v40=")
j = s.index("PY\n", i)
PYV = r'''import hashlib,json,re,sys
from pathlib import Path
new,old,v41=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
changed=set(sys.argv[4].split()); hdr40,hdr41=sys.argv[5].split(); FFR,FEN,v40css,v40js=sys.argv[6:10]
H=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L=lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.venv' not in p.parts}
fn,fo=L(new),L(old)
assert fo<=fn, sorted(fo-fn)[:10]
added=fn-fo
assert added<=changed and all(re.fullmatch(r'wiki/assets/icone-jeu-\d+\.webp|wiki/(fr/objets|en/items)/collections/index\.html',k) for k in added), sorted(added)[:5]
assert len(added)==__NNEW__, len(added)
diff={k for k in fo if H(old/k)!=H(new/k)}
assert diff|added==changed, (sorted((diff|added)-changed)[:5], sorted(changed-(diff|added))[:5])
assert all(k.startswith('wiki/') or k in ('tests/test_community.py','tests/wiki-baseline.json','community/templates/_v2_header.html') for k in diff)
for k in ('community/schema.sql','community/selfcheck.py','community/proxy.py','community/app.py','community/static/forum-v2.css','community/templates/base.html','community/templates/_v2_footer.html','wiki/theme-wow.css','wiki/assets/v25-map-azeroth-1280.webp','wiki/ui-core.mjs','wiki/theme.js','wiki/wk-header.js'):
    if (old/k).is_file():
        assert H(new/k)==H(old/k), k
assert H(old/'wiki/v2.css')==v40css and H(old/'wiki/wk-header.js')==v40js
o,n=(old/'wiki/v2.css').read_bytes(),(new/'wiki/v2.css').read_bytes()
assert n.startswith(o) and len(n)>len(o) and b'.v41-card' in n and b'@import' not in n
assert H(old/'community/templates/_v2_header.html')==hdr40 and H(new/'community/templates/_v2_header.html')==hdr41
oh=(old/'community/templates/_v2_header.html').read_text('utf-8'); nh=(new/'community/templates/_v2_header.html').read_text('utf-8')
assert oh.replace('Objets</span><span class="wk-count">8<','Objets</span><span class="wk-count">9<')==nh
assert not any(k.startswith('wiki/assets/') for k in diff)
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v41
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v41, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==453 and not any('sitemap' in f for f in files)
sys.path.insert(0,str(old/'tools'))
from content_blocks import article_blocks
ow=old/'wiki'
V41={'fr/objets/montures/index.html','fr/objets/mascottes/index.html','fr/objets/jouets/index.html','fr/quetes/recompenses-heritage/index.html',
     'en/items/mounts/index.html','en/items/companion-pets/index.html','en/items/toys/index.html','en/quests/legacy-rewards/index.html'}
for f in sorted(str(p.relative_to(ow)) for p in ow.rglob('index.html')):
    if f in V41: continue
    o,n=(ow/f).read_text('utf-8'),(w/f).read_text('utf-8')
    assert article_blocks(o)==article_blocks(n), f
for f in ('fr/index.html','en/index.html'):
    t=(w/f).read_text('utf-8')
    assert 'class="v40-home"' in t and 'v2-hero' not in t and 'v25-map' not in t
cnt=lambda t: re.sub(r'((?:Objets|Items)</span><span class="wk-count">)8<',r'\g<1>9<',t)
for f in ('fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html','en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html','fr/actualites/correctifs-forever-5-et-6-novembre/index.html','en/news/forever-hotfixes-november-5-6/index.html'):
    assert cnt((ow/f).read_text('utf-8'))==(w/f).read_text('utf-8'), f
for f,lab in (('fr/index.html','Correctifs Forever du 5 au 16 novembre'),('en/index.html','Forever hotfixes, November 5–16')):
    t=(w/f).read_text('utf-8'); assert lab in t and 'datetime="2026-11-17"' in t, f
def visible(t):
    t=re.sub(r'(?is)<script[^>]*>.*?</script>',' ',t); t=re.sub(r'(?is)<style[^>]*>.*?</style>',' ',t); return re.sub(r'<[^>]+>',' ',t)
for f in sorted(html):
    t=(w/f).read_text('utf-8'); vis=visible(t)
    redirect='http-equiv="refresh"' in t
    assert 'name="robots" content="noindex' in t, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',t), f
    assert not re.search(r'(src|srcset)="https?:',t), f
    assert 'wiki.gg' not in t.lower() and not re.search(r'Eternadex|Wowhead|wiki\.gg', vis, re.I), f
    if redirect: continue
    assert 'Site indépendant et non officiel de Blizzard Entertainment.' in t and '<html lang="' in t and 'data-theme="wow"' in t.split('<head>',1)[0] and '<span class="wk-wordmark">Wowkipedia</span>' in t, f
    assert (FEN if f.startswith('en/') else FFR) in t, f
game=[f for f in html if 'v39-figure is-game' in (w/f).read_text('utf-8')]
assert len(game)==28, len(game)
for f in game:
    t=(w/f).read_text('utf-8'); assert ('Image du jeu © Blizzard Entertainment' if f.startswith('fr/') else 'Game image © Blizzard Entertainment') in t and 'assets/zone-jeu-' in t, f
fh_wiki=(w/'fr/index.html').read_text('utf-8')
eh_wiki=(w/'en/index.html').read_text('utf-8')
for lab,c in (('Zones',54),('Créatures',14),('Quêtes et progression',23),('Objets',9),('Métiers',18),('Classes',11),('Donjons et raids',26)):
    assert f'<span class="wk-label">{lab}</span><span class="wk-count">{c}<' in nh, lab
for lab,c in (('Zones',54),('Donjons et raids',26),('Créatures',14),('Métiers',18),('Objets',9),('Collections',238),('Quêtes et progression',23),('JcJ',6),('Actualités',15),('Classes',11),('Races',11),('Bien débuter',18),('Glossaire',3)):
    assert f'<strong>{lab}</strong><span class="wk-count">{c}<' in fh_wiki, lab
for lab,c in (('Zones',54),('Dungeons and raids',26),('Creatures',14),('Professions',18),('Items',9),('Collections',238),('Quests and progression',23),('PvP',6),('News',15),('Classes',11),('Races',11),('Getting started',18),('Glossary',3)):
    assert f'<strong>{lab}</strong><span class="wk-count">{c}<' in eh_wiki, lab
tj=(w/'theme.js').read_text('utf-8'); assert "localStorage.removeItem('wk-theme')" in tj and 'createElement' not in tj
idx=json.loads((w/'search-index.json').read_text('utf-8')); ids={e['id'] for e in idx['entries']}
assert len(ids)==210
assert all(e.get('verification') is None for e in idx['entries'])
alltext=' '.join(visible((w/f).read_text('utf-8')) for f in html)
assert not re.search(r'Stone Key|Clé de pierre|sleeping bag|sac de couchage',alltext,re.I)
'''.replace('__NNEW__', str(NNEW))
s = s[:i] + PYV + s[j:]
s = s.replace('la nouvelle release ne diffère pas de la v39 par les seuls fichiers v40 attendus', 'la nouvelle release ne diffère pas de la v40 par les seuls fichiers v41 attendus')
s = s.replace('say "   v40 : style journal de quêtes + accueil restructuré ; 451 pages, 209 fiches ; contenu des fiches identique à la v39 ; forum inchangé"',
              'say "   v41 : catégorie Collections ; 453 pages, 210 fiches ; 8 pages révisées + 2 nouvelles ; forum : seul le compteur Objets change"')
# libellés restants v40 -> v41, v39 -> v40 (via jeton)
s = s.replace('V40REL', '@@PREVREL@@').replace('V40TAR_', '@@PREVTAR@@').replace('V40CSS', '@@PREVCSS@@').replace('V40JS', '@@PREVJS@@').replace('HDR40', '@@PH@@').replace('V41TAR', '@@NT@@')
body_start = s.index('set -eEuo pipefail')
hd, bd = s[:body_start], s[body_start:]
PROT = {'v39-figure': '@@P1@@', 'v40-home': '@@P2@@', 'body.v39': '@@P3@@', 'v39-': '@@P4@@'}
for a, z in PROT.items(): bd = bd.replace(a, z)
bd = bd.replace('v40', '@@41@@').replace('V40', '@@V41@@').replace('W40_', 'W41_').replace('v39', 'v40').replace('V39', 'V40')
bd = bd.replace('@@41@@', 'v41').replace('@@V41@@', 'V41')
for a, z in PROT.items(): bd = bd.replace(z, a)
s = hd + bd
s = s.replace('@@PREVREL@@', 'V40REL').replace('@@PREVTAR@@', 'V40TAR_').replace('@@PREVCSS@@', 'V40CSS').replace('@@PREVJS@@', 'V40JS').replace('@@PH@@', 'HDR40').replace('@@NT@@', 'V41TAR')
s = re.sub(r'(?m)^V40REL=.*$', 'V40REL=releases/20261117T201412', s)
k = s.index('\n', s.index('W41_EXPECT_OLD:-}" ]')) + 1
s = s[:k] + '[ -n "${W41_TEST:-}" ] || [ "$OLD" = "$V40REL" ] || die "la release en ligne est $OLD (attendu la v40b $V40REL) : rien modifié."\n' + s[k:]
s = s.replace('say "   v40 reconnue (wiki', 'say "   v40b reconnue (wiki')
# pages en ligne attendues en plus après bascule
s = s.replace('for p in $KEPT_FR $POD_FR $POD_EN $DISCORD $DISCORD_EN /fr/wiki/ /en/wiki/ /community/; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done',
              'for p in $KEPT_FR $POD_FR $POD_EN $DISCORD $DISCORD_EN /fr/wiki/ /en/wiki/ /community/ /fr/objets/collections/ /en/items/collections/ /fr/objets/montures/ /assets/icone-jeu-3753812.webp; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done')
(D / 'update-v41.sh').write_text(s); (D / 'update-v41.template.sh').write_text(s)
RB = f"""#!/bin/bash
# APERÇU du retour arrière v41 -> v40b.
# Ce fichier est une PREVIEW : le vrai /root/wow4ever-rollback-v41.sh est écrit par update-v41.sh
# au moment du déploiement (cible : la release v40b en ligne).
# NE PAS LANCER ici. Ne pas téléverser. La publication exigera un Oui distinct de Mathieu.
# Cible prévue : releases/20261117T201412 (v40b, empreinte wiki {V40TAR}).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261117T201412
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || {{ echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }}
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V41_DONE
"""
(D / 'rollback-v41.sh').write_text(RB)
json.dump({'archive_sha256': SUM, 'wiki_v41': V41TAR, 'wiki_v40': V40TAR, 'files': NALL, 'new': NNEW, 'changed': len(ch), 'header_v41': HDR41}, open(D / 'empreintes.json', 'w'), indent=1)
print(json.dumps({'archive': SUM, 'files': NALL, 'new': NNEW, 'changed': len(ch), 'size': arc.stat().st_size, 'v41': V41TAR}))

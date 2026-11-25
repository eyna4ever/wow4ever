#!/usr/bin/env python3
"""v42b (t409u/t410u) : prépare v42b-test/v42b-deploy (archive delta v42 -> v42b + update-v42b.sh dérivé de update-v42.sh, publié).
Exige la v42 en ligne (releases/20261117T215520, wiki 4c9a4378…) et revient vers elle. Aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, tarfile, io, gzip
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42-test/tree'; B = R / 'v42b-test/tree'; D = R / 'v42b-test/v42b-deploy'
S42 = R / 'v42-test/v42-deploy/update-v42.sh'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B); assert fa <= fb
new = sorted(fb - fa); ch = sorted(k for k in fa if H(A / k) != H(B / k))
assert new == ['wiki/search-detail-en.json', 'wiki/search-detail-fr.json'], new
assert all(k.startswith('wiki/') or k in ('tests/test_community.py', 'tests/wiki-baseline.json', 'community/app.py') for k in ch), ch
members = sorted(new + ch)
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v42b.tar.gz'
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in members:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = 1795449600; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
V42 = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']; assert V42 == '4c9a437871db7bc1efe24d56206944fdb4f6f1260f65555e66909c170ac682ed'
V42B = json.loads((B / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
HDR = H(B / 'community/templates/_v2_header.html'); assert HDR == H(A / 'community/templates/_v2_header.html')
APP42, APP42B = H(A / 'community/app.py'), H(B / 'community/app.py')
CSS42, JS42, UI42 = H(A / 'wiki/v2.css'), H(A / 'wiki/wk-header.js'), H(A / 'wiki/ui-core.mjs')
NALL = len(members)
s = S42.read_text()
def rp(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, n, a[:90]); s = s.replace(a, b)
HEAD = f"""#!/bin/bash
# update-v42b.sh : Wowkipedia v42 -> v42b (préparé en t409u/t410u, 17 novembre 2026, Europe/Paris).
#   Production : wowkipedia.com. Publication approuvée par Mathieu : « Oui » t411u (17/11/2026 23:29 Europe/Paris), avec l'ajout
#   des mots-clés français cachés des créatures (« rajoute sanglier ») : sanglier, loup, araignée… (index FR seulement).
#   v42b = recherche détaillée : la recherche du site trouve aussi ce qui est DANS les pages (PNJ, formateurs, vendeurs, donneurs
#   de quêtes, créatures, boss, quêtes, objets de quête, objets vendus, matériaux, recettes, montures, mascottes, jouets, héritage,
#   classes, sorts et maîtres, passages d'articles, sections) avec un lien vers l'ancre exacte. Deux index légers chargés à la
#   demande (wiki/search-detail-fr.json, wiki/search-detail-en.json), ancres id ajoutées aux lignes/éléments de {len([k for k in ch if k.endswith('.html')])} pages
#   (texte inchangé), wk-header.js + ui-core.mjs (rendu DOM uniquement, même origine), v2.css (ajout en fin), liste blanche des
#   fichiers du wiki dans community/app.py (+ les 2 index ; seul changement de l'application). 473 pages, 220 fiches.
#   Inchangés : textes des pages, adresses et slugs, CSP, Caddyfile (blocs raveforge compris), /opt/raveforge, noindex (pas de
#   sitemap), .env (jamais lu), schéma, en-tête et pied du forum, page Discord et correctifs (aucune ancre ajoutée).
# A lancer en root : bash update-v42b.sh   (sortie courte ; journal détaillé dans /root/wow4ever-v42b-*.log)
# Exige la v42 en ligne (release connue : releases/20261117T215520 ; empreinte wiki {V42}),
#   même application, CSS, JS et en-tête du forum.
# Sauvegarde : /root/wow4ever-v42b-backup-<horodatage>. Retour arrière automatique en cas d'échec ; manuel :
#   bash /root/wow4ever-rollback-v42b.sh (-> releases/20261117T215520, v42). N'écrase aucun rollback-v42.sh, v41.sh, v40b.sh … v30.sh.
# Archive : /root/wow4ever-wiki-v42b.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W42B_URL.
"""
s = HEAD + s[s.index('set -eEuo pipefail'):]
# variables
rp('R="${W42_ROOT:-}"', 'R="${W42B_ROOT:-}"')
s = s.replace('W42_', 'W42B_')
rp('NAME=wow4ever-wiki-v42.tar.gz', 'NAME=wow4ever-wiki-v42b.tar.gz')
s = re.sub(r'(?m)^SUM=.*$', f'SUM={SUM}', s)
rp('BK=$R/root/wow4ever-v42-backup-$TS', 'BK=$R/root/wow4ever-v42b-backup-$TS')
rp('LOG=$R/root/wow4ever-v42-$TS.log', 'LOG=$R/root/wow4ever-v42b-$TS.log')
rp('RBS=$R/root/wow4ever-rollback-v42.sh', 'RBS=$R/root/wow4ever-rollback-v42b.sh')
rp('RBLIST="41 40b 40 39 38 37 36 35 34 33 32 31 30"', 'RBLIST="42 41 40b 40 39 38 37 36 35 34 33 32 31 30"')
rp('V40REL=releases/20261117T201412', 'V42REL=releases/20261117T215520')
rp('V40TAR_=e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce', f'V42TAR_={V42}')
rp(f'V42TAR={V42}', f'V42BTAR={V42B}')
rp('V40CSS=0758ffb0d1488471d4f24e73f9448f5e25420f6672ad9496bbd9983662a99d25', f'V42CSS={CSS42}')
rp('V40JS=016725e764bfa489c24e16d25a53fa0d577a910a7895b46cd92e82f295065cdd', f'V42JS={JS42}\nV42UI={UI42}')
rp(f'APPSUM={APP42}', f'APPSUM={APP42}\nAPP42B={APP42B}')
rp('HDR40=f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019', f'HDR40={HDR}')
s = s.replace('$V40REL', '$V42REL').replace('$V40TAR_', '$V42TAR_').replace('"$V40CSS"', '"$V42CSS"').replace('"$V40JS"', '"$V42JS"')
s = s.replace('"$V42TAR"', '"$V42BTAR"').replace('$V42TAR ', '$V42BTAR ')
# messages et contrôles préalables
rp('say "Retour arrière vers la v40 ($OLD)…"', 'say "Retour arrière vers la v42 ($OLD)…"')
rp('say "Retour arrière OK : v40 ($OLD) restaurée, forum redémarré (Caddyfile jamais modifié)."', 'say "Retour arrière OK : v42 ($OLD) restaurée, forum redémarré (Caddyfile jamais modifié)."')
rp('die "$RBS existe déjà (v42 déjà tentée ?) : rien modifié."', 'die "$RBS existe déjà (v42b déjà tentée ?) : rien modifié."')
rp('die "la v42 est déjà en ligne ($OLD) : rien modifié."', 'die "la v42b est déjà en ligne ($OLD) : rien modifié."')
rp('(attendu la v40b $V42REL)', '(attendu la v42 $V42REL)')
rp("la release actuelle n'est pas la v40 (wiki $BASE, attendu $V42TAR_)", "la release actuelle n'est pas la v42 (wiki $BASE, attendu $V42TAR_)")
rp('die "application différente de la v40 : rien modifié."', 'die "application différente de la v42 : rien modifié."')
rp("wiki/v2.css n'est pas celle de la v40", "wiki/v2.css n'est pas celle de la v42")
rp("""[ "$(sha < "$OLDREL/wiki/wk-header.js")" = "$V42JS" ] || die "wiki/wk-header.js n'est pas celui de la v40 : rien modifié." """.strip(),
   """[ "$(sha < "$OLDREL/wiki/wk-header.js")" = "$V42JS" ] || die "wiki/wk-header.js n'est pas celui de la v42 : rien modifié."
[ "$(sha < "$OLDREL/wiki/ui-core.mjs")" = "$V42UI" ] || die "wiki/ui-core.mjs n'est pas celui de la v42 : rien modifié." """.strip())
rp("_v2_header.html n'est pas celui de la v40", "_v2_header.html n'est pas celui de la v42")
rp("v40b reconnue (wiki $V42TAR_", "v42 reconnue (wiki $V42TAR_")
rp('[ "$(wc -w <<<"$OLDURLS")" = 451 ] || die "la release v40 n\'a pas 451 pages : rien modifié."', '[ "$(wc -w <<<"$OLDURLS")" = 473 ] || die "la release v42 n\'a pas 473 pages : rien modifié."')
# archive
rp(r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json)|community/templates/_v2_header\.html)$'",
   r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json)|community/app\.py)$'")
rp('[ "$(wc -l <<<"$LIST")" = 1041 ] || die "archive : 1041 fichiers attendus."', f'[ "$(wc -l <<<"$LIST")" = {NALL} ] || die "archive : {NALL} fichiers attendus."')
s = s.replace('release-v40.tar.gz', 'release-v42.tar.gz')
rp('say "4/7 Nouvelle release (copie de $OLD + wiki v42)"', 'say "4/7 Nouvelle release (copie de $OLD + recherche détaillée v42b)"')
rp("""<<'PY' || die "la nouvelle release ne diffère pas de la v42 par les seuls fichiers v42 attendus.\"""", """<<'PY' || die "la nouvelle release ne diffère pas de la v42 par les seuls fichiers v42b attendus.\"""")
rp('"$V42CSS" "$V42JS" <<\'PY\'', '"$V42CSS" "$V42JS" "$APPSUM" "$APP42B" <<\'PY\'')
# bloc Python de contrôle
i = s.index("import hashlib,json,re,sys\nfrom pathlib import Path\nnew,old,v42=")
j = s.index("PY\n", s.index("assert not re.search(r'Stone Key", i))
PYB = r"""import hashlib,json,re,sys,unicodedata
from pathlib import Path
new,old,v42b=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
changed=set(sys.argv[4].split()); hdr42,hdr42b=sys.argv[5].split(); FFR,FEN,v42css,v42js,app42,app42b=sys.argv[6:12]
H=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L=lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.venv' not in p.parts}
fn,fo=L(new),L(old)
assert fo<=fn, sorted(fo-fn)[:10]
added=fn-fo
assert added=={'wiki/search-detail-fr.json','wiki/search-detail-en.json'} and added<=changed, sorted(added)[:5]
diff={k for k in fo if H(old/k)!=H(new/k)}
assert diff|added==changed, (sorted((diff|added)-changed)[:5], sorted(changed-(diff|added))[:5])
assert all(k.startswith('wiki/') or k in ('tests/test_community.py','tests/wiki-baseline.json','community/app.py') for k in diff)
for k in ('community/schema.sql','community/selfcheck.py','community/proxy.py','community/static/forum-v2.css','community/templates/base.html','community/templates/_v2_header.html','community/templates/_v2_footer.html','wiki/theme-wow.css','wiki/theme.js','wiki/search-index.json'):
    if (old/k).is_file():
        assert H(new/k)==H(old/k), k
assert H(old/'wiki/v2.css')==v42css and H(old/'wiki/wk-header.js')==v42js and H(old/'community/app.py')==app42 and H(new/'community/app.py')==app42b
ao,an=(old/'community/app.py').read_text('utf-8'),(new/'community/app.py').read_text('utf-8')
assert an.replace("'search-index.json','search-detail-fr.json','search-detail-en.json',","'search-index.json',")==ao and an!=ao
o,n=(old/'wiki/v2.css').read_bytes(),(new/'wiki/v2.css').read_bytes()
assert n.startswith(o) and len(n)>len(o) and b'.wk-dresults' in n and b'@import' not in n
uo,un=(old/'wiki/ui-core.mjs').read_bytes(),(new/'wiki/ui-core.mjs').read_bytes()
assert un.startswith(uo) and b'export function searchDetails' in un
hj=(new/'wiki/wk-header.js').read_text('utf-8')
assert hj.count('fetch(')==1 and not re.search(r'innerHTML|outerHTML|insertAdjacentHTML|eval\(|new Function|https?://',hj) and 'search-detail-${lang}.json' in hj
assert H(new/'community/templates/_v2_header.html')==hdr42b==hdr42
assert not any(k.startswith('wiki/assets/') for k in diff)
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v42b
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v42b, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==473 and not any('sitemap' in f for f in files)
ow=old/'wiki'
# pages : seules des ancres id ont été ajoutées (texte, liens, structure identiques à la v42)
strip=lambda t: re.sub(r'<details class="v42-vendor" id="r-[a-z0-9-]+">','<details class="v42-vendor">',re.sub(r'<(tr|li|p) id="r-[a-z0-9-]+">',r'<\1>',t))
nchg=0
for f in sorted(html):
    o,n=(ow/f).read_text('utf-8'),(w/f).read_text('utf-8')
    if o!=n: nchg+=1
    assert strip(n)==o, f
for f in ('fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html','en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html','fr/actualites/correctifs-forever-5-et-6-novembre/index.html','en/news/forever-hotfixes-november-5-6/index.html'):
    assert (ow/f).read_text('utf-8')==(w/f).read_text('utf-8'), f
def slug(s):
    s=unicodedata.normalize('NFD',s); s=''.join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:40] or 'x'
for lang in ('fr','en'):
    d=json.loads((w/f'search-detail-{lang}.json').read_text('utf-8')); assert d['v']==1 and d['lang']==lang and len(d['r'])>15000
    ids={}
    for path,_ in d['pages']:
        assert path.startswith(lang+'/') and (w/path/'index.html').is_file(), path
        ids[path]=set(re.findall(r'\sid="([^"]+)"',(w/path/'index.html').read_text('utf-8')))
    miss=[r for r in d['r'] if (r[3] or 'r-'+slug(r[0])) not in ids[d['pages'][r[2]][0]]]
    assert not miss, miss[:3]
idx=json.loads((w/'search-index.json').read_text('utf-8')); assert len({e['id'] for e in idx['entries']})==220
def visible(t):
    t=re.sub(r'(?is)<script[^>]*>.*?</script>',' ',t); t=re.sub(r'(?is)<style[^>]*>.*?</style>',' ',t); return re.sub(r'<[^>]+>',' ',t)
for f in sorted(html):
    t=(w/f).read_text('utf-8')
    assert 'name="robots" content="noindex' in t, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',t), f
for lang in ('fr','en'):
    dj=(w/f'search-detail-{lang}.json').read_text('utf-8')
    assert not re.search(r'Eternadex|Wowhead|wiki\.gg|https?://',dj,re.I), lang
    assert not re.search(r'Stone Key|Clé de pierre|sleeping bag|sac de couchage',dj,re.I), lang
print('pages_avec_ancres',nchg)
"""
s = s[:i] + PYB + s[j:]
rp('say "   v42 (inclut la v41) : matériaux + PNJ des zones ; 473 pages, 220 fiches ; 194 pages révisées + 22 nouvelles ; forum : seuls les compteurs Objets et Métiers changent"',
   f'say "   v42b : recherche détaillée ; 473 pages, 220 fiches ; ancres ajoutées sur {len([k for k in ch if k.endswith(".html")])} pages (texte inchangé) ; 2 index ; app.py : liste blanche seulement"')
s = s.replace('wow4ever-v42-tests-$TS.txt', 'wow4ever-v42b-tests-$TS.txt')
# retour arrière
k0 = s.index('cat > "$RBS" <<RB'); k1 = s.index('\nRB\n', k0)
RBB = '''cat > "$RBS" <<RB
# Retour arrière v42b -> v42 : release $OLD (v42, $V42REL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v42b.
# N'écrase aucun rollback-v42.sh … rollback-v30.sh. Sauvegarde : $BK
set -euo pipefail
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || { echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V42B_DONE'''
s = s[:k0] + RBB + s[k1:]
# contrôles après bascule : index détaillés servis, ancre de Baine, langue non prévue refusée
rp('''[ "$(code /fr/zones/mulgore/ $HOST)" = 200 ] || die "/fr/zones/mulgore/ ne répond pas 200."''',
   '''[ "$(code /fr/zones/mulgore/ $HOST)" = 200 ] || die "/fr/zones/mulgore/ ne répond pas 200."
for p in /search-detail-fr.json /search-detail-en.json /search-index.json /ui-core.mjs /wk-header.js; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
[ "$(code /search-detail-de.json $HOST)" = 404 ] || die "/search-detail-de.json devrait répondre 404."
get /search-detail-fr.json | head -c 300 | grep -q '"lang":"fr"' || die "index détaillé FR illisible."
get /fr/zones/mulgore/ | grep -q 'id="r-baine-bloodhoof"' || die "ancre r-baine-bloodhoof absente de Mulgore."''')
rp('say "7/7 Terminé (paquet appliqué localement${W42B_TEST:+ — mode test, pas de bascule production})"', 'say "7/7 Terminé (paquet appliqué localement${W42B_TEST:+ — mode test, pas de bascule production})"')
rp('say WOW4EVER_UPDATE_V42_DONE', 'say WOW4EVER_UPDATE_V42B_DONE')
s = s.replace('$OLD / $V42REL', '$OLD / $V42REL')
exec(open(Path(__file__).with_name('fix_post42b.py')).read())
assert 'W42_' not in s and 'V40REL' not in s and 'V40TAR_' not in s and 'V40CSS' not in s and 'V40JS' not in s and 'WOW4EVER_UPDATE_V42_DONE' not in s
(D / 'update-v42b.sh').write_text(s)
RB = f"""# APERÇU du retour arrière v42b -> v42.
# Ce fichier est une PREVIEW : le vrai /root/wow4ever-rollback-v42b.sh est écrit par update-v42b.sh
# (avec la release en ligne au moment du lancement et le chemin de sauvegarde).
# Cible prévue : releases/20261117T215520 (v42, empreinte wiki {V42}).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261117T215520
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || {{ echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }}
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V42B_DONE
"""
(D / 'rollback-v42b.sh').write_text(RB)
json.dump({'archive_sha256': SUM, 'update_v42b_sh_sha256': H(D / 'update-v42b.sh'), 'wiki_v42b': V42B, 'wiki_v42': V42, 'files': NALL, 'new': len(new), 'changed': len(ch),
           'app_v42': APP42, 'app_v42b': APP42B, 'header': HDR, 'html_with_anchors': len([k for k in ch if k.endswith('.html')])}, open(D / 'empreintes.json', 'w'), indent=1)
print(json.dumps({'archive': SUM, 'size': arc.stat().st_size, 'files': NALL, 'new': len(new), 'changed': len(ch), 'v42b': V42B, 'update': H(D / 'update-v42b.sh')}))

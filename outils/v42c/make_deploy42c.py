#!/usr/bin/env python3
"""v42c (t412u/t413u) : prépare v42c-test/v42c-deploy (archive delta v42b -> v42c + update-v42c.sh dérivé de update-v42b.sh corrigé).
Exige la v42b en ligne (releases/20261117T224840, wiki 002361bf…) et revient vers elle. Aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, tarfile, io, gzip, time
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42b-test/tree'; B = R / 'v42c-test/tree'; D = R / 'v42c-test/v42c-deploy'
S = R / 'v42b-test/v42b-deploy/update-v42b.sh'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B); assert fa == fb
ch = sorted(k for k in fa if H(A / k) != H(B / k))
assert all(k.startswith('wiki/') or k in ('tests/test_community.py', 'tests/wiki-baseline.json') for k in ch), ch
NH = len([k for k in ch if k.endswith('.html')]); assert NH == 473 and len(ch) == 477, (NH, len(ch))
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v42c.tar.gz'
MT = int(time.time())  # date réelle de construction : ETag / Last-Modified des fichiers changés différents de la v42b
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in ch:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = MT; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
V42B = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']; assert V42B == '002361bf959a5df5b118146dd861265357d50361a1ba576de5ed70609ed27067'
V42C = json.loads((B / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
APP = H(A / 'community/app.py'); assert APP == H(B / 'community/app.py') == 'dc9e3e997da1e9fa014cb573ba25639c88de67f5ed93e4c8de8e4551a94f225f'
CSS, JS, UI = H(A / 'wiki/v2.css'), H(A / 'wiki/wk-header.js'), H(A / 'wiki/ui-core.mjs')
s = S.read_text()
# 1) renommage : v42b -> v42c (le paquet), puis v42 -> v42b (la base en ligne)
s = s.replace('42b', '42\x01').replace('42B', '42\x02')
s = re.sub(r'(?<=[vV])42(?![0-9\x01\x02])', lambda m: '42b', s)
s = re.sub(r'(?<=V)42b', '42B', s)
s = s.replace('42\x01', '42c').replace('42\x02', '42C')
def rp(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, n, a[:100]); s = s.replace(a, b)
i = s.index('set -eEuo pipefail')
s = f"""#!/bin/bash
# update-v42c.sh : Wowkipedia v42b -> v42c (préparé en t412u/t413u, 17 novembre 2026, Europe/Paris).
#   Production : wowkipedia.com. Correctif de la recherche sur téléphone (« Sur le mobile je peux pas faire de recherche
#   textuelle », « ça ouvre la page du wiki ») :
#   - la page « Tout le wiki » (/fr/wiki/, /en/wiki/, et /fr/wiki/?q=mot) affiche la case de recherche et les résultats
#     DANS la page (même recherche détaillée que la fenêtre) : si la loupe ouvre cette page, on peut chercher quand même ;
#   - adresses versionnées ?v=42c de wk-header.js, ui-core.mjs et v2.css sur les 473 pages (un ancien script gardé en cache
#     par le téléphone ne peut plus être réutilisé) ; dates des fichiers changés = date de construction (ETag nouveaux).
#   Inchangés : textes des pages, adresses et slugs, index de recherche, application (community/app.py), CSP, Caddyfile (blocs
#   raveforge compris), /opt/raveforge, noindex (pas de sitemap), .env (jamais lu), schéma, en-tête et pied du forum,
#   page Discord et correctifs (seule l'adresse des 3 fichiers change). 473 pages, 220 fiches.
# A lancer en root : bash update-v42c.sh   (sortie courte ; journal détaillé dans /root/wow4ever-v42c-*.log)
# Exige la v42b en ligne (release connue : releases/20261117T224840 ; empreinte wiki {V42B}),
#   même application, CSS, JS et en-tête du forum.
# Sauvegarde : /root/wow4ever-v42c-backup-<horodatage>. Retour arrière automatique en cas d'échec ; manuel :
#   bash /root/wow4ever-rollback-v42c.sh (-> releases/20261117T224840, v42b). N'écrase aucun rollback-v42b.sh, v42.sh … v30.sh.
# Archive : /root/wow4ever-wiki-v42c.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W42C_URL.
""" + s[i:]
rp('SUM=e9899ee7e6eafdc0367ea32571d7ef4a9b2a03cccc3da3e75c31d9aaa34dae09', f'SUM={SUM}')
rp('RBLIST="42 41 40b 40 39 38 37 36 35 34 33 32 31 30"', 'RBLIST="42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"')
rp('V42BREL=releases/20261117T215520', 'V42BREL=releases/20261117T224840')
rp('V42BTAR_=4c9a437871db7bc1efe24d56206944fdb4f6f1260f65555e66909c170ac682ed', f'V42BTAR_={V42B}')
rp('V42CTAR=002361bf959a5df5b118146dd861265357d50361a1ba576de5ed70609ed27067', f'V42CTAR={V42C}')
rp('V42BCSS=9f5107332a66317f39f182d7b4a0bdfe34544dc4cfed4af32817cea201c45bbe', f'V42BCSS={CSS}')
rp('V42BJS=016725e764bfa489c24e16d25a53fa0d577a910a7895b46cd92e82f295065cdd', f'V42BJS={JS}')
rp('V42BUI=49dccab2225791f0cf459dc4b838c03dbe59af00500253b64cad5dfa13b8e5b5', f'V42BUI={UI}')
rp('APPSUM=71c05b7259f8e139fa23cb2bcea8ecdc8216978452acc4bfa97e828d18f0218a', f'APPSUM={APP}')
rp('APP42C=dc9e3e997da1e9fa014cb573ba25639c88de67f5ed93e4c8de8e4551a94f225f', f'APP42C={APP}')
rp(r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json)|community/app\.py)$'", r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json))$'")
rp('[ "$(wc -l <<<"$LIST")" = 348 ] || die "archive : 348 fichiers attendus."', f'[ "$(wc -l <<<"$LIST")" = {len(ch)} ] || die "archive : {len(ch)} fichiers attendus."')
a = s.index('python3 - "$NEWREL" "$OLDREL" "$V42CTAR"'); b = s.index('PY\n', s.index("print('pages_avec_ancres',nchg)")) + 3
s = s[:a] + r'''python3 - "$NEWREL" "$OLDREL" "$V42CTAR" "$CHANGED" "$HDR40 $HDR42" "$V42BCSS" "$V42BJS" "$V42BUI" "$APPSUM" <<'PY' || die "la nouvelle release ne diffère pas de la v42b par les seuls fichiers v42c attendus."
import hashlib,json,re,sys
from pathlib import Path
new,old,v42c=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
changed=set(sys.argv[4].split()); hdr42,hdr42b=sys.argv[5].split(); css,js,ui,app=sys.argv[6:10]
H=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L=lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.venv' not in p.parts}
fn,fo=L(new),L(old)
assert fn==fo, sorted(fn^fo)[:10]
diff={k for k in fo if H(old/k)!=H(new/k)}
assert diff==changed, (sorted(diff-changed)[:5], sorted(changed-diff)[:5])
assert all(k.startswith('wiki/') or k in ('tests/test_community.py','tests/wiki-baseline.json') for k in diff)
assert H(old/'wiki/v2.css')==css and H(old/'wiki/wk-header.js')==js and H(old/'wiki/ui-core.mjs')==ui and H(old/'community/app.py')==app
for k in ('community/app.py','community/schema.sql','community/selfcheck.py','community/proxy.py','community/static/forum-v2.css','community/templates/base.html','community/templates/_v2_header.html','community/templates/_v2_footer.html','wiki/theme-wow.css','wiki/theme.js','wiki/search-index.json','wiki/search-detail-fr.json','wiki/search-detail-en.json','wiki/ui-core.mjs'):
    if (old/k).is_file():
        assert H(new/k)==H(old/k), k
o,n=(old/'wiki/v2.css').read_bytes(),(new/'wiki/v2.css').read_bytes()
assert n.startswith(o) and b'.wk-search-inline' in n[len(o):] and b'@import' not in n
hj=(new/'wiki/wk-header.js').read_text('utf-8')
assert hj.count('fetch(')==1 and not re.search(r'innerHTML|outerHTML|insertAdjacentHTML|eval\(|new Function|https?://',hj)
assert "from './ui-core.mjs?v=42c'" in hj and 'wk-search-inline' in hj and 'search-detail-${lang}.json' in hj
assert H(new/'community/templates/_v2_header.html')==hdr42b==hdr42
assert not any(k.startswith('wiki/assets/') for k in diff)
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v42c
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v42c, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==473 and not any('sitemap' in f for f in files)
ow=old/'wiki'
# pages : seule l'adresse des 3 fichiers change (?v=42c), 4 fois par page ; texte, liens et structure identiques à la v42b
for f in sorted(html):
    o,n=(ow/f).read_text('utf-8'),(w/f).read_text('utf-8')
    assert n.count('?v=42c"')==4 and n.replace('?v=42c"','"')==o, f
    assert 'name="robots" content="noindex' in n, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',n), f
print('pages_versionnees',len(html))
PY
''' + s[b:]
rp('say "   v42c : recherche détaillée ; 473 pages, 220 fiches ; ancres ajoutées sur 340 pages (texte inchangé) ; 2 index ; app.py : liste blanche seulement"',
   'say "   v42c : recherche dans la page « Tout le wiki » + adresses ?v=42c ; 473 pages, 220 fiches ; textes, index et application inchangés"')
# contrôles après bascule : adresses versionnées servies, script v42c, page « Tout le wiki » avec ?q=
rp('''for l in fr en; do json_ok /search-detail-$l.json $l || die "index détaillé $l illisible (JSON, langue ou taille)."; done''',
   '''for l in fr en; do json_ok /search-detail-$l.json $l || die "index détaillé $l illisible (JSON, langue ou taille)."; done
grep -qF 'wk-header.js?v=42c"' <<<"$HF" && grep -qF 'v2.css?v=42c"' <<<"$HF" || die "accueil FR sans les adresses ?v=42c."
grep -qF 'wk-header.js?v=42c"' <<<"$HE" || die "accueil EN sans les adresses ?v=42c."
for p in '/wk-header.js?v=42c' '/ui-core.mjs?v=42c' '/v2.css?v=42c' '/fr/wiki/?q=baine' '/en/wiki/?q=boar'; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
HJ=$(get '/wk-header.js?v=42c'); grep -qF 'wk-search-inline' <<<"$HJ" && grep -qF "ui-core.mjs?v=42c" <<<"$HJ" || die "wk-header.js servi n'est pas celui de la v42c."
HC=$(get '/v2.css?v=42c'); grep -qF '.wk-search-inline' <<<"$HC" || die "v2.css servie n'est pas celle de la v42c."
HW=$(get /fr/wiki/); grep -qF 'id="wk-search-input"' <<<"$HW" && grep -qF 'wk-header.js?v=42c"' <<<"$HW" || die "page « Tout le wiki » FR inattendue."''')
rp('''say "4/7 Nouvelle release (copie de $OLD + recherche détaillée v42c)"''', '''say "4/7 Nouvelle release (copie de $OLD + correctif recherche mobile v42c)"''')
rp('# Retour arrière v42c -> v42b : release $OLD (v42b, $V42BREL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v42c.\n# N\'écrase aucun rollback-v42b.sh … rollback-v30.sh.',
   '# Retour arrière v42c -> v42b : release $OLD (v42b, $V42BREL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v42c.\n# N\'écrase aucun rollback-v42b.sh, v42.sh … rollback-v30.sh.')
for bad in ('V42REL', 'V42TAR_', 'V42CSS', 'V42JS', 'V42UI', 'W42B_', 'V42B_DONE', '20261117T215520', 'e9899ee7', 'search-detail-fr.json\',\'search-detail-en.json\','):
    assert bad not in s, bad
(D / 'update-v42c.sh').write_text(s)
RB = f"""# APERÇU du retour arrière v42c -> v42b.
# Ce fichier est une PREVIEW : le vrai /root/wow4ever-rollback-v42c.sh est écrit par update-v42c.sh
# (avec la release en ligne au moment du lancement et le chemin de sauvegarde).
# Cible prévue : releases/20261117T224840 (v42b, empreinte wiki {V42B}).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261117T224840
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || {{ echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }}
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V42C_DONE
"""
(D / 'rollback-v42c.sh').write_text(RB)
G = 'https://github.com/eyna4ever/wow4ever/releases/download/deploy-v5-20261030'
(D / 'd42c.sh').write_text(f"""# Commandes serveur v42c (t412u/t413u) — base v42b en ligne : releases/20261117T224840, wiki 002361bf….
# NE PAS LANCER sans l'accord explicite de Mathieu (publication + mise en production). Lancement sur le serveur : par Mathieu.
cd /root
curl -fsSLo u42c.sh {G}/update-v42c.sh
sha256sum u42c.sh   # attendu : {H(D / 'update-v42c.sh')}
W42C_URL={G}/wow4ever-wiki-v42c.tar.gz bash u42c.sh </dev/null >u42c.log 2>&1; echo CODE $?
tail -n 15 u42c.log
echo FIN_V42C
# Succès : WOW4EVER_UPDATE_V42C_DONE · Retour arrière manuel vers la v42b : bash /root/wow4ever-rollback-v42c.sh
""")
(D / 'LIRE-MOI.txt').write_text(f"""Wowkipedia v42c — correctif de la recherche sur téléphone (t412u/t413u, 17/11/2026, Europe/Paris). Build de TEST, non publié.
Symptôme : sur Android, la loupe ou la case de l'accueil ouvrait la page « Tout le wiki » (liste A–Z) au lieu de la recherche.
Cause probable : le script de recherche n'était pas (encore) actif sur le téléphone (ancien script en cache, onglet ouvert avant
la mise à jour, réseau lent) ; dans ce cas le lien de secours de la loupe mène à « Tout le wiki », où il n'y avait pas de recherche.
Correctif : 1) la page « Tout le wiki » contient la recherche (et ?q=mot y montre les résultats) ; 2) adresses ?v=42c des
3 fichiers (le cache ne peut plus servir l'ancien script) ; 3) dates des fichiers = date de construction.
Archive : {arc.name} sha256 {SUM} ({len(ch)} fichiers : 473 pages, wk-header.js, v2.css, 2 tests).
Empreinte wiki v42c : {V42C} (base v42b : {V42B}).
Commandes : d42c.sh. Retour arrière : bash /root/wow4ever-rollback-v42c.sh (-> releases/20261117T224840).
""")
json.dump({'archive_sha256': SUM, 'update_v42c_sh_sha256': H(D / 'update-v42c.sh'), 'wiki_v42c': V42C, 'wiki_v42b': V42B, 'files': len(ch), 'html': NH, 'tar_mtime': MT,
           'app': APP, 'v42b_css': CSS, 'v42b_js': JS, 'v42b_ui': UI, 'v42c_css': H(B / 'wiki/v2.css'), 'v42c_js': H(B / 'wiki/wk-header.js')}, open(D / 'empreintes.json', 'w'), indent=1)
(D / 'SHA256SUMS').write_text(''.join(f'{H(D / n)}  {n}\n' for n in (arc.name, 'update-v42c.sh', 'rollback-v42c.sh', 'd42c.sh', 'LIRE-MOI.txt', 'empreintes.json')))
print(json.dumps({'archive': SUM, 'size': arc.stat().st_size, 'files': len(ch), 'v42c': V42C, 'update': H(D / 'update-v42c.sh'), 'mtime': MT}))

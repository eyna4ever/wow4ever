#!/usr/bin/env python3
"""v43b (t420u) : prépare v43b-test/v43b-deploy (archive delta v43 -> v43b + update-v43b.sh dérivé de update-v43.sh).
Exige la v43 en ligne (releases/20261118T002429, wiki fd0c62ca…) et y revient en cas d'échec. Aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, tarfile, io, gzip, time
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'polestar-test/tree'; B = R / 'v43b-test/tree'; D = R / 'v43b-test/v43b-deploy'
S = R / 'polestar-test/v43-deploy/update-v43.sh'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B); assert fa == fb, sorted(fa ^ fb)[:5]
ch = sorted(k for k in fa if H(A / k) != H(B / k))
TILE = re.compile(r'wiki/assets/carte/[0-9]{1,5}/r[0-9]{1,2}-c[0-9]{1,2}\.webp')
tiles = [k for k in ch if TILE.fullmatch(k)]
pages = [k for k in ch if re.fullmatch(r'wiki/(fr|en)/zones/[a-z0-9-]+/index\.html', k)]
cred = [k for k in ch if re.fullmatch(r'wiki/(fr/sources-et-licences|en/sources-and-licences)/index\.html', k)]
assert sorted(set(ch) - set(tiles) - set(pages) - set(cred)) == ['tests/test_community.py', 'tests/wiki-baseline.json']
assert len(pages) == 100 and len(cred) == 2
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v43b.tar.gz'; MT = int(time.time()); raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in ch:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = MT; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
V43 = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']; assert V43 == 'fd0c62ca454498c97964c1b3c701089cb27a7a494f976dad05ec26c0fb9216f7'
V43B = json.loads((B / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
APP = H(A / 'community/app.py'); assert APP == H(B / 'community/app.py') == 'd159df252913b0c569c644e1dfccaddfadb4e3ec2ba468a1f097cc38dc1bbda9'
CSS, JS, UI = H(A / 'wiki/v2.css'), H(A / 'wiki/wk-header.js'), H(A / 'wiki/ui-core.mjs')
TSHA = H(B / 'wiki/assets/carte/1411/r1-c2.webp'); assert TSHA != H(A / 'wiki/assets/carte/1411/r1-c2.webp')
s = S.read_text()
def rp(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, n, a[:120]); s = s.replace(a, b)
a = s.index('python3 - "$NEWREL" "$OLDREL" "$V43TAR"'); b = s.index('PY\n', s.index("print('pages_zones',len(zones)")) + 3
s = s[:a] + r'''python3 - "$NEWREL" "$OLDREL" "$V43BTAR" "$CHANGED" "$V43CSS" "$V43JS" "$V43UI" "$APPSUM" <<'PY' || die "la nouvelle release ne diffère pas de la v43 par les seuls fichiers v43b attendus."
import hashlib,json,re,sys
from pathlib import Path
new,old,v43b=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
changed=set(sys.argv[4].split()); css,js,ui,app=sys.argv[5:9]
H=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L=lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.venv' not in p.parts}
fn,fo=L(new),L(old)
assert fn==fo, sorted(fn^fo)[:10]
diff={k for k in fo if H(old/k)!=H(new/k)}
assert diff==changed, (sorted(diff-changed)[:5], sorted(changed-diff)[:5])
TILE=re.compile(r'wiki/assets/carte/[0-9]{1,5}/r[0-9]{1,2}-c[0-9]{1,2}\.webp'); ZONE=re.compile(r'wiki/(fr|en)/zones/[a-z0-9-]+/index\.html')
CRED=('wiki/fr/sources-et-licences/index.html','wiki/en/sources-and-licences/index.html')
assert all(TILE.fullmatch(k) or ZONE.fullmatch(k) or k in CRED or k in ('tests/test_community.py','tests/wiki-baseline.json') for k in diff), sorted(diff)[:5]
zones=sorted(k for k in diff if ZONE.fullmatch(k)); assert len(zones)==100, len(zones)
for k in ('community/app.py','community/schema.sql','community/selfcheck.py','community/proxy.py','community/static/forum-v2.css','community/templates/base.html','community/templates/_v2_header.html','community/templates/_v2_footer.html','wiki/v2.css','wiki/wk-header.js','wiki/ui-core.mjs','wiki/wk-map.js','wiki/wk-map.css','wiki/theme-wow.css','wiki/theme.js','wiki/search-index.json','wiki/search-detail-fr.json','wiki/search-detail-en.json','wiki/index.html'):
    if (old/k).is_file():
        assert H(new/k)==H(old/k), k
assert H(new/'wiki/v2.css')==css and H(new/'wiki/wk-header.js')==js and H(new/'wiki/ui-core.mjs')==ui and H(new/'community/app.py')==app
for k in sorted(k for k in diff if TILE.fullmatch(k)):
    b=(new/k).read_bytes(); assert b[:4]==b'RIFF' and b[8:12]==b'WEBP', k
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v43b
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v43b, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==475 and not any('sitemap' in f for f in files)
for f in sorted(html):
    n=(w/f).read_text('utf-8')
    assert 'name="robots" content="noindex' in n, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',n), f
# fiches : seules les adresses des tuiles (?v=43b) et la phrase de crédit changent
for k in zones:
    o,n=(old/k).read_text('utf-8'),(new/k).read_text('utf-8')
    assert not re.search(r'assets/carte/\d+/r\d+-c\d+\.webp"',n) and '.webp?v=43b"' in n, k
    o2=re.sub(r'(assets/carte/\d+/r\d+-c\d+\.webp)"',r'\1?v=43b"',o)
    cut=lambda x: re.sub(r'<p class="wk-map-credit">.*?</p>|<figcaption[^>]*>.*?</figcaption>','',x,flags=re.S)
    assert ('calques des zones explorées' in n) or ('explored-area layers' in n), k
    assert len(n)-len(o2) < 400, k
for k in CRED:
    assert 'WorldMapOverlay' in (new/k).read_text('utf-8'), k
print('pages_zones',len(zones),'tuiles',len([k for k in diff if TILE.fullmatch(k)]))
PY
''' + s[b:]
rp('''say "   v43 : quêtes fusionnées + carte interactive sur 100 fiches de zone, 2 pages « Sources et licences » ; 475 pages ; liste blanche de l'application élargie aux seuls fichiers v43"''',
   f'''say "   v43b : cartes entièrement explorées ({len(tiles)} tuiles, adresses ?v=43b) ; crédit mis à jour sur 100 fiches et 2 pages Sources ; application, données et autres pages inchangées"''')
rp('say "4/7 Nouvelle release (copie de $OLD + quêtes et carte interactive v43)"', 'say "4/7 Nouvelle release (copie de $OLD + cartes explorées v43b)"')
rp(r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json)|community/app\.py)$'", r"grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json))$'")
rp('[ "$(wc -l <<<"$LIST")" = 750 ] || die "archive : 750 fichiers attendus."', f'[ "$(wc -l <<<"$LIST")" = {len(ch)} ] || die "archive : {len(ch)} fichiers attendus."')
rp('''[ "$(wc -w <<<"$OLDURLS")" = 473 ] || die "la release v42c n'a pas 473 pages : rien modifié."''', '''[ "$(wc -w <<<"$OLDURLS")" = 475 ] || die "la release v42c n'a pas 475 pages : rien modifié."''')
anchor = 'map_ok || die "données de carte de Durotar illisibles (JSON ou repères)."\n'
rp(anchor, anchor + r'''grep -qF 'assets/carte/1411/r1-c2.webp?v=43b"' <<<"$HD" && grep -qF 'calques des zones explorées' <<<"$HD" || die "Durotar FR : tuiles ?v=43b ou crédit v43b absents."
grep -qF '.webp?v=43b"' <<<"$HDE" && grep -qF 'explored-area layers' <<<"$HDE" || die "Durotar EN : tuiles ?v=43b ou crédit v43b absents."
HS2=$(get /en/sources-and-licences/); grep -qF 'WorldMapOverlay' <<<"$HS2" || die "page Sources EN : crédit des cartes non mis à jour."
tile_ok || die "tuile explorée de Durotar non servie (empreinte inattendue)."
for p in '/assets/carte/1429/r1-c1.webp?v=43b' '/assets/carte/1454/r0-c0.webp?v=43b' '/fr/zones/foret-d-elwynn/' '/en/zones/elwynn-forest/'; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
''')
rp('wiki_checks(){\n', r'''tile_ok(){
  local f="$R/root/wow4ever-v43b-check-tuile.webp" n
  for n in $(seq 1 5); do
    if curl -fsS -m 60 "${RES[@]}" -o "$f" "$(U '/assets/carte/1411/r1-c2.webp?v=43b')" && [ "$(sha < "$f")" = "$TILE43B" ]; then rm -f "$f"; return 0; fi
    sleep 2
  done
  rm -f "$f"; return 1
}
wiki_checks(){
''')
for x, y in (('W43_', 'W43B_'), ('wow4ever-wiki-v43', 'wow4ever-wiki-v43b'), ('wow4ever-v43-', 'wow4ever-v43b-'), ('rollback-v43', 'rollback-v43b'),
             ('ROLLBACK_V43', 'ROLLBACK_V43B'), ('UPDATE_V43', 'UPDATE_V43B'), ('V43TAR', 'V43BTAR'), ('APP43=', 'APP43B=')):
    s = s.replace(x, y)
s = s.replace('wow4ever-v43b-check-tuile', 'wow4ever-v43b-check-tuile')
for x, y in (('V42CREL', 'V43REL'), ('V42CTAR_', 'V43TAR_'), ('V42CCSS', 'V43CSS'), ('V42CJS', 'V43JS'), ('V42CUI', 'V43UI')):
    s = s.replace(x, y)
s = re.sub(r'\bv43\b', 'v43b', s)
s = re.sub(r'\bv42c\b', 'v43', s)
rp('RBLIST="42c 42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"', 'RBLIST="43 42c 42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"')
rp('V43REL=releases/20261117T232038', 'V43REL=releases/20261118T002429')
rp('V43TAR_=c59626b1c32b73aadaa4971a1b5b36b5a2999aaa24e2aaf48a4b997ec32ac9aa', f'V43TAR_={V43}')
rp(f'V43BTAR=fd0c62ca454498c97964c1b3c701089cb27a7a494f976dad05ec26c0fb9216f7', f'V43BTAR={V43B}\nTILE43B={TSHA}')
rp('APPSUM=dc9e3e997da1e9fa014cb573ba25639c88de67f5ed93e4c8de8e4551a94f225f', f'APPSUM={APP}')
rp('APP43B=d159df252913b0c569c644e1dfccaddfadb4e3ec2ba468a1f097cc38dc1bbda9', f'APP43B={APP}')
s = re.sub(r'(?m)^SUM=[0-9a-f]{64}$', f'SUM={SUM}', s); assert s.count(f'SUM={SUM}') == 1
for x, y in (('V43CSS=', CSS), ('V43JS=', JS), ('V43UI=', UI)):
    s, n = re.subn(rf'(?m)^{x}[0-9a-f]{{64}}$', x + y, s); assert n == 1, x
s = s.replace("N'écrase aucun rollback-v43.sh, v42b.sh, v42.sh", "N'écrase aucun rollback-v43.sh, v42c.sh, v42b.sh, v42.sh")
i = s.index('set -eEuo pipefail'); j = s.index('\n', s.index('#!/bin/bash'))
s = f"""#!/bin/bash
# update-v43b.sh : Wowkipedia v43 -> v43b (préparé en t420u, 18 novembre 2026, Europe/Paris). Build de TEST, non publié.
#   « Pourquoi la carte interactive a le brouillard de guerre ? » : la v43 n'affichait que la carte de base (zones « non
#   explorées »). La v43b pose, comme le jeu pour une carte entièrement explorée, les calques officiels des zones explorées
#   (tables WorldMapOverlay / WorldMapOverlayTile du client 1.60.1.70862) à leurs décalages officiels, sans autre retouche.
#   {len(tiles)} tuiles remplacées (mêmes noms), adresses des tuiles ?v=43b sur les 100 fiches de zone (cache), phrase de crédit
#   mise à jour (100 fiches + 2 pages « Sources et licences »). Application, CSP, Caddyfile, données, autres pages inchangés.
# A lancer en root : bash update-v43b.sh   (journal détaillé dans /root/wow4ever-v43b-*.log)
# Exige la v43 en ligne (release connue : releases/20261118T002429 ; empreinte wiki {V43}).
# Retour arrière automatique en cas d'échec ; manuel : bash /root/wow4ever-rollback-v43b.sh (-> releases/20261118T002429, v43).
# Archive : /root/wow4ever-wiki-v43b.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W43B_URL.
""" + s[i:]
for bad in ('W43_', 'V42C', '20261117T232038', 'c59626b1', 'community/app\\.py)$', 'dcd61ed6'):
    assert bad not in s, bad
assert not re.search(r'(?m)^(?!\s*#)[^\n]*curl[^\n]*\|\s*(head|grep)', s)
(D / 'update-v43b.sh').write_text(s)
(D / 'rollback-v43b.sh').write_text(f"""# APERÇU du retour arrière v43b -> v43 (le vrai /root/wow4ever-rollback-v43b.sh est écrit par update-v43b.sh).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261118T002429
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || {{ echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }}
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V43B_DONE
""")
(D / 'd43b.sh').write_text(f"""# Commandes serveur v43b (t420u) — base v43 en ligne : releases/20261118T002429, wiki fd0c62ca….
# NE PAS LANCER sans l'accord explicite de Mathieu. Rien n'est publié : update-v43b.sh et wow4ever-wiki-v43b.tar.gz doivent d'abord
# être mis à disposition (décision de Mathieu), puis copiés dans /root.
cd /root
sha256sum update-v43b.sh wow4ever-wiki-v43b.tar.gz   # attendu : {H(D / 'update-v43b.sh')} / {SUM}
bash update-v43b.sh </dev/null >u43b.log 2>&1; echo CODE $?
tail -n 15 u43b.log
# Succès : WOW4EVER_UPDATE_V43B_DONE · Retour arrière manuel vers la v43 : bash /root/wow4ever-rollback-v43b.sh
""")
(D / 'LIRE-MOI.txt').write_text(f"""Wowkipedia v43b — cartes entièrement explorées (t420u, 18/11/2026, Europe/Paris). Build de TEST, non publié.
Archive : {arc.name} sha256 {SUM} ({len(ch)} fichiers : {len(tiles)} tuiles, 100 fiches, 2 pages Sources, 2 tests).
Empreinte wiki v43b : {V43B} (base v43 : {V43}). Application inchangée : {APP}.
Commandes : d43b.sh. Retour arrière : bash /root/wow4ever-rollback-v43b.sh (-> releases/20261118T002429).
""")
json.dump({'archive_sha256': SUM, 'archive_bytes': arc.stat().st_size, 'update_v43b_sh_sha256': H(D / 'update-v43b.sh'), 'wiki_v43b': V43B, 'wiki_v43': V43,
           'files': len(ch), 'tiles': len(tiles), 'tar_mtime': MT, 'app': APP, 'tile_durotar_r1c2': TSHA}, open(D / 'empreintes.json', 'w'), indent=1)
(D / 'SHA256SUMS').write_text(''.join(f'{H(D / n)}  {n}\n' for n in (arc.name, 'update-v43b.sh', 'rollback-v43b.sh', 'd43b.sh', 'LIRE-MOI.txt', 'empreintes.json')))
print(json.dumps({'archive': SUM, 'size': arc.stat().st_size, 'files': len(ch), 'tiles': len(tiles), 'v43b': V43B, 'update': H(D / 'update-v43b.sh')}))

#!/usr/bin/env python3
"""v43c (2026-11-24) : prépare v43c-test/v43c-deploy (archive delta v43b -> v43c + update-v43c.sh dérivé de update-v43b.sh).
Exige la v43b en ligne (releases/20261118T005337, wiki c82421…) et y revient en cas d'échec. Aucun déploiement."""
import hashlib, json, re, shutil, tarfile, io, gzip, time
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v43b-test/tree'; B = R / 'v43c-test/tree'; D = R / 'v43c-test/v43c-deploy'
S = R / 'v43b-test/v43b-deploy/update-v43b.sh'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
NEW = ['wiki/en/news/blackmaw-hold-abuse-actions/index.html', 'wiki/fr/actualites/sanctions-abus-blackmaw-hold/index.html']
fa, fb = L(A), L(B); assert fa <= fb and sorted(fb - fa) == NEW, sorted(fa ^ fb)[:5]
ch = sorted(k for k in fa if H(A / k) != H(B / k))
HTML = re.compile(r'wiki/(?:[a-z0-9-]+/)*index\.html')
JS = ['wiki/search-detail-en.json', 'wiki/search-detail-fr.json', 'wiki/search-index.json']
TESTS = ['tests/test_community.py', 'tests/wiki-baseline.json']
html = [k for k in ch if HTML.fullmatch(k)]
assert sorted(set(ch) - set(html)) == sorted(JS + TESTS), sorted(set(ch) - set(html))
pack = sorted(ch + NEW)
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v43c.tar.gz'; MT = int(time.time()); raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in pack:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = MT; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
V43B = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']; assert V43B == 'c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517'
V43C = json.loads((B / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
APP = H(A / 'community/app.py'); assert APP == H(B / 'community/app.py') == 'd159df252913b0c569c644e1dfccaddfadb4e3ec2ba468a1f097cc38dc1bbda9'
s = S.read_text()
def rp(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, n, a[:120]); s = s.replace(a, b)
# 1) bloc de vérification de la nouvelle release
a = s.index('python3 - "$NEWREL" "$OLDREL" "$V43BTAR"'); b = s.index('PY\n', s.index("print('pages_zones',len(zones)")) + 3
s = s[:a] + r'''python3 - "$NEWREL" "$OLDREL" "$V43CTAR" "$CHANGED" "$V43BCSS" "$V43BJS" "$V43BUI" "$APPSUM" <<'PY' || die "la nouvelle release ne diffère pas de la v43b par les seuls fichiers v43c attendus."
import hashlib,json,re,sys
from pathlib import Path
new,old,v43c=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
changed=set(sys.argv[4].split()); css,js,ui,app=sys.argv[5:9]
H=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L=lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.venv' not in p.parts}
NEW={'wiki/en/news/blackmaw-hold-abuse-actions/index.html','wiki/fr/actualites/sanctions-abus-blackmaw-hold/index.html'}
fn,fo=L(new),L(old)
assert fo<=fn and fn-fo==NEW, sorted(fn^fo)[:10]
diff={k for k in fo if H(old/k)!=H(new/k)}
assert diff|NEW==changed, (sorted(diff-changed)[:5], sorted(changed-diff-NEW)[:5])
HTML=re.compile(r'wiki/(?:[a-z0-9-]+/)*index\.html')
OK={'wiki/search-index.json','wiki/search-detail-fr.json','wiki/search-detail-en.json','tests/test_community.py','tests/wiki-baseline.json'}
assert all(HTML.fullmatch(k) or k in OK for k in diff), sorted(k for k in diff if not (HTML.fullmatch(k) or k in OK))[:5]
for k in ('community/app.py','community/schema.sql','community/selfcheck.py','community/proxy.py','community/static/forum-v2.css','community/templates/base.html','community/templates/_v2_header.html','community/templates/_v2_footer.html','wiki/v2.css','wiki/wk-header.js','wiki/ui-core.mjs','wiki/wk-map.js','wiki/wk-map.css','wiki/theme-wow.css','wiki/theme.js'):
    if (old/k).is_file():
        assert H(new/k)==H(old/k), k
assert H(new/'wiki/v2.css')==css and H(new/'wiki/wk-header.js')==js and H(new/'wiki/ui-core.mjs')==ui and H(new/'community/app.py')==app
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v43c
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v43c, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==477 and not any('sitemap' in f for f in files)
for f in sorted(html):
    n=(w/f).read_text('utf-8')
    assert 'name="robots" content="noindex' in n, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',n), f
for f in sorted(html):
    n=(w/f).read_text('utf-8'); assert 'du 5 au 16 novembre' not in n and 'November 5–16' not in n, f
hot=(w/'fr/actualites/correctifs-forever-5-et-6-novembre/index.html').read_text('utf-8'); en=(w/'en/news/forever-hotfixes-november-5-6/index.html').read_text('utf-8')
assert 'Correctifs Forever du 5 au 20 novembre' in hot and 'Forever hotfixes, November 5–20' in en
for p in (hot,en):
    for d in ('nov17','nov19','nov20'): assert f'id="details-{d}"' in p, d
    assert 'id="source-23"' in p and 'id="source-24"' not in p
for l in ('fr','en'):
    d=json.loads((w/f'search-detail-{l}.json').read_text('utf-8')); assert d['lang']==l and len(d['pages'])==221 and len(d['r'])>15000
si=json.loads((w/'search-index.json').read_text('utf-8')); assert len(si['entries'])==221
print('pages_html_modifiees',len([k for k in diff if HTML.fullmatch(k)]),'nouvelles',len(NEW))
PY
''' + s[b:]
rp('''say "   v43b : cartes entièrement explorées (436 tuiles, adresses ?v=43b) ; crédit mis à jour sur 100 fiches et 2 pages Sources ; application, données et autres pages inchangées"''',
   f'''say "   v43c : article Correctifs Forever (lots des 17, 19 et 20 novembre, titre « du 5 au 20 novembre » sur 79 pages), nouvel article Blackmaw Hold FR/EN, podcast épisode 8, menu Actualités 16 ; {len(html)} pages HTML et index de recherche mis à jour ; application, CSS, JS et images inchangés"''')
rp('say "4/7 Nouvelle release (copie de $OLD + cartes explorées v43b)"', 'say "4/7 Nouvelle release (copie de $OLD + actualités v43c)"')
rp('[ "$(wc -l <<<"$LIST")" = 540 ] || die "archive : 540 fichiers attendus."', f'[ "$(wc -l <<<"$LIST")" = {len(pack)} ] || die "archive : {len(pack)} fichiers attendus."')
rp("assert d.get('v')==1 and d.get('lang')==sys.argv[2] and len(d.get('r',[]))>15000 and len(d.get('pages',[]))==220",
   "assert d.get('v')==1 and d.get('lang')==sys.argv[2] and len(d.get('r',[]))>15000 and len(d.get('pages',[]))==221")
# 2) contrôles après bascule propres à la v43c
anchor = "for p in '/assets/carte/1429/r1-c1.webp?v=43b' '/assets/carte/1454/r0-c0.webp?v=43b' '/fr/zones/foret-d-elwynn/' '/en/zones/elwynn-forest/'; do [ \"$(code \"$p\" $HOST)\" = 200 ] || die \"$p ne répond pas 200.\"; done\n"
rp(anchor, anchor + r'''for p in $BM_FR $BM_EN $HOT_FR $HOT_EN; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
HB=$(get $BM_FR); grep -qF 'Repaire des Noiregueules' <<<"$HB" && grep -qF 'content="noindex' <<<"$HB" && grep -qF 'data-wk-header' <<<"$HB" && ! grep -qF '[src:' <<<"$HB" || die "article Blackmaw FR inattendu."
HBE=$(get $BM_EN); grep -qF 'Blackmaw Hold' <<<"$HBE" && grep -qF 'us.forums.blizzard.com/en/wow/t/2419757' <<<"$HBE" || die "article Blackmaw EN inattendu."
HH=$(get $HOT_FR); grep -qF 'Correctifs Forever du 5 au 20 novembre' <<<"$HH" && grep -qF 'id="details-nov20"' <<<"$HH" && grep -qF 'id="source-23"' <<<"$HH" || die "article Correctifs FR sans les lots v43c."
HHE=$(get $HOT_EN); grep -qF 'Forever hotfixes, November 5–20' <<<"$HHE" && grep -qF 'id="details-nov17"' <<<"$HHE" || die "article Correctifs EN sans les lots v43c."
HP=$(get $POD_FR); grep -qF 'news.blizzard.com/fr-fr/article/24317086' <<<"$HP" && grep -qF 'id="source-8"' <<<"$HP" || die "podcast FR sans l'épisode 8."
HPE=$(get $POD_EN); grep -qF 'news.blizzard.com/en-us/article/24317086' <<<"$HPE" || die "podcast EN sans l'épisode 8."
grep -qF 'actualites/sanctions-abus-blackmaw-hold/' <<<"$HF" || die "accueil FR sans l'article Blackmaw."
grep -qF 'news/blackmaw-hold-abuse-actions/' <<<"$HE" || die "accueil EN sans l'article Blackmaw."
HSI=$(get /search-index.json); grep -qF 'sanctions-abus-blackmaw-hold' <<<"$HSI" || die "search-index.json sans l'article Blackmaw."
''')
rp("POD_EN=/en/news/the-official-wow-forever-podcast/\n", "POD_EN=/en/news/the-official-wow-forever-podcast/\nBM_FR=/fr/actualites/sanctions-abus-blackmaw-hold/\nBM_EN=/en/news/blackmaw-hold-abuse-actions/\n"
   "HOT_FR=/fr/actualites/correctifs-forever-5-et-6-novembre/\nHOT_EN=/en/news/forever-hotfixes-november-5-6/\n")
# 3) renommages v43b -> v43c (base : v43b)
for x, y in (('V43BTAR', 'V43CTAR'), ('V43TAR_', 'V43BTAR_'), ('V43REL', 'V43BREL'), ('V43CSS', 'V43BCSS'), ('V43JS', 'V43BJS'), ('V43UI', 'V43BUI'), ('APP43B=', 'APP43C=')):
    s = s.replace(x, y) if x not in ('V43CSS', 'V43JS', 'V43UI') else re.sub(rf'\b{x}\b', y, s)
for x, y in (('W43B_', 'W43C_'), ('wow4ever-wiki-v43b', 'wow4ever-wiki-v43c'), ('wow4ever-v43b-', 'wow4ever-v43c-'), ('rollback-v43b', 'rollback-v43c'),
             ('ROLLBACK_V43B', 'ROLLBACK_V43C'), ('UPDATE_V43B', 'UPDATE_V43C')):
    s = s.replace(x, y)
s = re.sub(r'\bv43b\b', 'v43c', s)
s = re.sub(r'\bv43\b', 'v43b', s)
s = s.replace('wow4ever-v43c-check-tuile', 'wow4ever-v43c-check-tuile')
rp('ne diffère pas de la v43c par', 'ne diffère pas de la v43b par')
rp('ou crédit v43c absents', 'ou crédit v43b absents', 2)
rp('RBLIST="43 42c 42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"', 'RBLIST="43b 43 42c 42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"')
rp('V43BREL=releases/20261118T002429', 'V43BREL=releases/20261118T005337')
rp('V43BTAR_=fd0c62ca454498c97964c1b3c701089cb27a7a494f976dad05ec26c0fb9216f7', f'V43BTAR_={V43B}')
rp(f'V43CTAR={V43B}', f'V43CTAR={V43C}')
rp(f'APP43C={APP}', f'APP43C={APP}')
s = re.sub(r'(?m)^SUM=[0-9a-f]{64}$', f'SUM={SUM}', s); assert s.count(f'SUM={SUM}') == 1
for x, f in (('V43BCSS=', 'wiki/v2.css'), ('V43BJS=', 'wiki/wk-header.js'), ('V43BUI=', 'wiki/ui-core.mjs')):
    assert re.search(rf'(?m)^{x}{H(A / f)}$', s), x
s = s.replace("N'écrase aucun rollback-v43b.sh, v42c.sh", "N'écrase aucun rollback-v43b.sh, v43.sh, v42c.sh")
i = s.index('set -eEuo pipefail')
s = f"""#!/bin/bash
# update-v43c.sh : Wowkipedia v43b -> v43c (préparé le 24 novembre 2026, Europe/Paris). Paquet de TEST : ne pas lancer sans le « Oui » de Mathieu.
#   Article « Correctifs Forever » FR/EN : lots officiels de correctifs des 17, 19 et 20 novembre (news.blizzard 24315281, Kaivax
#   US 2403040 #12-#14 / EU 639885 #11-#13), titre « du 5 au 20 novembre » / « November 5–20 » repris sur 79 pages (liens, accueils,
#   index de recherche). Nouvel article FR/EN « Repaire des Noiregueules (Blackmaw Hold) » : sanctions après l'abus de butin
#   (forums US 2419757 / EU 643759). Podcast officiel : épisode 8 (news.blizzard 24317086). Pages HTML et index de recherche seulement :
#   application, CSP, Caddyfile, CSS, JS, images, données inchangés. {len(html)} pages modifiées (dont le compteur du menu Actualités : 16) ; 477 pages (+2).
# A lancer en root : bash update-v43c.sh   (journal détaillé dans /root/wow4ever-v43c-*.log)
# Exige la v43b en ligne (release connue : releases/20261118T005337 ; empreinte wiki {V43B}).
# Retour arrière automatique en cas d'échec ; manuel : bash /root/wow4ever-rollback-v43c.sh (-> releases/20261118T005337, v43b).
# Archive : /root/wow4ever-wiki-v43c.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W43C_URL.
""" + s[i:]
for bad in ('W43B_', 'W43_', '20261118T002429', 'fd0c62ca', 'TEST, non publié', 'V43TAR_'):
    assert bad not in s, bad
assert not re.search(r'(?m)^(?!\s*#)[^\n]*curl[^\n]*\|\s*(head|grep)', s)
(D / 'update-v43c.sh').write_text(s)
(D / 'rollback-v43c.sh').write_text(f"""# APERÇU du retour arrière v43c -> v43b (le vrai /root/wow4ever-rollback-v43c.sh est écrit par update-v43c.sh).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261118T005337
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || {{ echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }}
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V43C_DONE
""")
U = 'https://github.com/eyna4ever/wow4ever/releases/download/deploy-v5-20261030'
UPD = H(D / 'update-v43c.sh')
(D / 'd43c.sh').write_text(f"""# Commandes serveur v43c (24/11/2026) — base v43b en ligne : releases/20261118T005337, wiki c82421613a35….
# NE PAS LANCER sans le « Oui » explicite de Mathieu.
curl -fsSLo /root/u43c.sh {U}/update-v43c.sh && sha256sum /root/u43c.sh | grep -q ^{UPD[:16]} && W43C_URL={U}/wow4ever-wiki-v43c.tar.gz bash /root/u43c.sh </dev/null >/root/u43c.log 2>&1; echo CODE $?
tail -n 15 /root/u43c.log
# attendu : update-v43c.sh {UPD} ; archive {SUM} (vérifiée par le script)
# Succès : WOW4EVER_UPDATE_V43C_DONE · Retour arrière manuel vers la v43b : bash /root/wow4ever-rollback-v43c.sh
""")
(D / 'LIRE-MOI.txt').write_text(f"""Wowkipedia v43c — Correctifs Forever (17, 19, 20 novembre), article Blackmaw Hold FR/EN, podcast épisode 8 (24/11/2026, Europe/Paris). Paquet de TEST, non déployé.
Archive : {arc.name} sha256 {SUM} ({len(pack)} fichiers : {len(html)} pages HTML modifiées, 2 nouvelles pages, 3 index de recherche, 2 tests).
Empreinte wiki v43c : {V43C} (base v43b : {V43B}). Application inchangée : {APP}.
Commandes : d43c.sh. Retour arrière : bash /root/wow4ever-rollback-v43c.sh (-> releases/20261118T005337).
""")
json.dump({'archive_sha256': SUM, 'archive_bytes': arc.stat().st_size, 'update_v43c_sh_sha256': UPD, 'wiki_v43c': V43C, 'wiki_v43b': V43B,
           'files': len(pack), 'html_changed': len(html), 'new_pages': NEW, 'tar_mtime': MT, 'app': APP}, open(D / 'empreintes.json', 'w'), indent=1)
(D / 'SHA256SUMS').write_text(''.join(f'{H(D / n)}  {n}\n' for n in (arc.name, 'update-v43c.sh', 'rollback-v43c.sh', 'd43c.sh', 'LIRE-MOI.txt', 'empreintes.json')))
print(json.dumps({'archive': SUM, 'size': arc.stat().st_size, 'files': len(pack), 'html': len(html), 'v43c': V43C, 'update': UPD}))

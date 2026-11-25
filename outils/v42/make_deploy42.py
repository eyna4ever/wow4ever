#!/usr/bin/env python3
"""v42 (t407u) : prépare v42-test/v42-deploy (archive delta v40b -> v42 + update-v42.sh dérivé de update-v41.sh).
Exige la v40b en ligne (releases/20261117T201412, wiki e5ecbb6c…) et revient vers elle ; la v42 inclut la v41 (jamais publiée).
Aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, tarfile, io, gzip
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v40b-test/tree'; B = R / 'v42-test/tree'; D = R / 'v42-test/v42-deploy'
S41 = R / 'v41-test/v41-deploy/update-v41.sh'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
L = lambda r: {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
fa, fb = L(A), L(B); assert fa <= fb
new = sorted(fb - fa); ch = sorted(k for k in fa if H(A / k) != H(B / k))
NEWRX = r'wiki/assets/icone-jeu-\d+\.webp|wiki/(fr/objets|en/items)/collections/index\.html|wiki/fr/metiers/materiaux(-[a-z-]+)?/index\.html|wiki/en/professions/materials(-[a-z-]+)?/index\.html'
assert all(re.fullmatch(NEWRX, k) for k in new), [k for k in new if not re.fullmatch(NEWRX, k)]
assert all(k.startswith('wiki/') or k in ('tests/test_community.py', 'tests/wiki-baseline.json', 'community/templates/_v2_header.html') for k in ch)
members = sorted(new + ch)
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)
arc = D / 'wow4ever-wiki-v42.tar.gz'
raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as t:
    for k in members:
        data = (B / k).read_bytes(); ti = tarfile.TarInfo(k); ti.size = len(data); ti.mode = 0o644; ti.mtime = 1795449600; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'
        t.addfile(ti, io.BytesIO(data))
with open(arc, 'wb') as f:
    with gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as g: g.write(raw.getvalue())
SUM = H(arc)
V42TAR = json.loads((B / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
V40TAR = json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256']
assert V40TAR == 'e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce'
HDR42 = H(B / 'community/templates/_v2_header.html')
NNEW, NALL = len(new), len(members)
# pages du périmètre (blocs d'article modifiés autorisés) : v41 + v42
ENT = {e['id']: e for e in json.load(open('/tmp/v42-pipeline/runtime/entries.json'))}
CATS = {'zones': ('zones', 'zones'), 'professions': ('metiers', 'professions'), 'items': ('objets', 'items'), 'quests': ('quetes', 'quests'), 'creatures': ('creatures', 'creatures'), 'instances': ('donjons-raids', 'dungeons-raids'), 'classes': ('classes', 'classes')}
rev = [json.loads(p.read_text())['id'] for p in sorted((R / 'v42-test/out/entries').glob('rev-*.json'))]
SCOPE = sorted({f'{l}/{CATS[ENT[i]["category"]][0 if l == "fr" else 1]}/{ENT[i]["article"]["slug"][l]}/index.html' for i in rev for l in ('fr', 'en')} |
               {'fr/objets/montures/index.html', 'fr/objets/mascottes/index.html', 'fr/objets/jouets/index.html', 'fr/quetes/recompenses-heritage/index.html',
                'en/items/mounts/index.html', 'en/items/companion-pets/index.html', 'en/items/toys/index.html', 'en/quests/legacy-rewards/index.html'})
s = S41.read_text()
def rp(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, n, a[:90]); s = s.replace(a, b)
head_end = s.index('set -eEuo pipefail')
HEAD = f"""#!/bin/bash
# update-v42.sh : Wowkipedia v40b -> v42 (préparé en t407u, 17 novembre 2026, Europe/Paris).
#   Production : wowkipedia.com. Publication approuvée par Mathieu : « Oui » t408u (17/11/2026 22:45 Europe/Paris).
#   v42 = v41 (Collections, jamais publiée) + matériaux de métier « où les trouver » (10 nouvelles fiches FR+EN : accueil +
#   9 familles, 589 matériaux), section « PNJ : où les trouver » sur les fiches de zone (formateurs, vendeurs et stock,
#   donneurs de quêtes avec position, objets de quête et leur source — base non officielle, « à confirmer »), liste de PNJ
#   des zones ré-étiquetée « à confirmer » (elle était présentée à tort comme « fichiers du jeu »), matériaux liés sur les
#   12 pages de recettes, 4 montures vendues par un PNJ (à confirmer) ; bestiaire (10 fiches), donjons (17) et maîtres de classe :
#   PNJ, boss et recettes de la base non officielle marqués « à confirmer » (ils étaient présentés comme « données du jeu »). 473 pages, 220 fiches. Compteurs « Objets » 8 -> 9
#   et « Métiers » 18 -> 28 dans le menu de toutes les pages, dans l'en-tête du forum (seul changement du forum) et sur l'accueil.
#   Inchangés : adresses et slugs existants, CSP, Caddyfile (blocs raveforge compris), /opt/raveforge, noindex (pas de
#   sitemap), .env (jamais lu), code du forum (app.py, schéma, CSS, base.html, pied), page Discord (hors compteurs),
#   wk-header.js, theme-wow.css, article « Correctifs Forever » FR/EN de la v40b (compteurs seulement).
# A lancer en root : bash update-v42.sh   (sortie courte ; journal détaillé dans /root/wow4ever-v42-*.log)
# Exige la v40b en ligne (release connue : releases/20261117T201412 ; empreinte wiki {V40TAR}),
#   même application, CSS, JS et en-tête du forum.
# Sauvegarde : /root/wow4ever-v42-backup-<horodatage>. Retour arrière automatique en cas d'échec ; manuel :
#   bash /root/wow4ever-rollback-v42.sh (-> releases/20261117T201412, v40b). N'écrase aucun rollback-v41.sh (absent), v40b.sh … v30.sh.
# Archive : /root/wow4ever-wiki-v42.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W42_URL.
"""
s = HEAD + s[head_end:]
s = re.sub(r'(?m)^SUM=.*$', f'SUM={SUM}', s)
s = re.sub(r'(?m)^V41TAR=.*$', f'V42TAR={V42TAR}', s)
s = re.sub(r'(?m)^HDR41=.*$', f'HDR42={HDR42}', s)
s = re.sub(r'(?m)^RBLIST=.*$', 'RBLIST="41 40b 40 39 38 37 36 35 34 33 32 31 30"', s)
rp("COUNTS='Zones|54;Créatures|14;Quêtes et progression|23;Objets|9;Collections|238;Métiers|18;Classes|11;Donjons et raids|26'",
   "COUNTS='Zones|54;Créatures|14;Quêtes et progression|23;Objets|9;Collections|238;Métiers|28;Classes|11;Donjons et raids|26'")
m = re.search(r'\[ "\$\(wc -l <<<"\$LIST"\)" = (\d+) \] \|\| die "archive : \d+ fichiers attendus."', s); assert m
s = s.replace(m.group(0), f'[ "$(wc -l <<<"$LIST")" = {NALL} ] || die "archive : {NALL} fichiers attendus."')
# bloc python de vérification
rp(r"assert added<=changed and all(re.fullmatch(r'wiki/assets/icone-jeu-\d+\.webp|wiki/(fr/objets|en/items)/collections/index\.html',k) for k in added), sorted(added)[:5]",
   "assert added<=changed and all(re.fullmatch(r'" + NEWRX + "',k) for k in added), sorted(added)[:5]")
m = re.search(r"assert len\(added\)==(\d+), len\(added\)", s); assert m; s = s.replace(m.group(0), f"assert len(added)=={NNEW}, len(added)")
rp("assert n.startswith(o) and len(n)>len(o) and b'.v41-card' in n and b'@import' not in n", "assert n.startswith(o) and len(n)>len(o) and b'.v41-card' in n and b'.v42-chip' in n and b'@import' not in n")
rp("""assert oh.replace('Objets</span><span class="wk-count">8<','Objets</span><span class="wk-count">9<')==nh""",
   """assert oh.replace('Objets</span><span class="wk-count">8<','Objets</span><span class="wk-count">9<').replace('Métiers</span><span class="wk-count">18<','Métiers</span><span class="wk-count">28<')==nh""")
rp("assert len(html)==453 and not any('sitemap' in f for f in files)", "assert len(html)==473 and not any('sitemap' in f for f in files)")
i = s.index("V41={'fr/objets/montures/index.html'"); j = s.index("\n", s.index("'en/items/mounts/index.html'", i))
s = s[:i] + "SCOPE=set(" + json.dumps(SCOPE) + ")" + s[j:]
rp("    if f in V41: continue", "    if f in SCOPE: continue")
rp("""cnt=lambda t: re.sub(r'((?:Objets|Items)</span><span class="wk-count">)8<',r'\\g<1>9<',t)""",
   """cnt=lambda t: re.sub(r'((?:Métiers|Professions)</span><span class="wk-count">)18<',r'\\g<1>28<',re.sub(r'((?:Objets|Items)</span><span class="wk-count">)8<',r'\\g<1>9<',t))""")
rp("for lab,c in (('Zones',54),('Créatures',14),('Quêtes et progression',23),('Objets',9),('Métiers',18),('Classes',11),('Donjons et raids',26)):",
   "for lab,c in (('Zones',54),('Créatures',14),('Quêtes et progression',23),('Objets',9),('Métiers',28),('Classes',11),('Donjons et raids',26)):")
rp("('Créatures',14),('Métiers',18),('Objets',9),('Collections',238)", "('Créatures',14),('Métiers',28),('Objets',9),('Collections',238)")
rp("('Creatures',14),('Professions',18),('Items',9),('Collections',238)", "('Creatures',14),('Professions',28),('Items',9),('Collections',238)")
rp("assert len(ids)==210", "assert len(ids)==220")
rp('say "   v41 : catégorie Collections ; 453 pages, 210 fiches ; 8 pages révisées + 2 nouvelles ; forum : seul le compteur Objets change"',
   f'say "   v42 (inclut la @@VQ@@) : matériaux + PNJ des zones ; 473 pages, 220 fiches ; {len(SCOPE)} pages révisées + 22 nouvelles ; forum : seuls les compteurs Objets et Métiers changent"')
rp("/fr/objets/collections/ /en/items/collections/ /fr/objets/montures/ /assets/icone-jeu-3753812.webp;",
   "/fr/objets/collections/ /en/items/collections/ /fr/objets/montures/ /assets/icone-jeu-3753812.webp /fr/metiers/materiaux/ /en/professions/materials/ /fr/metiers/materiaux-minerais-barres-pierres/ /fr/zones/orgrimmar/;")
# renommage v41 -> v42 (corps), sans toucher aux classes CSS v41-
body_start = s.index('set -eEuo pipefail'); hd, bd = s[:body_start], s[body_start:]
bd = bd.replace('.v41-card', '@@C41@@').replace('V41={', '@@S41@@').replace('in V41:', '@@I41@@').replace('rollback-v$v', '@@RBV@@')
bd = bd.replace('W41_', 'W42_').replace('v41', 'v42').replace('V41', 'V42')
bd = bd.replace('@@C41@@', '.v41-card').replace('@@S41@@', 'V41={').replace('@@I41@@', 'in V41:').replace('@@RBV@@', 'rollback-v$v')
bd = bd.replace('HDR41', 'HDR42').replace('@@VQ@@', 'v41')
s = hd + bd
assert 'W41_' not in s and 'HDR41' not in s and 'V41TAR' not in s, [l for l in s.splitlines() if 'W41_' in l or 'HDR41' in l or 'V41TAR' in l][:5]
(D / 'update-v42.sh').write_text(s)
RB = f"""#!/bin/bash
# APERÇU du retour arrière v42 -> v40b.
# Ce fichier est une PREVIEW : le vrai /root/wow4ever-rollback-v42.sh est écrit par update-v42.sh
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
echo WOW4EVER_ROLLBACK_V42_DONE
"""
(D / 'rollback-v42.sh').write_text(RB)
json.dump({'archive_sha256': SUM, 'update_v42_sh_sha256': H(D / 'update-v42.sh'), 'wiki_v42': V42TAR, 'wiki_v40b': V40TAR, 'files': NALL, 'new': NNEW, 'changed': len(ch),
           'header_v42': HDR42, 'scope_pages': len(SCOPE)}, open(D / 'empreintes.json', 'w'), indent=1)
print(json.dumps({'archive': SUM, 'size': arc.stat().st_size, 'files': NALL, 'new': NNEW, 'changed': len(ch), 'v42': V42TAR, 'update': H(D / 'update-v42.sh')}))

#!/bin/bash
# update-v43d.sh : Wowkipedia v43b -> v43d (préparé le 25 novembre 2026, Europe/Paris). Paquet de TEST : ne pas lancer sans le « Oui » de Mathieu.
#   Article « Correctifs Forever » FR/EN : lots officiels des 17, 19, 20 et 23 novembre (news.blizzard 24315281, Kaivax
#   US 2403040 #12-#15 / EU 639885 #11-#14) et encadré « problèmes en cours » (lockboxes, monte épique) ; titre « du 5 au 23 novembre » / « November 5–23 » repris sur 79 pages (liens, accueils,
#   index de recherche). Nouvel article FR/EN « Repaire des Noiregueules (Blackmaw Hold) » (forums US 2419757 / EU 643759), avec lien vers la fiche du donjon.
#   Podcast officiel : épisode 8 (news.blizzard 24317086). Pages HTML et index de recherche seulement :
#   application, CSP, Caddyfile, CSS, JS, images, données inchangés. 471 pages modifiées (dont le compteur du menu Actualités : 16) ; 477 pages (+2).
# A lancer en root : bash update-v43d.sh   (journal détaillé dans /root/wow4ever-v43d-*.log)
# Exige la v43b en ligne (release connue : releases/20261118T005337 ; empreinte wiki c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517).
# Retour arrière automatique en cas d'échec ; manuel : bash /root/wow4ever-rollback-v43d.sh (-> releases/20261118T005337, v43b).
# Archive : /root/wow4ever-wiki-v43d.tar.gz si présente avec la bonne empreinte, sinon téléchargement depuis $W43D_URL.
set -eEuo pipefail
R="${W43D_ROOT:-}"
TS=$(date +%Y%m%dT%H%M%S)
HOST=wowkipedia.com
NAME=wow4ever-wiki-v43d.tar.gz
SUM=454a7aa35509e3fd09ff14a4a87a73088946c529af39b8b54e0aaab18c50a9db
URL="${W43D_URL:-}"
CF="${W43D_CADDYFILE:-$R/etc/caddy/Caddyfile}"
ENVF=$R/etc/wow4ever-community.env
DB=$R/var/lib/wow4ever-community/community.sqlite3
APP=$R/srv/wow4ever-app
RVF=$R/opt/raveforge
BK=$R/root/wow4ever-v43d-backup-$TS
LOG=$R/root/wow4ever-v43d-$TS.log
RBS=$R/root/wow4ever-rollback-v43d.sh
RBLIST="43b 43 42c 42b 42 41 40b 40 39 38 37 36 35 34 33 32 31 30"
SVC=wow4ever-community.service
V43BREL=releases/20261118T005337
V43BTAR_=c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517
V43DTAR=5875d6be00b3d058195bd8000f0ea194b323ab5dfb78e8bb7eb91858421e8dd4
TILE43B=a2d80c2b9bfc40b61a80fcaa3950dd189c626159fa62a162c7ac07c26a5d0303
V43BCSS=0ca08088faae203de08fc9ced2c21d4f8c5333d4210789c0a3c45d56668c1630
V43BJS=0003a3490c92d0c4ec6b8bd9298658181c9640de0e7c5741159af1550be9a414
V43BUI=4416a7dd51928e5267b3118312246b238bf27a2086c99e92322500deb1a73f67
APPSUM=d159df252913b0c569c644e1dfccaddfadb4e3ec2ba468a1f097cc38dc1bbda9
APP43D=d159df252913b0c569c644e1dfccaddfadb4e3ec2ba468a1f097cc38dc1bbda9
FCSS=ca7dc096b12c0a464b08004f2faa521f8b1d30505ac86d62e0bc25784b711397
SCHEMA=1e0eed47b71f9426cb3b216b7c2433a0c4ccabb79f905104cbb0f416f8b68a18
HDR40=392336a1ff7a793f6a4600e2c73680921f4fe7c0f10dac9205be619572471756
HDR42=392336a1ff7a793f6a4600e2c73680921f4fe7c0f10dac9205be619572471756
FOOT38=52e3d86c955882b7e64a3628f68493651fccc63aad1a35db1a5974688c34140f
CHANGED=   # rempli depuis la liste de l'archive (étape 2)
KEPT_FR=/fr/actualites/lancement-mondial-annonce/
POD_FR=/fr/actualites/le-podcast-officiel-wow-forever/
POD_EN=/en/news/the-official-wow-forever-podcast/
BM_FR=/fr/actualites/sanctions-abus-blackmaw-hold/
BM_EN=/en/news/blackmaw-hold-abuse-actions/
HOT_FR=/fr/actualites/correctifs-forever-5-et-6-novembre/
HOT_EN=/en/news/forever-hotfixes-november-5-6/
DISCORD=/fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/
DISCORD_EN=/en/news/official-wow-portal-room-discord-welcomes-forever-players/
NOTICE='Site indépendant et non officiel de Blizzard Entertainment.'
FOOT_FR='Illustrations : illustrations d’ambiance originales ou images du jeu © Blizzard Entertainment.'
FOOT_EN='Illustrations: original ambiance artwork or game images © Blizzard Entertainment.'
COUNTS='Zones|54;Créatures|14;Quêtes et progression|23;Objets|9;Collections|238;Métiers|28;Classes|11;Donjons et raids|26'

mkdir -p "$R/root"; umask 022
exec 3>&1 >>"$LOG" 2>&1
say(){ echo "$*"; echo "$*" >&3; }
STAGE=pre; OLD=; NEWREL=
die(){
  trap - ERR; set +e
  say "ERREUR: $*"
  if [ "$STAGE" = pre ]; then say "Rien n'a été modifié."; fi
  if [ "$STAGE" = prep ]; then [ -n "$NEWREL" ] && rm -rf "$NEWREL"; say "Site en ligne inchangé (sauvegardes : $BK)."; fi
  if [ "$STAGE" = live ]; then rollback "$*"; fi
  say "Journal : $LOG"; exit 1
}
trap 'die "commande en échec (ligne $LINENO)"' ERR
rollback(){
  trap - ERR; set +e
  say "Retour arrière vers la v43b ($OLD)…"
  if [ -n "$OLD" ]; then ln -sfn "$OLD" "$APP/current.rb" && mv -Tf "$APP/current.rb" "$APP/current"; fi
  systemctl restart $SVC || true
  if [ "$(readlink "$APP/current")" = "$OLD" ]; then say "Retour arrière OK : v43b ($OLD) restaurée, forum redémarré (Caddyfile jamais modifié)."
  else say "RETOUR ARRIERE INCOMPLET : lancer bash $RBS"; fi
  STAGE="done"
}
U(){ echo "${W43D_SCHEME:-https}://$HOST${W43D_PORT:-}$1"; }
RES=(--resolve "$HOST:${W43D_RPORT:-443}:127.0.0.1")
code(){ curl -s -o /dev/null -m 30 -w '%{http_code}' --resolve "$2:${W43D_RPORT:-443}:127.0.0.1" "${W43D_SCHEME:-https}://$2${W43D_PORT:-}$1" || true; }
get(){ curl -fsS -m 30 "${RES[@]}" "$(U "$1")"; }
hdr(){ curl -sS -o /dev/null -D - -m 30 "${RES[@]}" "$(U "$1")" | tr -d '\r'; }
sha(){ sha256sum | cut -d' ' -f1; }
fsum(){ [ -f "$1" ] && sha < "$1" || echo absent; }
rvf(){ [ -e "$RVF" ] && find "$RVF" -xdev -printf '%P %y %s %T@ %m %u\n' 2>/dev/null | LC_ALL=C sort | sha || echo absent; }
counts_ok(){ local h="$1" item IFS=';'; for item in $COUNTS; do grep -qF "<strong>${item%|*}</strong><span class=\"wk-count\">${item#*|}<" <<<"$h" || return 1; done; }

say "1/7 Vérifications"
[ -n "${W43D_TEST:-}" ] || [ "$(id -u)" = 0 ] || die "à lancer en root."
for c in python3 curl tar sha256sum systemctl find; do command -v "$c" >/dev/null || die "$c introuvable."; done
[ -f "$CF" ] && [ -f "$ENVF" ] || die "$CF ou $ENVF introuvable."   # existence seulement : .env jamais lu
CFSUM=$(sha < "$CF"); RVF0=$(rvf)
declare -A RBSUM; for v in $RBLIST; do RBSUM[$v]=$(fsum "$R/root/wow4ever-rollback-v$v.sh"); done
[ ! -e "$RBS" ] || die "$RBS existe déjà (v43d déjà tentée ?) : rien modifié."
[ -L "$APP/current" ] || die "$APP/current n'est pas un lien symbolique."
OLD=$(readlink "$APP/current"); OLDREL=$(cd "$APP" && cd "$OLD" && pwd -P)
case "$OLD" in releases/*) ;; *) die "cible inattendue pour current : $OLD";; esac
[ -f "$OLDREL/community/app.py" ] && [ -d "$OLDREL/wiki" ] && [ -x "$OLDREL/.venv/bin/gunicorn" ] || die "release actuelle incomplète ($OLD)."
BASE=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["tarball_sha256"])' "$OLDREL/tests/wiki-baseline.json") || die "référence du wiki illisible."
[ "$BASE" != "$V43DTAR" ] || die "la v43d est déjà en ligne ($OLD) : rien modifié."
[ -z "${W43D_EXPECT_OLD:-}" ] || [ "$OLD" = "$W43D_EXPECT_OLD" ] || die "la release en ligne est $OLD (attendu $W43D_EXPECT_OLD) : rien modifié."
[ -n "${W43D_TEST:-}" ] || [ "$OLD" = "$V43BREL" ] || die "la release en ligne est $OLD (attendu la v43b $V43BREL) : rien modifié."
[ "$BASE" = "$V43BTAR_" ] || die "la release actuelle n'est pas la v43b (wiki $BASE, attendu $V43BTAR_) : rien modifié."
[ -f "$OLDREL/community/selfcheck.py" ] && [ "$(sha < "$OLDREL/community/app.py")" = "$APPSUM" ] || die "application différente de la v43b : rien modifié."
[ "$(sha < "$OLDREL/wiki/v2.css")" = "$V43BCSS" ] || die "wiki/v2.css n'est pas celle de la v43b : rien modifié."
[ "$(sha < "$OLDREL/wiki/wk-header.js")" = "$V43BJS" ] || die "wiki/wk-header.js n'est pas celui de la v43b : rien modifié."
[ "$(sha < "$OLDREL/wiki/ui-core.mjs")" = "$V43BUI" ] || die "wiki/ui-core.mjs n'est pas celui de la v43b : rien modifié."
[ "$(sha < "$OLDREL/community/schema.sql")" = "$SCHEMA" ] || die "schema.sql inattendu : rien modifié."
[ "$(sha < "$OLDREL/community/templates/_v2_header.html")" = "$HDR40" ] || die "_v2_header.html n'est pas celui de la v43b : rien modifié."
[ "$(sha < "$OLDREL/community/templates/_v2_footer.html")" = "$FOOT38" ] || die "_v2_footer.html inattendu : rien modifié."
[ -f "$OLDREL/tools/content_blocks.py" ] || die "tools/content_blocks.py absent : rien modifié."
[ "$(sha < "$OLDREL/community/static/forum-v2.css")" = "$FCSS" ] || die "forum-v2.css inattendue : rien modifié."
[ -n "${W43D_TEST:-}" ] || systemctl is-active --quiet $SVC || die "$SVC inactif : rien modifié."
[ -n "${W43D_TEST:-}" ] || [ -f "$DB" ] || die "base $DB introuvable : rien modifié."
AVAIL=$(df -Pk "${APP:-/}" | awk 'NR==2{print $4}'); [ "${AVAIL:-0}" -ge 1024000 ] || die "moins de 1 Go libre."
say "   v43b reconnue (wiki $V43BTAR_, application, CSS, JS, schéma, en-tête, pied de page) : $OLD$([ "$OLD" = "$V43BREL" ] && echo ' (release connue)' || echo " (release connue : $V43BREL ; empreintes conformes)")"
if [ -z "${W43D_TEST:-}" ]; then
OTHERS=$(python3 - "$CF" <<'PY'
import re,sys
t=open(sys.argv[1]).read()
print(' '.join(sorted({m for m in re.findall(r'(?m)^([a-z0-9.-]+\.[a-z]{2,})[\s,{]',t) if m not in ('wow4ever.raveforge.eu','wowkipedia.com','www.wowkipedia.com')} | {'raveforge.eu','www.raveforge.eu'})))
PY
)
declare -A BEFORE; for h in $OTHERS; do BEFORE[$h]=$(code / "$h"); done
[ "$(code /fr/ $HOST)" = 200 ] || die "wowkipedia.com /fr/ ne répond pas 200 : rien modifié."
CSP0=$(hdr /fr/ | grep -i '^content-security-policy:' || true); [ -n "$CSP0" ] || die "pas de CSP sur /fr/ : rien modifié."
CSPC0=$(hdr /community/ | grep -i '^content-security-policy:' || true); [ -n "$CSPC0" ] || die "pas de CSP sur /community/ : rien modifié."
SM0=$(code /sitemap.xml $HOST); [ "$SM0" != 200 ] || die "/sitemap.xml répond 200 avant la mise à jour (inattendu) : rien modifié."
for p in /fr/ $KEPT_FR $POD_FR $DISCORD /community/; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200 avant : rien modifié."; done
[ "${BEFORE[raveforge.eu]}" = 401 ] && [ "${BEFORE[www.raveforge.eu]}" = 301 ] || die "raveforge.eu ${BEFORE[raveforge.eu]} / www ${BEFORE[www.raveforge.eu]} (401 / 301 attendus) : rien modifié."
fi
OLDURLS=$(python3 - "$OLDREL/wiki" <<'PY'
import sys
from pathlib import Path
w=Path(sys.argv[1])
print(' '.join(sorted('/' if x=='.' else f'/{x}/' for x in (p.relative_to(w).parent.as_posix() for p in w.rglob('index.html')))))
PY
)
[ "$(wc -w <<<"$OLDURLS")" = 475 ] || die "la release v43b n'a pas 475 pages : rien modifié."

say "2/7 Archive + SHA-256"
TMP=$R/root/$NAME
if [ -f "$TMP" ] && echo "$SUM  $TMP" | sha256sum -c - >/dev/null 2>&1; then say "   archive déjà présente ($TMP), empreinte conforme"
else
  [ -n "$URL" ] || die "archive absente de $TMP et W43D_URL non défini."
  curl -fsSL --retry 6 --retry-all-errors --retry-delay 3 -o "$TMP" "$URL" || die "téléchargement impossible ($URL)."
  echo "$SUM  $TMP" | sha256sum -c - >/dev/null 2>&1 || die "SHA-256 de l'archive incorrect."
  say "   archive téléchargée, SHA-256 conforme ($SUM)"
fi
LIST=$(tar -tzf "$TMP")
grep -vqE '^(wiki/[a-z0-9./_-]+|tests/(test_community\.py|wiki-baseline\.json))$' <<<"$LIST" && die "archive : fichier inattendu."
grep -qE '(^/|(^|/)\.\.(/|$))' <<<"$LIST" && die "archive : chemin dangereux."
TV=$(tar -tvzf "$TMP"); ! grep -qvE '^-' <<<"$TV" || die "archive : lien, dossier ou fichier spécial."
[ "$(wc -l <<<"$LIST")" = 478 ] || die "archive : 478 fichiers attendus."
CHANGED=$(tr '\n' ' ' <<<"$LIST")

say "3/7 Sauvegardes ($BK)"
mkdir -p "$BK"; chmod 700 "$BK"
tar -C "$OLDREL" --exclude=./.venv --exclude='__pycache__' -czf "$BK/release-v43b.tar.gz" .
if [ -z "${W43D_TEST:-}" ]; then
python3 - "$DB" "$BK/community.sqlite3" <<'PY' || die "sauvegarde de la base impossible."
import sqlite3,sys
src=sqlite3.connect(f'file:{sys.argv[1]}?mode=ro',uri=True); dst=sqlite3.connect(sys.argv[2])
src.backup(dst); dst.execute('pragma journal_mode=DELETE'); dst.close(); src.close()
PY
chmod 600 "$BK/community.sqlite3"
python3 - "$BK/community.sqlite3" <<'PY' || die "copie de la base illisible."
import sqlite3,sys
c=sqlite3.connect(f'file:{sys.argv[1]}?mode=ro',uri=True); assert c.execute('pragma integrity_check').fetchone()[0]=='ok'; assert c.execute('select max(version) from migrations').fetchone()[0]==3
PY
fi
cp -a "$CF" "$BK/Caddyfile"
echo "$OLD" > "$BK/current.target"
BKLIST=$(tar -tzf "$BK/release-v43b.tar.gz") || die "sauvegarde de la release illisible."
grep -qx './community/app.py' <<<"$BKLIST" && grep -qx './wiki/index.html' <<<"$BKLIST" || die "sauvegarde de la release incomplète."
STAGE=prep

say "4/7 Nouvelle release (copie de $OLD + actualités v43d)"
NEWREL=$APP/releases/$TS
mkdir -p "$NEWREL"
cp -a "$OLDREL"/. "$NEWREL/"
rm -rf "$NEWREL/.venv"
if [ -e "$OLDREL/.venv" ]; then ln -s "$OLDREL/.venv" "$NEWREL/.venv"; fi
tar -xzf "$TMP" -C "$NEWREL" --no-same-owner
python3 - "$NEWREL" "$OLDREL" "$V43DTAR" "$CHANGED" "$V43BCSS" "$V43BJS" "$V43BUI" "$APPSUM" <<'PY' || die "la nouvelle release ne diffère pas de la v43b par les seuls fichiers v43d attendus."
import hashlib,json,re,sys
from pathlib import Path
new,old,v43d=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
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
b=json.loads((new/'tests/wiki-baseline.json').read_text('utf-8')); assert b['tarball_sha256']==v43d
w=new/'wiki'; files={str(p.relative_to(w)) for p in w.rglob('*') if p.is_file()}
assert files==set(b['files']), sorted(files^set(b['files']))[:5]
bad=[k for k in sorted(files) if H(w/k)!=b['files'][k]]; assert not bad, bad[:5]
fp=hashlib.sha256(('\n'.join(f'{k}\t{b["files"][k]}' for k in sorted(files))+'\n').encode()).hexdigest(); assert fp==v43d, fp
html=[f for f in files if f.endswith('.html')]
assert len(html)==477 and not any('sitemap' in f for f in files)
for f in sorted(html):
    n=(w/f).read_text('utf-8')
    assert 'name="robots" content="noindex' in n, f
    assert not re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>|<style|\sstyle="',n), f
for f in sorted(html):
    n=(w/f).read_text('utf-8'); assert 'du 5 au 16 novembre' not in n and 'November 5–16' not in n and 'du 5 au 20 novembre' not in n and 'November 5–20' not in n, f
hot=(w/'fr/actualites/correctifs-forever-5-et-6-novembre/index.html').read_text('utf-8'); en=(w/'en/news/forever-hotfixes-november-5-6/index.html').read_text('utf-8')
assert 'Correctifs Forever du 5 au 23 novembre' in hot and 'Forever hotfixes, November 5–23' in en
for p in (hot,en):
    for d in ('nov17','nov19','nov20','nov23'): assert f'id="details-{d}"' in p, d
    assert 'id="problemes-en-cours"' in p and 'id="source-30"' in p and 'id="source-31"' not in p
for l in ('fr','en'):
    d=json.loads((w/f'search-detail-{l}.json').read_text('utf-8')); assert d['lang']==l and len(d['pages'])==221 and len(d['r'])>15000
si=json.loads((w/'search-index.json').read_text('utf-8')); assert len(si['entries'])==221
print('pages_html_modifiees',len([k for k in diff if HTML.fullmatch(k)]),'nouvelles',len(NEW))
PY
say "   v43d : article Correctifs Forever (lots des 17, 19, 20 et 23 novembre, encadré « problèmes en cours », titre « du 5 au 23 novembre » sur 79 pages), article Blackmaw Hold FR/EN avec lien vers la fiche du donjon, podcast épisode 8, menu Actualités 16 ; 471 pages HTML et index de recherche mis à jour ; application, CSS, JS et images inchangés"
[ -n "${W43D_TEST:-}" ] || chown -R root:root "$NEWREL"
chmod -R u=rwX,go=rX "$NEWREL"
if [ -z "${W43D_TEST:-}" ]; then
RUNAPP=(runuser -u wow4ever-app --)
( cd "$NEWREL" && "${RUNAPP[@]}" env -u SECRET_KEY HOME=/tmp TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests >"$R/root/wow4ever-v43d-tests-$TS.txt" 2>&1 ) \
  || { rm -rf "$NEWREL"; die "tests de la nouvelle release en échec (voir $R/root/wow4ever-v43d-tests-$TS.txt)."; }
say "   tests OK ($(grep -oE '^Ran [0-9]+ tests' "$R/root/wow4ever-v43d-tests-$TS.txt" || true))"
fi
cat > "$RBS" <<RB
# Retour arrière v43d -> v43b : release $OLD (v43b, $V43BREL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v43d.
# N'écrase aucun rollback-v43b.sh, v43.sh, v42c.sh, v42b.sh, v42.sh … rollback-v30.sh. Sauvegarde : $BK
set -euo pipefail
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || { echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V43D_DONE
RB
chmod 700 "$RBS"

# Contrôles du wiki après bascule (aussi lancés en mode test avec W43D_TEST_POST=1 contre un serveur local).
# Aucun « curl | head/grep » : sous pipefail, un lecteur qui s'arrête tôt fait échouer curl (code 23).
json_ok(){
  local f="$R/root/wow4ever-v43d-check-$2.json" n
  for n in $(seq 1 10); do
    if curl -fsS --compressed -m 60 "${RES[@]}" -o "$f" "$(U "$1")" && python3 - "$f" "$2" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
assert d.get('v')==1 and d.get('lang')==sys.argv[2] and len(d.get('r',[]))>15000 and len(d.get('pages',[]))==221
PY
    then rm -f "$f"; return 0; fi
    sleep 2
  done
  rm -f "$f"; return 1
}
map_ok(){
  local f="$R/root/wow4ever-v43d-check-carte.json" n
  for n in $(seq 1 5); do
    if curl -fsS --compressed -m 60 "${RES[@]}" -o "$f" "$(U '/assets/carte/1411/donnees.json?v=43')" && python3 - "$f" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
assert d.get('status')=='a-confirmer' and len(d.get('pins',[]))>100 and len(d.get('quests',{}))>10
PY
    then rm -f "$f"; return 0; fi
    sleep 2
  done
  rm -f "$f"; return 1
}
tile_ok(){
  local f="$R/root/wow4ever-v43d-check-tuile.webp" n
  for n in $(seq 1 5); do
    if curl -fsS -m 60 "${RES[@]}" -o "$f" "$(U '/assets/carte/1411/r1-c2.webp?v=43b')" && [ "$(sha < "$f")" = "$TILE43B" ]; then rm -f "$f"; return 0; fi
    sleep 2
  done
  rm -f "$f"; return 1
}
wiki_checks(){
[ "$(code /fr/ $HOST)" = 200 ] || die "/fr/ ne répond pas 200."
[ "$(code /en/ $HOST)" = 200 ] || die "/en/ ne répond pas 200."
HF=$(get /fr/); counts_ok "$HF" || die "compteurs de l'accueil FR inattendus."
grep -q 'class="v40-home"' <<<"$HF" || die "accueil FR sans structure v43b."
grep -q 'v2-hero' <<<"$HF" && die "accueil FR : bannière encore présente."
HE=$(get /en/); grep -q 'class="v40-home"' <<<"$HE" || die "accueil EN sans structure v43b."
grep -qF '<strong>Zones</strong><span class="wk-count">54<' <<<"$HE" || die "compteurs de l\'accueil EN inattendus."
grep -qF '<strong>Dungeons and raids</strong><span class="wk-count">26<' <<<"$HE" || die "compteurs de l\'accueil EN inattendus."
[ "$(code /fr/zones/mulgore/ $HOST)" = 200 ] || die "/fr/zones/mulgore/ ne répond pas 200."
for p in /search-detail-fr.json /search-detail-en.json /search-index.json /ui-core.mjs /wk-header.js; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
[ "$(code /search-detail-de.json $HOST)" = 404 ] || die "/search-detail-de.json devrait répondre 404."
for l in fr en; do json_ok /search-detail-$l.json $l || die "index détaillé $l illisible (JSON, langue ou taille)."; done
grep -qF 'wk-header.js?v=42c"' <<<"$HF" && grep -qF 'v2.css?v=42c"' <<<"$HF" || die "accueil FR sans les adresses ?v=42c."
grep -qF 'wk-header.js?v=42c"' <<<"$HE" || die "accueil EN sans les adresses ?v=42c."
for p in '/wk-header.js?v=42c' '/ui-core.mjs?v=42c' '/v2.css?v=42c' '/fr/wiki/?q=baine' '/en/wiki/?q=boar'; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
HJ=$(get '/wk-header.js?v=42c'); grep -qF 'wk-search-inline' <<<"$HJ" && grep -qF "ui-core.mjs?v=42c" <<<"$HJ" || die "wk-header.js servi n'est pas celui de la v43b (inchangé en v43d)."
HC=$(get '/v2.css?v=42c'); grep -qF '.wk-search-inline' <<<"$HC" || die "v2.css servie n'est pas celle de la v43b (inchangée en v43d)."
HW=$(get /fr/wiki/); grep -qF 'id="wk-search-input"' <<<"$HW" && grep -qF 'wk-header.js?v=42c"' <<<"$HW" || die "page « Tout le wiki » FR inattendue."
HM=$(get /fr/zones/mulgore/); grep -qF 'id="r-baine-bloodhoof"' <<<"$HM" || die "ancre r-baine-bloodhoof absente de Mulgore."
grep -qF 'Image du jeu © Blizzard Entertainment' <<<"$HM" || die "crédit image du jeu manquant sur Mulgore."
for p in $KEPT_FR $POD_FR $POD_EN $DISCORD $DISCORD_EN /fr/wiki/ /en/wiki/ /community/ /fr/objets/collections/ /en/items/collections/ /fr/objets/montures/ /assets/icone-jeu-3753812.webp /fr/metiers/materiaux/ /en/professions/materials/ /fr/metiers/materiaux-minerais-barres-pierres/ /fr/zones/orgrimmar/; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
HD=$(get /fr/zones/durotar/); grep -qF 'id="carte-interactive"' <<<"$HD" && grep -qF 'wk-map.js?v=43"' <<<"$HD" && grep -qF 'id="quetes-liste"' <<<"$HD" || die "Durotar FR : carte ou quêtes v43d absentes."
HDE=$(get /en/zones/durotar/); grep -qF 'id="carte-interactive"' <<<"$HDE" && grep -qF 'wk-map.css?v=43"' <<<"$HDE" || die "Durotar EN : carte v43d absente."
for p in '/wk-map.js?v=43' '/wk-map.css?v=43' '/assets/carte/1411/r0-c0.webp' '/fr/sources-et-licences/' '/en/sources-and-licences/' '/fr/sources-et-licences/donnees-polestar.json.gz' '/en/sources-and-licences/objets-classic.json.gz' '/fr/zones/mont-hyjal/' '/en/zones/stormwind-city/' '/fr/zones/orgrimmar/'; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
for p in '/assets/carte/1411/manifest.json' '/assets/carte/1411/../../community/app.py' '/fr/sources-et-licences/autre.json.gz'; do [ "$(code "$p" $HOST)" = 404 ] || die "$p devrait répondre 404."; done
HMJ=$(get '/wk-map.js?v=43'); grep -qF 'data-map' <<<"$HMJ" || die "wk-map.js servi inattendu."
HS=$(get /fr/sources-et-licences/); grep -qF 'content="noindex' <<<"$HS" && grep -qF 'GPL' <<<"$HS" && grep -qF 'data-wk-header' <<<"$HS" || die "page « Sources et licences » inattendue."
map_ok || die "données de carte de Durotar illisibles (JSON ou repères)."
grep -qF 'assets/carte/1411/r1-c2.webp?v=43b"' <<<"$HD" && grep -qF 'calques des zones explorées' <<<"$HD" || die "Durotar FR : tuiles ?v=43b ou crédit v43b absents."
grep -qF '.webp?v=43b"' <<<"$HDE" && grep -qF 'explored-area layers' <<<"$HDE" || die "Durotar EN : tuiles ?v=43b ou crédit v43b absents."
HS2=$(get /en/sources-and-licences/); grep -qF 'WorldMapOverlay' <<<"$HS2" || die "page Sources EN : crédit des cartes non mis à jour."
tile_ok || die "tuile explorée de Durotar non servie (empreinte inattendue)."
for p in '/assets/carte/1429/r1-c1.webp?v=43b' '/assets/carte/1454/r0-c0.webp?v=43b' '/fr/zones/foret-d-elwynn/' '/en/zones/elwynn-forest/'; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
for p in $BM_FR $BM_EN $HOT_FR $HOT_EN; do [ "$(code "$p" $HOST)" = 200 ] || die "$p ne répond pas 200."; done
HB=$(get $BM_FR); grep -qF 'Repaire des Noiregueules' <<<"$HB" && grep -qF 'content="noindex' <<<"$HB" && grep -qF 'data-wk-header' <<<"$HB" && ! grep -qF '[src:' <<<"$HB" || die "article Blackmaw FR inattendu."
HBE=$(get $BM_EN); grep -qF 'Blackmaw Hold' <<<"$HBE" && grep -qF 'dungeons-raids/blackmaw-hold/' <<<"$HBE" && grep -qF 'us.forums.blizzard.com/en/wow/t/2419757' <<<"$HBE" || die "article Blackmaw EN inattendu."
HH=$(get $HOT_FR); grep -qF 'Correctifs Forever du 5 au 23 novembre' <<<"$HH" && grep -qF 'id="details-nov23"' <<<"$HH" && grep -qF 'id="problemes-en-cours"' <<<"$HH" && grep -qF 'id="source-30"' <<<"$HH" || die "article Correctifs FR sans les lots v43d."
HHE=$(get $HOT_EN); grep -qF 'Forever hotfixes, November 5–23' <<<"$HHE" && grep -qF 'id="details-nov23"' <<<"$HHE" && grep -qF 'id="problemes-en-cours"' <<<"$HHE" || die "article Correctifs EN sans les lots v43d."
HP=$(get $POD_FR); grep -qF 'news.blizzard.com/fr-fr/article/24317086' <<<"$HP" && grep -qF 'id="source-8"' <<<"$HP" || die "podcast FR sans l'épisode 8."
HPE=$(get $POD_EN); grep -qF 'news.blizzard.com/en-us/article/24317086' <<<"$HPE" || die "podcast EN sans l'épisode 8."
grep -qF 'actualites/sanctions-abus-blackmaw-hold/' <<<"$HF" || die "accueil FR sans l'article Blackmaw."
grep -qF 'news/blackmaw-hold-abuse-actions/' <<<"$HE" || die "accueil EN sans l'article Blackmaw."
HSI=$(get /search-index.json); grep -qF 'sanctions-abus-blackmaw-hold' <<<"$HSI" || die "search-index.json sans l'article Blackmaw."
}

say "5/7 Bascule : current -> releases/$TS"
STAGE=live
ln -sfn "releases/$TS" "$APP/current.new" && mv -Tf "$APP/current.new" "$APP/current"
if [ -z "${W43D_TEST:-}" ]; then
systemctl restart $SVC
OK=; for _ in $(seq 1 20); do
  HZ=$(curl -fsS -m 3 -H "Host: $HOST" http://127.0.0.1:8014/healthz 2>/dev/null || true)
  if grep -q '"schema": *3' <<<"$HZ" && grep -q '"status": *"ok"' <<<"$HZ"; then OK=1; break; fi; sleep 1
done
[ -n "$OK" ] || die "l'application ne répond pas (schéma 3 attendu) sur 127.0.0.1:8014."
[ -z "${W43D_TEST_FAIL:-}" ] || die "échec simulé (test)."

say "6/7 Contrôles après bascule"
wiki_checks
CSP=$(hdr /fr/le-jeu/ | grep -i '^content-security-policy:' || true); [ "$CSP" = "$CSP0" ] || die "CSP du wiki différente."
CSPC=$(hdr /community/ | grep -i '^content-security-policy:' || true); [ "$CSPC" = "$CSPC0" ] || die "CSP du forum différente."
[ "$(code /sitemap.xml $HOST)" = "$SM0" ] || die "/sitemap.xml a changé."
[ "$(sha < "$CF")" = "$CFSUM" ] || die "Caddyfile modifié (inattendu)."
for v in $RBLIST; do [ "$(fsum "$R/root/wow4ever-rollback-v$v.sh")" = "${RBSUM[$v]}" ] || die "rollback-v$v.sh a été modifié (inattendu)."; done
[ "$(rvf)" = "$RVF0" ] || die "/opt/raveforge a changé (inattendu)."
say "   /account/ et CSP / sitemap / Caddyfile / raveforge / rollbacks antérieurs inchangés"
L=; for h in $OTHERS; do A=$(code / "$h"); L="$L $h ${BEFORE[$h]}>$A"; [ "$A" = "${BEFORE[$h]}" ] || die "$h a changé (${BEFORE[$h]} -> $A)."; done
[ "$(code / raveforge.eu)" = 401 ] && [ "$(code / www.raveforge.eu)" = 301 ] || die "raveforge.eu / www.raveforge.eu ne répondent plus 401 / 301."
say "  $L (autres sites inchangés)"
fi
if [ -n "${W43D_TEST:-}" ] && [ -n "${W43D_TEST_POST:-}" ]; then
  say "6/7 (test) Contrôles du wiki après bascule (serveur local $(U /))"
  wiki_checks
  [ -z "${W43D_TEST_FAIL:-}" ] || die "échec simulé (test)."
  say "   contrôles du wiki après bascule OK (test)"
fi
STAGE="done"; trap - ERR

say "7/7 Terminé (paquet appliqué localement${W43D_TEST:+ — mode test, pas de bascule production})"
say "Sauvegardes : $BK · Retour arrière : bash $RBS (-> $OLD / $V43BREL)"
say WOW4EVER_UPDATE_V43D_DONE

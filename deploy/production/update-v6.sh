#!/bin/bash
# update-v6.sh : wow4ever.raveforge.eu -> wiki v6 (6 actualités du 30/10) + communauté en lecture publique.
# A lancer en root : bash update-v6.sh   (sortie courte ; journal détaillé dans /root/wow4ever-v6-*.log)
# Remplace UNIQUEMENT le bloc Caddy wow4ever.raveforge.eu (autres blocs vérifiés identiques octet par octet).
# Aucun secret affiché. Retour arrière automatique en cas d'échec ; manuel : bash /root/wow4ever-rollback-v6.sh
set -eEuo pipefail
R="${W6_ROOT:-}"                                   # préfixe de test local uniquement (vide en production)
TS=$(date +%Y%m%dT%H%M%S)
HOST=wow4ever.raveforge.eu
NAME=wow4ever-wiki-v6.tar.gz
SUM=0406474507d1c81918f15ac1e5aa0190f36699a116bdd16ba697f6f841e0b7ff
URL="${W6_URL:-https://github.com/eyna4ever/wow4ever/releases/download/deploy-v5-20261030/$NAME}"
CF="${W6_CADDYFILE:-$R/etc/caddy/Caddyfile}"
CADDY="${W6_CADDY:-caddy}"
APP=$R/srv/wow4ever-app
HASHF=$R/root/wow4ever-basicauth.hash
TOOL=$R/root/wow4ever-caddy-block-v6.py
BK=$R/root/wow4ever-v6-backup-$TS
LOG=$R/root/wow4ever-v6-$TS.log
RBS=$R/root/wow4ever-rollback-v6.sh
SVC=wow4ever-community.service
NEWS=/fr/actualites/lancement-mondial-le-4-novembre-ce-qu-il-faut-savoir/
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
  say "RETOUR ARRIERE automatique ($1)"
  if [ -n "$OLD" ]; then ln -sfn "$OLD" "$APP/current.rb" && mv -Tf "$APP/current.rb" "$APP/current"; fi
  [ -f "$BK/Caddyfile" ] && cat "$BK/Caddyfile" > "$CF"
  systemctl reload caddy; systemctl restart $SVC; sleep 2
  if cmp -s "$BK/Caddyfile" "$CF" && [ "$(readlink "$APP/current")" = "$OLD" ]; then say "Retour arrière OK : wiki ($OLD) et Caddyfile restaurés."
  else say "RETOUR ARRIERE INCOMPLET : lancer bash $RBS"; fi
  STAGE=done
}
code(){ curl -s -o /dev/null -m 10 -w '%{http_code}' --resolve "$2:${W6_RPORT:-443}:127.0.0.1" "${W6_SCHEME:-https}://$2${W6_PORT:-}$1" || true; }

say "1/6 Vérifications"
[ -n "${W6_TEST:-}" ] || [ "$(id -u)" = 0 ] || die "à lancer en root."
for c in python3 curl tar sha256sum "$CADDY" systemctl; do command -v "$c" >/dev/null || die "$c introuvable."; done
[ -f "$CF" ] || die "$CF introuvable."
[ -s "$HASHF" ] || die "empreinte $HASHF absente."
[ -L "$APP/current" ] || die "$APP/current n'est pas un lien symbolique."
OLD=$(readlink "$APP/current"); OLDREL=$(cd "$APP" && cd "$OLD" && pwd -P)
case "$OLD" in releases/*) ;; *) die "cible inattendue pour current : $OLD";; esac
[ -f "$OLDREL/community/app.py" ] && [ -d "$OLDREL/wiki" ] && [ -x "$OLDREL/.venv/bin/gunicorn" ] || die "release actuelle incomplète ($OLD)."
systemctl is-active --quiet $SVC || die "$SVC inactif : rien modifié."
AVAIL=$(df -Pk "$APP" | awk 'NR==2{print $4}'); [ "${AVAIL:-0}" -ge 512000 ] || die "moins de 500 Mo libres."
VER=$("$CADDY" version | grep -oE 'v2\.[0-9]+' | head -1 | cut -d. -f2 || true); DIR=basic_auth; [ "${VER:-0}" -ge 8 ] || DIR=basicauth
cat > "$TOOL" <<'PYEOF'
#!/usr/bin/env python3
"""Replace ONLY the top-level `wow4ever.raveforge.eu { ... }` block of a Caddyfile.

  extract CADDYFILE                      -> print the current wow4ever block
  render  DIRECTIVE HASHFILE OUT         -> write the new v6 block (basic_auth|basicauth)
  hashcheck CADDYFILE HASHFILE           -> exit 0 if the current block uses that hash, 3 otherwise
  replace CADDYFILE NEWBLOCK OUT         -> write CADDYFILE with only that block replaced
Every other byte (global options, Raveforge and any other site) is asserted identical.
"""
import hashlib, re, sys

HOST = 'wow4ever.raveforge.eu'
MARK = '# wow4ever-v6 : bloc géré par update-v6.sh (ne pas éditer à la main)'


def die(msg):
    sys.stderr.write('ERREUR: ' + msg + '\n')
    sys.exit(2)


def blocks(text):
    """Top-level segments as (header_start, close_end, header). Handles quotes, backticks, comments."""
    out, depth, i, n = [], 0, 0, len(text)
    seg_start, header_start = 0, None
    quote = None
    while i < n:
        c = text[i]
        if quote:
            if c == '\\' and quote == '"':
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in '"`':
            quote = c
        elif c == '#' and (i == 0 or text[i - 1] in ' \t\n'):
            j = text.find('\n', i)
            i = n if j < 0 else j
            continue
        elif c == '{':
            if depth == 0:
                header_start = seg_start
                header = text[seg_start:i]
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                die('accolade fermante orpheline')
            if depth == 0:
                out.append((header_start, i + 1, header))
                seg_start = i + 1
        elif c == '\n' and depth == 0:
            seg_start = i + 1
        i += 1
    if depth != 0 or quote:
        die('Caddyfile déséquilibré (accolades ou guillemets)')
    return out


def addresses(header):
    lines = [l for l in header.split('\n') if l.strip() and not l.strip().startswith('#')]
    return [a for a in re.split(r'[\s,]+', ' '.join(lines)) if a]


def is_ours(header):
    addrs = [re.sub(r'^https?://', '', a) for a in addresses(header)]
    addrs = [re.sub(r':443$', '', a) for a in addrs]
    if HOST in addrs:
        if addrs != [HOST]:
            die(f'le bloc {HOST} partage son en-tête avec d’autres adresses : {addrs} (arrêt, rien modifié)')
        return True
    return False


def find(text):
    found = [b for b in blocks(text) if is_ours(b[2])]
    if len(found) != 1:
        die(f'{len(found)} bloc(s) {HOST} trouvé(s) au niveau racine du Caddyfile (attendu : 1). Rien modifié.')
    s, e, h = found[0]
    s += len(h) - len(h.lstrip('\n'))  # keep preceding blank lines outside the block
    return s, e


def others(text):
    return [(text[s:e]) for s, e, h in blocks(text) if not is_ours(h)]


NEW = '''wow4ever.raveforge.eu {
	MARK
	encode zstd gzip

	# Espace privé de la communauté (connexion Discord, compte, notifications, modération) : mot de passe HTTP.
	@private path /auth/* /account /account/* /notifications /notifications/* /moderation /moderation/*
	handle @private {
		DIRECTIVE {
			mathieu HASH
		}
		reverse_proxy 127.0.0.1:8014 {
			header_up X-Forwarded-For {remote_host}
		}
	}

	# Forums en lecture publique et politique de confidentialité (application Flask sur loopback), sans mot de passe.
	@app path /community /community/* /privacy /privacy/*
	handle @app {
		reverse_proxy 127.0.0.1:8014 {
			header_up X-Forwarded-For {remote_host}
		}
	}

	# Wiki statique public (build v6 : 28/10 + 6 actualités du 30/10, liens communauté), servi directement par Caddy.
	handle {
		root * /srv/wow4ever-app/current/wiki
		header {
			Content-Security-Policy "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'"
			X-Content-Type-Options "nosniff"
			Referrer-Policy "strict-origin-when-cross-origin"
			X-Frame-Options "DENY"
			Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
			Cross-Origin-Opener-Policy "same-origin"
			Strict-Transport-Security "max-age=31536000"
			X-Robots-Tag "noindex, nofollow"
			-Server
		}
		@mjs path *.mjs
		header @mjs Content-Type "text/javascript; charset=utf-8"
		@assets path /assets/*
		header @assets Cache-Control "public, max-age=604800"
		file_server {
			hide .*
		}
	}
	# Pas de directive log : aucun journal d'accès pour ce site (callback OAuth, IP).
}'''


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'extract':
        text = open(sys.argv[2], encoding='utf-8').read()
        s, e = find(text)
        sys.stdout.write(text[s:e] + '\n')
    elif mode == 'render':
        directive, hashfile, out = sys.argv[2:5]
        if directive not in ('basic_auth', 'basicauth'):
            die('directive inconnue')
        h = open(hashfile, encoding='utf-8').read().strip()
        if not re.fullmatch(r'\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}|\$argon2id\$[^\s{}]+', h):
            die('empreinte de mot de passe invalide')
        open(out, 'w', encoding='utf-8').write(NEW.replace('MARK', MARK).replace('DIRECTIVE', directive).replace('HASH', h) + '\n')
    elif mode == 'hashcheck':
        text = open(sys.argv[2], encoding='utf-8').read()
        s, e = find(text)
        h = open(sys.argv[3], encoding='utf-8').read().strip()
        sys.exit(0 if re.search(r'(?m)^\s*mathieu\s+' + re.escape(h) + r'\s*$', text[s:e]) else 3)
    elif mode == 'replace':
        src, newfile, out = sys.argv[2:5]
        raw = open(src, 'rb').read()
        text = raw.decode('utf-8')
        new_block = open(newfile, encoding='utf-8').read().rstrip('\n')
        s, e = find(text)
        old_block = text[s:e]
        if re.search(r'(?m)^\s*log\b', old_block):
            sys.stderr.write('ATTENTION: l’ancien bloc wow4ever avait une directive log ; le nouveau bloc n’en a pas.\n')
        result = text[:s] + new_block + text[e:]
        # Byte-identical guarantees outside the replaced block.
        pre, post, r = text[:s].encode(), text[e:].encode(), result.encode()
        if not (raw.startswith(pre) and raw.endswith(post) and r.startswith(pre) and r.endswith(post)):
            die('contrôle octet par octet hors bloc échoué : arrêt (rien écrit)')
        before, after = others(text), others(result)
        if before != after:
            die('les autres blocs ont changé : arrêt (rien écrit)')
        rave = [b for b in before if 'raveforge' in b.split('{', 1)[0].lower()]
        digest = lambda xs: hashlib.sha256('\x00'.join(xs).encode()).hexdigest()[:16]
        find(result)  # still exactly one wow4ever block
        open(out, 'w', encoding='utf-8').write(result)
        print(f'OK: bloc wow4ever remplacé ; {len(before)} autre(s) bloc(s) identiques '
              f'(dont {len(rave)} Raveforge, empreinte {digest(rave)} avant = {digest([b for b in after if "raveforge" in b.split("{",1)[0].lower()])} après).')
    else:
        die(__doc__)


if __name__ == '__main__':
    main()
PYEOF
python3 "$TOOL" extract "$CF" > "$R/root/wow4ever-block-pre-v6-$TS.caddy"
grep -qE 'wow4ever-v[56] :' "$R/root/wow4ever-block-pre-v6-$TS.caddy" || die "le bloc actuel n'est pas le bloc v5/v6 attendu."
python3 "$TOOL" hashcheck "$CF" "$HASHF" || say "ATTENTION: l'empreinte du fichier diffère de celle du bloc actuel ; le fichier $HASHF est utilisé."
python3 "$TOOL" render "$DIR" "$HASHF" "$R/root/wow4ever-v6-block.caddy"
python3 "$TOOL" replace "$CF" "$R/root/wow4ever-v6-block.caddy" "$CF.v6-new" >/dev/null
"$CADDY" validate --config "$CF.v6-new" --adapter caddyfile >/dev/null 2>&1 || { rm -f "$CF.v6-new"; die "caddy validate refuse le nouveau bloc."; }
rm -f "$CF.v6-new"
OTHERS=$(python3 - "$CF" <<'PY'
import re,sys
t=open(sys.argv[1]).read()
print(' '.join(sorted({m for m in re.findall(r'(?m)^([a-z0-9.-]+\.[a-z]{2,})[\s,{]',t) if m!='wow4ever.raveforge.eu'} | {'raveforge.eu','www.raveforge.eu'})))
PY
)
declare -A BEFORE; for h in $OTHERS; do BEFORE[$h]=$(code / "$h"); done
echo "avant : $(for h in $OTHERS; do printf '%s=%s ' "$h" "${BEFORE[$h]}"; done)"

say "2/6 Téléchargement + SHA-256"
TMP=$R/root/$NAME
curl -fsSL --retry 6 --retry-all-errors --retry-delay 3 -o "$TMP" "$URL" || die "téléchargement impossible."
echo "$SUM  $TMP" | sha256sum -c - >/dev/null 2>&1 || die "SHA-256 de l'archive incorrect."
LIST=$(tar -tzf "$TMP")
echo "$LIST" | grep -vqE '^(wiki/.*|wiki/|tests/|tools/|docs/|tests/test_community\.py|tests/wiki-baseline\.json|tools/integrate_wiki\.py|docs/MERGE\.md)$' && die "archive : fichier inattendu."
echo "$LIST" | grep -qE '(^/|(^|/)\.\.(/|$))' && die "archive : chemin dangereux."

say "3/6 Sauvegardes ($BK)"
mkdir -p "$BK"; chmod 700 "$BK"
tar -C "$OLDREL" -czf "$BK/wiki.tar.gz" wiki
cp -a "$CF" "$BK/Caddyfile"; cp -a "$CF" "$CF.bak-v6-$TS"
echo "$OLD" > "$BK/current.target"
STAGE=prep

say "4/6 Nouvelle release (copie de $OLD, wiki remplacé)"
[ ! -e "$APP/releases/$TS" ] || die "$APP/releases/$TS existe déjà."; NEWREL=$APP/releases/$TS
cp -a "$OLDREL" "$NEWREL"
# Le venv contient le chemin absolu de la release : on le réécrit vers la nouvelle.
{ grep -rlIF "$OLDREL" "$NEWREL/.venv/bin" "$NEWREL/.venv/pyvenv.cfg" 2>/dev/null || true; } | while read -r f; do sed -i "s#$OLDREL#$NEWREL#g" "$f"; done
! grep -rqIF "$OLDREL" "$NEWREL/.venv/bin" || die "chemins du venv non réécrits."
rm -rf "$NEWREL/wiki"
tar -xzf "$TMP" -C "$NEWREL" --no-same-owner
find "$NEWREL" -name __pycache__ -prune -exec rm -rf {} +
W=$NEWREL/wiki
[ -f "$W$NEWS/index.html" ] || die "page d'actualité absente du nouveau wiki."
[ -z "$(find "$W" -name '*.html' -exec grep -L 'Site indépendant et non officiel de Blizzard Entertainment.' {} + || true)" ] || die "mention Blizzard manquante."
! grep -rqE 'forever-news-beta"|forever-class-priest' "$W" || die "brouillon AC2/CL3 présent."
[ -n "${W6_TEST:-}" ] || chown -R root:root "$NEWREL"
chmod -R u=rwX,go=rX "$NEWREL"
RUNAPP=(); [ -n "${W6_TEST:-}" ] || RUNAPP=(runuser -u wow4ever-app --)
( cd "$NEWREL" && "${RUNAPP[@]}" env -u SECRET_KEY HOME=/tmp TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests >"$R/root/wow4ever-v6-tests-$TS.txt" 2>&1 ) \
  || { rm -rf "$NEWREL"; die "tests de la nouvelle release en échec (voir $R/root/wow4ever-v6-tests-$TS.txt)."; }
say "   tests OK ($(grep -oE '^Ran [0-9]+ tests' "$R/root/wow4ever-v6-tests-$TS.txt" || true))"
cat > "$RBS" <<RB
#!/bin/bash
# Retour arrière v6 : release $OLD + Caddyfile d'avant v6 ($BK).
set -euo pipefail
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
cp $BK/Caddyfile $CF.rollback-v6-new
$CADDY validate --config $CF.rollback-v6-new --adapter caddyfile >/dev/null 2>&1 || { rm -f $CF.rollback-v6-new; echo "ERREUR: caddy validate refuse la sauvegarde"; exit 1; }
cp -a $CF $CF.before-rollback-v6-\$(date +%Y%m%dT%H%M%S) && cat $CF.rollback-v6-new > $CF && rm -f $CF.rollback-v6-new
systemctl reload caddy
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V6_DONE
RB
chmod 700 "$RBS"

say "5/6 Bascule : current -> releases/$TS, application, Caddy"
STAGE=live
ln -sfn "releases/$TS" "$APP/current.new" && mv -Tf "$APP/current.new" "$APP/current"
systemctl restart $SVC
OK=; for i in $(seq 1 20); do
  if curl -fsS -m 3 -H "Host: $HOST" http://127.0.0.1:8014/healthz 2>/dev/null | grep -q '"status": *"ok"'; then OK=1; break; fi; sleep 1
done
[ -n "$OK" ] || die "l'application ne répond pas sur 127.0.0.1:8014."
RES=$(python3 "$TOOL" replace "$CF" "$R/root/wow4ever-v6-block.caddy" "$CF.v6-new") || die "remplacement du bloc refusé."
say "   $RES"
"$CADDY" validate --config "$CF.v6-new" --adapter caddyfile >/dev/null 2>&1 || die "caddy validate refuse le nouveau Caddyfile."
cat "$CF.v6-new" > "$CF"; rm -f "$CF.v6-new"
"$CADDY" validate --config "$CF" --adapter caddyfile >/dev/null 2>&1 || die "validation après copie."
systemctl reload caddy || die "reload Caddy en échec."
sleep 3
[ -z "${W6_TEST_FAIL:-}" ] || die "échec simulé (test)."

say "6/6 Contrôles finaux"
FR=$(code /fr/ $HOST); NW=$(code $NEWS $HOST); CO=$(code /community/ $HOST); AC=$(code /account/ $HOST); PR=$(code /privacy/ $HOST)
say "   /fr/ $FR · actu $NW · /community/ $CO · /privacy/ $PR · /account/ $AC (attendu 200 200 200 200 401)"
[ "$FR" = 200 ] && [ "$NW" = 200 ] && [ "$CO" = 200 ] && [ "$PR" = 200 ] && [ "$AC" = 401 ] || die "contrôle wow4ever en échec."
L=; for h in $OTHERS; do A=$(code / "$h"); L="$L $h ${BEFORE[$h]}>$A"; [ "$A" = "${BEFORE[$h]}" ] || die "$h a changé (${BEFORE[$h]} -> $A)."; done
say "  $L (raveforge.eu 401 / www 301 attendus)"
[ "${BEFORE[raveforge.eu]}" = 401 ] && [ "${BEFORE[www.raveforge.eu]}" = 301 ] || say "ATTENTION: raveforge.eu/www n'étaient pas 401/301 avant (inchangés quand même)."
STAGE=done; trap - ERR
say "Sauvegardes : $BK · Retour arrière : bash $RBS"
say WOW4EVER_UPDATE_V6_DONE

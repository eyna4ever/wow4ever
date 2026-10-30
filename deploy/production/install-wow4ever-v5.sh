#!/bin/bash
# install-wow4ever-v5.sh : communauté (Flask, 127.0.0.1:8014) + wiki statique pour wow4ever.raveforge.eu.
# Usage : bash install-wow4ever-v5.sh URL_ARCHIVE SHA256_ARCHIVE
# Remplace UNIQUEMENT le bloc Caddy « wow4ever.raveforge.eu » (Raveforge vérifié identique octet par octet).
# Ré-exécutable. N'affiche aucun secret. Prérequis : bash set-wow4ever-password.sh (empreinte du mot de passe).
set -euo pipefail
R="${W5_ROOT:-}"                       # préfixe de test local uniquement (vide en production)
TS=$(date +%Y%m%dT%H%M%S)
HOST=wow4ever.raveforge.eu
CF="${W5_CADDYFILE:-$R/etc/caddy/Caddyfile}"
CADDY="${W5_CADDY:-caddy}"
APP=$R/srv/wow4ever-app
REL=$APP/releases/$TS
ENVF=$R/etc/wow4ever-community.env
UNITS=$R/etc/systemd/system
HASHF=$R/root/wow4ever-basicauth.hash
TOOL=$R/root/wow4ever-caddy-block.py
PRE=$R/root/wow4ever-pre-v5-block.caddy
LOG=$R/root/wow4ever-v5-$TS.log
SVC="wow4ever-community.service wow4ever-community-purge.timer wow4ever-community-backup.timer"
URL="${1:-}"; SUM="${2:-}"
die(){ echo "ERREUR: $*" >&2; exit 1; }
say(){ echo "== $*"; }
mkdir -p "$R/root"
exec > >(tee -a "$LOG") 2>&1

[ -n "$URL" ] && [[ "$SUM" =~ ^[0-9a-f]{64}$ ]] || die "usage : bash $0 URL SHA256"
[ -n "${W5_TEST:-}" ] || [ "$(id -u)" = 0 ] || die "à lancer en root."

say "1/9 Vérifications préalables (rien n'est modifié)"
command -v python3 >/dev/null || die "python3 absent."
python3 -c 'import sys; sys.exit(sys.version_info < (3,12))' || die "Python >= 3.12 requis (trouvé $(python3 -V 2>&1)). Rien modifié."
python3 -c 'import sqlite3,sys; sys.exit(tuple(map(int,sqlite3.sqlite_version.split("."))) < (3,35))' || die "SQLite >= 3.35 requis. Rien modifié."
if ! python3 -c 'import ensurepip, venv' 2>/dev/null; then
  [ -z "${W5_TEST:-}" ] || die "venv absent (test)."
  V=$(python3 -c 'import sys;print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  say "installation de python3-venv (apt)"
  DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3-venv "python$V-venv" >/dev/null || die "apt-get install python3-venv a échoué."
fi
command -v "$CADDY" >/dev/null || die "caddy introuvable."
[ -f "$CF" ] || die "$CF introuvable."
[ -s "$HASHF" ] || die "empreinte absente : lancer d'abord le helper set-wow4ever-password.sh. Rien modifié."
if ss -Hltn 'sport = :8014' | grep -q . && ! systemctl is-active --quiet wow4ever-community.service; then
  die "port 8014 déjà utilisé par un autre programme. Rien modifié."
fi
AVAIL=$(df -Pk "$R/srv" 2>/dev/null | awk 'NR==2{print $4}'); [ "${AVAIL:-0}" -ge 512000 ] || die "moins de 500 Mo libres sur /srv."
curl -sS -m 8 -o /dev/null https://discord.com/api/v10/gateway 2>/dev/null || echo "ATTENTION: discord.com injoignable en HTTPS (la connexion Discord ne marchera pas tant que ce n'est pas réglé)."
VER=$("$CADDY" version | grep -oE 'v2\.[0-9]+' | head -1 | cut -d. -f2); DIR=basic_auth; [ "${VER:-0}" -ge 8 ] || DIR=basicauth
cat > "$TOOL" <<'PYEOF'
#!/usr/bin/env python3
"""Replace ONLY the top-level `wow4ever.raveforge.eu { ... }` block of a Caddyfile.

  extract CADDYFILE                      -> print the current wow4ever block
  render  DIRECTIVE HASHFILE OUT         -> write the new v5 block (basic_auth|basicauth)
  replace CADDYFILE NEWBLOCK OUT         -> write CADDYFILE with only that block replaced
Every other byte (global options, Raveforge and any other site) is asserted identical.
"""
import hashlib, re, sys

HOST = 'wow4ever.raveforge.eu'
MARK = '# wow4ever-v5 : bloc géré par install-wow4ever-v5.sh (ne pas éditer à la main)'


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

	# Communauté (application Flask sur loopback), protégée par mot de passe HTTP.
	@app path /community /community/* /auth/* /account /account/* /notifications /notifications/* /moderation /moderation/* /privacy /privacy/*
	handle @app {
		DIRECTIVE {
			mathieu HASH
		}
		reverse_proxy 127.0.0.1:8014 {
			header_up X-Forwarded-For {remote_host}
		}
	}

	# Wiki statique public (build du 28/10 + liens communauté), servi directement par Caddy.
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
python3 "$TOOL" extract "$CF" > "$R/root/wow4ever-block-$TS.caddy"   # échoue proprement si le bloc est absent/ambigu
python3 "$TOOL" render "$DIR" "$HASHF" "$R/root/wow4ever-v5-block.caddy"
python3 "$TOOL" replace "$CF" "$R/root/wow4ever-v5-block.caddy" /dev/null >/dev/null   # essai à blanc
code(){ curl -s -o /dev/null -m 10 -w '%{http_code}' ${W5_RESOLVE:---resolve $HOST:443:127.0.0.1} "${W5_BASE:-https://$HOST}$1" || true; }
OTHERS=$(python3 - "$CF" <<'PY'
import re,sys
t=open(sys.argv[1]).read()
print(' '.join(sorted({m for m in re.findall(r'(?m)^([a-z0-9.-]+\.[a-z]{2,})[\s,{]',t) if m!='wow4ever.raveforge.eu'})))
PY
)
declare -A BEFORE; for h in $OTHERS; do BEFORE[$h]=$(curl -s -o /dev/null -m 10 -w '%{http_code}' --resolve "$h:443:127.0.0.1" "https://$h/" || true); done

say "2/9 Téléchargement et vérification de l'archive"
TMP=$R/root/wow4ever-v5-$TS.tar.gz
curl -fsSL --retry 6 --retry-all-errors --retry-delay 3 -o "$TMP" "$URL"
echo "$SUM  $TMP" | sha256sum -c - >/dev/null || die "SHA-256 de l'archive incorrect. Rien modifié."
tar -tzf "$TMP" | grep -qE '(^/|(^|/)\.\.(/|$))' && die "archive avec chemins dangereux."

say "3/9 Sauvegardes"
[ -d "$R/srv/wow4ever" ] && cp -a "$R/srv/wow4ever" "$R/srv/wow4ever.bak-$TS" && echo "wiki actuel copié : /srv/wow4ever.bak-$TS"
cp -a "$CF" "$CF.bak-$TS" && echo "Caddyfile : $CF.bak-$TS"
if ! grep -q 'wow4ever-v5' "$R/root/wow4ever-block-$TS.caddy" && [ ! -f "$PRE" ]; then cp "$R/root/wow4ever-block-$TS.caddy" "$PRE"; fi

say "4/9 Utilisateur et code ($REL)"
if [ -z "${W5_TEST:-}" ]; then id wow4ever-app >/dev/null 2>&1 || useradd --system --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin wow4ever-app; fi
mkdir -p "$REL"; tar -xzf "$TMP" -C "$REL" --no-same-owner
[ -f "$REL/community/app.py" ] && [ -d "$REL/wiki" ] || die "archive inattendue."

say "5/9 Environnement Python (wheelhouse local, sinon PyPI)"
python3 -m venv "$REL/.venv"
if ! "$REL/.venv/bin/pip" install -q --no-index --find-links "$REL/wheelhouse" -r "$REL/requirements.lock"; then
  echo "wheelhouse insuffisante, tentative via PyPI"
  "$REL/.venv/bin/pip" install -q -r "$REL/requirements.lock" || die "installation des dépendances impossible (pas d'accès PyPI ?). Site public inchangé."
fi
"$REL/.venv/bin/pip" check >/dev/null
[ -n "${W5_TEST:-}" ] || chown -R root:root "$REL"
chmod -R u=rwX,go=rX "$REL"; chmod 755 "$R/srv/wow4ever-app" "$APP/releases"
RUNAPP=(); [ -n "${W5_TEST:-}" ] || RUNAPP=(runuser -u wow4ever-app --)
( cd "$REL" && "${RUNAPP[@]}" env -u SECRET_KEY HOME=/tmp TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests >"$R/root/wow4ever-v5-tests-$TS.txt" 2>&1 ) \
  || die "tests de la révision en échec (voir $R/root/wow4ever-v5-tests-$TS.txt). Site public inchangé."
echo "tests OK ($(grep -oE '^Ran [0-9]+ tests' "$R/root/wow4ever-v5-tests-$TS.txt"))"

say "6/9 Secrets et configuration ($ENVF, jamais affichés)"
umask 077
if [ ! -f "$ENVF" ]; then
  K=$(python3 -c 'import secrets;print(secrets.token_urlsafe(48))')
  printf 'SECRET_KEY=%s\n' "$K" > "$ENVF"; unset K
fi
add(){ grep -q "^$1=" "$ENVF" || printf '%s=%s\n' "$1" "$2" >> "$ENVF"; }
add PUBLIC_URL "https://$HOST"
add DATABASE /var/lib/wow4ever-community/community.sqlite3
add TRUSTED_PROXY_IPS 127.0.0.1
add DISCORD_CLIENT_ID ""
add DISCORD_CLIENT_SECRET ""
add CONTROLLER_NAME ""
add PRIVACY_CONTACT ""
chmod 600 "$ENVF"; [ -n "${W5_TEST:-}" ] || chown root:wow4ever-app "$ENVF"
umask 022

say "7/9 Services systemd"
ln -sfn "releases/$TS" "$APP/current.new" && mv -Tf "$APP/current.new" "$APP/current"
mkdir -p "$UNITS"; cp "$REL"/deploy/production/wow4ever-community*.service "$REL"/deploy/production/wow4ever-community*.timer "$UNITS/"
systemctl daemon-reload
systemd-run --quiet --wait --pipe -p User=wow4ever-app -p Group=wow4ever-app -p EnvironmentFile=/etc/wow4ever-community.env \
  -p StateDirectory="wow4ever-community wow4ever-community-backups" -p StateDirectoryMode=0700 -p WorkingDirectory=/srv/wow4ever-app/current \
  /srv/wow4ever-app/current/.venv/bin/flask --app community.app:create_app init-db
systemctl enable --quiet $SVC
systemctl restart wow4ever-community.service
systemctl start wow4ever-community-purge.timer wow4ever-community-backup.timer
OK=; for i in $(seq 1 20); do
  if curl -fsS -m 3 -H "Host: $HOST" http://127.0.0.1:8014/healthz 2>/dev/null | grep -q '"status": *"ok"'; then OK=1; break; fi; sleep 1
done
[ -n "$OK" ] || die "l'application ne répond pas sur 127.0.0.1:8014 (journalctl -u wow4ever-community). Caddy NON modifié, site public inchangé."
echo "application OK sur 127.0.0.1:8014"

say "8/9 Caddy : remplacement du seul bloc $HOST"
cat > "$R/root/wow4ever-rollback.sh" <<RB
#!/bin/bash
# Retour arrière v5 : remet l'ancien bloc wow4ever (wiki /srv/wow4ever), recharge Caddy, arrête la communauté.
set -euo pipefail
python3 $TOOL replace $CF $PRE $CF.rollback-new
$CADDY validate --config $CF.rollback-new --adapter caddyfile >/dev/null
cp -a $CF $CF.before-rollback-\$(date +%Y%m%dT%H%M%S) && cat $CF.rollback-new > $CF && rm -f $CF.rollback-new
systemctl reload caddy
systemctl disable --now $SVC
echo WOW4EVER_ROLLBACK_DONE
RB
chmod 700 "$R/root/wow4ever-rollback.sh"
NEW="$CF.v5-new"
python3 "$TOOL" replace "$CF" "$R/root/wow4ever-v5-block.caddy" "$NEW"
"$CADDY" validate --config "$NEW" --adapter caddyfile >/dev/null 2>"$R/root/wow4ever-v5-validate-$TS.txt" \
  || { rm -f "$NEW"; die "caddy validate refuse le nouveau Caddyfile (voir $R/root/wow4ever-v5-validate-$TS.txt). Caddyfile inchangé ; l'application tourne en local seulement."; }
cat "$NEW" > "$CF"; rm -f "$NEW"
restore(){ echo "RESTAURATION du Caddyfile : $*" >&2; cat "$CF.bak-$TS" > "$CF"; systemctl reload caddy || true; die "$* : Caddyfile restauré ($CF.bak-$TS)."; }
"$CADDY" validate --config "$CF" --adapter caddyfile >/dev/null 2>&1 || restore "validation après copie"
systemctl reload caddy || restore "reload Caddy en échec"
sleep 3

say "9/9 Contrôles finaux"
FR=$(code /fr/); CO=$(code /community/); JPG=$(code /assets/art-ar01-calendar-1280.jpg)
echo "/fr/ -> $FR (attendu 200) ; /community/ -> $CO (attendu 401) ; illustration .jpg -> $JPG (attendu 200)"
[ "$FR" = 200 ] || restore "/fr/ ne répond pas 200"
[ "$CO" = 401 ] || restore "/community/ n'est pas protégé (code $CO)"
for h in $OTHERS; do A=$(curl -s -o /dev/null -m 10 -w '%{http_code}' --resolve "$h:443:127.0.0.1" "https://$h/" || true)
  echo "$h : avant ${BEFORE[$h]} / après $A"
  if [ "${BEFORE[$h]:0:1}" != 5 ] && [ "${BEFORE[$h]}" != 000 ] && { [ "${A:0:1}" = 5 ] || [ "$A" = 000 ]; }; then restore "$h en erreur après reload"; fi
done
echo
echo "Wiki public : https://$HOST/fr/  ·  Communauté (mot de passe, utilisateur mathieu) : https://$HOST/community/"
echo "Discord : renseigner DISCORD_CLIENT_ID/SECRET, CONTROLLER_NAME et PRIVACY_CONTACT dans $ENVF puis : systemctl restart wow4ever-community"
echo "Retour arrière : bash /root/wow4ever-rollback.sh   (secours : cp $CF.bak-$TS $CF && systemctl reload caddy && systemctl disable --now $SVC)"
echo "Journal : $LOG"
echo WOW4EVER_INSTALL_V5_DONE

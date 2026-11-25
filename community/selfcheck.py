#!/usr/bin/env python3
"""Discord login self-check for the operator (v14). Run as root on the server:
    python3 /srv/wow4ever-app/current/community/selfcheck.py /etc/wow4ever-community.env
Reads the service environment file WITHOUT ever printing a secret value: only its length and its shape.
Checks: Client ID, Client Secret shape (a 64-hex "Public Key" is a classic mistake), PUBLIC_URL and the exact redirect
URI to declare on the Discord developer portal, discord.com reachability, and whether Discord accepts the
Client ID + Client Secret pair (client_credentials request; the app token received is revoked at once, never shown).
--offline skips the network checks. Standard library only (runs with the system python3)."""
import json, re, sys, urllib.error, urllib.parse, urllib.request

EXPECTED_CLIENT_ID = '1565699718397296672'
API = 'https://discord.com/api/v10'


def read_env(path):
    values = {}
    with open(path, encoding='utf-8', errors='replace') as handle:
        lines = handle.read().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        values[key] = value
    return values


def secret_shape(secret):
    """(verdict, explanation) from length/charset only."""
    if not secret:
        return 'absent', 'DISCORD_CLIENT_SECRET est vide.'
    n = len(secret)
    if re.fullmatch(r'[0-9a-f]{64}', secret):
        return 'public-key', f'{n} caractères hexadécimaux : c’est le format de la « Public Key », PAS du Client Secret.'
    if re.fullmatch(r'[A-Za-z0-9_-]{32}', secret):
        return 'ok', f'{n} caractères [A-Za-z0-9_-] : format d’un Client Secret Discord.'
    if secret != secret.strip() or any(c.isspace() for c in secret):
        return 'suspect', f'{n} caractères dont des espaces : secret mal collé.'
    if re.fullmatch(r'[A-Za-z0-9._-]{50,90}', secret) and secret.count('.') == 2:
        return 'bot-token', f'{n} caractères en trois parties : ressemble à un token de BOT, pas au Client Secret.'
    return 'suspect', f'{n} caractères : format inhabituel pour un Client Secret (32 caractères attendus).'


def request(url, data=None, timeout=10):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                                 headers={'User-Agent': 'wow4ever-selfcheck (https://wowkipedia.com, 1.0)', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(65536)
    except urllib.error.HTTPError as e:
        return e.code, e.read(65536)


def error_code(body):
    try:
        return re.sub(r'[^a-z_]', '', str(json.loads(body).get('error', '')))[:40]
    except (ValueError, AttributeError):
        return ''


def main(argv):
    offline = '--offline' in argv
    args = [a for a in argv if not a.startswith('--')]
    env = read_env(args[0] if args else '/etc/wow4ever-community.env')
    ok = True
    out = lambda tag, msg: print(f'[{tag}] {msg}')
    cid = env.get('DISCORD_CLIENT_ID', '')
    if cid == EXPECTED_CLIENT_ID:
        out('OK', f'Client ID {cid} (application Discord attendue).')
    elif re.fullmatch(r'\d{17,20}', cid):
        out('ATTENTION', f'Client ID {cid} différent de celui attendu ({EXPECTED_CLIENT_ID}).')
    else:
        out('ERREUR', 'DISCORD_CLIENT_ID absent ou invalide.'); ok = False
    secret = env.get('DISCORD_CLIENT_SECRET', '')
    verdict, why = secret_shape(secret)
    out('OK' if verdict == 'ok' else 'ERREUR', 'Client Secret : ' + why)
    ok &= verdict == 'ok'
    public = env.get('PUBLIC_URL', '').rstrip('/')
    out('OK' if public in ('https://wowkipedia.com', 'https://wow4ever.raveforge.eu') else 'ATTENTION', f'PUBLIC_URL = {public or "(vide)"}')
    redirect = public + '/auth/discord/callback'
    out('INFO', f'Adresse de retour à déclarer EXACTEMENT sur le portail Discord (OAuth2 > Redirects) : {redirect}')
    out('INFO', 'TRUSTED_PROXY_IPS ' + ('défini' if env.get('TRUSTED_PROXY_IPS') else 'VIDE (toutes les connexions comptent comme une seule IP)'))
    if offline:
        out('INFO', 'contrôles réseau ignorés (--offline).')
    else:
        try:
            status, _ = request(API + '/gateway')
            out('OK' if status == 200 else 'ERREUR', f'discord.com joignable depuis le serveur (HTTP {status}).')
            ok &= status == 200
        except OSError as exc:
            out('ERREUR', f'discord.com injoignable depuis le serveur ({type(exc).__name__}).'); ok = False
            status = None
        if status == 200 and cid and secret:
            try:
                code, body = request(API + '/oauth2/token', {'grant_type': 'client_credentials', 'scope': 'identify',
                                                              'client_id': cid, 'client_secret': secret})
                if code == 200:
                    out('OK', 'Discord accepte le couple Client ID + Client Secret.')
                    try:
                        token = json.loads(body).get('access_token', '')
                        if token:
                            request(API + '/oauth2/token/revoke', {'token': token, 'client_id': cid, 'client_secret': secret})
                    except (ValueError, OSError):
                        pass
                    token = None
                elif code == 400 and error_code(body) == 'invalid_scope':
                    out('OK', 'Discord accepte le Client ID + Client Secret (portée de test refusée, sans importance).')
                else:
                    err = error_code(body)
                    hint = ' → recoller le Client Secret (portail Discord > OAuth2 > Reset Secret, puis discord-web.sh).' if err in ('invalid_client', 'unauthorized_client') else ''
                    out('ERREUR', f'Discord refuse le Client ID + Client Secret (HTTP {code}, {err or "sans code"}){hint}'); ok = False
            except OSError as exc:
                out('ERREUR', f'échange avec Discord impossible ({type(exc).__name__}).'); ok = False
    secret = None
    print('WOW4EVER_DISCORD_CHECK_' + ('OK' if ok else 'PROBLEME'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

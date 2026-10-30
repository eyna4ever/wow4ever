# Plan d'installation sur le serveur Hetzner : BROUILLON, NE PAS EXÉCUTER sans accord explicite de Mathieu

Préparé le 30/10/2026, sans aucun accès au serveur. Serveur : `178.104.54.20`. Il est **partagé avec Raveforge**, dont le bloc Caddy ne doit **jamais** être touché.

Le site actuel est le wiki statique, dans `/srv/wow4ever`, servi par le bloc Caddy `wow4ever.raveforge.eu`. **`/srv/wow4ever` n'est ni modifié ni supprimé : il sert de retour arrière.**

Archive à installer : `wow4ever-community-merge-<date>.tar.gz` (voir son `.sha256`).

Toutes les commandes sont lancées par Mathieu, ou par un agent qu'il autorise **étape par étape**. Aucun secret ne transite par le chat.

## 0. Décisions préalables (Mathieu)
- **Ouverture** : privée (`basic_auth` Caddy sur les préfixes de la communauté) ou publique. Recommandé : **privée** pour la recette Discord.
- **Liens « Communauté » du wiki** : actifs, ou wiki reconstruit avec `--no-community-links` pendant la phase privée.
- **Sauvegardes hors serveur** : Storage Box, Backups Hetzner ou machine personnelle (les deux premières sont payantes), et snapshot Hetzner avant intervention ou non.
- **Créneau d'intervention** : le rechargement de Caddy concerne tous les sites, y compris Raveforge. Il est gracieux, mais à faire hors pointe.

## 1. Vérifications en lecture seule (aucune modification)
```sh
python3 --version                                    # exigé : >= 3.12
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'   # exigé : >= 3.35 (RETURNING)
caddy version; systemctl --version | head -1
ss -ltnp | grep -E ':8014\b' || echo "port 8014 libre"
curl -sS -o /dev/null -w '%{http_code}\n' https://discord.com/api/v10/gateway      # sortie HTTPS vers Discord
curl -sS -o /dev/null -w '%{http_code}\n' https://cdn.discordapp.com/embed/avatars/0.png
df -h /srv /var/lib
grep -n 'wow4ever.raveforge.eu' -A40 /etc/caddy/Caddyfile   # repérer le bloc et ses directives log/header
grep -n '^import' /etc/caddy/Caddyfile
ls -la /srv/wow4ever | head
dig +short wow4ever.raveforge.eu   # un proxy de type Cloudflare devant ? Si oui, revoir X-Forwarded-For / TRUSTED_PROXY_IPS
```
Si Python est en dessous de 3.12, ne pas l'installer à la volée : décider d'abord entre un paquet de la distribution (backports) et un Python isolé, dédié à l'application.

## 2. Sauvegardes avant intervention
```sh
TS=$(date +%Y%m%dT%H%M%S)
sudo cp -a /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak-$TS
# /srv/wow4ever reste en place, inchangé (retour arrière).
```
Optionnel : un snapshot Hetzner (payant, décision de Mathieu).

## 3. Transfert de l'archive (depuis la machine de Mathieu, pas d'hébergeur public de fichiers)
```sh
scp wow4ever-community-merge-<date>.tar.gz wow4ever-community-merge-<date>.tar.gz.sha256 UTILISATEUR@178.104.54.20:/tmp/
ssh UTILISATEUR@178.104.54.20 'cd /tmp && sha256sum -c wow4ever-community-merge-<date>.tar.gz.sha256'
```

## 4. Utilisateur, code et environnement Python
```sh
REV=merge-<date>
sudo useradd --system --no-create-home --shell /usr/sbin/nologin wow4ever-app
sudo mkdir -p /srv/wow4ever-app/releases/$REV
sudo tar -xzf /tmp/wow4ever-community-merge-<date>.tar.gz -C /srv/wow4ever-app/releases/$REV
cd /srv/wow4ever-app/releases/$REV
sudo python3 -m venv .venv && sudo .venv/bin/pip install -r requirements.lock && sudo .venv/bin/pip check
sudo chown -R root:root . && sudo chmod -R u=rwX,go=rX .   # code en lecture seule pour l'application ; wiki/ lisible par Caddy
# Tests dans la révision, sous l'utilisateur dédié, sur base temporaire (aucun secret nécessaire) :
sudo -u wow4ever-app env -u SECRET_KEY HOME=/tmp TMPDIR=/tmp .venv/bin/python -m unittest discover -s tests
sudo ln -sfn /srv/wow4ever-app/releases/$REV /srv/wow4ever-app/current
```

## 5. Secrets : saisis par Mathieu sur le serveur, jamais dans le chat
```sh
sudo install -m 0600 -o root -g root /dev/null /etc/wow4ever-community.env
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'   # SECRET_KEY, à copier directement dans le fichier
sudoedit /etc/wow4ever-community.env
```
Contenu attendu (les valeurs sont saisies par Mathieu) :
```dotenv
PUBLIC_URL=https://wow4ever.raveforge.eu
DATABASE=/var/lib/wow4ever-community/community.sqlite3
SECRET_KEY=<généré sur le serveur>
DISCORD_CLIENT_ID=<application Discord>
DISCORD_CLIENT_SECRET=<application Discord>
CONTROLLER_NAME=<responsable du traitement>
PRIVACY_CONTACT=<contact RGPD>
TRUSTED_PROXY_IPS=127.0.0.1,::1
```
Dans le Discord Developer Portal, régler l'onglet OAuth2 :
- redirection **exacte** `https://wow4ever.raveforge.eu/auth/discord/callback` ;
- scope `identify` uniquement ;
- aucun bot ni permission de guilde.

## 6. Services systemd (application sur 127.0.0.1:8014, données et sauvegardes séparées)
```sh
sudo cp /srv/wow4ever-app/current/deploy/production/wow4ever-community*.service \
        /srv/wow4ever-app/current/deploy/production/wow4ever-community*.timer /etc/systemd/system/
sudo systemctl daemon-reload
# Initialisation de la base, sous l'utilisateur dédié, sans exposer les secrets dans la ligne de commande :
sudo systemd-run --wait --pipe -p User=wow4ever-app -p Group=wow4ever-app \
  -p EnvironmentFile=/etc/wow4ever-community.env -p StateDirectory=wow4ever-community -p StateDirectoryMode=0700 \
  -p WorkingDirectory=/srv/wow4ever-app/current \
  /srv/wow4ever-app/current/.venv/bin/flask --app community.app:create_app init-db
sudo systemctl enable --now wow4ever-community.service wow4ever-community-purge.timer wow4ever-community-backup.timer
sudo systemctl start wow4ever-community-backup.service && sudo ls -la /var/lib/wow4ever-community-backups
curl -s -H 'Host: wow4ever.raveforge.eu' http://127.0.0.1:8014/healthz        # {"status":"ok","schema":2}
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: wow4ever.raveforge.eu' http://127.0.0.1:8014/fr/
journalctl -u wow4ever-community -n 50 --no-pager
```
À ce stade, le site public n'a pas changé : Caddy sert toujours `/srv/wow4ever`.

Chemins utilisés :

| Rôle | Chemin |
|---|---|
| Code | `/srv/wow4ever-app/releases/<rev>`, lien `current` |
| Base de données | `/var/lib/wow4ever-community` (0700) |
| Sauvegardes locales, 30 jours | `/var/lib/wow4ever-community-backups` (0700) |
| Secrets | `/etc/wow4ever-community.env` (0600) |

## 7. Caddy : SEULEMENT le bloc `wow4ever.raveforge.eu`
1. Copier le bloc actuel dans un fichier de retour arrière, par exemple `/etc/caddy/wow4ever-block.bak-$TS`.
2. Remplacer **ce seul bloc** par `deploy/production/Caddy-wow4ever.fragment` :
   - wiki servi par Caddy depuis `/srv/wow4ever-app/current/wiki`, avec la CSP actuelle du wiki limitée au statique ;
   - préfixes de la communauté proxifiés vers `127.0.0.1:8014` ;
   - `basic_auth` à décommenter pour la phase privée (empreinte du mot de passe produite par `caddy hash-password` et saisie par Mathieu).
   Ne toucher à aucun autre bloc, ni aux options globales.
3. Lancer `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`. **Si la validation échoue, restaurer la copie et s'arrêter.**
4. `sudo systemctl reload caddy`, puis vérifier immédiatement :
   ```sh
   curl -sI https://wow4ever.raveforge.eu/fr/ | head -20            # 200 + CSP du wiki
   curl -sI https://wow4ever.raveforge.eu/assets/art-ar01-calendar-1280.jpg | head -5
   curl -sI https://wow4ever.raveforge.eu/community/ | head -20     # 401 si basic_auth, sinon 200 + CSP de l'application
   curl -sI https://raveforge.eu/ | head -5                          # Raveforge toujours OK (adapter aux hôtes Raveforge réels)
   ```
5. Vérifier qu'aucun journal d'accès Caddy n'enregistre la query string de `/auth/discord/callback`.

## 8. Recette
- Pages du wiki FR/EN : la page d'accueil « À la une », un article AR avec son illustration, AC2 et CL3 absents.
- Connexion Discord réelle : première connexion, refus, rejeu, déconnexion, révocation.
- `set-role <discord_id> admin` pour deux administrateurs (même méthode `systemd-run` qu'à l'étape 6).
- Sujet, réponse, signalement, modération, export et suppression RGPD.
- Restauration d'une sauvegarde sur une copie.

## 9. Retour arrière (quelques minutes)
1. Remettre la copie du bloc `wow4ever.raveforge.eu` (root `/srv/wow4ever`), puis `caddy validate` et `systemctl reload caddy`. Le wiki d'avant est de nouveau servi, inchangé.
2. `sudo systemctl disable --now wow4ever-community.service wow4ever-community-purge.timer wow4ever-community-backup.timer`.
3. Conserver `/var/lib/wow4ever-community*` (données des comptes) pour analyse, ou les effacer selon la politique RGPD.

## Points ouverts avant une ouverture publique
Voir `REVUE.md` (contre-revue lot 2) :
- contournement d'un bannissement par suppression puis reconnexion ;
- conservation des preuves de modération ;
- informations RGPD complètes ;
- sauvegardes chiffrées hors serveur ;
- recette d'accessibilité manuelle ;
- harmonisation visuelle de la communauté avec le thème du wiki ;
- maquettes.

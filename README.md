# WoW Forever — wiki et communauté

Le wiki HTML/CSS/JavaScript français et anglais est conservé. Le service Flask ajoute les forums, les comptes Discord et la modération sur la même origine. SQLite stocke uniquement les données communautaires. Aucune génération de faux comptes, sujets ou activité.

Branche de travail : `codex/community-redesign`. Base auditée : `9b51f381bba732e084157b7335afb5f6f503c3b5` de [eyna4ever/wow4ever](https://github.com/eyna4ever/wow4ever).

## Prévisualiser en local

Python 3.12 ou supérieur, SQLite 3.35 ou supérieur, Linux pour Gunicorn.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.lock
cp .env.example .env
```

Renseigner une `SECRET_KEY` aléatoire d’au moins 32 caractères dans `.env`. Génération possible : `python -c 'import secrets; print(secrets.token_urlsafe(48))'`. Ne jamais partager cette valeur. L’application refuse de démarrer sans clé. Laisser les paramètres Discord vides pour une visite publique locale sans authentification.

```bash
set -a
. ./.env
set +a
.venv/bin/flask --app community.app:create_app init-db
.venv/bin/gunicorn 'community.app:create_app()' --bind 127.0.0.1:8000 --workers 2 --access-logfile /dev/null
```

Ouvrir `http://localhost:8000/community/` pour les forums et `http://localhost:8000/fr/` pour le wiki. Le nom d’hôte doit correspondre exactement à `PUBLIC_URL`. Aucune publication réseau n’est nécessaire ; utiliser un tunnel SSH pour une préproduction privée. `init-db` est idempotente et crée quatre salons vides, jamais de membres de démonstration.

Le serveur sert les fichiers du wiki par une liste autorisée. **Ne jamais exposer la racine du dépôt par un serveur de fichiers générique** : elle contient désormais du code et peut contenir des données privées. `install.sh` est volontairement neutralisé : il échoue sans modifier de fichier ou de service. La future architecture statique/proxy séparée est préparée dans le guide de déploiement, sans aucune modification de production.

## Vérifier

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/pip check
git diff --check
```

Les tests utilisent exclusivement une base temporaire et des identités de test. Les réponses Discord sont simulées. Pour les contrôles navigateur et axe-core, voir [tests/README.md](tests/README.md).

## Exploiter

```bash
.venv/bin/flask --app community.app:create_app purge
.venv/bin/flask --app community.app:create_app backup /chemin/prive/snapshot.sqlite3
.venv/bin/flask --app community.app:create_app backup-daily /chemin/prive/snapshots --keep-days 30
.venv/bin/flask --app community.app:create_app set-role IDENTIFIANT_DISCORD admin
```

La purge est quotidienne. La sauvegarde refuse tout écrasement et utilise l’API SQLite pour un instantané cohérent, même en mode WAL. Le rôle initial exige que le compte ait déjà effectué une vraie connexion Discord ; l’opération est journalisée. Les rôles ne sont jamais déduits du pseudonyme ni d’un paramètre navigateur.

Les cinq unités systemd de préproduction comprennent deux timers : purge et sauvegarde locale avec rotation. Elles ne sont pas installées par le projet. Le chiffrement et la sauvegarde hors serveur restent à configurer avant le public. En accès direct, laisser `TRUSTED_PROXY_IPS` vide ; derrière le seul Caddy local explicitement autorisé, configurer les adresses exactes `127.0.0.1,::1` et lui faire remplacer X-Forwarded-For. Voir les contraintes de confiance dans `docs/DEPLOYMENT.md`.

## Documents de livraison

- [Audit et architecture](docs/AUDIT.md)
- [Configuration Discord](docs/DISCORD.md)
- [Préproduction, déploiement et retour arrière](docs/DEPLOYMENT.md)
- [Sécurité, données et conservation](docs/SECURITY.md)
- [Rapport de validation et limites](docs/REPORT.md)
- [Suite donnée à la revue de livraison](docs/REVIEW-FOLLOWUP.md)

La communauté est en français ; les 100 pages du wiki gardent leurs langues et leurs URL. Le Talent Builder et la gestion de guilde sont hors périmètre.

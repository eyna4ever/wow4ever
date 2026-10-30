# Préproduction et retour arrière

Ces instructions et unités sont préparées ; elles n’ont pas été installées sur un serveur distant. Aucun déploiement public n’est autorisé à ce stade. `install.sh` est neutralisé et échoue immédiatement sans aucune modification. Selon la revue fournie, le site actuel est sous `/srv/wow4ever` : ne pas y copier cette branche pendant la préproduction. Ce chemin n’a pas été vérifié par Codex sur le serveur.

## Préproduction privée

Utiliser un clone dédié du seul dépôt `eyna4ever/wow4ever`, une application Discord de test et une base vide. Ne copier aucune donnée personnelle de production. Le service préparé écoute exclusivement `127.0.0.1:8014` ; il est accessible par tunnel SSH. Aucune ouverture de pare-feu ni modification d’un autre hôte Caddy n’est nécessaire.

Disposition proposée, à créer par l’administrateur de la machine :

```text
/srv/wow4ever-staging/releases/REVISION/  # code et .venv propres à la révision
/srv/wow4ever-staging/current            # lien vers la révision choisie
/var/lib/wow4ever-staging/               # base et WAL, droits 0700
/var/lib/wow4ever-staging-backups/       # snapshots locaux de test, droits 0700
/etc/wow4ever-staging.env                # secrets 0600, lu par systemd
```

Créer l’utilisateur système non privilégié `wow4ever-staging`. Garder le code en lecture seule pour lui et la base dans son répertoire d’état. Installer les dépendances du fichier `requirements.lock` dans la `.venv` de la révision. Configurer :

```dotenv
PUBLIC_URL=http://localhost:8014
DATABASE=/var/lib/wow4ever-staging/community.sqlite3
SECRET_KEY=VALEUR_ALEATOIRE_UNIQUE_A_GENERER
DISCORD_CLIENT_ID=IDENTIFIANT_APPLICATION_TEST
DISCORD_CLIENT_SECRET=SECRET_APPLICATION_TEST
CONTROLLER_NAME='Identité du responsable à renseigner'
PRIVACY_CONTACT='Contact des droits à renseigner'
TRUSTED_PROXY_IPS=''
```

Les valeurs ci-dessus sont des emplacements à renseigner, pas une configuration utilisable telle quelle. Générer au minimum 32 caractères aléatoires pour `SECRET_KEY`. L’application ne charge pas automatiquement `.env` : le README montre le chargement shell local, et systemd utilise `EnvironmentFile`.

1. Sous l’utilisateur applicatif et avec cet environnement, lancer `flask --app community.app:create_app init-db` avant le démarrage. Le répertoire de la base doit préexister et lui appartenir. Vérifier que l’utilisateur peut créer les fichiers WAL/SHM.
2. Examiner puis installer les cinq unités `deploy/wow4ever-staging*` dans systemd : serveur, purge et son timer, sauvegarde et son timer. Les chemins sont exclusivement réservés à ce projet. Activer le serveur et les deux timers. Rien n’est installé par cette livraison locale.
3. Ouvrir un tunnel `ssh -L 8014:127.0.0.1:8014 UTILISATEUR@SERVEUR`, puis visiter `http://localhost:8014/community/`. Configurer la callback Discord localhost avec ce même port. Pour un accès multiutilisateur, préparer un hôte TLS protégé par authentification ou VPN ; son origine doit correspondre à `PUBLIC_URL`.
4. Vérifier `/healthz`, les pages FR/EN, la recherche, les droits et la recette Discord réelle. Les actions administratives sensibles imposent une authentification datant de moins de dix minutes.
5. Configurer sauvegardes chiffrées, rotation de 30 jours, supervision et revue mensuelle de modération avant ouverture.

En accès direct/tunnel, conserver `TRUSTED_PROXY_IPS` vide. Derrière un Caddy local expressément autorisé, utiliser `TRUSTED_PROXY_IPS='127.0.0.1,::1'`. Seule l’adresse du client transmise par un pair immédiat de cette liste est acceptée, avec exactement un saut de proxy. Les proxys doivent remplacer X-Forwarded-For par l’adresse de leur client, et le serveur applicatif doit rester sur loopback. Un autre pair ne peut pas répartir ses budgets en forgeant cet en-tête. Les en-têtes de protocole, hôte, port ou préfixe ne sont pas acceptés. Le vrai `Host` doit correspondre à `PUBLIC_URL`. Ne pas utiliser de joker ni de sous-réseau ; ne pas ajouter une chaîne CDN/proxy sans revoir cette configuration et ses tests.

Les GET anonymes n’allouent plus de session SQLite et ne consomment pas le budget de création. Le formulaire de connexion utilise un cookie CSRF signé de 10 minutes, sans état en base. Une vraie session est créée au POST de connexion valide. Omettre la configuration de confiance derrière un proxy regrouperait encore les budgets des écritures et connexions : vérifier les adresses réellement vues avant toute ouverture publique.

## Configuration TLS à préparer uniquement après autorisation

La préproduction par tunnel ne modifie aucun bloc Caddy, y compris Forever. Pour une future production autorisée, préparer un export statique public contenant uniquement `assets/`, `fr/`, `en/`, `index.html`, `robots.txt` et `sitemap.xml`, dans un répertoire distinct (exemple : `/srv/wow4ever-public`). Ne jamais utiliser la racine du dépôt comme racine publique. Router seulement les chemins dynamiques vers le backend pour qu’une panne applicative n’emporte pas le wiki. Exemple à examiner et valider sur l’infrastructure cible, uniquement après autorisation :

```caddyfile
wow4ever.raveforge.eu {
    encode gzip zstd
    @community path /community /community/* /auth/* /account /account/* /notifications /notifications/* /moderation /moderation/* /privacy /privacy/* /healthz
    handle @community {
        reverse_proxy 127.0.0.1:8014 {
            header_up X-Forwarded-For {remote_host}
        }
    }
    handle {
        root * /srv/wow4ever-public
        file_server
    }
}
```

Ce fragment n’a pas été validé ni appliqué sur le serveur réel. Il n’inclut pas de journal d’accès. Examiner aussi les règles de logs héritées : ne jamais journaliser les paramètres de callback OAuth ni les cookies. Conserver tous les autres blocs inchangés. Dans cette configuration future, `PUBLIC_URL` doit être `https://wow4ever.raveforge.eu`, `TRUSTED_PROXY_IPS` doit contenir les seules adresses du Caddy local, et la callback Discord correspondante doit être enregistrée. Les cookies utilisent alors le préfixe `__Host-`, `Secure`, `HttpOnly`, `SameSite=Lax` ; HSTS est émis par l’application pour les chemins dynamiques sans `includeSubDomains`. Les en-têtes des pages statiques doivent être prévus par l’opérateur dans ce seul bloc.

## Sauvegarde et restauration

Utiliser la commande applicative `backup DESTINATION` avec une destination neuve dans un répertoire privé. Elle utilise `sqlite3.Connection.backup`, inclut les transactions WAL validées et contrôle l’intégrité. Ne pas copier uniquement le fichier principal à chaud.

Chiffrer hors application, transférer vers un stockage restreint indépendant, vérifier les restaurations et supprimer les générations au-delà de 30 jours. Ne pas mettre les exports ou snapshots sous le répertoire public. Inventorier les personnes habilitées et le prestataire de sauvegarde.

Pour les seules données de test en préproduction, le timer fourni appelle `backup-daily /var/lib/wow4ever-staging-backups --keep-days 30`. La commande vérifie chaque nouveau snapshot, exige un répertoire privé 0700, crée des fichiers 0600 puis retire uniquement ses anciens fichiers réguliers nommés `community-DATE-ALEA.sqlite3`. Les liens symboliques et les autres fichiers sont ignorés. La rotation n’a lieu qu’après une sauvegarde réussie. Cette automatisation locale n’assure ni chiffrement ni copie hors serveur ; elle ne suffit pas pour une ouverture publique.

La migration de schéma 2 type les cibles d’audit (`user:12`, `post:12`, etc.) de manière idempotente. Les anciens `report.create` désignaient un message et gardent donc une cible `post:`. Les cibles déjà écrasées par l’ancienne suppression ne sont pas reconstructibles. La révision de retour arrière doit comprendre ces cibles typées : ne pas réutiliser les opérations d’effacement du commit `dc364da` sur la base migrée.

Exercice de restauration : arrêter le service, conserver un instantané cohérent de l’état courant, restaurer dans un nouveau fichier, contrôler `PRAGMA integrity_check` et `PRAGMA foreign_key_check`, rétablir les permissions. Supprimer toutes les lignes `sessions`, `oauth` et `rate_limits` de la copie restaurée. Rejouer les demandes d’effacement reçues depuis la sauvegarde avant de remettre en service ; tenir le registre nécessaire hors de la sauvegarde, avec accès et conservation limités. Ne pas réouvrir une ancienne sauvegarde contenant des comptes effacés.

## Déploiement d’une nouvelle révision

Après autorisation explicite seulement : sélectionner un commit revu, exécuter les tests dans sa révision isolée, sauvegarder, arrêter le service pour toute migration de schéma, exécuter `init-db`, basculer le lien `current` et redémarrer. Vérifier santé, lecture wiki, connexion, publication et droits. Surveiller erreurs et contention SQLite. La première migration est additive et idempotente ; toute migration future doit prévoir sa compatibilité et sa procédure propre.

## Retour arrière

- Régression applicative sur schéma compatible : arrêter, repointer `current` vers la précédente révision approuvée, redémarrer et vérifier. Préserver la base et les contributions récentes.
- Échec de migration : arrêter et restaurer l’instantané testé avec la révision correspondante ; identifier et réconcilier les écritures postérieures avant ouverture. Une restauration ne doit jamais faire disparaître silencieusement des contributions.
- Retour au wiki d’avant la communauté : servir une **copie exportée propre du commit initial**, sans `.git`, code, secrets ni base. Préserver la base privée pour récupération. Les nouvelles pages de la branche comportent des liens communautaires : ne pas les servir seules si le backend est retiré.

Ne jamais lancer de `git pull`, `reset --hard`, suppression de répertoire ni reload global improvisé dans un répertoire partagé de production. La validation humaine d’ouverture inclut l’autorisation de changement du seul hôte Forever.

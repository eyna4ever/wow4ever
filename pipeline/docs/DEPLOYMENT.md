# Déploiement et retour arrière — préparation, aucune mise en production effectuée

L’intégration actuelle se construit comme site statique sans dépendances externes. L’adaptateur Next.js est fourni, mais sa compilation reste bloquée par l’absence de dépendances. Les comptes, contributions et PostgreSQL ne sont pas connectés à cette livraison. Ne pas déployer ce lot comme une encyclopédie complète.

1. Identifier l’hébergement réel, les accès autorisés, le reverse proxy, les ports utilisés et les applications voisines. Inspecter DNS/HTTPS en lecture seule. Aucun accès serveur n’est disponible dans cette session.
2. Sauvegarder les configurations et la version courante avant toute intervention. Tester le retour à cette version sur une instance isolée. Pour une base future, tester aussi sa restauration sur une base distincte ; ne jamais utiliser une base partagée par défaut.
3. Exécuter `npm test`, `npm run check:data`, `npm run build:static`, puis `node scripts/check-release.mjs artifacts/wow-forever-integre.html data/entries.json`. Si le magasin runtime est utilisé, le passer explicitement au contrôle.
4. Tester le dossier **dist/** sur un serveur HTTP isolé, puis Android/ordinateur, clavier, lecteurs d’écran et permissions. Vérifier les sources et traductions des fiches éventuelles. Ces tests navigateur restent à exécuter ; ils sont bloqués dans le sandbox de cette session.
5. Le `Dockerfile` prépare une image statique et `deploy/compose.static.yaml` propose un port loopback `127.0.0.1:3107` vers le port conteneur 8080. Vérifier qu’il est libre avant usage. Conteneur séparé, lecture seule et privilèges minimisés. Ces fichiers ne sont pas encore exécutés ni validés par une construction Docker.
6. Ne publier que le dossier statique `dist/` — ou `site/` de l’archive. **Ne jamais exposer sources/, runtime/, data/ ou les archives de sauvegarde.** Le site statique n’a besoin d’aucun secret. Les futurs secrets backend devront être placés dans le gestionnaire de l’hébergeur.
7. Après réussite effective des critères du cahier des charges et de l’audit de l’hébergement, demander la validation unique de mise en production. Ne pas modifier le DNS, le proxy existant ni le site public avant cet accord.
8. Déployer une version datée en conservant la précédente. Tester la syntaxe du proxy avant rechargement. Vérifier après bascule le nouveau site et les autres services, sans modifier leurs configurations.

## Retour arrière statique

Conserver la version précédente dans un répertoire ou une image distincte et sa configuration de proxy. Rebasculer vers ce répertoire ou cette image, après validation de la syntaxe du proxy, puis vérifier le site et les services voisins. Ne pas supprimer la version remplacée avant analyse. La rétention et les commandes exactes dépendront de l’hébergement identifié.

## Adaptateur Next.js, étape ultérieure

Il faudra d’abord installer les dépendances via le registre autorisé, générer et versionner le lockfile, contrôler les vulnérabilités, puis exécuter `npm ci`, `npm run typecheck`, `npm run build` et un démarrage isolé. Le Dockerfile livré concerne la variante statique, pas le serveur Next. Une stratégie de déploiement Next distincte sera nécessaire si ce runtime est retenu pour le backend.

## Sauvegardes PostgreSQL futures

La migration `db/001_initial.sql` est une proposition non exécutée et non branchée. Avant tout usage public, le schéma devra être aligné sur les attestations et empreintes du circuit documentaire, puis ses rôles et permissions testés. Le rôle SQL déclaré n’implémente pas une authentification.

Exemple de sauvegarde future : `pg_dump --format=custom --file=backup.dump "$DATABASE_URL"` depuis l’ordonnanceur de l’hébergeur, avec stockage chiffré et rétention définie. Restauration uniquement vers une base isolée vide : `pg_restore --dbname="$RESTORE_DATABASE_URL" --no-owner backup.dump`. Ces commandes ne constituent pas une sauvegarde ou une restauration de serveur testée.

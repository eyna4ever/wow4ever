# Synchronisation avec le wiki en ligne — v43d

Date : 25 novembre 2026 (Europe/Paris).

Cette branche aligne le dépôt `eyna4ever/wow4ever` sur la version actuellement
déployée sur [wowkipedia.com](https://wowkipedia.com) : **v43d**, release
`20261125T175344`, construite à partir de l’arbre v43b/v43c puis du paquet
`wow4ever-wiki-v43d.tar.gz`.

Aucun développement nouveau, aucune fusion, aucun déploiement n’accompagnent
ce commit. La branche `main` et la branche du brouillon Polestar
(`feat/polestar-import`, PR #1) ne sont pas modifiées.

## Empreintes vérifiées

| Élément | SHA-256 |
| --- | --- |
| Empreinte wiki v43d (fichiers de `wiki/`, chemins relatifs) | `5875d6be00b3d058195bd8000f0ea194b323ab5dfb78e8bb7eb91858421e8dd4` |
| Archive déployée `wow4ever-wiki-v43d.tar.gz` (478 fichiers, delta sur v43b) | `454a7aa35509e3fd09ff14a4a87a73088946c529af39b8b54e0aaab18c50a9db` |
| Script `deploy/production/update-v43d.sh` | `8ee4c1fc97a40f4b0cd62972d7944d473e0ae9ca7c015391d187ef6b8195a295` |
| Base wiki v43b (avant le delta v43d) | `c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517` |

Les 1940 fichiers de `wiki/` correspondent fichier par fichier à l’empreinte
v43d et aux 478 fichiers de l’archive (pages HTML, index de recherche, tests).
Les assets déjà présents dans l’arbre v43b/v43c complètent l’archive, qui
n’est qu’un delta.

Détails du paquet : [v43d/empreintes.json](v43d/empreintes.json),
[v43d/LIRE-MOI.txt](v43d/LIRE-MOI.txt), [v43d/RAPPORT-v43d.txt](v43d/RAPPORT-v43d.txt).

## Contenu ajouté ou mis à jour

- `wiki/` : site encyclopédique FR/EN en ligne (pages, assets, index de recherche, carte, page Sources et licences).
- `tests/wiki-baseline.json` et tests associés : référence d’empreinte v43d.
- `tools/` : outils de l’arbre déployé (empreinte de contenu, intégration).
- `community/` : application Flask qui accompagne le wiki sur le serveur (inchangée côté empreinte applicative depuis la v43b). Les pages communauté restent non publiées sur le site.
- `deploy/production/update-v43d.sh`, `rollback-v43d.sh`, `d43d.sh` : mise à jour et retour arrière (non exécutés ici).
- `outils/` : scripts de génération et d’importation par lot (v40b à v43d, métiers, bestiaire, complétion, collections).
- `pipeline/` : pipeline documentaire (scripts d’import, librairies, données de lots, entrées compilées v39, sources d’illustrations). Sans caches, sans `runtime/backups`, sans `dist` ni `node_modules`.
- `docs/sources/`, `docs/v43d/`, `docs/v21-elite/` : documentation technique, rapports et modèle d’import.

## Exclu volontairement

- Secrets : fichiers `.env`, clés, jetons, mots de passe, bases de comptes. Les seuls `.env.example` sont des modèles.
- Données personnelles : bases SQLite d’utilisateurs, journaux avec IP, en-têtes HTTP (`.hdr`/`.head`), identifiants Discord ou e-mails.
- Caches et binaires de construction : `runtime/backups`, `dist-v2`, `public`, `node_modules`, `__pycache__`, cache TACT/DB2 de collections-v41 (~1,2 Go), icônes générées.
- HTML brut de sites tiers (sources-brutes). Les lots structurés (JSON, TSV, XML) sont conservés.
- Brouillons de veille non publiés (dont la BD des Al'Aketh refusée et les sujets communauté/Stone Key restés hors ligne).
- L’archive `wow4ever-wiki-v43d.tar.gz` elle-même (contenu déjà présent dans `wiki/` + tests).
- Scripts d’envoi réseau (`nc/`) utilisés uniquement pour transférer le paquet sur le serveur.

## Limites de reproductibilité

Le wiki en ligne n’est plus généré d’un seul jet depuis le pipeline Node :
les lots v40 à v43d ont été appliqués par scripts Python successifs sur
l’arbre précédent. `pipeline/data/entries-runtime-v39.json` reflète l’état
compilé à la v39 (211 fiches). Les ajouts postérieurs sont dans
`pipeline/data/lots/` et dans `outils/`, et le résultat final vérifiable
est l’arbre `wiki/` (empreinte ci-dessus). Relancer toute la chaîne depuis
zéro ne reproduit pas à lui seul le site v43d sans rejouer ces lots dans
l’ordre, ce que ce commit ne fait pas.

# Validation

## Lot documentaire du 19 octobre 2026

- `npm test` exécuté après stabilisation des fichiers : **112 tests réussis, 0 échec, 0 ignoré**. La suite couvre notamment le rapport de couverture, la relecture privée, l’export SQLite et l’import des 36 notices.
- `npm run content:prepare` exécuté : import idempotent, rapports JSON/Markdown, dossier HTML, JSON des fiches, base SQLite et archive produits sans réseau ni publication. La reprise réelle reconnaît 36 doublons et n’en crée aucun.
- `node scripts/check-data.mjs runtime/entries.json` : **36 entrées, 0 publication, 0 erreur, 0 fiche signalée obsolète**.
- Archive réelle de relecture inspectée : **10 fichiers**, CRC et toutes les empreintes SHA-256 conformes. Le fichier HTML téléchargé correspond à celui du ZIP.
- Base SQLite réelle ouverte en lecture seule : `PRAGMA integrity_check` retourne `ok`, `foreign_key_check` ne retourne aucune anomalie, **36 brouillons et 12 catégories**.
- `npm run build:static` exécuté avec le magasin de travail rempli : **0 brouillon exporté**, 12 rubriques et 0 fiche publique. Le dossier de relecture demeure séparé du site.
- Lecture automatisée et vérifications documentaires ciblées effectuées ; aucune revue humaine ou validation en jeu n’est revendiquée. Le HTML de relecture est testé structurellement et pour l’échappement, sans nouveau test navigateur/Android.
- Aucun backend PostgreSQL hébergé ni sauvegarde de production n’a été testé. La démo reste privée et aucune nouvelle publication n’a été effectuée pour ce lot.

Le domaine et son certificat ont été confirmés actifs précédemment par Sites ; l’utilisateur a ensuite confirmé que la bonne version s’affichait. Les limites de navigateur/Next ci-dessous décrivent les essais historiques et ne remplacent pas ces constats distincts.

## Historique — intégration locale du 18 octobre 2026

État au **18 octobre 2026**. **69 tests automatisés réussis, 0 échec dans la suite Node.** La compilation statique a réussi. Le lot n’est pas prêt pour une mise en production : les essais de navigateur sont bloqués et la compilation Next.js n’a pas pu démarrer.

## Contrôles exécutés

| Contrôle | Commande ou méthode | Résultat observé |
| --- | --- | --- |
| Pipeline documentaire | `node --test --test-isolation=none tests/documentary.test.mjs` | 44 tests réussis ; import, déduplication, reprise, quotas, revue, correction, verrouillage, sauvegarde et restauration JSON dans des dossiers temporaires. |
| Catalogue public strict | `tests/public-catalog.test.mjs` dans la suite Node | 8 tests réussis ; refus des statuts non publiés, revues incomplètes ou périmées, doublons et étapes malformées ; absence de métadonnées privées dans les DTO. |
| Logique d’interface | `tests/ui-core.test.mjs` dans la suite Node | 8 tests réussis ; recherche et filtres, suggestions, liens HTTPS, stockage refusé ou corrompu, favoris, progression par révision et relations publiques. |
| Intégrité de livraison | `tests/release-integrity.test.mjs` dans la suite Node | 9 tests réussis ; structure HTML, liens internes, libellé de recherche, JSON échappé, chargement du magasin de travail, exclusion des brouillons, chemins ZIP et checksums. |
| Suite complète | `npm test` | 69/69 réussis, 0 échec. |
| Catalogue réel | `npm run check:data` | 0 entrée, 0 publication, aucune erreur d’intégrité. Aucune fiche de jeu artificielle ajoutée. |
| Construction statique | `npm run build:static` | Réussie : dossiers FR/EN, ressources locales, HTML autonome et rapport public générés. |
| HTML autonome construit | `node scripts/check-release.mjs artifacts/wow-forever-integre.html data/entries.json` | Réussi : 39 identifiants uniques, 12 catégories, 0 fiche, 1 script classique compilé ; ressources embarquées et catalogue conforme à la sélection stricte. |
| JavaScript et images | Contrôles syntaxiques Node ; inspection des assets et comparaison des pixels PNG/WebP | Syntaxe contrôlée ; les trois variantes WebP sans perte conservent dimensions et pixels des PNG. Provenance dans `ASSETS.md`. |
| Scripts Python | `python3 -m py_compile scripts/serve.py scripts/package-local.py scripts/export-preview.py` | Vérification syntaxique réussie. |
| Compilation Next.js | `npm run build` | **Échec de démarrage : code 127, `next: not found`**, dépendances absentes. Aucune compilation Next.js réussie déclarée. |
| Serveur HTTP local | `python3 scripts/serve.py --port 3000` | **Bloqué** par le sandbox : `PermissionError`, errno 1 à l’ouverture du socket. Aucun serveur démarré ; ce résultat n’est pas présenté comme un échec de navigation de l’application. |
| Navigateur Chromium | Tentative locale dans le sandbox | **Bloquée** : code 133, opération de socket refusée (`setsockopt: Operation not permitted`). Aucun parcours navigateur ni capture d’écran de l’application déclaré réussi. |

Les tests utilisent des données synthétiques uniquement en mémoire ou dans des répertoires temporaires supprimés ensuite. Ils ne valident ni la véracité des informations de jeu, ni une traduction éditoriale réelle, ni une permission de réutilisation documentaire.

## Contrôle de l’archive finale

Après génération de l’archive, exécuter :

```sh
node scripts/check-release.mjs artifacts/wow-forever-integre.html data/entries.json artifacts/deliveries/wow-forever-integration.zip
```

Ce contrôle a été **exécuté avec succès sur l’archive réelle** : 72 fichiers, chemins sûrs, CRC conformes, aucun dossier privé ni secret identifié par les règles du contrôleur ; le HTML autonome correspond à la version construite. L’archive inspectée pesait environ 22 Mo, pour environ 24,6 Mo décompressés ; ces tailles peuvent varier lors de la régénération finale de la documentation.

Le contrôle vérifie les tailles et CRC des fichiers, les chemins d’extraction, l’absence de liens symboliques et de dossiers privés, la présence de `site/index.html` et de `sources/README.md`, ainsi que l’identité du fichier HTML autonome avec la version construite. Le script d’empaquetage vérifie aussi les CRC par `zipfile.testzip()`. Réexécuter ce contrôle après toute régénération du paquet ; les tests unitaires du contrôleur ne remplacent pas l’inspection du livrable réel.

Si le magasin `runtime/entries.json` devient la source de construction, passer ce même fichier en deuxième argument du contrôle à la place de `data/entries.json`.

## Limites de la validation

Le balisage a été relu : lien d’évitement, champ de recherche étiqueté, boutons natifs, états de sélection, noms accessibles traduits, destinations de focus, panneaux nommés et règle de réduction des animations sont présents. Ce constat et les tests structurels ne constituent pas un audit WCAG, un contrôle de contraste sur images ou un essai avec lecteur d’écran.

Ne sont pas vérifiés : rendu et débordements sur Android réel, interactions complètes dans un navigateur, clavier et focus rendus, persistance après fermeture du navigateur, performances/Lighthouse, cache PWA, démarrage HTTP/Next.js, authentification et rôles serveur, base PostgreSQL, sauvegardes planifiées, restauration de production, DNS, HTTPS et coexistence avec les applications de l’hébergeur.

Les illustrations représentent des concepts fantasy. Aucune carte réelle, coordonnée, classe, zone ou statistique n’est confirmée par une image. Le site affiche l’état vide du catalogue et explique les services encore à connecter.

## Reprise des vérifications

```sh
npm test
npm run check:data
npm run build:static
node scripts/check-release.mjs artifacts/wow-forever-integre.html data/entries.json
```

Dans un environnement disposant des dépendances et d’un navigateur autorisé, poursuivre par la compilation Next.js, le démarrage isolé, les parcours ordinateur/Android et les audits. Aucune autorisation de production n’est demandée sur la seule base de cette intégration locale.

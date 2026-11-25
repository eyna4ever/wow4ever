# Historique du premier aperçu local autonome

Le premier aperçu décrit ci-dessous a été remplacé par l’intégration fantasy réelle. Voir `docs/INTEGRATION.md` et `docs/VALIDATION.md` pour la livraison actuelle, ses 69 tests et ses limites. `preview/index.html` est désormais une copie générée de cette intégration.

Ouvrir `preview/index.html` dans un navigateur. Le fichier inclut son CSS et son JavaScript : aucune installation ni connexion requise. Une copie est livrée sous le nom `wow-forever-apercu.html`.

Cet export montre le socle actuel avec 12 rubriques et 0 fiche de jeu : bascule FR/EN, sélection d'une rubrique, recherche sur catalogue vide, filtre favori vide, réinitialisation et console documentaire en lecture seule. Aucun contenu de test synthétique n'est ajouté. Il ne démontre pas les fiches, les favoris enregistrés ni la progression d'un guide réel. Il ne remplace pas le démarrage Next.js et n'est pas un déploiement.

Génération : `python3 scripts/export-preview.py` depuis cet environnement. Le script dépose aussi une copie dans `artifacts/deliveries/` (ou `--output-dir`, ou `WOW_FOREVER_OUTPUT_DIR`).

Contrôles exécutés le 2026-10-18 :

- PASS : export HTML autonome et analyse de sa structure.
- PASS : syntaxe du JavaScript intégré (`node --check`).
- PASS : 44 tests du pipeline documentaire, 0 échec (`node --test --test-isolation=none tests/documentary.test.mjs`).
- PASS : contrôle du catalogue vide, aucune erreur (`node scripts/check-data.mjs`).
- BLOCKED : lancement Chromium pour vérification visuelle et interactions, restriction de sockets du sandbox (`setsockopt: Operation not permitted`). Aucune capture réalisée ; aucun test Android/navigateur déclaré réussi.
- BLOCKED : installation des dépendances et démarrage Next.js, proxy inaccessible depuis les commandes sandboxées. Les tentatives précédentes d'autorisation réseau ont été interrompues ; aucun téléchargement réussi.
- NOT VERIFIED : domaine public, DNS/HTTPS et hébergement. Aucun site Sites existant retrouvé dans le compte connecté. Aucun déploiement effectué.

Le script de contrôle navigateur `scripts/check-preview.cjs` est fourni pour réexécution dans un environnement autorisant Chromium. Il emploie l'installation Playwright de cet environnement ; ce chemin doit être adapté sur une autre machine.

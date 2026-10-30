# Validation

## Tests serveur

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Bases temporaires indépendantes, jamais la base de prévisualisation ni la production. Les identités et réponses Discord sont simulées. Le test de conservation compare les 100 pages bilingues aux empreintes SHA-256 du manifeste `tests/wiki-baseline.json`, généré depuis le commit initial. Il fonctionne aussi dans une archive sans `.git`. Dans un clone Git complet, il vérifie en plus le manifeste contre les blobs du commit initial (ne pas utiliser un historique tronqué pour cette vérification indépendante). Le manifeste n’est pas une signature d’authenticité de l’archive.

## Navigateur et accessibilité

```bash
.venv/bin/pip install -r requirements-dev.txt
npm --prefix qa ci --cache /tmp/wow4ever-npm-cache
.venv/bin/python -m playwright install chromium
.venv/bin/python tests/browser_checks.py
```

Si Chromium est installé par le système, définir `BROWSER_EXECUTABLE=/usr/bin/chromium`. `AXE_PATH` permet de sélectionner une installation axe-core locale. Aucun code du CDN n’est chargé dans le produit. Le script utilise son propre serveur sur `127.0.0.1:8015`, une base temporaire et des comptes QA exclusivement internes à cette base ; ils sont supprimés à la fin.

Les parcours fonctionnels s’exécutent avec la CSP réelle. Seul le contexte d’audit axe autorise l’injection locale du moteur de test. Les contrôles couvrent 320, 390, 768 et 1440 pixels, la navigation clavier vers le contenu, la création/édition/citation/réaction/suivi/favori/signalement/modération et les rôles. Le résultat est écrit dans `test-results/browser-checks.json` (non versionné).

axe-core ne démontre pas à lui seul une conformité WCAG : recette lecteur d’écran, zoom, navigation clavier complète et vérification de toutes les pages restent nécessaires.

## Audits de sécurité

Dans un environnement d’outillage séparé :

```bash
pip-audit -r requirements.lock --no-deps --disable-pip
bandit -r community
```

Toutes les dépendances transitives du runtime sont épinglées dans `requirements.lock`. L’audit doit être renouvelé à chaque livraison et régulièrement ensuite. Les constructions SQL détectées par Bandit sont analysées dans `docs/SECURITY.md` : aucune entrée utilisateur n’y devient un identifiant SQL. Conserver les rapports, même lorsqu’un résultat nécessite un examen manuel.

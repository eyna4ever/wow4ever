# Archive de travail pour SuperGrok

1. Joindre ce ZIP à SuperGrok et lui demander de lire `PROMPT-SUPERGROK.md`, puis d’analyser et corriger la copie isolée.
2. `source/` contient le code, les tests, les scripts, les lots documentaires et les références graphiques. Il n’y a ni historique Git ni identité de production active.
3. Ouvrir `apercu-site.html` pour voir l’interface réelle sans installation. Le catalogue public contient 0 fiche ; les 36 notices restent en brouillon.
4. Ouvrir `documentation/relecture.html` pour consulter les 36 notices FR/EN. Ce dossier privé inclut JSON, SQLite et rapport de couverture. Il ne doit pas être servi comme site public.
5. Lire `ETAT-VERIFIE.json` et `verification/` pour les contrôles réellement exécutés le 24 octobre 2026. 112 tests passent dans une copie isolée du code transmis. La reconstruction de l’aperçu est identique.

## Commandes locales depuis source/

Node.js 24 et Python 3 suffisent pour la partie statique et documentaire, sans installation de dépendances :

```sh
npm test
node scripts/import-library.mjs --dry-run
node scripts/import-library.mjs
node scripts/check-data.mjs runtime/entries.json
node scripts/content-review.mjs --output artifacts/relecture.html
node scripts/export-content-sqlite.mjs --output artifacts/wiki.sqlite
npm run build:static
```

Les anciens scripts `prepare-content.mjs`, `package-local.py` et `export-preview.py` utilisent un chemin de téléchargement propre à l’ancien environnement. Cela fait partie des points de portabilité à corriger ; les commandes individuelles ci-dessus utilisent des chemins relatifs. Les dépendances Next.js ne sont pas installées et leur compilation n’a pas été exécutée ici.

## Confidentialité, graphisme et limites

Les secrets, accès, identifiants de production, preuves DNS, historiques Git et anciens journaux de déploiement sont exclus. Le modèle `.env.example` contient uniquement une valeur localhost `CHANGE_ME`. Les documents neutralisés sont recensés dans le manifeste. Aucun accès au site distant ni autorisation de le modifier n’est donné par cette archive.

Les deux PNG de `source/design/` sont des références de conception ; ils ne prouvent pas le rendu du code. Les illustrations utilisées par le site sont fournies en WebP sans perte. Les PNG d’assets identiques décodés ne sont pas dupliqués. La provenance et les limites de droits sont décrites dans `source/docs/ASSETS.md`.

Les faits viennent d’annonces et de bêta consultées le 19 octobre. Ils doivent être réexaminés au 24 octobre, particulièrement l’état de la bêta annoncé jusqu’au 21 octobre. L’identité éditoriale du wiki reste à confirmer par son propriétaire. Aucune autre IA ne doit signer une validation humaine ou publier les brouillons pour remplir artificiellement le site.

Demander en retour : code corrigé, rapport P0/P1/P2, tests réellement exécutés et nouvelle archive ZIP. Ne pas demander une publication sur le site actif.

# Intégration de la conception V2.1

L’interface fantasy a été intégrée dans le projet le 18 octobre 2026 : panorama d’accueil, recherche centrale, blason original, encadrements médiévaux, bandeau parchemin, six cartes illustrées et accès aux douze rubriques. Les textes restent en HTML et se traduisent en français et en anglais. Les illustrations sont décoratives et ne documentent pas le jeu.

Cette livraison est une intégration locale. Aucun déploiement, changement DNS, accès à l’hébergement ou remplacement d’application existante n’a été effectué. Le catalogue comporte **0 fiche documentée et 0 fiche publiée**. Les cartes, comptes et contributions affichent leur état de préparation.

## Sources de l’interface

| Chemin | Rôle |
| --- | --- |
| `public/wiki/template.html` | Structure de page commune, navigation et commandes accessibles. |
| `public/wiki/site.css` | Direction noire et dorée, ornements, parchemin, adaptations mobile et réduction des animations. |
| `public/wiki/app.js` | Contrôleur partagé : navigation, FR/EN, recherche, filtres, panneaux et état personnel. |
| `lib/ui-core.mjs` | Fonctions testables de recherche, liens, favoris et progression. |
| `lib/public-catalog.mjs` | Sélection documentaire stricte côté serveur ou construction. |
| `lib/site.mjs` | Chargement du catalogue, rendu commun et sérialisation sûre du JSON. |
| `app/wiki.tsx` | Adaptateur Next.js du même rendu ; compilation Next.js restant à vérifier. |
| `public/wiki/assets/` | Illustrations originales générées, variantes WebP sans perte et ornements SVG locaux. |

Voir [ASSETS.md](ASSETS.md) pour la provenance des images. Aucun CDN ni police distante n’est nécessaire. Les variantes WebP conservent les dimensions et les pixels des PNG ; les originaux restent dans les sources. La taille des illustrations impose encore une mesure des performances sur un appareil réel.

## Utilisation locale

Ouvrir `wow-forever-integre.html` dans un navigateur après téléchargement. Ce fichier embarque ses images, son CSS, son catalogue public et son JavaScript classique ; il ne dépend pas d’un serveur pour charger ses ressources.

Pour reconstruire le dossier statique et le fichier autonome, Node.js 24 suffit, sans installer les dépendances Next.js :

```sh
node scripts/build-static.mjs
```

Résultats : `dist/` pour un serveur HTTP statique, `artifacts/wow-forever-integre.html` pour l’ouverture directe, et `artifacts/public-report.json` pour le bilan du catalogue exporté. Les routes statiques sont `/`, `/fr/` et `/en/`. Le dossier `dist/` utilise des modules JavaScript ; le servir par HTTP au lieu de l’ouvrir en `file://` :

```sh
python3 scripts/serve.py --port 3000
```

Le serveur fourni écoute uniquement `127.0.0.1`. Sa tentative de démarrage dans cet environnement a été bloquée par l’interdiction des sockets ; le démarrage reste à vérifier dans un environnement les autorisant. Pour préparer l’archive locale :

```sh
python3 scripts/package-local.py
```

L’archive comporte le fichier HTML autonome, le dossier `site/` prêt à servir et le dossier `sources/` avec documentation et tests. **Sur un hébergement, servir uniquement `site/`** : le dossier `sources/` n’est pas une racine web. Les secrets, données `runtime/`, dépendances installées et dossiers techniques sont exclus du paquet.

## Comportements intégrés

- Recherche instantanée avec normalisation des accents, suggestions et filtres combinables de catégorie/favoris.
- Sélection des douze rubriques, menu mobile, bascule FR/EN et panneaux d’information.
- Présentation des futures fiches avec description, références, historique public et relations entre publications.
- Favoris et étapes de guides enregistrés sur cet appareil ; progression propre à chaque révision du guide.
- État de stockage indisponible signalé sans bloquer la consultation.
- Atelier documentaire public en lecture seule et explication de l’état des comptes, cartes et contributions.

Les fiches, favoris et étapes sont exercés avec des fixtures isolées dans les tests. Aucune fixture n’est ajoutée au catalogue livré. Avec le catalogue actuel vide, les parcours de fiches et de guides ne sont pas démontrables sur des données de jeu réelles.

## Frontière de publication

`sitePayload()` lit le magasin local `runtime/entries.json` s’il existe, sinon la graine `data/entries.json`. Un magasin courant corrompu provoque une erreur, sans repli silencieux vers une ancienne graine.

`selectPublicEntries()` retient exclusivement des publications uniques, valides, dont la revue humaine correspond à l’empreinte actuelle du contenu et confirme l’identité du jeu, les droits et les traductions. Les étapes optionnelles doivent être bilingues et bornées. Le résultat contient seulement des champs publics autorisés ; attestations internes, reçus d’import, champs arbitraires et noms d’acteurs ne sont pas exportés. Les relations vers des brouillons sont retirées.

L’approbation locale est liée à une empreinte de contenu ; elle n’est pas une signature cryptographique ni une authentification de compte. Les procédures de revue et de restauration sont décrites dans [PIPELINE.md](PIPELINE.md). Le JSON intégré est échappé afin qu’un texte contenant `</script>` reste du texte.

## Suite avant production

L’identité cible du jeu, le contenu initial sourcé et la validation humaine restent nécessaires. Authentification, rôles serveur, contributions modérées, réputation, PostgreSQL connecté, cartes avec coordonnées vérifiées, comparateurs et PWA avec cache ne sont pas livrés dans ce lot. Un HTML autonome embarqué ne constitue pas une PWA hors ligne.

Il reste à exécuter la compilation Next.js avec ses dépendances, les parcours dans un vrai navigateur Android et ordinateur, les audits d’accessibilité et de performance, puis l’inventaire de l’hébergement, HTTPS, sauvegardes et retour arrière isolé. La restauration JSON est testée en répertoire temporaire ; aucune restauration de serveur ou de PostgreSQL n’est attestée. Voir [VALIDATION.md](VALIDATION.md) et [DEPLOYMENT.md](DEPLOYMENT.md).

La validation unique de mise en production ne doit être demandée qu’après résolution de ces points. Aucun achat de serveur ni service payant n’a été engagé par les scripts de cette livraison.

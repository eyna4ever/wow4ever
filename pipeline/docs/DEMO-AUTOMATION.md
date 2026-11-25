# Démo privée : préparation automatique et publication Sites

La préparation locale et la publication sont deux opérations distinctes. `scripts/prepare-demo.mjs` ne contacte aucun service, ne lit aucune identité Sites et n'utilise aucun jeton. Il ne déploie rien, ne modifie aucun DNS et ne touche pas au domaine de production.

## Préparer une version

Depuis la racine du projet, avec Node.js 24 :

```sh
node scripts/prepare-demo.mjs
```

Le script exécute successivement les tests Node, le contrôle documentaire, la construction statique, puis le contrôle de la livraison HTML autonome. Un échec interrompt le circuit et conserve les anciennes versions. Le magasin `runtime/entries.json`, s'il existe, est utilisé pour les deux contrôles documentaires comme pour la construction ; sinon le magasin initial `data/entries.json` est utilisé. Aucun brouillon ne doit apparaître dans les trois entrées HTML publiques FR/EN.

Après les contrôles, le script prépare :

- `artifacts/demo-releases/sha256-<empreinte>/site/` : copie isolée des seuls fichiers publics autorisés, à transmettre à Sites.
- `release.json` à côté de `site/` : inventaire SHA-256 et taille de chaque fichier, contrôles effectivement exécutés, nombre de fiches publiées et limites des contrôles.
- `site-demo.zip` à côté de `site/` : archive portable et reproductible des seuls fichiers publics, directement extractible comme site statique.
- `artifacts/demo-latest.json` : rapport local et chemin de la dernière préparation réussie.

L'empreinte identifie les octets du site et leurs chemins, sans date variable. Une sortie inchangée réutilise le même instantané après vérification ; elle n'écrase jamais son contenu. Toute modification détectée dans un instantané existant provoque un échec. Cette immutabilité est vérifiée par empreinte ; elle ne remplace pas des permissions de stockage ou un stockage d'archives protégé. Le ZIP n'embarque ni sources, ni données éditoriales, ni identité de déploiement, ni secret. Les fichiers de rapport restent en dehors du dossier public.

```sh
node scripts/prepare-demo.mjs --verify artifacts/demo-releases/sha256-<empreinte>
```

Cette commande vérifie l'inventaire, les empreintes et la correspondance exacte entre ZIP et instantané. Elle n'exécute pas à nouveau les tests applicatifs et ne vérifie pas un site distant.

## Publier et mettre à jour la démo

La publication privée passe par les outils Sites connectés, sous le contrôle du propriétaire de la session. Le propriétaire doit préparer et vérifier la version ci-dessus, publier exactement son dossier `site/`, puis conserver l'URL et l'identifiant de déploiement retournés par Sites. Il doit contrôler l'URL HTTPS ainsi que les interactions dans un navigateur et la visibilité réellement appliquée. Une métadonnée `noindex` empêche l'indexation volontaire ; elle ne constitue pas un contrôle d'accès.

Pour chaque mise à jour : relancer la préparation, vérifier l'instantané, puis publier ce nouvel instantané dans la même identité Sites. Le dossier `.openai` et l'identité de site restent la propriété du circuit Sites et ne sont ni créés ni modifiés par le script. Conserver l'ancienne empreinte et son identifiant de déploiement permet de republier une version antérieure vérifiée si nécessaire. La restauration distante et sa disponibilité doivent être contrôlées après publication ; la présence d'un instantané local ne prouve pas un retour arrière distant réussi.

Il n'existe pas ici d'identifiant API permanent ni de raccordement CI documenté permettant à GitHub Actions de publier vers Sites sans session. Aucun workflow ne prétend le contraire. La préparation est automatique en une commande ; la publication par les outils Sites et ses mises à jour effectives doivent être distinguées d'un déploiement continu sans intervention. Un véritable déclenchement à chaque changement nécessitera un dépôt distant et un mode d'authentification de publication officiellement disponible. Le propriétaire complète le bilan de session avec l'URL, la visibilité et les contrôles réellement observés.

## Limites à conserver dans le bilan

La version statique présente les fonctions disponibles dans l'intégration : navigation, langue, filtres et états locaux du navigateur. Un catalogue vide reste vide. Les futurs comptes, la modération serveur, PostgreSQL, la validation documentaire humaine et le moteur Next.js complet ne deviennent pas opérationnels par une publication statique.

Les tests de préparation portent sur l'intégrité de la livraison, la protection des données éditoriales, les empreintes, l'archive et le refus des sorties non approuvées. Les contrôles visuels Android/ordinateur, HTTPS, accès privé et comportement réel en navigateur doivent être exécutés séparément. Si l'environnement interdit les sous-processus Node, la commande échoue explicitement et ne marque aucun contrôle comme réussi ; le propriétaire peut exécuter les commandes de contrôle accessibles dans l'environnement, mais ne doit pas annoncer une préparation automatique complète réussie tant que ce script n'a pas pu terminer.

Aucun coût réseau ou de service n'est engagé par le script local. Les conditions et quotas de l'hébergement Sites doivent être vérifiés dans le service avant d'annoncer un hébergement sans frais.

## Raccordement Sites de cette démo

L’espace privé a été créé avec l’identifiant persistant de `.openai/hosting.json`. La source n’est pas encore publiée tant qu’un résultat de déploiement Sites ne le confirme pas. L’option native de publication sur push a répondu `publish_on_push_accepted: false` : aucune CI de publication sur push n’est active pour ce compte.

Le helper officiel `site-workflow.mjs` n’est pas installé dans cet environnement, après recherche locale et via les ressources disponibles. Le script `scripts/push-demo-source.py` utilise donc le protocole Git standard pour synchroniser le dépôt **après** préparation et commit. Il reçoit l’identifiant temporaire uniquement sur l’entrée standard masquée, garde le jeton en mémoire, le transmet à Git via sa configuration de processus et n’enregistre ni n’affiche ce jeton. Il vérifie que le dépôt correspond à l’identité Sites locale, refuse tout écrasement d’historique et confirme le commit distant après envoi. Ce script n’est pas présenté comme le helper officiel.

`npm run archive:demo` vérifie l’instantané préparé et crée `artifacts/wow-forever-sites.tar.gz` avec les seuls fichiers publics et le manifeste Sites. Le propriétaire utilise ensuite les outils Sites pour enregistrer et publier exactement le commit synchronisé et cette archive. Une version enregistrée permet le retour arrière via son identifiant, sans modifier le DNS ni les autres applications.

Cette préparation et ce transport ne fabriquent aucune API de publication permanente. La mise à jour se fait via une session Sites autorisée ; une automatisation CI sans session reste non configurée.

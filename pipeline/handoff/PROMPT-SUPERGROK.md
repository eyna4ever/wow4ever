# Mission SuperGrok — audit et correction de WoW Forever Wiki V2.1

Tu reçois l’archive de travail de **WoW Forever Wiki V2.1**. Analyse le projet et corrige les défauts accessibles dans une copie isolée. L’objectif est une encyclopédie FR/EN fiable, utilisable sur Android et ordinateur, avec une architecture permettant l’enrichissement documentaire et une mise en ligne reproductible.

Travaille avec les exigences d’une équipe senior réunissant architecture/full-stack, documentation MMORPG, vérification des sources, UX/accessibilité/SEO/i18n et sécurité/DevOps/QA. Si ton environnement permet une délégation réelle, répartis des tâches bornées sans écritures concurrentes sur les mêmes fichiers. Sinon, examine successivement ces angles. **Des rôles simulés ne prouvent ni la présence d’une équipe réelle ni l’exécution d’outils ou de tests.**

## Contexte établi et limites

- Domaine de démonstration : `https://wow4ever.raveforge.eu`. Le projet est indépendant de WORLD OF HACKCRAFT, ForgeCraft et RaveForge, et n’est pas affilié à Blizzard.
- Une démo privée a été publiée via un hébergement géré Sites. L’activation du domaine et de HTTPS a été confirmée lors de la session du 19 octobre 2026 ; l’utilisateur a ensuite confirmé que la bonne version s’affichait. Ce sont des constats historiques, pas un contrôle de disponibilité au jour de ton audit.
- Le frontend réel est en HTML/CSS/JavaScript, avec un rendu partagé, un export statique et un adaptateur Next.js/TypeScript. Ne présente pas la simple présence de Next.js dans `package.json` comme une compilation réussie.
- Les comptes applicatifs, les rôles serveur, PostgreSQL connecté, la modération communautaire, la réputation, les cartes à marqueurs vérifiés, les comparateurs complets et la PWA restent à réaliser ou à valider. L’atelier documentaire visible dans le site est en lecture seule ; il ne constitue pas une administration connectée.
- Le dernier lot contient **36 notices FR/EN en brouillon**, couvrant les douze rubriques, avec **24 URL de référence correspondant à 14 articles primaires distincts**. Cela ne constitue pas une encyclopédie complète. Les variantes FR/EN d’un article ne sont pas des confirmations indépendantes.
- Le périmètre candidat est **World of Warcraft: Forever de Blizzard, annonces et bêta consultées le 19 octobre 2026**. Le propriétaire n’a pas encore confirmé explicitement que son wiki vise ce jeu/version. Conserve cette incertitude ; aucune donnée Retail, Classic, de serveur privé ou de WORLD OF HACKCRAFT ne doit être transposée par analogie.
- La date de préparation de cette transmission est le **24 octobre 2026**. Les sources documentaires doivent être revalidées : l’annonce de bêta incluse dans le lot prévoyait le 21 octobre comme dernière journée complète de test. Ne décris donc pas automatiquement la bêta comme encore ouverte et ne transforme pas une annonce en constat actuel.
- Le compte rendu du 19 octobre documente **112 tests réussis et 0 échec**. Les vérifications réexécutées le **24 octobre** pour cette archive sont recensées dans `ETAT-VERIFIE.json` et `verification/`, notamment dans une copie isolée du code transmis. Reproduis les tests dans ton propre environnement ; ne réutilise pas ces bilans comme preuve d’une exécution chez toi.

## Exigences à préserver

Conserve la direction artistique fantasy premium noire et dorée, les cadres médiévaux, les textures parchemin, l’accueil immersif, la recherche centrale et les cartes de catégories. Les composants doivent rester du vrai HTML interactif et accessible, avec des textes traduisibles ; une image de maquette n’est pas une interface. Les illustrations d’ambiance ne constituent aucune preuve documentaire. Si une référence graphique indispensable manque, signale-la avant de prétendre reproduire exactement la maquette validée.

Les douze rubriques sont : classes/spécialisations, races/factions, zones/exploration, donjons/raids, métiers/artisanat, objets/équipements, quêtes/progression, PvP/activités, créatures/boss, guides, actualités/annonces, glossaire/références.

Chaque fiche doit conserver identifiant stable, FR/EN, catégorie/sous-catégorie, description, sources datées et versionnées, statut, date de mise à jour, révision, relations et historique. Les nouvelles données non vérifiées restent en brouillon. Aucun objet, statistique, quête, classe, taux de butin, coordonnée ou mécanique ne doit être inventé pour remplir une catégorie.

La sélection publique stricte et le circuit de revue sont des exigences fonctionnelles : **ne change pas les statuts ou les attestations à la main pour rendre le site artificiellement rempli**. Une autre IA n’est pas le relecteur humain demandé. Ne signe aucune attestation humaine à la place du propriétaire. Ne désactive pas les tests qui protègent ces règles.

Respecte les licences et les conditions de collecte. Utilise les sources primaires en priorité, rédige des synthèses originales, conserve les URL et les dates d’accès, et signale les contradictions. Une contradiction FR/EN sur Flèches multiples/Multi-Shot et Visée/Aimed Shot est déjà recensée dans `data/research/forever-classes-sources.json` ; le détail litigieux a été exclu des notices.

## Méthode d’audit et de correction

1. **Inventaire reproductible.** Lis d’abord les consignes présentes dans le projet, le README, `docs/CONTENT-LIBRARY.md`, `docs/PIPELINE.md`, `docs/VALIDATION.md`, les preuves `data/research/` et la structure des scripts/tests. Distingue source, export web, brouillons et documents historiques. Signale les pièces absentes et les limites d’outillage.
2. **État initial mesuré.** Lance les contrôles disponibles, puis reproduis chaque défaut avant de conclure. Utilise une copie locale ; ne modifie aucun site distant. Relève les versions de Node/Python, les commandes, codes de sortie et résultats. Si un outil manque, note « non exécuté » et la cause.
3. **Diagnostic P0/P1/P2.** Pour chaque constat, indique fichier/ligne, preuve, conséquence, correction proposée et test pertinent. P0 : fuite de secrets/brouillons, contournement des droits ou revue, perte de données, faille exploitable. P1 : fonctionnalité principale cassée, incohérence documentaire, migration/import non fiable, blocage mobile/accessibilité. P2 : amélioration non bloquante. Ne classe pas une fonctionnalité honnêtement indiquée comme absente parmi les régressions sans distinguer les deux.
4. **Corrections concrètes.** Corrige en lots limités, garde des sauvegardes avant les mutations de données et préserve les identifiants/historiques. Adapte les chemins absolus liés à l’environnement lorsque cela améliore la portabilité, sans exposer les données privées. Réutilise les outils déjà présents. Ne réécris pas l’architecture entière sans défaut démontré ou besoin explicite.
5. **Validation après correction.** Exécute les tests utiles aux changements ; vérifie compilation statique, sélection des publications, déduplication/reprise, intégrité SQLite, sauvegarde/restauration, liens et traductions. Si un navigateur est disponible, teste navigation mobile/ordinateur, clavier, focus, recherche, filtres, favoris et progression. Un test structurel ne remplace pas un essai Android ou un audit WCAG. Distingue également test unitaire, test d’intégration et fonctionnement distant réel.
6. **Livraison exploitable.** Fournis le code corrigé, les migrations/scripts nécessaires, le README actualisé, le rapport de corrections et une archive ZIP vérifiée. Sépare clairement le dossier à servir sur le web des sources, brouillons, bases locales et outils de relecture.

## Commandes de départ

Node.js 24 et Python 3 permettent de travailler sur la partie statique et documentaire sans dépendances réseau. Vérifie les scripts et adapte les chemins à ton environnement avant exécution.

```sh
npm test
npm run content:import -- --dry-run
npm run content:prepare
node scripts/check-data.mjs runtime/entries.json
npm run build:static
node scripts/check-release.mjs artifacts/wow-forever-integre.html runtime/entries.json
```

`content:prepare` effectue un import local avec sauvegarde, puis génère les rapports, le dossier HTML privé, le JSON et un export SQLite. SQLite est une base locale transportable, pas PostgreSQL hébergé. Ces commandes ne publient pas le contenu sur le site.

Pour l’adaptateur Next.js, inspecte d’abord les dépendances et les accès disponibles. Si l’installation est possible et pertinente, génère un lockfile, contrôle les dépendances et exécute typecheck/build. N’annonce pas ces contrôles réussis s’ils n’ont pas eu lieu. Les restrictions réseau de l’ancien environnement ne prouvent pas que ton environnement aura les mêmes limites.

## Autorisations et autonomie

Effectue de façon autonome les lectures, analyses, corrections et tests locaux réversibles dans la copie reçue. Ne demande que les informations réellement indispensables ; poursuis en parallèle le travail indépendant de leurs réponses. Les questions ouvertes ne deviennent pas des décisions par défaut.

**L’archive ne donne aucun accès ni autorisation d’agir sur la production.** Ne modifie ni DNS, ni site déployé, ni audience de partage, ni autres services hébergés ; ne déploie rien et n’achète aucun service sans instruction explicite du propriétaire. Ne sollicite pas de mot de passe ou de clé privée dans le chat et ne recherche pas des secrets dans d’autres projets.

Si une opération distante devient nécessaire, prépare d’abord un résultat local testé, une procédure de déploiement et un retour arrière. Soumets ensuite une seule demande de validation concrète pour cette opération précise. Ne traite pas une correction de code comme une approbation de publication documentaire.

## Résultat attendu

Retourne :

- Un rapport des défauts P0/P1/P2, avec preuves et statut corrigé/restant.
- Les fichiers corrigés et une explication concise de chaque changement important.
- Les tests réellement exécutés, réussis, échoués ou non exécutés, avec les limites.
- Le décompte des notices par catégorie et statut ; ne prétends pas à une couverture complète sans inventaire de référence.
- Les lacunes documentaires et fonctionnelles restantes, les coûts éventuels, et la préparation réelle au déploiement.
- Une archive ZIP corrigée, un manifeste de fichiers/empreintes et des instructions simples pour l’ouvrir ou reconstruire le projet.
- Une seule action indispensable du propriétaire, s’il en reste une ; explique précisément ce qu’elle débloque.

Commence par inspecter l’archive. Ne t’arrête pas à un plan ou à une promesse de compétence : livre les corrections accessibles, leurs preuves et le paquet final, sans présenter une hypothèse, un rôle simulé ou un test non exécuté comme un résultat.

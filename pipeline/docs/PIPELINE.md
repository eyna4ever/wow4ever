# Pipeline documentaire local

Le pipeline fonctionne sans réseau, abonnement ni service de traduction. Il accepte un fichier JSON local obtenu avec autorisation, contrôle sa structure, prépare des brouillons et conserve les décisions humaines. Il ne certifie pas les faits du jeu. L'identité exacte de WoW Forever doit être établie avant toute approbation.

## État des étapes

| Étape | Fonctionnement livré |
| --- | --- |
| Recherche, extraction | Réalisées en amont avec autorisation. Aucun robot de collecte ni téléchargement n'est activé. |
| Normalisation | Unicode NFC, espaces extérieurs retirés, URL HTTPS canoniques, références et relations identiques dédupliquées. Aucun texte ou chiffre de jeu n'est créé. |
| Déduplication et reprise | Empreinte SHA-256 du document source, y compris son statut initial. Le même lot est reconnu après interruption, même s'il provenait d'une publication ou a été approuvé localement depuis. |
| Contrôles | Schéma bilingue, dates réelles, droits référencés, versions des sources, relations, unicité des identifiants et cohérence des révisions. Les désaccords sur un même ID sont signalés; le contenu existant est conservé. |
| Traduction | Deux textes FR/EN obligatoires. Leur qualité reste à vérifier par un humain. Aucune traduction automatique n'est présentée comme validée. |
| Prévisualisation | La CLI affiche la fiche entière, ses références, son historique et les erreurs de la base. |
| Validation et publication | Actions humaines séparées. Chaque décision a un auteur, un motif et une révision; l'approbation est liée à l'empreinte du contenu. |
| Corrections et retour arrière | Révision explicite revenant en brouillon, sauvegarde avant écriture, restauration contrôlée par checksum. |

Les contradictions détectées automatiquement concernent les versions des sources et les documents distincts portant le même ID. Une contradiction de sens entre deux sources exige une lecture humaine. Les seuils d'ancienneté signalent les fiches ou références datant de plus de 180 jours; ils ne prouvent pas qu'un fait est obsolète.

## Données et invariants

`data/entries.json` est la graine du projet. Les écritures locales utilisent `runtime/entries.json`; la graine reste intacte. Le chargeur du site doit sélectionner ce magasin et filtrer les fiches valides publiées avant de les afficher. Les brouillons ne doivent jamais être exportés dans un cache public.

Un lot est un tableau JSON de fiches. Une correction contient une seule fiche JSON.

| Champ | Règle |
| --- | --- |
| `id` | Identifiant stable de 3 à 100 caractères, minuscules ASCII, chiffres et tirets. Il ne change pas lors d'une correction. |
| `title`, `description` | Objets contenant chacun un texte non vide `fr` et `en`. |
| `category` | `classes`, `races`, `zones`, `instances`, `professions`, `items`, `quests`, `pvp`, `creatures`, `guides`, `news` ou `glossary`. |
| `subcategory`, `gameVersion` | Textes obligatoires. `gameVersion` doit identifier précisément la version et le projet concernés, sans assimiler d'autres serveurs à WoW Forever. |
| `status` | `draft`, `review`, `verified` ou `published`. Tout import revient à `draft`, retire la revue externe et remet `identityConfirmed` à `false`. |
| `version`, `updatedAt` | Révision entière positive et date ISO valide. Chaque décision ou correction locale incrémente la révision. |
| `sources` | De 1 à 20 références comprenant `url` HTTPS sans identifiants, `license` et `accessedAt`. `title` est facultatif. Une `gameVersion` omise hérite de celle de la fiche à l'import; une version explicite différente bloque la fiche. |
| `relations` | Tableau d'identifiants existants, uniques, différents de l'ID de la fiche. Les références futures dans le même lot sont autorisées. |
| `history` | Historique non vide comprenant `actor`, `note`, `at`, et éventuellement la révision `version`. |
| `review` | Pour `verified`/`published` : `approved: true`, `reviewer`, `at`, `rightsConfirmed: true`, `translationsConfirmed: true`, `contentDigest` correspondant au contenu courant. Produit par la commande d'approbation. |
| `identityConfirmed` | Booléen obligatoire à `true` avant approbation/publication. |
| `importMeta` | Reçu technique local : empreinte d'origine, date d'import et statut d'origine. Il ne constitue pas une preuve documentaire. |

Une licence renseignée n'est pas une autorisation automatiquement vérifiée. Le relecteur doit vérifier ses termes, l'attribution, l'autorisation d'extraction et le droit de publier la synthèse. Les références servent à produire un texte original, sans copie massive. Les dates acceptées sont `AAAA-MM-JJ` ou un horodatage ISO avec fuseau.

## Commandes

Depuis la racine du projet, Node.js 22 ou ultérieur suffit pour ces scripts. Les noms, motifs et chemins ci-dessous sont à adapter; aucun exemple ne publie de donnée de jeu.

```sh
# Simulation sans écriture.
node scripts/import.mjs /chemin/lot-autorise.json --dry-run

# Import réel local; les données restent en brouillon.
node scripts/import.mjs /chemin/lot-autorise.json

# Contrôle de la graine puis du magasin local.
node scripts/check-data.mjs
node scripts/check-data.mjs runtime/entries.json

# Lecture de toutes les données d'une fiche.
node scripts/review.mjs preview IDENTIFIANT

# Soumission à la relecture.
node scripts/review.mjs submit IDENTIFIANT --actor "Nom du relecteur" --note "Sources prêtes pour vérification"

# Seulement après vérification effective du projet, des faits, des droits et des deux langues.
node scripts/review.mjs approve IDENTIFIANT --actor "Nom du relecteur" --note "Motif documenté" --confirm-human-review --confirm-identity --confirm-rights --confirm-translations

# Décision éditoriale explicite, distincte de la mise en production du site.
node scripts/review.mjs publish IDENTIFIANT --actor "Nom du responsable" --note "Publication validée" --confirm-publish

# Résolution explicite d'un conflit ou correction : retrait de la publication, historique conservé.
node scripts/review.mjs revise IDENTIFIANT /chemin/correction.json --actor "Nom du relecteur" --note "Motif de correction"

# Retrait simple vers le brouillon.
node scripts/review.mjs reject IDENTIFIANT --actor "Nom du modérateur" --note "Motif du retrait"
```

Les commandes de revue acceptent `--dry-run`. `--runtime-dir /chemin/isole` et `--seed /chemin/graine.json` permettent un environnement de test indépendant. Chaque script expose `--help`. La publication documentaire locale n'autorise aucune modification du DNS, du serveur public ou des autres applications.

## Quotas et rapports

Valeurs par défaut d'un import : 100 fiches, 2 000 000 octets, 10 000 fiches au total et 20 références par fiche. Les options `--max-records`, `--max-bytes`, `--max-total-records`, `--max-sources` et `--stale-days` permettent de réduire ou ajuster les plafonds. Les valeurs négatives, non entières ou infinies sont refusées. Le dépassement global arrête le lot avant remplacement de la base.

Un rapport JSON indique les insertions, doublons, conflits, fiches invalides, références trop anciennes, volumes traités et limites de vérification. Il affiche un coût réel et un plafond de **0 EUR** : aucun service payant ni requête réseau n'est appelé. Il n'existe aucun automatisme capable d'engager une dépense.

Hors simulation, les rapports sont conservés dans `runtime/reports/`, y compris lorsqu'un lot ne modifie aucune fiche. Une ligne rejetée n'empêche pas l'import d'une fiche indépendante valide. Les fiches dont les relations pointent vers une ligne rejetée sont également retenues en erreur, par propagation.

Codes de sortie : `0` terminé sans conflit, `1` erreur de commande/lecture/intégrité/quota, `2` lot traité avec lignes invalides ou conflits. Le code `2` peut correspondre à un import partiel réussi : consulter `committed`, `inserted`, `invalid` et `conflicts` du rapport.

## Sauvegarde, reprise et restauration

Chaque modification acquiert `runtime/.documentary-lock/`, écrit une sauvegarde et son checksum dans `runtime/backups/`, prépare un rapport, puis remplace atomiquement `runtime/entries.json`. Les fichiers sont créés en mode `0600` et les dossiers techniques en `0700` sur les systèmes POSIX. Le verrou évite les écritures concurrentes par les scripts fournis. Une simulation ne crée aucun dossier.

Un processus interrompu avant le remplacement laisse la base précédente. Après remplacement, les reçus d'import rendent la relance idempotente. Un rapport `committed: false` peut avoir été écrit juste avant une interruption : comparer `afterChecksum` avec l'empreinte de la base, puis relancer le lot. Les fichiers temporaires orphelins peuvent être archivés après vérification. La synchronisation des fichiers réduit le risque de perte; l'atomicité ne remplace pas une sauvegarde externe contre une panne du disque.

Après arrêt brutal, le verrou peut rester. Lire `runtime/.documentary-lock/owner.json` et vérifier que le processus mentionné ne travaille plus avant de supprimer ce seul verrou. Aucune suppression automatique d'un verrou ancien n'est tentée.

```sh
# Vérification de la sauvegarde et simulation.
node scripts/restore.mjs runtime/backups/NOM-SAUVEGARDE.json --actor "Nom" --note "Motif" --dry-run

# Restauration locale. L'état remplacé est sauvegardé à son tour.
node scripts/restore.mjs runtime/backups/NOM-SAUVEGARDE.json --actor "Nom" --note "Motif"

node scripts/check-data.mjs runtime/entries.json
```

La restauration vérifie le format, le checksum et toutes les fiches. Une sauvegarde altérée est refusée. Elle ne supprime pas les anciennes sauvegardes; prévoir leur copie externe et une rétention adaptée avant production. Si le fichier courant a été modifié manuellement au point de devenir du JSON illisible, le conserver à part avant de restaurer à partir d'une graine valide. Les sauvegardes JSON d'anciennes versions sans enveloppe/checksum doivent être examinées et réimportées en brouillon; elles ne sont pas restaurées aveuglément.

Le magasin JSON est un outil local à écrivain unique. Il ne fournit pas d'authentification multiutilisateur, de signature cryptographique d'un relecteur, de transaction PostgreSQL ni de sauvegarde planifiée du serveur. Ces fonctions doivent être raccordées et testées avant une ouverture aux contributions publiques.

## Validation exécutée

```sh
node --test --test-isolation=none tests/documentary.test.mjs
```

La suite couvre les données malformées, liens et versions, sources, reprise des publications importées, conflits, limites, retrait/correction, validation humaine, verrouillage, écritures atomiques, checksums et restauration. Les commandes sont exercées par leur point d'entrée exporté dans des répertoires temporaires. Cette méthode évite le blocage des processus Node enfants observé dans l'environnement de développement; un lancement direct des scripts doit également être vérifié sur la machine de déploiement.

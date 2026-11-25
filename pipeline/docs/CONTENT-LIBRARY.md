# Premier lot documentaire — 19 octobre 2026

La base locale contient **36 brouillons FR/EN** répartis dans les douze rubriques. Les textes sont des synthèses originales de sources primaires Blizzard réellement consultées. Ils ne constituent pas une encyclopédie exhaustive et ne sont pas des données testées dans le client de jeu.

Le périmètre candidat est **World of Warcraft: Forever de Blizzard, annonces et bêta consultées le 19 octobre 2026**. L’existence de ce jeu a été vérifiée ; le propriétaire du wiki doit encore confirmer que son projet vise bien cette version. Aucune règle de WORLD OF HACKCRAFT, guilde d’artisanat personnalisée ou mécanique QTE n’a été transposée à ces fiches.

## Répartition

| Catégorie | Brouillons |
| --- | ---: |
| Classes et spécialisations | 9 |
| Races et factions | 1 |
| Zones et exploration | 4 |
| Donjons et raids | 3 |
| Métiers et artisanat | 2 |
| Objets et équipements | 2 |
| Quêtes et progression | 3 |
| PvP et activités | 3 |
| Créatures et boss | 2 |
| Guides | 2 |
| Actualités | 3 |
| Glossaire | 2 |

Le décompte indique une première présence dans chaque catégorie, pas sa complétude. Les neuf fiches de classes ne sont pas neuf guides exhaustifs : talents, équipement, rotations et spécialisations détaillées restent à documenter séparément.

## Données et commandes

Les trois lots versionnés sont `data/batches/forever-classes.json`, `forever-world.json` et `forever-systems.json`. Les références et limites de recherche se trouvent dans `data/research/`. La graine `data/entries.json` demeure inchangée. L’import transactionnel écrit dans `runtime/entries.json`, conserve une sauvegarde à checksum et laisse toutes les entrées en brouillon. Une relance reconnaît les fiches importées sans les dupliquer.

```sh
# Contrôle sans écriture.
npm run content:import -- --dry-run

# Import, rapports, dossier HTML autonome et export SQLite local.
npm run content:prepare

# Contrôle du magasin documentaire.
node scripts/check-data.mjs runtime/entries.json
```

Le paquet de relecture contient le JSON, une base SQLite, les références, un rapport et un HTML autonome consultable sur téléphone. Il est privé et ne doit pas être servi sous `public/` ou `dist/`. L’export SQLite est une base locale transportable, pas une connexion à un serveur PostgreSQL ni à une base Sites hébergée. Le site actuel est statique ; aucune base distante n’est remplie par ces commandes.

## Relecture avant publication

Ouvrir le dossier HTML, vérifier le périmètre et chaque synthèse FR/EN, puis contrôler les droits et l’actualité des sources. Les noms FR non fournis officiellement sont des propositions de traduction, jamais des localisations validées. Les états, identifiants, dates et références restent consultables pour cette revue.

Une contradiction repérée dans l’article 24301515 concerne le partage du temps de recharge de Flèches multiples/Multi-Shot et Visée/Aimed Shot entre les versions FR et EN. Ce détail a été exclu des synthèses et conservé dans `data/research/forever-classes-sources.json` pour résolution. Les variantes linguistiques d’un article ne sont pas deux confirmations indépendantes.

Les commandes de validation humaine puis de publication éditoriale figurent dans [PIPELINE.md](PIPELINE.md). Aucun `reviewer` humain ni consentement n’est inventé. L’import ne modifie aucune attestation. Les brouillons restent exclus du catalogue web par `selectPublicEntries()`.

## Lacunes prioritaires

- Confirmer le périmètre du wiki et la version exacte de contenu.
- Établir un inventaire de référence avant d’annoncer une proportion de complétude.
- Documenter les autres races et factions ainsi que toutes les spécialisations.
- Compléter les listes de donjons, raids, boss, zones et leurs relations.
- Obtenir des sources autorisées pour les recettes, quêtes, objets, statistiques et tables de butin détaillées ; les annonces ne fournissent pas de catalogue exploitable exhaustif.
- Faire vérifier les deux langues, les conditions de réutilisation et les changements intervenus pendant la bêta.
- Connecter un backend documentaire sécurisé pour les contributions et la relecture en ligne. Le formulaire public actuel n’est pas un service d’administration.

Coût externe de ce lot : **0 EUR** ; aucun service de traduction ou d’import payant n’a été appelé. Les scripts de préparation ne font aucune requête réseau, ne changent pas le DNS et ne déploient pas le site.

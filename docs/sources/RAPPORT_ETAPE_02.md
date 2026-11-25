# Rapport — Étape 02 (sources et modèle), 9 novembre 2026, 20 h (heure de Paris)

**Production : rien n’a été modifié.** Pas de push, de branche, de PR, de fusion, ni d’import réel. Tous les tests ont tourné sur des copies dans /tmp.

**Sources vérifiées**
- Les 123 sources citées par le wiki répondent toutes en HTTP 200 : 84 Blizzard News, 17 pages officielles du jeu, 19 messages de forum, 3 comptes support X.
- Les messages de forum sont bien signés Kaivax, ou contiennent une réponse d’Aggrend.
- 16 pages de races sont génériques (pas spécifiques à Forever) : acceptables pour l’histoire seulement.
- 9 dates de fiches sont à corriger.

**Eternadex : NO-GO pour l’import**
- C’est un site fan allemand financé par la publicité, non affilié à Blizzard.
- Ses données viennent des fichiers du jeu et d’un addon de joueurs.
- Il ne publie **aucune licence ni conditions d’utilisation**.
- Ses chiffres varient d’une page à l’autre (5 167 ou 5 165 quêtes ; 14, 26 ou 31 donjons).
- On peut le citer comme référence communautaire, sans reprendre ses données. Même règle pour Wowhead, qui interdit robots et data-mining.
- Plan de repli : sources officielles Blizzard seulement, ce qui couvre déjà 100 % des fiches actuelles.

**Les chiffres de la mission**
- **65 défis** : confirmé par Blizzard (article sur l’héritage du 23/09).
- **5 167 quêtes** et **48 factions** : ils viennent uniquement d’Eternadex. Ce ne sont pas des faits officiels ; ils sont mis en quarantaine.

**Modèle**
- On garde `entries.json` et les 12 catégories, et on ajoute une couche de faits sourcés en amont, sans CMS parallèle ni nouvelle rubrique.
- Tests :
  - schéma SQLite en mémoire OK (doublons refusés, statuts contrôlés) ;
  - tests du pipeline : 162/165 OK, 3 ignorés, 0 échec ;
  - import à blanc : nouvelle fiche acceptée, doublon et conflit bien détectés.
- **Faille trouvée** : le validateur actuel accepterait une fiche sourcée uniquement par Eternadex. La correction est prévue et doit précéder le lot 1.

**Statut : GO pour l’étape 03, en environnement de test uniquement**, à condition de corriger d’abord cette faille du validateur.

**À trancher par toi**
1. Confirmes-tu que Wowkipedia est non commercial (pas de publicité, pas de revenus) ? C’est une condition de la licence fan-site de Blizzard.
2. Veux-tu interdire définitivement toute donnée d’extraction client (Eternadex, Wowhead), ou la garder visible en « à confirmer » sans publication ?
3. Veux-tu exclure warcraft.wiki.gg ? Sa licence CC BY-SA imposerait la même licence à nos pages, et ses contenus mélangent Classic et Retail.

Livrables : `SOURCES.csv` (138 sources), `MODELE.md`, `PLAN_IMPORT.md`, `DATA_QUALITY.md`, `exemples/`, `preuves/`.

# Exemples pilotes (étape 02), non importés et non publiés

- `faits-pilotes.json` : 7 faits **officiel confirmé**, avec 9 sources vérifiées le 09/11/2026 (HTTP 200, citations courtes), plus 2 éléments en **quarantaine** (chiffres Eternadex 5 167 et 48). Les 7 faits :
  1. 65 défis d’héritage ;
  2. les 6 catégories de défis et leurs points ;
  3. la suite de quêtes Valthalak, défi Aventure ;
  4. le nom FR/EN de Taldramir ;
  5. le correctif du 08/11 (+50 % d’XP en donjon) ;
  6. l’équilibrage annoncé pour le 10/11 ;
  7. l’ouverture des 3 raids le 09/12.
- `lot-pilote.entries.json` : 1 fiche brouillon au format `entries.json` actuel, enrichie de `facts` et `sources[].verification` (Taldramir comme objet légendaire annoncé). L’import à blanc isolé l’a acceptée : voir `../preuves/import_dry_run_report.json`.
- `002_modele_entites.sqlite.sql` : proposition de base de staging, testée en mémoire (`../preuves/schema_sqlite_test.txt`).

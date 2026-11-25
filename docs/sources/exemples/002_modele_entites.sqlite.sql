-- PROPOSITION étape 02 (non appliquée). Base de travail SÉPARÉE de la base communautaire (community.sqlite3, schéma 3) :
-- elle ne sert qu'au staging/validation ; la publication reste entries.json -> build-v2.mjs -> HTML statique.
PRAGMA foreign_keys = ON;

CREATE TABLE source (               -- catalogue SOURCES.csv
  id TEXT PRIMARY KEY CHECK (id GLOB '[a-z0-9]*'),
  url TEXT NOT NULL UNIQUE CHECK (url LIKE 'https://%'),
  publisher TEXT NOT NULL,
  proof_type TEXT NOT NULL CHECK (proof_type IN ('annonce officielle','message officiel forum','page officielle du jeu','compte support officiel','constat en jeu','extraction client','base communautaire','document juridique')),
  tier TEXT NOT NULL CHECK (tier IN ('officiel','en_jeu','extrait_client','communautaire')),
  published_at TEXT, verified_at TEXT NOT NULL, http_status INTEGER,
  build TEXT,                        -- ex. 1.60.1.70862 si la source l'indique
  rights TEXT NOT NULL,              -- conditions de réutilisation
  import_allowed INTEGER NOT NULL DEFAULT 0 CHECK (import_allowed IN (0,1)),  -- 1 seulement sur décision écrite
  forever_specific INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE entity (               -- une ligne par objet du jeu ; id stable = id d'entrée wiki si elle existe
  id TEXT PRIMARY KEY CHECK (length(id) BETWEEN 3 AND 100),
  type TEXT NOT NULL CHECK (type IN ('quest','quest_chain','zone','subzone','npc','creature','item','profession','recipe','camp','legacy_system','legacy_challenge','legacy_perk','faction','dungeon','raid','book','collection','event','class','race')),
  name_fr TEXT, name_en TEXT NOT NULL,
  wiki_entry_id TEXT,                -- lien vers entries.json (catégorie existante), NULL si pas de page
  game_ids TEXT,                     -- JSON {"questId":…, "npcId":…} si une source autorisée le fournit
  status TEXT NOT NULL CHECK (status IN ('officiel confirmé','vérifié en jeu','extrait client','communautaire','à confirmer','obsolète')),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE fact (                 -- assertion atomique sourcée
  id TEXT PRIMARY KEY,
  entity_id TEXT NOT NULL REFERENCES entity(id),
  property TEXT NOT NULL,
  value_json TEXT NOT NULL CHECK (json_valid(value_json)),
  status TEXT NOT NULL CHECK (status IN ('officiel confirmé','vérifié en jeu','extrait client','communautaire','à confirmer','obsolète')),
  build TEXT, valid_from TEXT, valid_to TEXT, superseded_by TEXT REFERENCES fact(id),
  in_game_verified INTEGER NOT NULL DEFAULT 0,
  fingerprint TEXT NOT NULL UNIQUE,  -- sha256(entity_id|property|value canonique) => import idempotent
  UNIQUE (entity_id, property, fingerprint)
);

CREATE TABLE fact_source (          -- provenance : >= 1 par fait
  fact_id TEXT NOT NULL REFERENCES fact(id),
  source_id TEXT NOT NULL REFERENCES source(id),
  quote TEXT CHECK (length(quote) <= 400),   -- citation courte de preuve, jamais le texte intégral
  locator TEXT,                      -- ancre, n° de message forum, horodatage vidéo
  PRIMARY KEY (fact_id, source_id, quote)
);

CREATE TABLE relation (             -- graphe typé (le champ relations[] actuel ne porte pas de type)
  from_id TEXT NOT NULL REFERENCES entity(id), to_id TEXT NOT NULL REFERENCES entity(id),
  type TEXT NOT NULL CHECK (type IN ('located_in','part_of_chain','next_quest','starts_at','ends_at','drops','rewards','sold_by','taught_by','requires','crafted_by','member_of_faction','reputation_with','legacy_challenge_for','attunement_for','part_of_collection','mentions','event_affects')),
  fact_id TEXT REFERENCES fact(id),  -- la relation est elle-même sourcée
  PRIMARY KEY (from_id, to_id, type), CHECK (from_id <> to_id)
);

CREATE TABLE quarantine (           -- tout ce qui n'a pas le droit d'avancer
  id TEXT PRIMARY KEY, payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
  source_id TEXT REFERENCES source(id), reason TEXT NOT NULL, decided_by TEXT, decided_at TEXT,
  decision TEXT CHECK (decision IN ('rejeté','à confirmer','libéré'))
);

CREATE TABLE import_run (           -- reçu d'import (comme report de import.mjs)
  id TEXT PRIMARY KEY, started_at TEXT NOT NULL, batch_sha256 TEXT NOT NULL, dry_run INTEGER NOT NULL,
  inserted INTEGER, duplicates INTEGER, conflicts INTEGER, invalid INTEGER, quarantined INTEGER
);

-- Garde-fou : un fait publiable doit avoir au moins une source officielle ou un constat en jeu.
CREATE VIEW fact_publishable AS
SELECT f.* FROM fact f
WHERE f.status IN ('officiel confirmé','vérifié en jeu') AND f.valid_to IS NULL AND f.superseded_by IS NULL
  AND EXISTS (SELECT 1 FROM fact_source fs JOIN source s ON s.id = fs.source_id
              WHERE fs.fact_id = f.id AND s.tier IN ('officiel','en_jeu'));

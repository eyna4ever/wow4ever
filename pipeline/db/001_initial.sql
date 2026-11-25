BEGIN;
CREATE TYPE editorial_status AS ENUM ('draft','review','verified','published','archived');
CREATE TYPE member_role AS ENUM ('reader','contributor','moderator','administrator');
CREATE TABLE wiki_entries (
 id text PRIMARY KEY, category text NOT NULL, subcategory text NOT NULL,
 title_fr text NOT NULL, title_en text NOT NULL, description_fr text NOT NULL, description_en text NOT NULL,
 game_version text NOT NULL, version integer NOT NULL CHECK(version>0),
 status editorial_status NOT NULL DEFAULT 'draft', identity_confirmed boolean NOT NULL DEFAULT false,
 reviewed_by text, reviewed_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now(),
 search_fr tsvector GENERATED ALWAYS AS (to_tsvector('french',title_fr || ' ' || description_fr)) STORED,
 search_en tsvector GENERATED ALWAYS AS (to_tsvector('english',title_en || ' ' || description_en)) STORED,
 CHECK(status<>'published' OR (identity_confirmed AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL))
);
CREATE INDEX wiki_search_fr ON wiki_entries USING gin(search_fr);
CREATE INDEX wiki_search_en ON wiki_entries USING gin(search_en);
CREATE TABLE wiki_sources(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,entry_id text NOT NULL REFERENCES wiki_entries(id),url text NOT NULL CHECK(url LIKE 'https://%'), accessed_at timestamptz NOT NULL, license text NOT NULL);
CREATE TABLE wiki_relations(from_id text REFERENCES wiki_entries(id),to_id text REFERENCES wiki_entries(id),PRIMARY KEY(from_id,to_id));
CREATE TABLE wiki_revisions(id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,entry_id text NOT NULL REFERENCES wiki_entries(id),snapshot jsonb NOT NULL,actor text NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
REVOKE ALL ON wiki_entries,wiki_sources,wiki_relations,wiki_revisions FROM PUBLIC;
COMMIT;

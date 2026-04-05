-- migration_004_zmyhome.sql
-- ZMyHome project, listing, government appraisal, and price history tables
-- Run: psql npa_kb < migration_004_zmyhome.sql

BEGIN;

-- zmyhome_projects: project-level metadata from ZMyHome
CREATE TABLE IF NOT EXISTS zmyhome_projects (
    id                  TEXT PRIMARY KEY,            -- ZMyHome numeric project ID (as text)
    project_code        TEXT,                        -- "V{id}"
    name                TEXT,
    developer           TEXT,
    year_built          TEXT,
    total_units         INTEGER,
    num_floors          TEXT,
    common_area_fee     TEXT,
    lat                 NUMERIC,
    lng                 NUMERIC,
    listing_summary     JSONB,                       -- {type: {count, price_min, price_max, last_date}}
    raw_json            JSONB,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    market_registry_id  INTEGER REFERENCES project_registry(id)
);

-- zmyhome_listings: individual sale/rent/sold/rented listings
CREATE TABLE IF NOT EXISTS zmyhome_listings (
    property_id         TEXT PRIMARY KEY,
    project_id          TEXT REFERENCES zmyhome_projects(id),  -- nullable for discover mode
    listing_type        TEXT NOT NULL,                -- 'buy', 'rent', 'sold', 'rented'
    price_thb           INTEGER,
    price_psm           INTEGER,                     -- price per sqm
    size_sqm            NUMERIC,
    bedrooms            TEXT,
    bathrooms           TEXT,
    floor               TEXT,
    direction           TEXT,
    broker_ok           BOOLEAN,
    discover_source     TEXT,                         -- 'browse', 'province:{id}' (null = project-seeded)
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    is_active           BOOLEAN DEFAULT true
);

-- zmyhome_appraisals: government appraisal data (unique to ZMyHome)
CREATE TABLE IF NOT EXISTS zmyhome_appraisals (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          TEXT NOT NULL REFERENCES zmyhome_projects(id),
    building            TEXT,
    floor               TEXT,
    price_psm           TEXT,                        -- stored as text (has commas in source)
    unit_type           TEXT,
    scraped_at          TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(project_id, building, floor, unit_type)
);

-- zmyhome_price_history: append-only price snapshots
CREATE TABLE IF NOT EXISTS zmyhome_price_history (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          TEXT NOT NULL REFERENCES zmyhome_projects(id),
    sale_median_sqm     INTEGER,
    sale_count          INTEGER,
    rent_median         INTEGER,
    rent_count          INTEGER,
    change_type         VARCHAR(20) NOT NULL,         -- 'new', 'price_change'
    scraped_at          TIMESTAMP NOT NULL DEFAULT now()
);

-- zmyhome_scrape_logs: per-run metadata
CREATE TABLE IF NOT EXISTS zmyhome_scrape_logs (
    id                  BIGSERIAL PRIMARY KEY,
    started_at          TIMESTAMP,
    finished_at         TIMESTAMP,
    total_searched      INTEGER DEFAULT 0,
    total_found         INTEGER DEFAULT 0,
    new_count           INTEGER DEFAULT 0,
    updated_count       INTEGER DEFAULT 0,
    price_changed       INTEGER DEFAULT 0,
    appraisals_count    INTEGER DEFAULT 0,
    not_found_count     INTEGER DEFAULT 0,
    failed_count        INTEGER DEFAULT 0,
    error               TEXT,
    seed_source         TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_project     ON zmyhome_listings (project_id);
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_type        ON zmyhome_listings (listing_type);
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_scraped     ON zmyhome_listings (last_scraped_at);
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_discover    ON zmyhome_listings (discover_source) WHERE discover_source IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_active      ON zmyhome_listings (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_zmyhome_appraisals_project   ON zmyhome_appraisals (project_id);
CREATE INDEX IF NOT EXISTS idx_zmyhome_appraisals_scraped   ON zmyhome_appraisals (scraped_at);
CREATE INDEX IF NOT EXISTS idx_zmyhome_history_project      ON zmyhome_price_history (project_id);
CREATE INDEX IF NOT EXISTS idx_zmyhome_history_scraped      ON zmyhome_price_history (scraped_at);
CREATE INDEX IF NOT EXISTS idx_zmyhome_projects_registry    ON zmyhome_projects (market_registry_id);

COMMIT;

-- migration_005_ddproperty.sql
-- DDProperty project, listing, price history, and scrape log tables
-- Run: psql npa_kb < migration_005_ddproperty.sql

BEGIN;

-- ddproperty_projects: project-level metadata from DDProperty
CREATE TABLE IF NOT EXISTS ddproperty_projects (
    id                  INTEGER PRIMARY KEY,       -- DDProperty property_id
    name                TEXT,
    completion_year     INTEGER,
    total_units         INTEGER,
    starting_price      INTEGER,
    max_price           INTEGER,
    developer_name      TEXT,
    property_type_code  TEXT,
    tenure_code         TEXT,                      -- 'L' = leasehold, 'F' = freehold
    postcode            TEXT,
    adm_level1          TEXT,                      -- province code (TH10 = Bangkok)
    adm_level2          TEXT,                      -- district code
    raw_json            JSONB,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    market_registry_id  INTEGER REFERENCES project_registry(id)
);

-- ddproperty_listings: individual sale/rent listings
CREATE TABLE IF NOT EXISTS ddproperty_listings (
    id                  INTEGER PRIMARY KEY,       -- DDProperty listing ID
    project_id          INTEGER REFERENCES ddproperty_projects(id),
    listing_type        TEXT NOT NULL,              -- 'sale' or 'rent'
    price_thb           INTEGER,
    sqm                 NUMERIC,
    price_per_sqm       INTEGER,
    bedrooms            INTEGER,
    bathrooms           INTEGER,
    url                 TEXT,
    status_code         TEXT,
    is_verified         BOOLEAN,
    full_address        TEXT,
    raw_json            JSONB,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    is_active           BOOLEAN DEFAULT true
);

-- ddproperty_price_history: append-only price snapshots per project
CREATE TABLE IF NOT EXISTS ddproperty_price_history (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          INTEGER NOT NULL REFERENCES ddproperty_projects(id),
    sale_median_sqm     INTEGER,
    sale_avg_sqm        INTEGER,
    sale_count          INTEGER,
    rent_median         INTEGER,
    rent_avg            INTEGER,
    rent_count          INTEGER,
    change_type         VARCHAR(20) NOT NULL,       -- 'new', 'price_change'
    scraped_at          TIMESTAMP NOT NULL DEFAULT now()
);

-- ddproperty_scrape_logs: per-run metadata
CREATE TABLE IF NOT EXISTS ddproperty_scrape_logs (
    id                  BIGSERIAL PRIMARY KEY,
    started_at          TIMESTAMP,
    finished_at         TIMESTAMP,
    total_projects      INTEGER DEFAULT 0,
    total_listings      INTEGER DEFAULT 0,
    new_projects        INTEGER DEFAULT 0,
    updated_projects    INTEGER DEFAULT 0,
    price_changed       INTEGER DEFAULT 0,
    failed_count        INTEGER DEFAULT 0,
    error               TEXT,
    seed_source         TEXT,
    cookie_refreshes    INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ddproperty_listings_project     ON ddproperty_listings (project_id);
CREATE INDEX IF NOT EXISTS idx_ddproperty_listings_type        ON ddproperty_listings (listing_type);
CREATE INDEX IF NOT EXISTS idx_ddproperty_listings_scraped     ON ddproperty_listings (last_scraped_at);
CREATE INDEX IF NOT EXISTS idx_ddproperty_history_project      ON ddproperty_price_history (project_id);
CREATE INDEX IF NOT EXISTS idx_ddproperty_history_scraped      ON ddproperty_price_history (scraped_at);
CREATE INDEX IF NOT EXISTS idx_ddproperty_projects_adm1        ON ddproperty_projects (adm_level1);
CREATE INDEX IF NOT EXISTS idx_ddproperty_projects_adm2        ON ddproperty_projects (adm_level2);
CREATE INDEX IF NOT EXISTS idx_ddproperty_projects_registry    ON ddproperty_projects (market_registry_id);

COMMIT;

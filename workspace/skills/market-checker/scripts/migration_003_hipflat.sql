-- migration_003_hipflat.sql
-- Hipflat project-level market data tables for bulk scraping
-- Run: psql npa_kb < migration_003_hipflat.sql

BEGIN;

-- hipflat_projects: project-level market data from Hipflat
CREATE TABLE IF NOT EXISTS hipflat_projects (
    uuid                    TEXT PRIMARY KEY,
    name_th                 TEXT,
    name_en                 TEXT,
    slug_url                TEXT,
    lat                     NUMERIC,
    lng                     NUMERIC,
    avg_sale_sqm            INTEGER,                -- current listing avg ฿/sqm
    avg_sold_sqm            INTEGER,                -- historical txn avg ฿/sqm (most reliable)
    sale_price_min          INTEGER,
    sale_price_max          INTEGER,
    rent_price_min          INTEGER,
    rent_price_max          INTEGER,
    units_for_sale          INTEGER,
    units_for_rent          INTEGER,
    sold_below_asking_pct   NUMERIC,
    avg_days_on_market      INTEGER,
    price_trend             TEXT,                    -- 'ขาขึ้น' or 'ขาลง'
    yoy_change_pct          NUMERIC,
    year_completed          INTEGER,
    floors                  INTEGER,
    total_units             INTEGER,
    service_charge_sqm      INTEGER,
    district_name           TEXT,
    district_avg_sale_sqm   INTEGER,
    district_avg_rent_sqm   INTEGER,
    raw_html_hash           TEXT,                    -- hash of HTML for change detection
    first_seen_at           TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at         TIMESTAMP NOT NULL DEFAULT now(),
    market_registry_id      INTEGER REFERENCES project_registry(id)
);

-- hipflat_price_history: price snapshots over time
CREATE TABLE IF NOT EXISTS hipflat_price_history (
    id                      BIGSERIAL PRIMARY KEY,
    project_uuid            TEXT NOT NULL REFERENCES hipflat_projects(uuid),
    avg_sale_sqm            INTEGER,
    avg_sold_sqm            INTEGER,
    units_for_sale          INTEGER,
    units_for_rent          INTEGER,
    rent_price_min          INTEGER,
    rent_price_max          INTEGER,
    yoy_change_pct          NUMERIC,
    district_avg_sale_sqm   INTEGER,
    change_type             VARCHAR(20) NOT NULL,    -- 'new', 'price_change'
    scraped_at              TIMESTAMP NOT NULL DEFAULT now()
);

-- hipflat_scrape_logs: per-run metadata
CREATE TABLE IF NOT EXISTS hipflat_scrape_logs (
    id                      BIGSERIAL PRIMARY KEY,
    started_at              TIMESTAMP,
    finished_at             TIMESTAMP,
    total_searched          INTEGER DEFAULT 0,
    total_found             INTEGER DEFAULT 0,
    new_count               INTEGER DEFAULT 0,
    updated_count           INTEGER DEFAULT 0,
    price_changed           INTEGER DEFAULT 0,
    not_found_count         INTEGER DEFAULT 0,
    failed_count            INTEGER DEFAULT 0,
    error                   TEXT,
    seed_source             TEXT                     -- 'project_registry', 'npa', 'file', 'cli'
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_hipflat_history_uuid     ON hipflat_price_history (project_uuid);
CREATE INDEX IF NOT EXISTS idx_hipflat_history_scraped   ON hipflat_price_history (scraped_at);
CREATE INDEX IF NOT EXISTS idx_hipflat_projects_district ON hipflat_projects (district_name);
CREATE INDEX IF NOT EXISTS idx_hipflat_projects_registry ON hipflat_projects (market_registry_id);

COMMIT;

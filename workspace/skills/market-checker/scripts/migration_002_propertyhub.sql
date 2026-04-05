-- Migration 002: PropertyHub bulk scraper tables
-- Created: 2026-04-05

-- Table 1: Canonical project data from PropertyHub
CREATE TABLE IF NOT EXISTS propertyhub_projects (
    id                  TEXT PRIMARY KEY,
    name                TEXT,
    name_en             TEXT,
    slug                TEXT,
    address             TEXT,
    province_code       TEXT,
    district_code       TEXT,
    lat                 NUMERIC,
    lng                 NUMERIC,
    completed_year      TEXT,
    total_units         TEXT,
    floors              TEXT,
    buildings           TEXT,
    developer           TEXT,
    utility_fee         TEXT,
    facilities          JSONB,
    listing_count_sale  INTEGER DEFAULT 0,
    listing_count_rent  INTEGER DEFAULT 0,
    raw_json            JSONB,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    market_registry_id  INTEGER REFERENCES project_registry(id)
);

CREATE INDEX IF NOT EXISTS idx_phub_proj_province   ON propertyhub_projects (province_code);
CREATE INDEX IF NOT EXISTS idx_phub_proj_district   ON propertyhub_projects (district_code);
CREATE INDEX IF NOT EXISTS idx_phub_proj_slug       ON propertyhub_projects (slug);
CREATE INDEX IF NOT EXISTS idx_phub_proj_scraped    ON propertyhub_projects (last_scraped_at);
CREATE INDEX IF NOT EXISTS idx_phub_proj_registry   ON propertyhub_projects (market_registry_id);

-- Table 2: Individual sale/rent listings
CREATE TABLE IF NOT EXISTS propertyhub_listings (
    id                  TEXT PRIMARY KEY,
    project_id          TEXT REFERENCES propertyhub_projects(id),
    post_type           TEXT NOT NULL,
    title               TEXT,
    price_thb           NUMERIC,
    area_sqm            NUMERIC,
    price_per_sqm       NUMERIC,
    rent_monthly        NUMERIC,
    bedrooms            INTEGER,
    bathrooms           INTEGER,
    floor               TEXT,
    room_type           TEXT,
    raw_json            JSONB,
    first_seen_at       TIMESTAMP NOT NULL DEFAULT now(),
    last_scraped_at     TIMESTAMP NOT NULL DEFAULT now(),
    is_active           BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_phub_list_project    ON propertyhub_listings (project_id);
CREATE INDEX IF NOT EXISTS idx_phub_list_post_type  ON propertyhub_listings (post_type);
CREATE INDEX IF NOT EXISTS idx_phub_list_active     ON propertyhub_listings (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_phub_list_scraped    ON propertyhub_listings (last_scraped_at);

-- Table 3: Project-level price aggregate snapshots (append-only)
CREATE TABLE IF NOT EXISTS propertyhub_price_history (
    id              BIGSERIAL PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES propertyhub_projects(id),
    sale_median_sqm INTEGER,
    sale_avg_sqm    INTEGER,
    sale_min_sqm    INTEGER,
    sale_max_sqm    INTEGER,
    sale_count      INTEGER,
    rent_median     INTEGER,
    rent_avg        INTEGER,
    rent_min        INTEGER,
    rent_max        INTEGER,
    rent_count      INTEGER,
    change_type     VARCHAR(20) NOT NULL,
    scraped_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_phub_hist_project    ON propertyhub_price_history (project_id, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_phub_hist_scraped    ON propertyhub_price_history (scraped_at);

-- Table 4: Scrape run logs
CREATE TABLE IF NOT EXISTS propertyhub_scrape_logs (
    id               BIGSERIAL PRIMARY KEY,
    started_at       TIMESTAMP,
    finished_at      TIMESTAMP,
    total_projects   INTEGER DEFAULT 0,
    total_listings   INTEGER DEFAULT 0,
    new_projects     INTEGER DEFAULT 0,
    updated_projects INTEGER DEFAULT 0,
    price_changed    INTEGER DEFAULT 0,
    failed_count     INTEGER DEFAULT 0,
    error            TEXT,
    scope            TEXT
);

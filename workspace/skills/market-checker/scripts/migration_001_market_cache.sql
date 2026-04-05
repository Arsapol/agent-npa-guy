-- Migration 001: Market Price Caching System
-- Created: 2026-04-04

-- Table 1: Canonical project identity
CREATE TABLE IF NOT EXISTS project_registry (
    id                SERIAL PRIMARY KEY,
    name_canonical    TEXT NOT NULL,
    name_th           TEXT,
    name_en           TEXT,
    aliases           TEXT[] DEFAULT '{}',

    -- Source-specific IDs (for direct re-query without search)
    hipflat_uuid      TEXT,
    zmyhome_id        TEXT,
    propertyhub_id    TEXT,
    ddproperty_id     TEXT,

    -- Location
    lat               NUMERIC,
    lng               NUMERIC,

    -- Static project specs
    year_built        INTEGER,
    total_units       INTEGER,
    developer         TEXT,
    cam_fee_sqm       NUMERIC,

    created_at        TIMESTAMP NOT NULL DEFAULT now(),
    updated_at        TIMESTAMP NOT NULL DEFAULT now(),

    UNIQUE(name_canonical)
);

CREATE INDEX IF NOT EXISTS idx_registry_names    ON project_registry USING gin (aliases);
CREATE INDEX IF NOT EXISTS idx_registry_th       ON project_registry (name_th);
CREATE INDEX IF NOT EXISTS idx_registry_en       ON project_registry (name_en);
CREATE INDEX IF NOT EXISTS idx_registry_location ON project_registry (lat, lng);

-- Table 2: Price snapshots (append-only)
CREATE TABLE IF NOT EXISTS market_price_cache (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER NOT NULL REFERENCES project_registry(id),
    source              TEXT NOT NULL,

    matched_name        TEXT,

    -- Sale data
    sale_price_sqm      INTEGER,
    sale_count          INTEGER,
    sold_price_sqm      INTEGER,
    last_sold_date      DATE,

    -- Rental data
    rent_median         INTEGER,
    rent_min            INTEGER,
    rent_max            INTEGER,
    rent_count          INTEGER,
    last_rental_date    DATE,

    -- Trend
    yoy_change_pct      NUMERIC,

    -- Government appraisal
    govt_appraisal_sqm  INTEGER,

    -- Full response
    raw_data            JSONB,

    -- Metadata
    checked_at          TIMESTAMP NOT NULL DEFAULT now(),
    ttl_days            INTEGER NOT NULL DEFAULT 30
);

CREATE INDEX IF NOT EXISTS idx_cache_lookup ON market_price_cache (project_id, source, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_cache_stale  ON market_price_cache (checked_at, ttl_days);

-- Add market_registry_id to all 6 provider tables
ALTER TABLE bam_properties   ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);
ALTER TABLE jam_properties   ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);
ALTER TABLE sam_properties   ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);
ALTER TABLE ktb_properties   ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);
ALTER TABLE kbank_properties ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);
ALTER TABLE led_properties   ADD COLUMN IF NOT EXISTS market_registry_id INTEGER REFERENCES project_registry(id);

CREATE INDEX IF NOT EXISTS idx_bam_market_reg   ON bam_properties   (market_registry_id);
CREATE INDEX IF NOT EXISTS idx_jam_market_reg   ON jam_properties   (market_registry_id);
CREATE INDEX IF NOT EXISTS idx_sam_market_reg   ON sam_properties   (market_registry_id);
CREATE INDEX IF NOT EXISTS idx_ktb_market_reg   ON ktb_properties   (market_registry_id);
CREATE INDEX IF NOT EXISTS idx_kbank_market_reg ON kbank_properties (market_registry_id);
CREATE INDEX IF NOT EXISTS idx_led_market_reg   ON led_properties   (market_registry_id);

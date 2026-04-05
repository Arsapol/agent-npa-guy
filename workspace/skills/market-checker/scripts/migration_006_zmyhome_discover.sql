-- migration_006_zmyhome_discover.sql
-- Add discover_source column and indexes for ZMyHome browse-mode discovery.
-- Safe to re-run: all statements are IF NOT EXISTS / idempotent.
-- Run: psql npa_kb < migration_006_zmyhome_discover.sql

BEGIN;

-- Add discover_source column (nullable -- null means project-seeded)
ALTER TABLE zmyhome_listings
    ADD COLUMN IF NOT EXISTS discover_source TEXT;

-- Partial index for discover-mode listings
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_discover
    ON zmyhome_listings (discover_source)
    WHERE discover_source IS NOT NULL;

-- Partial index for active listings
CREATE INDEX IF NOT EXISTS idx_zmyhome_listings_active
    ON zmyhome_listings (is_active)
    WHERE is_active = true;

COMMIT;

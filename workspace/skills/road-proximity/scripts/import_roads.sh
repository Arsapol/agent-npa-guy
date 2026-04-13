#!/usr/bin/env bash
# Download Thailand OSM extract and import roads into PostGIS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
DB_URL="${DATABASE_URL:-postgresql://arsapolm@localhost:5432/npa_kb}"
PBF_URL="https://download.geofabrik.de/asia/thailand-latest.osm.pbf"
PBF_FILE="$DATA_DIR/thailand-latest.osm.pbf"
LUA_STYLE="$SCRIPT_DIR/roads.lua"

mkdir -p "$DATA_DIR"

# --- Step 1: Download ---
echo "=== Downloading Thailand OSM extract ==="
if command -v curl &>/dev/null; then
    curl -L -o "$PBF_FILE" -z "$PBF_FILE" "$PBF_URL"
elif command -v wget &>/dev/null; then
    wget -N -O "$PBF_FILE" "$PBF_URL"
else
    echo "ERROR: curl or wget required" && exit 1
fi

echo "File size: $(du -h "$PBF_FILE" | cut -f1)"

# --- Step 2: Ensure PostGIS ---
echo "=== Ensuring PostGIS extension ==="
psql "$DB_URL" -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null || true

# --- Step 3: Drop old data ---
echo "=== Dropping old osm_roads table ==="
psql "$DB_URL" -c "DROP TABLE IF EXISTS osm_roads CASCADE;" 2>/dev/null || true

# --- Step 4: Import with osm2pgsql ---
echo "=== Importing roads with osm2pgsql ==="
osm2pgsql \
    --create \
    --output=flex \
    --style="$LUA_STYLE" \
    --proj=4326 \
    --database="$DB_URL" \
    "$PBF_FILE"

# --- Step 5: Create indexes ---
echo "=== Creating spatial indexes ==="
psql "$DB_URL" <<SQL
CREATE INDEX IF NOT EXISTS idx_osm_roads_way ON osm_roads USING GIST (way);
CREATE INDEX IF NOT EXISTS idx_osm_roads_highway ON osm_roads (highway);
CREATE INDEX IF NOT EXISTS idx_osm_roads_name ON osm_roads USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_osm_roads_name_th ON osm_roads USING GIN (name_th gin_trgm_ops);
SQL

# --- Step 6: Stats ---
echo "=== Import complete ==="
psql "$DB_URL" -c "SELECT highway, COUNT(*) FROM osm_roads GROUP BY highway ORDER BY count DESC;"
psql "$DB_URL" -c "SELECT COUNT(*) AS total_roads FROM osm_roads;"

echo "Done. Last updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

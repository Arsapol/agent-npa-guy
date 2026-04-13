#!/usr/bin/env bash
# Pre-process Thailand OSM data for OSRM routing engine
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
PBF_FILE="$DATA_DIR/thailand-latest.osm.pbf"
OSRM_FILE="$DATA_DIR/thailand-latest.osrm"

if [ ! -f "$PBF_FILE" ]; then
    echo "ERROR: $PBF_FILE not found. Run import_roads.sh first."
    exit 1
fi

# Find car profile — brew installs profiles in share dir
PROFILE=""
for p in \
    /opt/homebrew/share/osrm/profiles/car.lua \
    /opt/homebrew/opt/osrm-backend/share/osrm/profiles/car.lua \
    /usr/local/share/osrm/profiles/car.lua \
    /usr/share/osrm/profiles/car.lua; do
    if [ -f "$p" ]; then
        PROFILE="$p"
        break
    fi
done

if [ -z "$PROFILE" ]; then
    echo "ERROR: Cannot find OSRM car.lua profile"
    echo "Searched: /opt/homebrew/share/osrm/profiles/ and /usr/local/share/osrm/profiles/"
    exit 1
fi

echo "=== Using profile: $PROFILE ==="

# Step 1: Extract
echo "=== Step 1/3: Extracting road network ==="
osrm-extract -p "$PROFILE" "$PBF_FILE"

# Step 2: Partition (MLD algorithm)
echo "=== Step 2/3: Partitioning graph ==="
osrm-partition "$OSRM_FILE"

# Step 3: Customize
echo "=== Step 3/3: Customizing edge weights ==="
osrm-customize "$OSRM_FILE"

echo "=== OSRM pre-processing complete ==="
echo "Start server with: osrm-routed --algorithm=MLD $OSRM_FILE"

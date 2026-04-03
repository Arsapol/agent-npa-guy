#!/bin/bash
# SAM NPA Scraper — Full pipeline
# Usage: ./run_scraper.sh [--list-only] [--detail-only] [--detail-limit N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DB_URI="${POSTGRES_URI:-postgresql://arsapolm@localhost:5432/npa_kb}"
DELAY="${SAM_DELAY:-3}"

echo "═══════════════════════════════════════════"
echo "  SAM NPA Scraper"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════"

# Step 1: Update dropdown options
if [[ "${1:-}" != "--detail-only" ]]; then
    echo ""
    echo "📦 Step 1: Updating dropdown options..."
    python3 update_options.py --db-uri "$DB_URI" --fetch-districts
fi

# Step 2: Scrape list pages
if [[ "${1:-}" != "--detail-only" ]]; then
    echo ""
    echo "📋 Step 2: Scraping property listings..."
    python3 scrape_list.py \
        --db-uri "$DB_URI" \
        --delay "$DELAY" \
        "$@"
fi

# Step 3: Scrape detail pages
if [[ "${1:-}" != "--list-only" ]]; then
    echo ""
    echo "🔍 Step 3: Scraping property details..."
    DETAIL_ARGS="--db-uri $DB_URI --delay $DELAY --only-missing"
    
    # Check for --detail-limit
    for arg in "$@"; do
        if [[ "$arg" == --detail-limit=* ]]; then
            LIMIT="${arg#--detail-limit=}"
            DETAIL_ARGS="$DETAIL_ARGS --limit $LIMIT"
        fi
    done
    
    python3 scrape_detail.py $DETAIL_ARGS
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ All done! $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════"

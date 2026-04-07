#!/usr/bin/env bash
# run_scraper.sh — LED property scraper runner for launchd
# Saves JSON output to NPA-guy's data directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="/Users/arsapolm/.nanobot-npa-guy/workspace/data/led-scrapes"
LOG_FILE="/Users/arsapolm/.nanobot-npa-guy/workspace/data/led-scraper.log"

mkdir -p "$DATA_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting LED scraper" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# Run scraper, save JSON to data directory, skip DB (use --save-to json)
python3 main.py \
  --save-to json \
  --max-pages 500 \
  --concurrent 10 \
  --parallel-batch-size 3 \
  --max-duration 840 \
  2>&1 | tee -a "$LOG_FILE"

# Move JSON output to data directory
mv -f "$SCRIPT_DIR"/led_properties_*.json "$DATA_DIR/" 2>/dev/null || true

echo "$(date '+%Y-%m-%d %H:%M:%S') — Scraper completed" >> "$LOG_FILE"

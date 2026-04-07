#!/bin/bash
# GHB NPA scraper — daily cron for all property types
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== GHB scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== GHB scraper finished at $(date) ==="

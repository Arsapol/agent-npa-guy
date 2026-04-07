#!/bin/bash
# GSB (ออมสิน) NPA scraper — daily cron
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== GSB scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== GSB scraper finished at $(date) ==="

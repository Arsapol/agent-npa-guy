#!/bin/bash
# SCB NPA scraper — daily cron
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== SCB scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== SCB scraper finished at $(date) ==="

#!/bin/bash
# BAY/Krungsri NPA scraper — daily cron
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== BAY scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== BAY scraper finished at $(date) ==="

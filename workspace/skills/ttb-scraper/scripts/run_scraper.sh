#!/bin/bash
# TTB/PAMCO NPA scraper — daily cron
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== TTB/PAMCO scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== TTB/PAMCO scraper finished at $(date) ==="

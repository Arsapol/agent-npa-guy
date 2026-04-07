#!/bin/bash
# LH Bank NPA scraper -- daily cron
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== LH Bank scraper starting at $(date) ==="

python3 -u scraper.py

echo "=== LH Bank scraper finished at $(date) ==="

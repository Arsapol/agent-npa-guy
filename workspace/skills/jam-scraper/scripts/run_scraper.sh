#!/bin/bash
# JAM Scraper runner
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== JAM Scraper ==="
echo "Time: $(date)"

python scraper.py "$@"

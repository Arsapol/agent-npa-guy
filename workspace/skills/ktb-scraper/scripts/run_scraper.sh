#!/bin/bash
# KTB NPA scraper — daily cron for priority provinces
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== KTB scraper starting at $(date) ==="

python scraper.py \
    --province \
    กรุงเทพมหานคร \
    ชลบุรี \
    สงขลา \
    ภูเก็ต \
    เชียงใหม่ \
    นนทบุรี \
    ปทุมธานี

echo "=== KTB scraper finished at $(date) ==="

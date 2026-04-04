#!/bin/bash
# KBank NPA Scraper — Daily cron for 7 target provinces
# กรุงเทพ(10) ชลบุรี(20) เชียงใหม่(50) นนทบุรี(12) ปทุมธานี(13) ภูเก็ต(83) สงขลา(90)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_PREFIX="$(date +%Y%m%d_%H%M%S)"

cd "$SCRIPT_DIR"

echo "=== KBank scraper started at $(date) ==="
/opt/anaconda3/bin/python3 scraper.py --province 10 20 50 12 13 83 90
echo "=== KBank scraper finished at $(date) ==="

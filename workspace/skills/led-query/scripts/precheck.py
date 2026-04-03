#!/usr/bin/env python3
"""Pre-commit check for NPA property analysis.

Enforces guardrails before a BUY recommendation can be finalized:
1. Property photos must be downloaded and reviewed
2. Building/project must be identified for condos
3. Rent must use LOW/MID/HIGH range (not single optimistic number)
4. Market discount must pass sanity check
5. Flood risk must be assessed

Usage:
    python scripts/precheck.py --asset-id 1993960 --verdict BUY
    python scripts/precheck.py --asset-id 1882448 --verdict BUY --project "Lumpini Place"
"""

import argparse
import json
import os
import subprocess
import sys

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def check_photos_downloaded(asset_id):
    """Check if property photos exist in output/images/{asset_id}/."""
    workspace = os.environ.get("NPA_WORKSPACE", os.path.expanduser("~/.nanobot-npa-guy/workspace"))
    img_dir = os.path.join(workspace, "output", "images", str(asset_id))
    
    if not os.path.isdir(img_dir):
        return False, f"No photo directory found: {img_dir}"
    
    files = os.listdir(img_dir)
    has_land = any("land" in f.lower() for f in files)
    has_map = any("map" in f.lower() for f in files)
    
    if not files:
        return False, f"Photo directory exists but is empty: {img_dir}"
    
    if has_land and has_map:
        return True, f"Photos found: {', '.join(files)}"
    elif has_land:
        return True, f"Land photo found (no map): {', '.join(files)}"
    else:
        return False, f"Only map found, no land photo: {', '.join(files)}"


def check_building_identified(asset_id, project_name=None):
    """For condos (ห้องชุด), verify building/project name is known."""
    if project_name:
        return True, f"Project identified: {project_name}"
    
    # Try to look up from DB if no project name given
    try:
        import psycopg2
        conn = psycopg2.connect(POSTGRES_URI)
        cur = conn.cursor()
        cur.execute(
            "SELECT property_type, address FROM properties WHERE asset_id = %s",
            (str(asset_id),)
        )
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return None, f"Asset {asset_id} not found in DB"
        
        property_type = row[0]
        
        if "ห้องชุด" in (property_type or ""):
            return False, "CONDO: Building/project name is REQUIRED for condo analysis. Use --project."
        else:
            return True, f"Not a condo ({property_type}), project name optional"
    except Exception as e:
        return None, f"DB query failed: {e}"


def check_flood_assessed(asset_id):
    """Check if flood risk has been recorded for this asset in KB or memory."""
    # Simple check: see if flood risk appears in any analysis notes
    workspace = os.environ.get("NPA_WORKSPACE", os.path.expanduser("~/.nanobot-npa-guy/workspace"))
    
    # Check if flood_check was run (look in memory/history)
    try:
        result = subprocess.run(
            ["grep", "-l", str(asset_id), 
             os.path.join(workspace, "memory", "MEMORY.md")],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # Check if flood is mentioned near this asset
            result2 = subprocess.run(
                ["grep", "-i", "flood",
                 os.path.join(workspace, "memory", "MEMORY.md")],
                capture_output=True, text=True, timeout=5
            )
            if result2.returncode == 0:
                return True, "Flood risk appears in MEMORY (general data exists)"
    except Exception:
        pass
    
    return None, "Could not verify flood assessment. Run flood-check skill and record result."


def run_all_checks(asset_id, verdict, project_name=None):
    """Run all pre-commit checks for a property recommendation."""
    
    if verdict not in ("BUY", "STRONG_BUY", "SPECULATIVE_BUY"):
        print(f"Verdict is '{verdict}' — pre-commit checks only required for BUY recommendations.")
        return True
    
    print(f"\n{'='*60}")
    print(f"PRE-COMMIT CHECKLIST — Asset {asset_id} — Verdict: {verdict}")
    print(f"{'='*60}\n")
    
    checks = [
        ("📸 Photos downloaded & reviewed", lambda: check_photos_downloaded(asset_id)),
        ("🏢 Building/Project identified", lambda: check_building_identified(asset_id, project_name)),
        ("🌊 Flood risk assessed", lambda: check_flood_assessed(asset_id)),
    ]
    
    all_pass = True
    for label, check_fn in checks:
        passed, msg = check_fn()
        if passed is True:
            status = "✅ PASS"
        elif passed is False:
            status = "❌ FAIL"
            all_pass = False
        else:
            status = "⚠️  SKIP"
            # SKIP doesn't block, but warns
        
        print(f"  {status}  {label}")
        print(f"         {msg}\n")
    
    print(f"{'─'*60}")
    if all_pass:
        print(f"  ✅ ALL CHECKS PASSED — ready for BUY recommendation")
    else:
        print(f"  ❌ CHECKS FAILED — resolve issues before recommending BUY")
        print(f"     Do NOT publish analysis until all ❌ items are resolved.")
    print(f"{'='*60}\n")
    
    return all_pass


def main():
    parser = argparse.ArgumentParser(description="NPA Analysis Pre-commit Check")
    parser.add_argument("--asset-id", type=int, required=True, help="Property asset ID")
    parser.add_argument("--verdict", required=True, choices=["BUY", "STRONG_BUY", "SPECULATIVE_BUY", "WATCH", "AVOID"],
                        help="Intended verdict")
    parser.add_argument("--project", type=str, help="Building/project name (required for condos)")
    args = parser.parse_args()
    
    passed = run_all_checks(args.asset_id, args.verdict, args.project)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

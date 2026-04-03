#!/usr/bin/env python3
"""Download LED property photos from image URLs in the database.

Usage:
    python scripts/download_photos.py --asset-id 1882448
    python scripts/download_photos.py --asset-ids 1882448,1882449,1935620
    python scripts/download_photos.py --all-missing  # Download for all active properties missing photos
"""

import argparse
import os
import sys

import psycopg2
import psycopg2.extras

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")
WORKSPACE = os.getenv("NPA_WORKSPACE", os.path.expanduser("~/.nanobot-npa-guy/workspace"))
OUTPUT_DIR = os.path.join(WORKSPACE, "output", "images")


def get_conn():
    return psycopg2.connect(POSTGRES_URI)


def get_image_urls(conn, asset_id):
    """Get image URLs for an asset from property_images table."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT image_url, image_type, image_order FROM property_images WHERE asset_id = %s ORDER BY image_type, image_order",
        (str(asset_id),)
    )
    rows = cur.fetchall()
    
    if not rows:
        # Try from memory or known URLs
        return []
    
    return rows


def download_image(url, filepath):
    """Download an image from URL to filepath."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return False


def download_for_asset(asset_id):
    """Download all images for a single asset."""
    img_dir = os.path.join(OUTPUT_DIR, str(asset_id))
    
    conn = get_conn()
    images = get_image_urls(conn, asset_id)
    conn.close()
    
    if not images:
        print(f"  ⚠️  No images in DB for asset {asset_id}")
        return False
    
    downloaded = 0
    for img in images:
        img_type = img["image_type"]  # "land" or "map"
        img_url = img["image_url"]
        
        filename = f"{img_type}_{asset_id}.jpg"
        filepath = os.path.join(img_dir, filename)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  ✅ Already exists: {filename} ({os.path.getsize(filepath):,} bytes)")
            downloaded += 1
            continue
        
        print(f"  ⬇️  Downloading {img_type}: {img_url}")
        if download_image(img_url, filepath):
            size = os.path.getsize(filepath)
            print(f"  ✅ Saved: {filename} ({size:,} bytes)")
            downloaded += 1
    
    return downloaded > 0


def get_active_assets_missing_photos(conn):
    """Get asset IDs from MEMORY that don't have downloaded photos."""
    # These are the asset IDs I've been tracking in MEMORY
    active_ids = [
        "1993960", "1993961", "1867367", "2007239", "1999047", "1939077",  # Bangkok
        "1882448", "1882449", "1935620", "1860423", "1961347", "1943236", "1892326",  # Provincial
        "1872721", "1873488", "1877889", "1898479",  # Songkhla
        "1896940", "1874562", "1900267",  # Songkhla PSU
    ]
    
    missing = []
    for aid in active_ids:
        img_dir = os.path.join(OUTPUT_DIR, aid)
        if not os.path.isdir(img_dir) or not os.listdir(img_dir):
            missing.append(aid)
    
    return missing


def main():
    parser = argparse.ArgumentParser(description="Download LED property photos")
    parser.add_argument("--asset-id", type=str, help="Single asset ID")
    parser.add_argument("--asset-ids", type=str, help="Comma-separated asset IDs")
    parser.add_argument("--all-missing", action="store_true", help="Download photos for all active properties missing them")
    args = parser.parse_args()
    
    if args.all_missing:
        conn = get_conn()
        missing = get_active_assets_missing_photos(conn)
        conn.close()
        print(f"Found {len(missing)} assets with missing photos: {missing}")
        for aid in missing:
            print(f"\n📥 Asset {aid}:")
            download_for_asset(aid)
    elif args.asset_id:
        print(f"\n📥 Asset {args.asset_id}:")
        download_for_asset(args.asset_id)
    elif args.asset_ids:
        ids = [x.strip() for x in args.asset_ids.split(",")]
        for aid in ids:
            print(f"\n📥 Asset {aid}:")
            download_for_asset(aid)
    else:
        parser.error("Specify --asset-id, --asset-ids, or --all-missing")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SAM Announcements — Fetch, parse, validate, and ingest SAM (บสส.) price history.

SAM publishes PDF announcements listing property price reductions.
Each PDF has columns: code, type, location, area, old_price, new_price.
This tool extracts that data, validates it, then ingests to KB.

Usage:
  python sam_announcements.py parse-url <url>         # Download & parse PDF into raw table
  python sam_announcements.py parse-file <path>        # Parse local PDF
  python sam_announcements.py validate [announcement_id]  # Validate parsed data
  python sam_announcements.py history <code>           # Show price history for a property
  python sam_announcements.py ingest <announcement_id> # Ingest validated data to KB
  python sam_announcements.py list                     # List all announcements
  python sam_announcements.py scan-db                  # Find unique promotion_links from sam_properties
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import psycopg2

DB_URL = os.environ.get("NPA_DB_URL", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_conn():
    return psycopg2.connect(DB_URL)


def download_pdf(url, dest_dir="/tmp"):
    """Download PDF and return local path."""
    import urllib.request
    filename = url.split("/")[-1].replace("%20", "_")
    dest = os.path.join(dest_dir, filename)
    if os.path.exists(dest):
        print(f"  Using cached: {dest}")
        return dest
    print(f"  Downloading: {url}")
    urllib.request.urlretrieve(url, dest)
    return dest


def file_hash(path):
    """SHA256 of file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext."""
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {result.stderr}")
    return result.stdout


def parse_price_table(text):
    """
    Parse SAM announcement PDF text to extract property rows with price data.
    
    Expected format (layout-preserved pdftotext output):
      5   8Z6930   ห้องชุดพาณิชยกรรม   ถนน รัชดาภิเษก ต. ดินแดง ...   352.00 ตร.ม.   13,410,000.00   12,730,000.00
    
    Columns: seq, code, type, location, area, old_price, new_price
    Some rows have only one price (no reduction = new price only).
    
    Returns list of dicts with parsed data.
    """
    rows = []
    lines = text.split('\n')
    
    # Property type patterns (handles PDF spacing artifacts like "ห้ องชุด")
    type_patterns = [
        (r'ห้\s*องชุดพาณิชยกรรม', 'ห้องชุดพาณิชยกรรม'),
        (r'ห้\s*องชุดพักอาศัย', 'ห้องชุดพักอาศัย'),
        (r'ทาวน์\s*เฮ้\s*าส์', 'ทาวน์เฮ้าส์'),
        (r'บ้\s*านเดี่ยว', 'บ้านเดี่ยว'),
        (r'บ้\s*านแฝด', 'บ้านแฝด'),
        (r'อาคารพาณิชย์', 'อาคารพาณิชย์'),
        (r'โรงงาน\s*/?\s*โกดัง', 'โรงงาน/โกดัง'),
        (r'ที่ดนิ\s*เปล่\s*าา', 'ที่ดินเปล่า'),
        (r'ที่ดินเปล่า', 'ที่ดินเปล่า'),
        (r'โฮมออฟฟิศ', 'โฮมออฟฟิศ'),
    ]
    
    for line in lines:
        # Match rows starting with a sequence number followed by property code
        m = re.match(r'^\s+(\d+)\s+([A-Z0-9]{5,8})\s+', line)
        if not m:
            continue
        
        seq = m.group(1)
        code = m.group(2)
        
        # Validate code format (known prefixes)
        valid_prefixes = ('8Z', '3A', 'CL', 'TL', 'HL', 'SL', 'LL', 'BL', '4T')
        if not any(code.upper().startswith(p) for p in valid_prefixes):
            continue
        
        # Extract prices — formatted numbers with commas and .00 (e.g., 13,410,000.00)
        price_strings = re.findall(r'(\d{1,3}(?:,\d{3})*\.\d{2})', line)
        large_prices = [float(p.replace(',', '')) for p in price_strings if float(p.replace(',', '')) >= 10000]
        
        if len(large_prices) < 1:
            continue
        
        # Determine old/new price
        # 2 prices = old (reduced from) + new (reduced to)
        # 1 price = new price only (no reduction in this round)
        old_price = None
        new_price = None
        
        if len(large_prices) >= 2:
            old_price = int(large_prices[0])
            new_price = int(large_prices[1])
        elif len(large_prices) == 1:
            new_price = int(large_prices[0])
        
        # Extract area (ตร.ม.)
        size_sqm = None
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*ตร', line)
        if area_match:
            size_sqm = float(area_match.group(1))
        
        # Extract property type (handles PDF spacing)
        property_type = None
        for pattern, ptype in type_patterns:
            if re.search(pattern, line):
                property_type = ptype
                break
        
        # Extract district
        district = None
        dist_match = re.search(r'อ\.\s*(\S+)', line)
        if dist_match:
            district = dist_match.group(1).rstrip(',')
        
        # Extract province
        province = None
        prov_match = re.search(r'จ\.\s*(\S+)', line)
        if prov_match:
            province = prov_match.group(1).rstrip(',')
        
        # Calculate derived values
        old_per_sqm = round(old_price / size_sqm, 0) if old_price and size_sqm else None
        new_per_sqm = round(new_price / size_sqm, 0) if new_price and size_sqm else None
        drop_pct = round((1 - new_price / old_price) * 100, 2) if old_price and new_price and old_price > 0 else None
        
        rows.append({
            "seq": int(seq),
            "property_code": code,
            "old_price_baht": old_price,
            "new_price_baht": new_price,
            "size_sqm": size_sqm,
            "old_price_per_sqm": old_per_sqm,
            "new_price_per_sqm": new_per_sqm,
            "price_drop_pct": drop_pct,
            "property_type": property_type,
            "district": district,
            "province": province,
            "raw_row_text": line.strip(),
        })
    
    return rows


def register_announcement(url, round_number=None, announcement_date=None):
    """Register a new announcement from URL. Returns announcement id."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Check if already exists
    cur.execute("SELECT id, pdf_hash FROM sam_announcements WHERE pdf_url = %s", (url,))
    existing = cur.fetchone()
    if existing:
        print(f"  Already registered: announcement #{existing[0]}")
        conn.close()
        return existing[0]
    
    # Download and hash
    pdf_path = download_pdf(url)
    phash = file_hash(pdf_path)
    
    cur.execute("""
        INSERT INTO sam_announcements (pdf_url, pdf_hash, round_number, announcement_date)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (url, phash, round_number, announcement_date))
    
    ann_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    print(f"  Registered announcement #{ann_id}")
    return ann_id, pdf_path


def parse_and_store(ann_id, pdf_path):
    """Parse PDF and store raw rows."""
    text = extract_text_from_pdf(pdf_path)
    rows = parse_price_table(text)
    
    if not rows:
        print("  ⚠️ No property rows found in PDF. May need manual review.")
        return 0
    
    conn = get_conn()
    cur = conn.cursor()
    
    stored = 0
    for row in rows:
        try:
            cur.execute("""
                INSERT INTO sam_price_history 
                (announcement_id, property_code, old_price_baht, new_price_baht,
                 size_sqm, old_price_per_sqm, new_price_per_sqm, price_drop_pct,
                 property_type, district, province, raw_row_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ann_id, row["property_code"],
                row["old_price_baht"], row["new_price_baht"],
                row["size_sqm"], row["old_price_per_sqm"], row["new_price_per_sqm"],
                row["price_drop_pct"], row["property_type"],
                row["district"], row["province"], row["raw_row_text"],
            ))
            stored += 1
        except Exception as e:
            print(f"  ⚠️ Error storing {row['property_code']}: {e}")
    
    # Update announcement count
    cur.execute("UPDATE sam_announcements SET total_properties = %s WHERE id = %s", (stored, ann_id))
    conn.commit()
    conn.close()
    
    print(f"  Parsed {len(rows)} rows, stored {stored} entries")
    return stored


def validate_data(announcement_id=None):
    """
    Validate parsed data with deterministic rules — NO LLM involved.
    Checks logic consistency and cross-references with sam_properties DB.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    if announcement_id:
        cur.execute("""
            SELECT id, property_code, old_price_baht, new_price_baht,
                   size_sqm, old_price_per_sqm, new_price_per_sqm,
                   price_drop_pct, raw_row_text
            FROM sam_price_history
            WHERE announcement_id = %s
        """, (announcement_id,))
    else:
        cur.execute("""
            SELECT id, property_code, old_price_baht, new_price_baht,
                   size_sqm, old_price_per_sqm, new_price_per_sqm,
                   price_drop_pct, raw_row_text
            FROM sam_price_history
            WHERE validation_status = 'pending'
        """)
    
    rows = cur.fetchall()
    if not rows:
        print("No rows to validate.")
        conn.close()
        return True
    
    total = len(rows)
    valid = 0
    suspect = 0
    invalid = 0
    issues = []
    
    for row in rows:
        rid, code, old_p, new_p, size, old_psm, new_psm, drop_pct, raw_text = row
        status = "valid"
        notes = []
        
        # Rule 1: If both prices exist, old should be >= new
        if old_p and new_p and old_p < new_p:
            status = "suspect"
            notes.append(f"old_price ({old_p}) < new_price ({new_p}) — price went UP?")
        
        # Rule 2: Price drop % should be 0-95% (SAM rarely drops >95%)
        if drop_pct is not None:
            if drop_pct < 0:
                status = "suspect"
                notes.append(f"negative drop_pct ({drop_pct}%)")
            elif drop_pct > 95:
                status = "suspect"
                notes.append(f"extreme drop_pct ({drop_pct}%) — verify")
        
        # Rule 3: Price per sqm sanity — commercial/residential in Bangkok typically 5K-250K/sqm
        if new_psm and (new_psm < 1000 or new_psm > 500000):
            status = "suspect"
            notes.append(f"new_price_per_sqm ({new_psm}) out of normal range")
        
        # Rule 4: Cross-reference with sam_properties — does this code exist?
        cur.execute("SELECT price_baht, size_sqm FROM sam_properties WHERE code = %s", (code,))
        db_row = cur.fetchone()
        if db_row:
            db_price, db_size = db_row
            # Rule 4a: If PDF has old price and DB current price, PDF's "new" price may be > DB
            # if there were further reductions after the announcement. This is NORMAL.
            # Only flag if new_price (from PDF) > old_price (from PDF) — which means no reduction
            # DB price being LOWER than PDF price is expected (SAM keeps reducing over time)
            
            # Rule 4b: Size should match
            if size and db_size and abs(float(size) - float(db_size)) > 1:
                notes.append(f"size mismatch: PDF={size} DB={db_size}")
                # Don't mark invalid — could be rounding
        else:
            notes.append(f"code {code} not found in sam_properties (may have been sold/removed)")
        
        # Rule 5: Recalculate derived values
        if old_p and size:
            calc_old_psm = round(old_p / float(size), 0)
            if old_psm and abs(calc_old_psm - float(old_psm)) > 100:
                status = "suspect"
                notes.append(f"old_price_per_sqm mismatch: stored={old_psm} calc={calc_old_psm}")
        
        if new_p and size:
            calc_new_psm = round(new_p / float(size), 0)
            if new_psm and abs(calc_new_psm - float(new_psm)) > 100:
                status = "suspect"
                notes.append(f"new_price_per_sqm mismatch: stored={new_psm} calc={calc_new_psm}")
        
        if old_p and new_p and old_p > 0:
            calc_drop = round((1 - new_p / old_p) * 100, 2)
            if drop_pct and abs(calc_drop - float(drop_pct)) > 0.5:
                status = "suspect"
                notes.append(f"drop_pct mismatch: stored={drop_pct} calc={calc_drop}")
        
        # Update validation
        if status == "suspect":
            suspect += 1
        else:
            valid += 1
        
        cur.execute("""
            UPDATE sam_price_history
            SET validation_status = %s, validation_note = %s
            WHERE id = %s
        """, (status, "; ".join(notes) if notes else None, rid))
        
        if notes:
            issues.append(f"  {code}: {status} — {'; '.join(notes)}")
    
    # Mark announcement as validated
    if announcement_id:
        all_valid = suspect == 0
        cur.execute("""
            UPDATE sam_announcements
            SET validated = %s, validated_at = NOW()
            WHERE id = %s
        """, (all_valid, announcement_id))
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Validation Results: {total} rows")
    print(f"  ✅ Valid: {valid}")
    print(f"  ⚠️  Suspect: {suspect}")
    print(f"  ❌ Invalid: {invalid}")
    
    if issues:
        print(f"\n⚠️ Issues found ({len(issues)}):")
        for issue in issues[:20]:  # Show first 20
            print(issue)
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    
    return suspect == 0


def show_history(code):
    """Show price history for a property."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Get current DB price
    cur.execute("""
        SELECT price_baht, size_sqm, project_name, status
        FROM sam_properties WHERE code = %s
    """, (code,))
    db = cur.fetchone()
    
    if db:
        db_price = float(db[0]) if db[0] else 0
        db_size = float(db[1]) if db[1] else 1
        print(f"📍 {code}: {db[2]} ({db[3]})")
        print(f"   Current: ฿{db_price:,.0f} / {db_size} sqm = ฿{db_price/db_size:,.0f}/sqm\n")
    else:
        print(f"📍 {code}: Not found in sam_properties\n")
    
    # Get price history
    cur.execute("""
        SELECT h.old_price_baht, h.new_price_baht, h.size_sqm,
               h.old_price_per_sqm, h.new_price_per_sqm, h.price_drop_pct,
               h.validation_status, h.validation_note,
               a.round_number, a.announcement_date
        FROM sam_price_history h
        JOIN sam_announcements a ON h.announcement_id = a.id
        WHERE h.property_code = %s
        ORDER BY a.announcement_date NULLS LAST, h.id
    """, (code,))
    
    history = cur.fetchall()
    conn.close()
    
    if not history:
        print("  No price history found.")
        return
    
    print(f"  Price History ({len(history)} records):")
    print(f"  {'Date':<12} {'Round':<12} {'Old Price':>14} {'New Price':>14} {'฿/sqm':>10} {'Drop':>6} {'Status':<10}")
    print(f"  {'-'*80}")
    
    for h in history:
        old_p, new_p, size, old_psm, new_psm, drop, vstatus, vnote, rnd, adate = h
        date_str = str(adate) if adate else "?"
        round_str = rnd or "?"
        old_str = f"฿{old_p:,}" if old_p else "-"
        new_str = f"฿{new_p:,}" if new_p else "-"
        psm_str = f"฿{new_psm:,.0f}" if new_psm else "-"
        drop_str = f"{drop}%" if drop else "-"
        status_str = vstatus or "?"
        
        print(f"  {date_str:<12} {round_str:<12} {old_str:>14} {new_str:>14} {psm_str:>10} {drop_str:>6} {status_str:<10}")
        if vnote:
            print(f"    └─ {vnote}")


def ingest_to_kb(announcement_id):
    """
    Ingest validated price history to KB.
    Only ingests rows with validation_status = 'valid'.
    Skips suspect/invalid rows.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Check announcement exists and is validated
    cur.execute("SELECT validated, round_number, pdf_url FROM sam_announcements WHERE id = %s", (announcement_id,))
    ann = cur.fetchone()
    if not ann:
        print(f"❌ Announcement #{announcement_id} not found")
        conn.close()
        return
    
    validated, round_num, pdf_url = ann
    if not validated:
        print(f"⚠️ Announcement #{announcement_id} not yet validated. Run validate first.")
        conn.close()
        return
    
    # Get valid rows only
    cur.execute("""
        SELECT h.property_code, h.old_price_baht, h.new_price_baht,
               h.size_sqm, h.new_price_per_sqm, h.price_drop_pct,
               h.property_type, h.district, h.province
        FROM sam_price_history h
        WHERE h.announcement_id = %s AND h.validation_status = 'valid'
        ORDER BY h.property_code
    """, (announcement_id,))
    
    rows = cur.fetchall()
    if not rows:
        print("No valid rows to ingest.")
        conn.close()
        return
    
    # Build summary text for KB
    lines = [f"SAM Price Reduction Announcement — Round {round_num or '?'} ({len(rows)} properties)"]
    lines.append("")
    
    for row in rows:
        code, old_p, new_p, size, psm, drop, ptype, district, province = row
        drop_str = f" (-{drop}%)" if drop else ""
        lines.append(f"{code}: {ptype or '?'} {district or '?'} {province or ''} "
                     f"{size or '?'}sqm — ฿{old_p:,}→฿{new_p:,} = ฿{psm:,.0f}/sqm{drop_str}")
    
    content = "\n".join(lines)
    description = f"SAM announcement round {round_num} — {len(rows)} property price changes"
    
    # Ingest via KB tools
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "kb" / "scripts"))
    try:
        from kb_tools import KBToolkit
        
        kb = KBToolkit()
        doc_id = kb.insert_document(
            content=content,
            description=description,
            category="pricing",
            area="multiple",
            source="SAM_announcement"
        )
        print(f"✅ Ingested to KB: {doc_id}")
        print(f"   {len(rows)} valid property price changes")
        
        # Mark as ingested
        cur.execute("""
            UPDATE sam_announcements
            SET ingested_to_kb = TRUE, ingested_at = NOW(), ingested_by = 'sam_announcements.py'
            WHERE id = %s
        """, (announcement_id,))
        conn.commit()
        
    except Exception as e:
        print(f"❌ KB ingestion failed: {e}")
        print("Data is still stored in sam_price_history. You can retry ingestion later.")
    finally:
        conn.close()


def list_announcements():
    """List all registered announcements."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, round_number, announcement_date, total_properties,
               validated, ingested_to_kb, pdf_url
        FROM sam_announcements
        ORDER BY id
    """)
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No announcements registered yet.")
        return
    
    print(f"{'ID':>3} | {'Round':<12} | {'Date':<12} | {'Props':>5} | {'Validated':>9} | {'Ingested':>8} | URL")
    print("-" * 100)
    for row in rows:
        wid, rnd, adate, total, valid, ingested, url = row
        v = "✅" if valid else "❌"
        i = "✅" if ingested else "❌"
        date_str = str(adate) if adate else "?"
        total_str = str(total) if total else "?"
        print(f"{wid:>3} | {rnd or '?':<12} | {date_str:<12} | {total_str:>5} | {v:>9} | {i:>8} | {url[:60]}")


def scan_db_links():
    """Find unique promotion_links URLs from sam_properties."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT unnest(promotion_links) as url, count(*)
        FROM sam_properties
        WHERE promotion_links IS NOT NULL
        GROUP BY url
        ORDER BY count DESC
    """)
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        print("No promotion links found in DB.")
        return
    
    print(f"Found {len(rows)} unique promotion URLs:\n")
    for url, count in rows:
        # Check if already registered
        conn2 = get_conn()
        cur2 = conn2.cursor()
        cur2.execute("SELECT id, validated, ingested_to_kb FROM sam_announcements WHERE pdf_url = %s", (url,))
        existing = cur2.fetchone()
        conn2.close()
        
        status = ""
        if existing:
            v = "validated" if existing[1] else "NOT validated"
            i = "ingested" if existing[2] else "NOT ingested"
            status = f" [#{existing[0]}: {v}, {i}]"
        
        print(f"  {url}")
        print(f"    → {count} properties{status}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAM Announcements — price history tracker")
    sub = parser.add_subparsers(dest="command")
    
    # parse-url
    p_url = sub.add_parser("parse-url", help="Download & parse PDF from URL")
    p_url.add_argument("url", help="PDF URL")
    p_url.add_argument("--round", help="Announcement round number (e.g., '7.1/2567')")
    p_url.add_argument("--date", help="Announcement date (YYYY-MM-DD)")
    
    # parse-file
    p_file = sub.add_parser("parse-file", help="Parse local PDF file")
    p_file.add_argument("path", help="Local PDF path")
    p_file.add_argument("--round", help="Announcement round number")
    p_file.add_argument("--date", help="Announcement date (YYYY-MM-DD)")
    
    # validate
    p_val = sub.add_parser("validate", help="Validate parsed data (deterministic rules)")
    p_val.add_argument("announcement_id", type=int, nargs="?", help="Specific announcement ID (default: all pending)")
    
    # history
    p_hist = sub.add_parser("history", help="Show price history for a property")
    p_hist.add_argument("code", help="Property code")
    
    # ingest
    p_ing = sub.add_parser("ingest", help="Ingest validated data to KB")
    p_ing.add_argument("announcement_id", type=int)
    
    # list
    sub.add_parser("list", help="List all announcements")
    
    # scan-db
    sub.add_parser("scan-db", help="Scan sam_properties for promotion links")
    
    args = parser.parse_args()
    
    if args.command == "parse-url":
        result = register_announcement(args.url, args.round, args.date)
        if isinstance(result, tuple):
            ann_id, pdf_path = result
        else:
            ann_id = result
            # Already registered, download anyway for parsing
            pdf_path = download_pdf(args.url)
        parse_and_store(ann_id, pdf_path)
        print(f"\n💡 Next: python sam_announcements.py validate {ann_id}")
    
    elif args.command == "parse-file":
        conn = get_conn()
        cur = conn.cursor()
        phash = file_hash(args.path)
        cur.execute("""
            INSERT INTO sam_announcements (pdf_url, pdf_hash, round_number, announcement_date)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (f"file://{args.path}", phash, args.round, args.date))
        ann_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        parse_and_store(ann_id, args.path)
        print(f"\n💡 Next: python sam_announcements.py validate {ann_id}")
    
    elif args.command == "validate":
        validate_data(args.announcement_id)
    
    elif args.command == "history":
        show_history(args.code)
    
    elif args.command == "ingest":
        ingest_to_kb(args.announcement_id)
    
    elif args.command == "list":
        list_announcements()
    
    elif args.command == "scan-db":
        scan_db_links()
    
    else:
        parser.print_help()

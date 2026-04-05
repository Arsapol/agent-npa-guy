#!/usr/bin/env python3
"""
Price Watch — Monitor specific SAM/LED properties for price drops.
Checks current DB prices against user-defined target thresholds.
Alerts via stdout (cron picks it up) when a property hits its target.

Usage:
  python price_watch.py check          # Check all watches, print alerts
  python price_watch.py add ...        # Add a new watch
  python price_watch.py list           # List all watches
  python price_watch.py remove <id>    # Remove a watch

Storage: price_watches table in npa_kb
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path

import psycopg2

DB_URL = os.environ.get("NPA_DB_URL", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_conn():
    return psycopg2.connect(DB_URL)


def ensure_table(conn):
    """Create price_watches table if not exists."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_watches (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL CHECK (source IN ('sam', 'led')),
            property_code TEXT NOT NULL,
            project_name TEXT,
            current_price_baht BIGINT,
            target_price_per_sqm_min INTEGER,
            target_price_per_sqm_max INTEGER,
            size_sqm NUMERIC,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            last_checked_at TIMESTAMP,
            last_price_baht BIGINT,
            triggered BOOLEAN DEFAULT FALSE,
            triggered_at TIMESTAMP
        )
    """)
    conn.commit()


def add_watch(source, code, target_min, target_max, notes=None):
    conn = get_conn()
    ensure_table(conn)
    cur = conn.cursor()

    # Fetch current property data
    project_name = None
    current_price = None
    size_sqm = None

    if source == "sam":
        cur.execute("""
            SELECT project_name, price_baht, size_sqm
            FROM sam_properties WHERE code = %s
        """, (code,))
    else:
        cur.execute("""
            SELECT address, primary_price_satang / 100, NULL
            FROM properties WHERE asset_id = %s
        """, (code,))

    row = cur.fetchone()
    if row:
        project_name = row[0]
        current_price = int(row[1]) if row[1] else None
        size_sqm = float(row[2]) if row[2] else None

    cur.execute("""
        INSERT INTO price_watches (source, property_code, project_name, current_price_baht,
                                    target_price_per_sqm_min, target_price_per_sqm_max,
                                    size_sqm, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (source, code, project_name, current_price, target_min, target_max, size_sqm, notes))
    
    watch_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    current_per_sqm = f"{current_price/size_sqm:,.0f}" if current_price and size_sqm else "N/A"
    print(f"✅ Watch #{watch_id} added: {source.upper()} {code}")
    print(f"   Project: {project_name or 'Unknown'}")
    print(f"   Current: ฿{current_price:,} ({current_per_sqm} ฿/ตร.ม.)" if current_price else "   Current price: N/A")
    print(f"   Target: ฿{target_min:,} - ฿{target_max:,} /ตร.ม.")
    print(f"   Notes: {notes or '-'}")
    return watch_id


def list_watches():
    conn = get_conn()
    ensure_table(conn)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, source, property_code, project_name, current_price_baht,
               target_price_per_sqm_min, target_price_per_sqm_max,
               size_sqm, notes, triggered, triggered_at
        FROM price_watches
        ORDER BY id
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No watches found.")
        return

    print(f"{'ID':>3} | {'Code':<10} | {'Project':<30} | {'Current':>14} | {'฿/sqm':>10} | {'Target ฿/sqm':>20} | {'Status':<10}")
    print("-" * 110)

    for row in rows:
        wid, source, code, project, price, tmin, tmax, size, notes, triggered, trig_at = row
        per_sqm = f"{price/size:,.0f}" if price and size else "N/A"
        price_str = f"฿{price:,}" if price else "N/A"
        target_str = f"฿{tmin:,}-{tmax:,}" if tmin and tmax else "N/A"
        status = "🔔 TRIGGERED" if triggered else "👀 Watching"
        proj = (project or "")[:30]
        print(f"{wid:>3} | {code:<10} | {proj:<30} | {price_str:>14} | {per_sqm:>10} | {target_str:>20} | {status:<10}")
        if notes:
            print(f"    └─ {notes}")


def check_watches():
    """Check all watches against current prices. Returns list of triggered alerts."""
    conn = get_conn()
    ensure_table(conn)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, source, property_code, project_name, current_price_baht,
               target_price_per_sqm_min, target_price_per_sqm_max,
               size_sqm, notes, triggered
        FROM price_watches
        WHERE triggered = FALSE
    """)
    watches = cur.fetchall()
    
    alerts = []

    for w in watches:
        wid, source, code, project, old_price, tmin, tmax, size, notes, triggered = w

        # Get latest price from source
        if source == "sam":
            cur.execute("""
                SELECT price_baht, size_sqm
                FROM sam_properties WHERE code = %s
            """, (code,))
        else:
            cur.execute("""
                SELECT primary_price_satang / 100, NULL
                FROM properties WHERE asset_id = %s
            """, (code,))

        row = cur.fetchone()
        if not row:
            continue

        current_price = int(row[0]) if row[0] else None
        current_size = float(row[1]) if row[1] else size

        if not current_price or not current_size:
            continue

        current_per_sqm = current_price / current_size

        # Update last checked
        cur.execute("""
            UPDATE price_watches
            SET last_checked_at = NOW(), last_price_baht = %s
            WHERE id = %s
        """, (current_price, wid))

        # Check if price dropped vs what we recorded
        price_changed = old_price and current_price != old_price
        if price_changed:
            cur.execute("""
                UPDATE price_watches SET current_price_baht = %s WHERE id = %s
            """, (current_price, wid))

        # Check if target hit
        if tmin and tmax and tmin <= current_per_sqm <= tmax:
            alert = {
                "watch_id": wid,
                "source": source.upper(),
                "code": code,
                "project": project or "Unknown",
                "current_price": current_price,
                "current_per_sqm": round(current_per_sqm, 0),
                "target_range": (tmin, tmax),
                "old_price": old_price,
                "notes": notes,
            }
            alerts.append(alert)

            # Mark as triggered
            cur.execute("""
                UPDATE price_watches
                SET triggered = TRUE, triggered_at = NOW()
                WHERE id = %s
            """, (wid,))
        elif price_changed and current_price < (old_price or current_price):
            # Price dropped but not yet at target — report progress
            drop_pct = (1 - current_price / old_price) * 100 if old_price else 0
            alert = {
                "watch_id": wid,
                "source": source.upper(),
                "code": code,
                "project": project or "Unknown",
                "current_price": current_price,
                "current_per_sqm": round(current_per_sqm, 0),
                "target_range": (tmin, tmax),
                "old_price": old_price,
                "drop_pct": round(drop_pct, 1),
                "notes": notes,
                "type": "price_drop",
            }
            alerts.append(alert)

    conn.commit()
    conn.close()
    return alerts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Price Watch for NPA properties")
    sub = parser.add_subparsers(dest="command")

    # add
    add_p = sub.add_parser("add", help="Add a price watch")
    add_p.add_argument("--source", required=True, choices=["sam", "led"])
    add_p.add_argument("--code", required=True, help="Property code")
    add_p.add_argument("--target-min", type=int, required=True, help="Target min ฿/sqm")
    add_p.add_argument("--target-max", type=int, required=True, help="Target max ฿/sqm")
    add_p.add_argument("--notes", default=None, help="Optional notes")

    # list
    sub.add_parser("list", help="List all watches")

    # check
    sub.add_parser("check", help="Check all watches for price drops")

    # remove
    rm_p = sub.add_parser("remove", help="Remove a watch")
    rm_p.add_argument("id", type=int)

    args = parser.parse_args()

    if args.command == "add":
        add_watch(args.source, args.code, args.target_min, args.target_max, args.notes)
    elif args.command == "list":
        list_watches()
    elif args.command == "check":
        alerts = check_watches()
        if not alerts:
            print("No alerts. All watches still above target.")
        for a in alerts:
            if a.get("type") == "price_drop":
                print(f"📉 PRICE DROP: {a['source']} {a['code']} ({a['project']})")
                print(f"   ฿{a['old_price']:,} → ฿{a['current_price']:,} (↓{a['drop_pct']}%)")
                print(f"   Current: ฿{a['current_per_sqm']:,.0f}/ตร.ม. | Target: ฿{a['target_range'][0]:,}-{a['target_range'][1]:,}/ตร.ม.")
                print(f"   ⏳ Not yet at target — keep waiting")
            else:
                print(f"🔔 TARGET HIT: {a['source']} {a['code']} ({a['project']})")
                print(f"   Current: ฿{a['current_price']:,} = ฿{a['current_per_sqm']:,.0f}/ตร.ม.")
                print(f"   Target: ฿{a['target_range'][0]:,}-{a['target_range'][1]:,}/ตร.ม. ✅")
                print(f"   Notes: {a['notes'] or '-'}")
    elif args.command == "remove":
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM price_watches WHERE id = %s RETURNING property_code", (args.id,))
        deleted = cur.fetchone()
        conn.commit()
        conn.close()
        if deleted:
            print(f"✅ Removed watch #{args.id} ({deleted[0]})")
        else:
            print(f"❌ Watch #{args.id} not found")
    else:
        parser.print_help()

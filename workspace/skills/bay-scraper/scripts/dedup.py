"""
BAY dedup — fix and remove duplicate data.

Handles:
  bay_price_history: duplicate entries for the same property on the same day
  → within each (property_code, DATE(scraped_at), change_type) group keep only
    the earliest row (first observation wins)
  → delete later duplicates

Note: bay_properties uses property code as PK so duplicates are impossible there.

Usage:
    python dedup.py            # dry run — prints what would be changed
    python dedup.py --apply    # actually execute
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import Session

from models import BayPriceHistory

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def dedup_price_history(session: Session, dry_run: bool) -> int:
    """
    Within each (property_code, DATE(scraped_at), change_type) group keep only
    the row with the smallest id (first inserted). Delete the rest.
    Returns number of rows deleted.
    """
    result = session.execute(text("""
        SELECT
            property_code,
            DATE(scraped_at AT TIME ZONE 'UTC') AS day,
            change_type,
            MIN(id)                             AS keep_id,
            COUNT(*)                            AS cnt,
            ARRAY_AGG(id ORDER BY id)           AS all_ids
        FROM bay_price_history
        GROUP BY property_code, DATE(scraped_at AT TIME ZONE 'UTC'), change_type
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)).fetchall()

    if not result:
        print("bay_price_history: no duplicates found")
        return 0

    total_deleted = 0
    delete_ids: list[int] = []

    for row in result:
        keep_id = row.keep_id
        drop_ids = [i for i in row.all_ids if i != keep_id]
        print(
            f"  code={row.property_code} day={row.day} type={row.change_type}: "
            f"keep id={keep_id}, drop {len(drop_ids)} rows"
        )
        delete_ids.extend(drop_ids)
        total_deleted += len(drop_ids)

    if not dry_run and delete_ids:
        session.execute(
            delete(BayPriceHistory).where(BayPriceHistory.id.in_(delete_ids))
        )

    return total_deleted


def main(apply: bool) -> None:
    dry_run = not apply
    mode = "DRY RUN" if dry_run else "APPLYING"
    print(f"=== BAY dedup [{mode}] — {datetime.now().isoformat()} ===\n")

    engine = get_engine()
    with Session(engine) as session:
        print("--- bay_price_history ---")
        hist_deleted = dedup_price_history(session, dry_run)

        if not dry_run:
            session.commit()
            print(f"\nCommitted.")

    print(f"\nSummary:")
    print(f"  bay_price_history rows {'would be' if dry_run else ''} deleted: {hist_deleted}")

    if dry_run and hist_deleted:
        print("\nRe-run with --apply to execute.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate BAY scraper tables")
    parser.add_argument(
        "--apply", action="store_true", help="Execute changes (default: dry run)"
    )
    args = parser.parse_args()
    main(apply=args.apply)

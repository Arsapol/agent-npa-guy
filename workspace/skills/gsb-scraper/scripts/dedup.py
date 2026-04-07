"""
GSB dedup — fix and remove duplicate data.

Handles two cases:
  1. gsb_properties: multiple rows sharing the same npa_id
     → npa_id is the PK so this shouldn't happen, but check anyway

  2. gsb_price_history: duplicate entries for the same asset on the same day
     → within each (npa_id, DATE(scraped_at), change_type) group keep only
       the earliest row (first observation wins)
     → delete later duplicates

Usage:
    python dedup.py            # dry run — prints what would be changed
    python dedup.py --apply    # actually execute
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime

from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.orm import Session

from models import GsbPriceHistory, GsbProperty

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


# ---------------------------------------------------------------------------
# Step 1: check gsb_properties for any anomalies
# ---------------------------------------------------------------------------


def check_properties(session: Session) -> int:
    """npa_id is PK so true duplicates can't exist, but report row count."""
    total = session.scalar(select(func.count(GsbProperty.npa_id)))
    print(f"gsb_properties: {total} rows (npa_id is PK, no duplicates possible)")
    return 0


# ---------------------------------------------------------------------------
# Step 2: deduplicate gsb_price_history
# ---------------------------------------------------------------------------


def dedup_price_history(session: Session, dry_run: bool) -> int:
    """
    Within each (npa_id, DATE(scraped_at), change_type) group keep only
    the row with the smallest id (first inserted). Delete the rest.
    Returns number of rows deleted.
    """
    result = session.execute(text("""
        SELECT
            npa_id,
            DATE(scraped_at AT TIME ZONE 'UTC') AS day,
            change_type,
            MIN(id)                             AS keep_id,
            COUNT(*)                            AS cnt,
            ARRAY_AGG(id ORDER BY id)           AS all_ids
        FROM gsb_price_history
        GROUP BY npa_id, DATE(scraped_at AT TIME ZONE 'UTC'), change_type
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)).fetchall()

    if not result:
        print("gsb_price_history: no duplicates found")
        return 0

    total_deleted = 0
    delete_ids: list[int] = []

    for row in result:
        keep_id = row.keep_id
        drop_ids = [i for i in row.all_ids if i != keep_id]
        print(
            f"  npa_id={row.npa_id} day={row.day} type={row.change_type}: "
            f"keep id={keep_id}, drop ids={drop_ids}"
        )
        delete_ids.extend(drop_ids)
        total_deleted += len(drop_ids)

    if not dry_run and delete_ids:
        session.execute(
            delete(GsbPriceHistory).where(GsbPriceHistory.id.in_(delete_ids))
        )

    return total_deleted


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(apply: bool) -> None:
    dry_run = not apply
    mode = "DRY RUN" if dry_run else "APPLYING"
    print(f"=== GSB dedup [{mode}] — {datetime.now().isoformat()} ===\n")

    engine = get_engine()
    with Session(engine) as session:
        print("--- gsb_properties ---")
        check_properties(session)

        print(f"\n--- gsb_price_history ---")
        hist_deleted = dedup_price_history(session, dry_run)

        if not dry_run:
            session.commit()
            print(f"\nCommitted.")

    print(f"\nSummary:")
    print(f"  gsb_price_history rows {'would be' if dry_run else ''} deleted: {hist_deleted}")

    if dry_run and hist_deleted:
        print("\nRe-run with --apply to execute.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate GSB scraper tables")
    parser.add_argument(
        "--apply", action="store_true", help="Execute changes (default: dry run)"
    )
    args = parser.parse_args()
    main(apply=args.apply)

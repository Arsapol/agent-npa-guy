"""
BAM dedup — fix and remove duplicate data.

Handles two cases:
  1. bam_properties: multiple rows sharing the same asset_no
     → keep the "best" row (has_detail=True preferred, else latest last_scraped_at)
     → re-point bam_price_history.asset_id to the surviving row
     → delete the losers

  2. bam_price_history: duplicate entries for the same asset on the same day
     → within each (asset_id, DATE(scraped_at), change_type) group keep only
       the earliest row (first observation wins)
     → delete later duplicates

Usage:
    python dedup.py            # dry run — prints what would be changed
    python dedup.py --apply    # actually execute
"""

from __future__ import annotations

import argparse
import os
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import create_engine, delete, select, text, update
from sqlalchemy.orm import Session

from models import BamPriceHistory, BamProperty

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


# ---------------------------------------------------------------------------
# Step 1: deduplicate bam_properties by asset_no
# ---------------------------------------------------------------------------


def find_property_duplicates(session: Session) -> dict[str, list[BamProperty]]:
    """Return {asset_no: [row, ...]} for asset_nos with more than one row."""
    stmt = select(BamProperty).where(BamProperty.asset_no.isnot(None)).order_by(
        BamProperty.asset_no, BamProperty.last_scraped_at.desc()
    )
    rows = session.execute(stmt).scalars().all()

    groups: dict[str, list[BamProperty]] = defaultdict(list)
    for row in rows:
        groups[row.asset_no].append(row)

    return {k: v for k, v in groups.items() if len(v) > 1}


def _best_row(rows: list[BamProperty]) -> BamProperty:
    """Pick the row to keep: prefer has_detail=True, then latest last_scraped_at."""
    with_detail = [r for r in rows if r.has_detail]
    candidates = with_detail if with_detail else rows
    return max(candidates, key=lambda r: r.last_scraped_at or datetime.min)


def dedup_properties(session: Session, dry_run: bool) -> int:
    """
    Merge duplicate bam_properties rows.
    Returns number of rows deleted.
    """
    duplicates = find_property_duplicates(session)
    if not duplicates:
        print("bam_properties: no duplicates found")
        return 0

    total_deleted = 0
    for asset_no, rows in duplicates.items():
        keeper = _best_row(rows)
        losers = [r for r in rows if r.id != keeper.id]
        loser_ids = [r.id for r in losers]

        print(
            f"  asset_no={asset_no}: keep id={keeper.id} "
            f"(has_detail={keeper.has_detail}, scraped={keeper.last_scraped_at}), "
            f"drop ids={loser_ids}"
        )

        if not dry_run:
            # Re-point price history rows from loser IDs → keeper ID
            session.execute(
                update(BamPriceHistory)
                .where(BamPriceHistory.asset_id.in_(loser_ids))
                .values(asset_id=keeper.id)
            )
            # Delete loser property rows
            session.execute(
                delete(BamProperty).where(BamProperty.id.in_(loser_ids))
            )

        total_deleted += len(loser_ids)

    return total_deleted


# ---------------------------------------------------------------------------
# Step 2: deduplicate bam_price_history
# ---------------------------------------------------------------------------


def dedup_price_history(session: Session, dry_run: bool) -> int:
    """
    Within each (asset_id, DATE(scraped_at), change_type) group keep only
    the row with the smallest id (first inserted). Delete the rest.
    Returns number of rows deleted.
    """
    # Find groups that have duplicates and the min id to keep per group
    result = session.execute(text("""
        SELECT
            asset_id,
            DATE(scraped_at AT TIME ZONE 'UTC') AS day,
            change_type,
            MIN(id)                             AS keep_id,
            COUNT(*)                            AS cnt,
            ARRAY_AGG(id ORDER BY id)           AS all_ids
        FROM bam_price_history
        GROUP BY asset_id, DATE(scraped_at AT TIME ZONE 'UTC'), change_type
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)).fetchall()

    if not result:
        print("bam_price_history: no duplicates found")
        return 0

    total_deleted = 0
    delete_ids: list[int] = []

    for row in result:
        keep_id = row.keep_id
        drop_ids = [i for i in row.all_ids if i != keep_id]
        print(
            f"  asset_id={row.asset_id} day={row.day} type={row.change_type}: "
            f"keep id={keep_id}, drop ids={drop_ids}"
        )
        delete_ids.extend(drop_ids)
        total_deleted += len(drop_ids)

    if not dry_run and delete_ids:
        session.execute(
            delete(BamPriceHistory).where(BamPriceHistory.id.in_(delete_ids))
        )

    return total_deleted


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(apply: bool) -> None:
    dry_run = not apply
    mode = "DRY RUN" if dry_run else "APPLYING"
    print(f"=== BAM dedup [{mode}] — {datetime.now(timezone.utc).isoformat()} ===\n")

    engine = get_engine()
    with Session(engine) as session:
        print("--- bam_properties ---")
        props_deleted = dedup_properties(session, dry_run)

        print(f"\n--- bam_price_history ---")
        hist_deleted = dedup_price_history(session, dry_run)

        if not dry_run:
            session.commit()
            print(f"\nCommitted.")

    print(f"\nSummary:")
    print(f"  bam_properties rows {'would be' if dry_run else ''} deleted: {props_deleted}")
    print(f"  bam_price_history rows {'would be' if dry_run else ''} deleted: {hist_deleted}")

    if dry_run and (props_deleted or hist_deleted):
        print("\nRe-run with --apply to execute.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate BAM scraper tables")
    parser.add_argument(
        "--apply", action="store_true", help="Execute changes (default: dry run)"
    )
    args = parser.parse_args()
    main(apply=args.apply)

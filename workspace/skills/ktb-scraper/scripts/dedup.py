"""
KTB dedup — fix and remove duplicate price history data.

ktb_properties has coll_grp_id as PK (confirmed stable provider ID), so no
property-level duplicates are possible. Only price history needs deduplication.

Usage:
    python dedup.py            # dry run
    python dedup.py --apply    # execute
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import Session

from models import KtbPriceHistory

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def dedup_price_history(session: Session, dry_run: bool) -> int:
    result = session.execute(text("""
        SELECT
            coll_grp_id,
            DATE(scraped_at)    AS day,
            change_type,
            MIN(id)             AS keep_id,
            COUNT(*)            AS cnt,
            ARRAY_AGG(id ORDER BY id) AS all_ids
        FROM ktb_price_history
        GROUP BY coll_grp_id, DATE(scraped_at), change_type
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """)).fetchall()

    if not result:
        print("ktb_price_history: no duplicates found")
        return 0

    delete_ids: list[int] = []
    for row in result:
        drop_ids = [i for i in row.all_ids if i != row.keep_id]
        print(
            f"  coll_grp_id={row.coll_grp_id} day={row.day} type={row.change_type}: "
            f"keep id={row.keep_id}, drop ids={drop_ids}"
        )
        delete_ids.extend(drop_ids)

    if not dry_run and delete_ids:
        session.execute(delete(KtbPriceHistory).where(KtbPriceHistory.id.in_(delete_ids)))

    return len(delete_ids)


def main(apply: bool) -> None:
    dry_run = not apply
    print(f"=== KTB dedup [{'DRY RUN' if dry_run else 'APPLYING'}] — {datetime.now().isoformat()} ===\n")

    engine = get_engine()
    with Session(engine) as session:
        deleted = dedup_price_history(session, dry_run)
        if not dry_run:
            session.commit()
            print("Committed.")

    print(f"\nSummary: ktb_price_history rows {'would be' if dry_run else ''} deleted: {deleted}")
    if dry_run and deleted:
        print("Re-run with --apply to execute.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deduplicate KTB price history")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    main(apply=args.apply)

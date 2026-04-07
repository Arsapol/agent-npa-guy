"""
TTB/PAMCO — Deduplicate price history rows.

Removes duplicate price_history entries that have the same property_id
and were scraped within 1 hour of each other with the same change_type.

Usage:
    python dedup.py            # dry-run (show what would be deleted)
    python dedup.py --apply    # actually delete duplicates
"""

import argparse

from sqlalchemy import text

from database import get_engine


DEDUP_QUERY = """
WITH ranked AS (
    SELECT id,
           property_id,
           change_type,
           scraped_at,
           ROW_NUMBER() OVER (
               PARTITION BY property_id, change_type,
                            date_trunc('hour', scraped_at)
               ORDER BY scraped_at ASC
           ) AS rn
    FROM ttb_price_history
)
SELECT id FROM ranked WHERE rn > 1
"""


def main():
    parser = argparse.ArgumentParser(description="TTB price history dedup")
    parser.add_argument("--apply", action="store_true", help="Actually delete duplicates")
    args = parser.parse_args()

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(DEDUP_QUERY))
        dup_ids = [row[0] for row in result]

        if not dup_ids:
            print("No duplicates found.")
            return

        print(f"Found {len(dup_ids)} duplicate price history rows.")

        if args.apply:
            # Delete in batches of 1000
            for i in range(0, len(dup_ids), 1000):
                batch = dup_ids[i : i + 1000]
                placeholders = ",".join(str(x) for x in batch)
                conn.execute(text(f"DELETE FROM ttb_price_history WHERE id IN ({placeholders})"))
            conn.commit()
            print(f"Deleted {len(dup_ids)} duplicate rows.")
        else:
            print("Dry run — pass --apply to delete.")


if __name__ == "__main__":
    main()

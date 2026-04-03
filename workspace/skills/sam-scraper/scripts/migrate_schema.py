"""
SAM NPA Schema Migration — One-time script to update sam_properties table.

Changes:
  - Float → Numeric for size/price/coordinate columns
  - BigInteger NOT NULL → Numeric nullable for price_baht
  - String NOT NULL → String nullable for status
  - Text (csv) → ARRAY(String) for related_property_codes
  - Replace auction_info with structured columns
  - Add new columns: thumbnail_url, map_image_url, promotion_links, house_number, auction fields

Usage: python migrate_schema.py [--db-uri ...]
"""

import argparse
import os
import sys

from sqlalchemy import create_engine, text

DEFAULT_DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


MIGRATIONS = [
    # --- Type changes: Float → Numeric ---
    "ALTER TABLE sam_properties ALTER COLUMN size_sqm TYPE NUMERIC(12,2)",
    "ALTER TABLE sam_properties ALTER COLUMN size_rai TYPE NUMERIC(8,2)",
    "ALTER TABLE sam_properties ALTER COLUMN size_ngan TYPE NUMERIC(8,2)",
    "ALTER TABLE sam_properties ALTER COLUMN size_wa TYPE NUMERIC(8,2)",
    "ALTER TABLE sam_properties ALTER COLUMN price_per_unit TYPE NUMERIC(12,2)",
    "ALTER TABLE sam_properties ALTER COLUMN lat TYPE NUMERIC(10,6)",
    "ALTER TABLE sam_properties ALTER COLUMN lng TYPE NUMERIC(10,6)",

    # --- price_baht: BigInteger NOT NULL → Numeric nullable ---
    "ALTER TABLE sam_properties ALTER COLUMN price_baht TYPE NUMERIC(15,0)",
    "ALTER TABLE sam_properties ALTER COLUMN price_baht DROP NOT NULL",
    # Convert fake 0 prices to NULL
    "UPDATE sam_properties SET price_baht = NULL WHERE price_baht = 0",

    # --- status: drop NOT NULL ---
    "ALTER TABLE sam_properties ALTER COLUMN status DROP NOT NULL",

    # --- New columns ---
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS house_number VARCHAR(100)",
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS thumbnail_url TEXT",
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS map_image_url TEXT",

    # --- Auction: structured columns replacing auction_info ---
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS announcement_start_date VARCHAR(10)",
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS registration_end_date VARCHAR(10)",
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS submission_date VARCHAR(10)",
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS auction_method_text TEXT",

    # --- ARRAY columns ---
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS promotion_links TEXT[]",

    # Convert related_property_codes from csv Text → ARRAY
    # Step 1: add new array column
    "ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS related_property_codes_arr VARCHAR[]",
    # Step 2: migrate csv data to array
    """UPDATE sam_properties
       SET related_property_codes_arr = string_to_array(related_property_codes, ',')
       WHERE related_property_codes IS NOT NULL
         AND related_property_codes != ''
         AND related_property_codes_arr IS NULL""",
    # Step 3: drop old, rename new
    "ALTER TABLE sam_properties DROP COLUMN IF EXISTS related_property_codes",
    "ALTER TABLE sam_properties RENAME COLUMN related_property_codes_arr TO related_property_codes",

    # --- Drop old auction_info blob ---
    "ALTER TABLE sam_properties DROP COLUMN IF EXISTS auction_info",
]


def main():
    parser = argparse.ArgumentParser(description="Migrate SAM schema")
    parser.add_argument("--db-uri", default=os.getenv("POSTGRES_URI", DEFAULT_DB_URI))
    parser.add_argument("--dry-run", action="store_true", help="Print SQL without executing")
    args = parser.parse_args()

    engine = create_engine(args.db_uri)

    print(f"Migrating schema: {args.db_uri}")
    if args.dry_run:
        print("(DRY RUN — no changes will be made)\n")

    errors = []
    for i, sql in enumerate(MIGRATIONS, 1):
        short = sql.strip().split("\n")[0][:80]
        if args.dry_run:
            print(f"  [{i}] {short}")
            continue

        try:
            with engine.begin() as conn:
                conn.execute(text(sql))
            print(f"  [{i}] OK: {short}")
        except Exception as e:
            err_msg = str(e).split("\n")[0]
            # Skip known-safe errors (column already exists, etc.)
            if "already exists" in err_msg or "does not exist" in err_msg:
                print(f"  [{i}] SKIP: {short} ({err_msg})")
            else:
                print(f"  [{i}] ERROR: {short}")
                print(f"       {err_msg}")
                errors.append(f"[{i}] {err_msg}")

    if errors:
        print(f"\n{len(errors)} errors occurred:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"\nMigration complete ({len(MIGRATIONS)} statements)")


if __name__ == "__main__":
    main()

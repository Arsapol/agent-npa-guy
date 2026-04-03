"""
Database Service for Property Tracking
PostgreSQL backend (local)
"""

from __future__ import annotations

import asyncio
import os
import time as time_module
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    AuctionHistory,
    Base,
    LedProperty,
    Property,
    PropertyImage,
    baht_to_satang,
    convert_be_to_iso,
    convert_image_path,
)

POSTGRES_DEFAULT_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


class PropertyDatabase:
    """Database manager for property tracking system (PostgreSQL)"""

    def __init__(self, database_url: Optional[str] = None):
        self._database_url = database_url or os.getenv("POSTGRES_URI", POSTGRES_DEFAULT_URI)
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        """Lazy-initialize SQLAlchemy engine"""
        if self._engine is None:
            self._engine = create_engine(self._database_url)
            self._session_factory = sessionmaker(bind=self._engine)
        return self._engine

    def create_tables(self):
        """Create all tables via SQLAlchemy metadata"""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables ready")

    def get_session(self) -> Session:
        """Get a new database session"""
        _ = self.engine
        return self._session_factory()

    def _get_conn(self):
        """Create a direct psycopg2 connection for bulk operations"""
        return psycopg2.connect(self._database_url)

    def insert_led_property(
        self, session: Session, property_data: Dict[str, Any], commit: bool = True
    ) -> Property:
        """Insert a single LED property via ORM"""
        asset_id = property_data["asset_id"]

        existing = session.query(Property).filter_by(asset_id=asset_id).first()
        if existing:
            print(f"⚠️  Property {asset_id} already exists, skipping...")
            return existing

        committee_price = property_data.get("committee_determined_price")
        enforcement_price = property_data.get("enforcement_officer_price")
        primary_price = committee_price or enforcement_price or 0

        property_obj = Property(
            asset_id=asset_id,
            asset_type="LED",
            source_name=property_data.get("source_name", "LED"),
            property_type=property_data.get("property_type", ""),
            address=property_data.get("address", ""),
            province=property_data.get("province", ""),
            ampur=property_data.get("ampur", ""),
            tumbol=property_data.get("tumbol", ""),
            province_id=property_data.get("province_id"),
            size_rai=float(property_data.get("size_rai", 0)),
            size_ngan=float(property_data.get("size_ngan", 0)),
            size_wa=float(property_data.get("size_wa", 0)),
            property_owner=property_data.get("property_owner"),
            primary_price_satang=baht_to_satang(primary_price),
            sale_status=property_data.get("sale_status", "unknown"),
            sale_type=property_data.get("sale_type"),
            extraction_timestamp=property_data.get("extraction_timestamp"),
        )

        led_property = LedProperty(
            asset_id=asset_id,
            case_number=property_data.get("case_number", ""),
            lot_number=property_data.get("lot_number"),
            court=property_data.get("court", ""),
            plaintiff=property_data.get("plaintiff"),
            defendant=property_data.get("defendant"),
            owner_suit_name=property_data.get("owner_suit_name"),
            issue_date=property_data.get("issue_date"),
            deed_type=property_data.get("land_type"),
            deed_number=property_data.get("deed_number"),
            enforcement_officer_price_satang=baht_to_satang(enforcement_price),
            department_appraisal_price_satang=baht_to_satang(
                property_data.get("department_appraisal_price")
            ),
            committee_determined_price_satang=baht_to_satang(committee_price),
            deposit_amount_satang=baht_to_satang(property_data.get("deposit_amount")),
            reserve_fund_special_satang=baht_to_satang(
                property_data.get("reserve_fund_special")
            ),
            sale_location=property_data.get("sale_location"),
            sale_time=property_data.get("sale_time"),
            contact_office=property_data.get("contact_office"),
            contact_phone=property_data.get("contact_phone"),
            is_extra_pledge=property_data.get("is_extra_pledge", False),
            occupant=property_data.get("occupant"),
            remark=property_data.get("remark"),
            law_court_id=property_data.get("law_court_id"),
        )

        session.add(property_obj)
        session.add(led_property)

        land_picture = property_data.get("land_picture")
        map_picture = property_data.get("map_picture")

        if land_picture:
            session.add(PropertyImage(
                asset_id=asset_id,
                image_type="land",
                image_url=convert_image_path(land_picture),
                image_order=1,
                is_primary=True,
            ))

        if map_picture:
            session.add(PropertyImage(
                asset_id=asset_id,
                image_type="map",
                image_url=convert_image_path(map_picture),
                image_order=2,
                is_primary=False,
            ))

        auction_dates = property_data.get("auction_dates", [])
        for auction_data in auction_dates:
            session.add(AuctionHistory(
                asset_id=asset_id,
                auction_number=auction_data.get("auction_number"),
                date_be=auction_data.get("date_be"),
                date_ce=convert_be_to_iso(auction_data.get("date_be", "")),
                status=auction_data.get("status", ""),
                status_code=auction_data.get("issale_value"),
                auction_type="government",
                raw_date=auction_data.get("raw_date"),
            ))

        if auction_dates:
            latest_auction = max(auction_dates, key=lambda x: x.get("auction_number", 0))
            property_obj.last_auction_date = convert_be_to_iso(latest_auction.get("date_be", ""))
            property_obj.last_auction_status = latest_auction.get("status")
            property_obj.total_auction_count = len(auction_dates)

            upcoming_auctions = [
                a for a in auction_dates if a.get("status") in ["ยังไม่ขาย", "scheduled"]
            ]
            if upcoming_auctions:
                next_auction = min(upcoming_auctions, key=lambda x: x.get("auction_number", 999))
                property_obj.next_auction_date = convert_be_to_iso(next_auction.get("date_be", ""))
                property_obj.next_auction_status = next_auction.get("status")

        if commit:
            session.commit()

        return property_obj

    async def bulk_insert_led_properties(
        self, properties_data: List[Dict[str, Any]], batch_size: int = 50
    ) -> tuple[int, int]:
        """
        Bulk insert LED properties using psycopg2 execute_values for speed.

        Args:
            properties_data: List of property dictionaries from scraper
            batch_size: Chunk size for inserts (default: 50)

        Returns:
            tuple: (successful_count, failed_count)
        """
        total = len(properties_data)
        successful = 0
        failed = 0
        duplicates_in_batch = 0
        skipped_db = 0

        print(f"\n📊 Starting bulk insert of {total} properties...")

        # STEP 1: Deduplicate within the batch
        print("🔍 Deduplicating batch...")
        seen_ids: set[str] = set()
        unique_properties: list[Dict[str, Any]] = []

        for prop_data in properties_data:
            asset_id = prop_data.get("asset_id")
            if asset_id not in seen_ids:
                seen_ids.add(asset_id)
                unique_properties.append(prop_data)
            else:
                duplicates_in_batch += 1

        if duplicates_in_batch > 0:
            print(f"   ⚠️  Found {duplicates_in_batch} duplicates within batch (keeping first occurrence)")

        # STEP 2: Check existing via direct query
        loop = asyncio.get_event_loop()
        conn = self._get_conn()
        try:
            print("🔍 Checking for existing properties...")
            check_start = time_module.time()
            asset_ids = [p.get("asset_id") for p in unique_properties]
            existing_ids: set[str] = set()

            with conn.cursor() as cur:
                for i in range(0, len(asset_ids), 500):
                    chunk = tuple(asset_ids[i:i + 500])
                    cur.execute(
                        "SELECT asset_id FROM properties WHERE asset_id IN %s",
                        (chunk,),
                    )
                    existing_ids.update(row[0] for row in cur.fetchall())

            new_properties = [
                p for p in unique_properties if p.get("asset_id") not in existing_ids
            ]
            skipped_db = len(unique_properties) - len(new_properties)

            print(
                f"   📊 Total: {total} | 🔄 Unique in batch: {len(unique_properties)} "
                f"| 🆕 New: {len(new_properties)} | ⏭️  Already in DB: {skipped_db} "
                f"({time_module.time() - check_start:.2f}s)"
            )
        except Exception as e:
            print(f"   ⚠️  Dedup check failed, will use ON CONFLICT DO NOTHING: {e}")
            new_properties = unique_properties
        finally:
            conn.close()

        if not new_properties:
            print("   ℹ️  No new properties to insert")
            return 0, 0

        # STEP 3: Prepare rows for each table
        print(f"\n🚀 Preparing {len(new_properties)} properties...")
        prep_start = time_module.time()

        property_rows = []
        led_rows = []
        image_rows = []
        auction_rows = []

        for i, prop_data in enumerate(new_properties, 1):
            try:
                asset_id = prop_data["asset_id"]
                committee_price = prop_data.get("committee_determined_price")
                enforcement_price = prop_data.get("enforcement_officer_price")
                primary_price = committee_price or enforcement_price or 0

                # Auction summary
                auction_dates = prop_data.get("auction_dates", [])
                last_auction_date = None
                last_auction_status = None
                next_auction_date = None
                next_auction_status = None

                if auction_dates:
                    latest = max(auction_dates, key=lambda x: x.get("auction_number", 0))
                    last_auction_date = convert_be_to_iso(latest.get("date_be", ""))
                    last_auction_status = latest.get("status")

                    upcoming = [
                        a for a in auction_dates
                        if a.get("status") in ["ยังไม่ขาย", "scheduled"]
                    ]
                    if upcoming:
                        next_a = min(upcoming, key=lambda x: x.get("auction_number", 999))
                        next_auction_date = convert_be_to_iso(next_a.get("date_be", ""))
                        next_auction_status = next_a.get("status")

                property_rows.append((
                    asset_id,
                    "LED",
                    prop_data.get("source_name", "LED"),
                    prop_data.get("property_type", ""),
                    prop_data.get("address", ""),
                    prop_data.get("province", ""),
                    prop_data.get("ampur", ""),
                    prop_data.get("tumbol", ""),
                    prop_data.get("province_id"),
                    float(prop_data.get("size_rai", 0)),
                    float(prop_data.get("size_ngan", 0)),
                    float(prop_data.get("size_wa", 0)),
                    prop_data.get("property_owner"),
                    baht_to_satang(primary_price),
                    prop_data.get("sale_status", "unknown"),
                    prop_data.get("sale_type"),
                    prop_data.get("extraction_timestamp"),
                    last_auction_date,
                    last_auction_status,
                    next_auction_date,
                    next_auction_status,
                    len(auction_dates),
                ))

                led_rows.append((
                    asset_id,
                    prop_data.get("case_number") or "",
                    prop_data.get("lot_number"),
                    prop_data.get("court") or "",
                    prop_data.get("plaintiff"),
                    prop_data.get("defendant"),
                    prop_data.get("owner_suit_name"),
                    prop_data.get("issue_date"),
                    prop_data.get("land_type"),
                    prop_data.get("deed_number"),
                    baht_to_satang(enforcement_price),
                    baht_to_satang(prop_data.get("department_appraisal_price")),
                    baht_to_satang(committee_price),
                    baht_to_satang(prop_data.get("deposit_amount")),
                    baht_to_satang(prop_data.get("reserve_fund_special")),
                    prop_data.get("sale_location"),
                    prop_data.get("sale_time"),
                    prop_data.get("contact_office"),
                    prop_data.get("contact_phone"),
                    prop_data.get("is_extra_pledge") or False,
                    prop_data.get("occupant"),
                    prop_data.get("remark"),
                    prop_data.get("law_court_id"),
                ))

                land_picture = prop_data.get("land_picture")
                if land_picture:
                    image_rows.append((
                        asset_id, "land", convert_image_path(land_picture), 1, True,
                    ))

                map_picture = prop_data.get("map_picture")
                if map_picture:
                    image_rows.append((
                        asset_id, "map", convert_image_path(map_picture), 2, False,
                    ))

                for auction_data in auction_dates:
                    auction_rows.append((
                        asset_id,
                        auction_data.get("auction_number"),
                        auction_data.get("date_be"),
                        convert_be_to_iso(auction_data.get("date_be", "")),
                        auction_data.get("status", ""),
                        auction_data.get("issale_value"),
                        "government",
                        auction_data.get("raw_date"),
                    ))

                successful += 1

                if i % 100 == 0:
                    print(
                        f"   📝 Prepared: {i}/{len(new_properties)} "
                        f"({i * 100 / len(new_properties):.1f}%)"
                    )

            except Exception as e:
                failed += 1
                print(f"   ❌ Error preparing {prop_data.get('asset_id', 'unknown')}: {e}")

        prep_elapsed = time_module.time() - prep_start
        total_rows = len(property_rows) + len(led_rows) + len(image_rows) + len(auction_rows)
        print(f"   ✅ Prepared {total_rows} rows across 4 tables ({prep_elapsed:.1f}s)")

        # STEP 4: Bulk insert via psycopg2 execute_values
        conn = self._get_conn()
        try:
            insert_start = time_module.time()
            with conn.cursor() as cur:
                # Properties
                if property_rows:
                    psycopg2.extras.execute_values(
                        cur,
                        """INSERT INTO properties (
                            asset_id, asset_type, source_name, property_type, address,
                            province, ampur, tumbol, province_id,
                            size_rai, size_ngan, size_wa, property_owner,
                            primary_price_satang, sale_status, sale_type,
                            extraction_timestamp, last_auction_date, last_auction_status,
                            next_auction_date, next_auction_status, total_auction_count
                        ) VALUES %s
                        ON CONFLICT (asset_id) DO NOTHING""",
                        property_rows,
                        page_size=batch_size,
                    )
                    print(f"   ⚡ properties: {len(property_rows)} rows")

                # LED properties
                if led_rows:
                    psycopg2.extras.execute_values(
                        cur,
                        """INSERT INTO led_properties (
                            asset_id, case_number, lot_number, court, plaintiff, defendant,
                            owner_suit_name, issue_date, deed_type, deed_number,
                            enforcement_officer_price_satang, department_appraisal_price_satang,
                            committee_determined_price_satang, deposit_amount_satang,
                            reserve_fund_special_satang, sale_location, sale_time,
                            contact_office, contact_phone, is_extra_pledge, occupant, remark,
                            law_court_id
                        ) VALUES %s
                        ON CONFLICT (asset_id) DO NOTHING""",
                        led_rows,
                        page_size=batch_size,
                    )
                    print(f"   ⚡ led_properties: {len(led_rows)} rows")

                # Images
                if image_rows:
                    psycopg2.extras.execute_values(
                        cur,
                        """INSERT INTO property_images (
                            asset_id, image_type, image_url, image_order, is_primary
                        ) VALUES %s""",
                        image_rows,
                        page_size=batch_size,
                    )
                    print(f"   ⚡ property_images: {len(image_rows)} rows")

                # Auction history
                if auction_rows:
                    psycopg2.extras.execute_values(
                        cur,
                        """INSERT INTO auction_history (
                            asset_id, auction_number, date_be, date_ce, status,
                            status_code, auction_type, raw_date
                        ) VALUES %s
                        ON CONFLICT (asset_id, auction_number) DO NOTHING""",
                        auction_rows,
                        page_size=batch_size,
                    )
                    print(f"   ⚡ auction_history: {len(auction_rows)} rows")

            conn.commit()

            insert_elapsed = time_module.time() - insert_start
            print(
                f"\n   ✅ All data inserted! "
                f"({total_rows} rows in {insert_elapsed:.1f}s = "
                f"{total_rows / max(insert_elapsed, 0.001):.0f} rows/sec)"
            )

        except Exception as e:
            conn.rollback()
            print(f"   ❌ Bulk insert failed: {e}")
            import traceback
            traceback.print_exc()
            failed = successful
            successful = 0
        finally:
            conn.close()

        print("\n✅ Database import complete:")
        print(f"   📥 Attempted: {total}")
        if duplicates_in_batch > 0:
            print(f"   🔄 Duplicates in batch: {duplicates_in_batch}")
        print(f"   ⏭️  Already in database: {skipped_db}")
        print(f"   ✅ Successfully inserted: {successful}")
        print(f"   ❌ Failed: {failed}")
        count = self.get_property_count()
        if count >= 0:
            print(f"   📊 Total in database: {count}")

        return successful, failed

    def get_property_count(self) -> int:
        """Get total number of properties in database"""
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM properties")
                return cur.fetchone()[0]
        except Exception:
            return -1
        finally:
            conn.close()

    def get_properties_by_province(
        self, province: str, limit: int = 100
    ) -> List[Property]:
        """Get properties by province"""
        session = self.get_session()
        try:
            return (
                session.query(Property)
                .filter(Property.province == province)
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def search_properties(
        self,
        province: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        asset_type: str = "LED",
        limit: int = 100,
    ) -> List[Property]:
        """Search properties with filters"""
        session = self.get_session()
        try:
            query = session.query(Property).filter(Property.asset_type == asset_type)

            if province:
                query = query.filter(Property.province == province)
            if min_price:
                query = query.filter(
                    Property.primary_price_satang >= baht_to_satang(min_price)
                )
            if max_price:
                query = query.filter(
                    Property.primary_price_satang <= baht_to_satang(max_price)
                )

            return query.limit(limit).all()
        finally:
            session.close()

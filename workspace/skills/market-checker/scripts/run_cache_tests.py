#!/usr/bin/env python3
"""End-to-end test suite for market_cache.py + market_checker.py integration."""

import asyncio
import sys
import traceback
from datetime import datetime

# Ensure we can import from same directory
sys.path.insert(0, "/Users/arsapolm/.nanobot-npa-guy/workspace/skills/market-checker/scripts")

from market_cache import (
    find_registry,
    create_or_update_registry,
    get_cached_prices,
    get_stale_sources,
    insert_price_snapshot,
    link_npa_property,
    get_unlinked_count,
    get_price_history,
)

results: list[dict] = []


def record(test_id: str, passed: bool, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append({"id": test_id, "status": status, "detail": detail})
    print(f"  [{status}] {test_id}: {detail}")


def run_test(test_id: str, fn):
    try:
        fn()
    except AssertionError as e:
        record(test_id, False, f"AssertionError: {e}")
    except Exception as e:
        record(test_id, False, f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# TEST 1: market_cache.py CRUD operations
# ---------------------------------------------------------------------------
print("\n=== TEST 1: market_cache.py CRUD Operations ===")

test_entry = None
test_entry_id = None

def test_1a():
    global test_entry, test_entry_id
    entry = create_or_update_registry(
        name_canonical="Test Project Alpha",
        name_th="โปรเจค อัลฟ่า ทดสอบ",
        name_en="Test Project Alpha",
        aliases=["test alpha", "alpha condo"],
        year_built=2015,
        total_units=200,
        developer="Test Developer",
        hipflat_uuid="test-uuid-123",
        zmyhome_id="99999",
    )
    assert entry.id > 0, f"Registry entry should have an ID, got {entry.id}"
    test_entry = entry
    test_entry_id = entry.id
    record("1a", True, f"Created registry id={entry.id}")

run_test("1a", test_1a)

def test_1b():
    found = find_registry("Test Project Alpha")
    assert found is not None, "find_registry returned None"
    assert found.id == test_entry_id, f"Expected id={test_entry_id}, got {found.id}"
    record("1b", True, "Found by canonical name")

run_test("1b", test_1b)

def test_1c():
    found = find_registry("โปรเจค อัลฟ่า ทดสอบ")
    assert found is not None, "find_registry returned None for Thai name"
    assert found.id == test_entry_id, f"Expected id={test_entry_id}, got {found.id}"
    record("1c", True, "Found by Thai name")

run_test("1c", test_1c)

def test_1d():
    found = find_registry("test alpha")
    assert found is not None, "find_registry returned None for alias"
    assert found.id == test_entry_id, f"Expected id={test_entry_id}, got {found.id}"
    record("1d", True, "Found by alias")

run_test("1d", test_1d)

def test_1e():
    found = find_registry("Alpha Condo")
    assert found is not None, "find_registry returned None for case-insensitive alias"
    assert found.id == test_entry_id, f"Expected id={test_entry_id}, got {found.id}"
    record("1e", True, "Found by alias (case insensitive)")

run_test("1e", test_1e)

def test_1f():
    updated = create_or_update_registry(
        name_canonical="Test Project Alpha",
        propertyhub_id="ph-12345",
        aliases=["alpha test", "test alpha"],  # "test alpha" already exists
        cam_fee_sqm=45.0,
    )
    assert updated.propertyhub_id == "ph-12345", f"Should have new propertyhub_id, got {updated.propertyhub_id}"
    assert updated.hipflat_uuid == "test-uuid-123", f"Should preserve hipflat_uuid, got {updated.hipflat_uuid}"
    assert updated.developer == "Test Developer", f"Should preserve developer, got {updated.developer}"
    assert "alpha test" in updated.aliases, f"Should have new alias 'alpha test', aliases={updated.aliases}"
    assert "test alpha" in updated.aliases, f"Should keep old alias 'test alpha', aliases={updated.aliases}"
    record("1f", True, f"Update merges correctly, aliases={len(updated.aliases)}: {updated.aliases}")

run_test("1f", test_1f)

def test_1g():
    if test_entry_id is None:
        raise AssertionError("No test_entry_id from 1a")
    for source, price, rent in [
        ("hipflat", 85000, 12000),
        ("zmyhome", 88000, 11500),
        ("propertyhub", 86000, 12500),
    ]:
        row_id = insert_price_snapshot(
            project_id=test_entry_id,
            source=source,
            matched_name=f"Test via {source}",
            sale_price_sqm=price,
            rent_median=rent,
            ttl_days=30,
        )
        assert row_id > 0, f"Expected positive row_id for {source}, got {row_id}"
    record("1g", True, "Inserted 3 price snapshots")

run_test("1g", test_1g)

def test_1h():
    if test_entry_id is None:
        raise AssertionError("No test_entry_id from 1a")
    cached = get_cached_prices(test_entry_id)
    assert len(cached) >= 3, f"Expected 3+ cached entries, got {len(cached)}"
    for c in cached:
        assert c.is_fresh, f"Source {c.source} should be fresh"
    record("1h", True, f"{len(cached)} cached prices, all fresh")

run_test("1h", test_1h)

def test_1i():
    if test_entry_id is None:
        raise AssertionError("No test_entry_id from 1a")
    stale = get_stale_sources(test_entry_id)
    assert "ddproperty" in stale, f"ddproperty should be stale, got {stale}"
    assert "hipflat" not in stale, f"hipflat should NOT be stale, got {stale}"
    record("1i", True, f"Stale sources correct: {stale}")

run_test("1i", test_1i)

def test_1j():
    if test_entry_id is None:
        raise AssertionError("No test_entry_id from 1a")
    insert_price_snapshot(
        project_id=test_entry_id,
        source="hipflat",
        sale_price_sqm=83000,  # price dropped
        rent_median=12500,
        ttl_days=30,
    )
    history = get_price_history(test_entry_id, source="hipflat")
    assert len(history) >= 2, f"Expected 2+ history entries for hipflat, got {len(history)}"
    record("1j", True, f"Price history has {len(history)} hipflat entries")

run_test("1j", test_1j)

def test_1k():
    unlinked = get_unlinked_count()
    assert isinstance(unlinked, dict), f"Expected dict, got {type(unlinked)}"
    assert "bam" in unlinked, f"Expected 'bam' in unlinked, got {unlinked.keys()}"
    record("1k", True, f"Unlinked counts: {unlinked}")

run_test("1k", test_1k)

# ---------------------------------------------------------------------------
# TEST 2: Integration with real market data
# ---------------------------------------------------------------------------
print("\n=== TEST 2: Integration with Real Market Data ===")

inspire_entry_id = None

def test_2a():
    from market_checker import check_market
    result = asyncio.run(check_market("inspire place abac", include_ddproperty=False, verbose=False))
    any_found = result.hipflat_found or result.zmyhome_found or result.propertyhub_found
    assert any_found, f"Expected at least one source to find data; hipflat={result.hipflat_found}, zmyhome={result.zmyhome_found}, propertyhub={result.propertyhub_found}"
    record("2a", True, f"market_checker works, consensus={result.sale_price_sqm_consensus}, hipflat={result.hipflat_found}, zmyhome={result.zmyhome_found}, propertyhub={result.propertyhub_found}")
    return result

result_2a = None
try:
    from market_checker import check_market
    result_2a = asyncio.run(check_market("inspire place abac", include_ddproperty=False, verbose=False))
    any_found = result_2a.hipflat_found or result_2a.zmyhome_found or result_2a.propertyhub_found
    if any_found:
        record("2a", True, f"market_checker works, consensus={result_2a.sale_price_sqm_consensus}")
    else:
        record("2a", False, "No source found data for 'inspire place abac'")
except Exception as e:
    record("2a", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

def test_2b():
    global inspire_entry_id
    if result_2a is None:
        raise AssertionError("result_2a not available (test 2a failed)")

    entry = create_or_update_registry(
        name_canonical="Inspire Place ABAC-Rama IX",
        name_th="อินสไปร์เพลส เอแบค พระราม 9",
        name_en="Inspire Place ABAC-Rama IX",
        aliases=["inspire place abac", "inspire place abac rama 9"],
        year_built=result_2a.year_built,
        total_units=result_2a.total_units,
        developer=result_2a.developer,
    )
    inspire_entry_id = entry.id

    snapshot_count = 0
    if result_2a.hipflat_found and result_2a.sale_price_sqm_hipflat is not None:
        insert_price_snapshot(
            project_id=entry.id,
            source="hipflat",
            sale_price_sqm=result_2a.sale_price_sqm_hipflat,
            rent_median=result_2a.rent_median,
        )
        snapshot_count += 1
    if result_2a.zmyhome_found and result_2a.sale_price_sqm_zmyhome_median is not None:
        insert_price_snapshot(
            project_id=entry.id,
            source="zmyhome",
            sale_price_sqm=result_2a.sale_price_sqm_zmyhome_median,
            rent_median=result_2a.rent_median,
            govt_appraisal_sqm=result_2a.govt_appraisal_sqm,
        )
        snapshot_count += 1
    if result_2a.propertyhub_found and result_2a.sale_price_sqm_propertyhub_median is not None:
        insert_price_snapshot(
            project_id=entry.id,
            source="propertyhub",
            sale_price_sqm=result_2a.sale_price_sqm_propertyhub_median,
            rent_median=result_2a.rent_median,
        )
        snapshot_count += 1

    cached = get_cached_prices(entry.id)
    assert len(cached) >= snapshot_count, f"Expected {snapshot_count}+ cached entries, got {len(cached)}"
    detail_lines = [f"Cached {len(cached)} sources for Inspire Place:"]
    for c in cached:
        detail_lines.append(f"  {c.source}: sale={c.sale_price_sqm}/sqm, fresh={c.is_fresh}")
    record("2b", True, " | ".join(detail_lines))

run_test("2b", test_2b)

def test_2c():
    if inspire_entry_id is None:
        raise AssertionError("inspire_entry_id not available (test 2b failed)")
    variants = [
        "inspire place abac",
        "Inspire Place ABAC-Rama IX",
        "อินสไปร์เพลส เอแบค พระราม 9",
    ]
    for variant in variants:
        found = find_registry(variant)
        assert found is not None, f"find_registry returned None for '{variant}'"
        assert found.id == inspire_entry_id, f"Expected id={inspire_entry_id}, got {found.id} for '{variant}'"
    record("2c", True, f"All {len(variants)} name variants resolve to same registry id={inspire_entry_id}")

run_test("2c", test_2c)

# ---------------------------------------------------------------------------
# TEST 3: Cleanup
# ---------------------------------------------------------------------------
print("\n=== TEST 3: Cleanup ===")

def test_3():
    import psycopg
    conn = psycopg.connect("postgresql://arsapolm@localhost:5432/npa_kb")
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM market_price_cache WHERE project_id IN "
            "(SELECT id FROM project_registry WHERE name_canonical = 'Test Project Alpha')"
        )
        deleted_cache = cur.rowcount
        cur.execute("DELETE FROM project_registry WHERE name_canonical = 'Test Project Alpha'")
        deleted_reg = cur.rowcount
    conn.commit()
    conn.close()
    record("3", True, f"Cleanup: deleted {deleted_cache} cache rows + {deleted_reg} registry rows (Inspire Place kept)")

run_test("3", test_3)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== SUMMARY ===")
passed = [r for r in results if r["status"] == "PASS"]
failed = [r for r in results if r["status"] == "FAIL"]
print(f"  Passed: {len(passed)}/{len(results)}")
if failed:
    print(f"  Failed: {len(failed)}")
    for f in failed:
        print(f"    - {f['id']}: {f['detail']}")
else:
    print("  All tests passed!")

# Write results to file
OUTPUT_PATH = "/Users/arsapolm/.nanobot-npa-guy/workspace/skills/market-checker/recon/cache_test_results.md"
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

lines = [
    f"# Market Cache Test Results",
    f"",
    f"Run date: {now_str}",
    f"",
    f"## Summary",
    f"",
    f"- Passed: {len(passed)}/{len(results)}",
    f"- Failed: {len(failed)}",
    f"",
    f"## Test Results",
    f"",
    "| Test | Status | Detail |",
    "|------|--------|--------|",
]
for r in results:
    status_icon = "PASS" if r["status"] == "PASS" else "FAIL"
    detail = r["detail"].replace("|", "\\|")
    lines.append(f"| {r['id']} | {status_icon} | {detail} |")

lines += [
    "",
    "## Test Groups",
    "",
    "### Test 1: market_cache.py CRUD Operations",
    "- 1a: Create registry entry",
    "- 1b: Find by canonical name",
    "- 1c: Find by Thai name",
    "- 1d: Find by alias",
    "- 1e: Find by alias (case insensitive)",
    "- 1f: Update merges correctly (no overwrites)",
    "- 1g: Insert 3 price snapshots",
    "- 1h: get_cached_prices returns fresh entries",
    "- 1i: get_stale_sources identifies missing/stale sources",
    "- 1j: Price history builds over time",
    "- 1k: get_unlinked_count returns dict",
    "",
    "### Test 2: Integration with Real Market Data",
    "- 2a: market_checker.check_market() runs successfully",
    "- 2b: Cache real results + verify retrieval",
    "- 2c: All name variants resolve to same registry entry",
    "",
    "### Test 3: Cleanup",
    "- 3: Remove test data (Inspire Place kept as real data)",
]

with open(OUTPUT_PATH, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"\nResults written to: {OUTPUT_PATH}")
sys.exit(0 if not failed else 1)

#!/usr/bin/env python3
"""
Unified Market Price Checker — queries Hipflat + ZMyHome + DDProperty in parallel.

Usage:
    python market_checker.py "15 sukhumvit residences"
    python market_checker.py "inspire place abac" --json
    python market_checker.py "circle condominium" --no-ddproperty

Sources:
    - Hipflat:     avg price/sqm, YoY trend, transaction history (fast, no CF)
    - ZMyHome:     กรมธนารักษ์ appraisal, sold/rented prices (fast, no CF)
    - DDProperty:  largest listing inventory, median price/sqm (slow, needs Camoufox)

Designed to plug into the npa-screener pipeline.
"""

import asyncio
import json
import re
import argparse
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(frozen=True)
class MarketResult:
    """Unified market data from all sources."""
    project_name: str

    # Price consensus
    sale_price_sqm_hipflat: Optional[int] = None
    sale_price_sqm_zmyhome_median: Optional[int] = None
    sale_price_sqm_propertyhub_median: Optional[int] = None
    sale_price_sqm_ddproperty_median: Optional[int] = None
    sale_price_sqm_consensus: Optional[int] = None  # best estimate

    # Historical transaction price (most reliable for NPA comparison)
    sold_price_sqm_hipflat: Optional[int] = None
    govt_appraisal_sqm: Optional[int] = None  # กรมธนารักษ์ from ZMyHome

    # Rental
    rent_min: Optional[int] = None
    rent_max: Optional[int] = None
    rent_median: Optional[int] = None

    # Project specs
    year_built: Optional[int] = None
    total_units: Optional[int] = None
    developer: Optional[str] = None

    # Liquidity signals
    units_for_sale: Optional[int] = None
    units_for_rent: Optional[int] = None

    # Trend
    yoy_change_pct: Optional[float] = None
    price_trend: Optional[str] = None

    # District benchmarks
    district_avg_sale_sqm: Optional[int] = None
    district_avg_rent_sqm: Optional[int] = None

    # PropertyHub extras
    utility_fee_sqm: Optional[str] = None  # ค่าส่วนกลาง THB/sqm/mo

    # Source availability
    hipflat_found: bool = False
    zmyhome_found: bool = False
    propertyhub_found: bool = False
    ddproperty_found: bool = False

    # For NPA screening
    confidence: str = "low"  # low / medium / high


def _safe_int(val: object) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(str(val))
    except (ValueError, TypeError):
        return None


def _normalize_year(year: Optional[int]) -> Optional[int]:
    """Convert Buddhist Era year to CE if needed."""
    if year is None:
        return None
    if year > 2400:  # Buddhist Era (พ.ศ.)
        return year - 543
    return year


# ── Smart Search: multi-query with name variants ─────────────────────────────

# Common suffixes to strip/add for search variants
_SUFFIXES_EN = [
    " condominium", " condo", " residence", " residences",
    " place", " tower", " mansion", " court",
]
_SUFFIXES_TH = [
    " คอนโดมิเนียม", " คอนโด", " เรสซิเดนเซส", " เรสซิเดนท์",
    " เพลส", " ทาวเวอร์", " แมนชั่น",
]

# Thai tone mark stripping table (sara/mai ek/mai tho etc.)
_TONE_MARKS = str.maketrans("", "", "\u0e48\u0e49\u0e4a\u0e4b")  # ่ ้ ๊ ๋


def _is_thai(text: str) -> bool:
    """Check if text contains Thai characters."""
    return bool(re.search(r"[\u0e00-\u0e7f]", text))


def _generate_name_variants(name: str) -> list[str]:
    """Generate search variants from a project name.

    Strategy:
    - Original name
    - Without common suffixes (condo, condominium, etc.)
    - Thai version without tone marks (Hipflat prefers this)
    - Key words only (first 2-3 meaningful words)
    """
    variants: list[str] = [name]
    name_lower = name.lower().strip()

    # Strip suffixes to get core name
    core = name_lower
    for suffix in _SUFFIXES_EN:
        if core.endswith(suffix):
            core = core[: -len(suffix)].strip()
            break

    core_th = name.strip()
    for suffix in _SUFFIXES_TH:
        if core_th.endswith(suffix):
            core_th = core_th[: -len(suffix)].strip()
            break

    if core != name_lower:
        variants.append(core)
    if core_th != name.strip():
        variants.append(core_th)

    # Thai without tone marks (Hipflat search works better this way)
    if _is_thai(name):
        no_tones = name.translate(_TONE_MARKS)
        if no_tones != name:
            variants.append(no_tones)
        no_tones_core = core_th.translate(_TONE_MARKS)
        if no_tones_core not in variants:
            variants.append(no_tones_core)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for v in variants:
        v_clean = v.strip()
        if v_clean and v_clean.lower() not in seen:
            seen.add(v_clean.lower())
            unique.append(v_clean)

    return unique


def _name_similarity(query: str, result_name: str) -> float:
    """Simple word-overlap similarity score (0.0 to 1.0).

    Uses lowercase word intersection over union.
    """
    q_words = set(re.findall(r"[\w\u0e00-\u0e7f]+", query.lower()))
    r_words = set(re.findall(r"[\w\u0e00-\u0e7f]+", result_name.lower()))
    if not q_words or not r_words:
        return 0.0
    intersection = q_words & r_words
    union = q_words | r_words
    return len(intersection) / len(union)


def _smart_search_hipflat(
    variants: list[str],
    min_similarity: float = 0.15,
) -> Optional[object]:
    """Try multiple name variants on Hipflat, return best match.

    When search returns exactly 1 result for a specific query, trust it
    (the platform already did the matching). Similarity check is a guard
    against wrong results when there are multiple candidates.
    """
    from hipflat_checker import search_project, fetch_project_data
    import time

    best_result = None
    best_score = 0.0

    for variant in variants:
        results = search_project(variant)
        if not results:
            continue

        # If search returns exactly 1 result, trust the platform's matching
        if len(results) == 1:
            best_result = results[0]
            best_score = 1.0
            break

        for r in results[:3]:
            r_name = r.get("name", "")
            score = max(_name_similarity(v, r_name) for v in variants)
            if score > best_score:
                best_score = score
                best_result = r

        if best_score >= 0.5:
            break

    if best_result is None:
        return None

    time.sleep(0.5)
    return fetch_project_data(best_result["id"])


def _smart_search_zmyhome(
    variants: list[str],
) -> Optional[object]:
    """Try multiple name variants on ZMyHome, return best match.

    When search returns exactly 1 result, trust the platform's matching.
    """
    from zmyhome_lookup import make_client, search_project, fetch_project_page, fetch_listings

    client = make_client()
    client.get("https://zmyhome.com")

    best_result = None
    best_score = 0.0

    try:
        for variant in variants:
            results = search_project(client, variant)
            if not results:
                continue

            if len(results) == 1:
                best_result = results[0]
                best_score = 1.0
                break

            for r in results[:3]:
                r_name = r.get("label", "")
                score = max(_name_similarity(v, r_name) for v in variants)
                if score > best_score:
                    best_score = score
                    best_result = r

            if best_score >= 0.5:
                break

        if best_result is None:
            return None

        project_id = best_result["id"]
        summary = fetch_project_page(client, project_id)
        summary.sale_listings = fetch_listings(client, project_id, "buy")
        summary.rent_listings = fetch_listings(client, project_id, "rent")
        return summary
    finally:
        client.close()


# ── Source query functions ────────────────────────────────────────────────────

async def _query_hipflat(project_name: str, name_variants: Optional[list[str]] = None) -> dict:
    """Query Hipflat with smart multi-variant search."""
    try:
        variants = name_variants or _generate_name_variants(project_name)
        proj = _smart_search_hipflat(variants)
        if proj is None:
            return {"found": False}
        g = lambda attr, default=None: getattr(proj, attr, default)  # noqa: E731
        return {
            "found": True,
            "matched_name": g("name_en") or g("name_th"),
            "avg_sale_sqm": g("avg_sale_sqm_thb"),
            "avg_sold_sqm": g("avg_sold_sqm_thb"),
            "rent_min": g("rent_price_min"),
            "rent_max": g("rent_price_max"),
            "units_for_sale": g("units_for_sale"),
            "units_for_rent": g("units_for_rent"),
            "year_completed": g("year_completed"),
            "total_units": g("total_units"),
            "yoy_change_pct": g("yoy_change_pct"),
            "price_trend": g("price_trend"),
            "district_avg_sale_sqm": g("district_avg_sale_sqm"),
            "district_avg_rent_sqm": g("district_avg_rent_sqm"),
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


async def _query_zmyhome(project_name: str, name_variants: Optional[list[str]] = None) -> dict:
    """Query ZMyHome with smart multi-variant search."""
    try:
        variants = name_variants or _generate_name_variants(project_name)
        summary = _smart_search_zmyhome(variants)
        if summary is None:
            return {"found": False}
        g = lambda attr, default=None: getattr(summary, attr, default)  # noqa: E731

        # Extract median sale price/sqm from listings
        sale_listings = g("sale_listings") or []
        sale_psms = [c.price_psm for c in sale_listings if c.price_psm]
        sale_median = int(sorted(sale_psms)[len(sale_psms) // 2]) if sale_psms else None

        # Extract rent prices
        rent_listings = g("rent_listings") or []
        rent_prices = [c.price_thb for c in rent_listings if c.price_thb]
        rent_median = int(sorted(rent_prices)[len(rent_prices) // 2]) if rent_prices else None
        rent_min = min(rent_prices) if rent_prices else None
        rent_max = max(rent_prices) if rent_prices else None

        # Extract govt appraisal (first entry as representative)
        govt_appraisal = None
        gov_appraisal_list = g("gov_appraisal") or []
        if gov_appraisal_list:
            first = gov_appraisal_list[0]
            psm_str = first.get("price_psm", "")
            psm_clean = psm_str.replace(",", "").replace(" ", "")
            try:
                govt_appraisal = int(float(psm_clean))
            except (ValueError, TypeError):
                pass

        year_built = _normalize_year(_safe_int(g("year_built")))

        return {
            "found": True,
            "sale_median_sqm": sale_median,
            "sale_count": len(sale_listings),
            "rent_median": rent_median,
            "rent_min": rent_min,
            "rent_max": rent_max,
            "rent_count": len(rent_listings),
            "developer": g("developer"),
            "year_built": year_built,
            "total_units": g("total_units"),
            "govt_appraisal_sqm": govt_appraisal,
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


async def _query_propertyhub(project_name: str, name_variants: Optional[list[str]] = None) -> dict:
    """Query PropertyHub GraphQL API. Returns structured data including CAM fee."""
    try:
        from propertyhub_checker import search_project, check_project

        variants = name_variants or _generate_name_variants(project_name)
        best_result = None
        best_score = 0.0

        for variant in variants:
            results = search_project(variant)
            if not results:
                continue

            if len(results) == 1:
                best_result = results[0]
                best_score = 1.0
                break

            for r in results[:3]:
                r_name = r.get("name", "") or r.get("nameEnglish", "")
                score = max(_name_similarity(v, r_name) for v in variants)
                if score > best_score:
                    best_score = score
                    best_result = r

            if best_score >= 0.5:
                break

        if best_result is None:
            return {"found": False}

        # Use the matched name for the full lookup
        matched_name = best_result.get("nameEnglish") or best_result.get("name", project_name)
        data = check_project(matched_name)
        if data is None:
            return {"found": False}

        sale_stats = data.sale_price_sqm_stats()
        rent_stats = data.rent_stats()
        p = data.project

        return {
            "found": True,
            "matched_name": p.name_en,
            "matched_name_slug": p.slug,
            "sale_median_sqm": sale_stats.get("median"),
            "sale_count": sale_stats.get("count", 0),
            "rent_median": rent_stats.get("median"),
            "rent_min": rent_stats.get("min"),
            "rent_max": rent_stats.get("max"),
            "rent_count": rent_stats.get("count", 0),
            "year_built": _normalize_year(_safe_int(p.completed_year)),
            "total_units": _safe_int(p.total_units),
            "developer": p.developer,
            "utility_fee_sqm": p.utility_fee,
            "lat": p.lat,
            "lng": p.lng,
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


async def _query_ddproperty(project_name: str) -> dict:
    """Query DDProperty and return raw data dict. Requires Camoufox."""
    try:
        from ddproperty_checker import check_market
        data = await check_market(project_name)

        sale_stats = data.sale_psm_stats()
        rent_stats = data.rent_stats()

        return {
            "found": bool(data.project or data.sale_listings),
            "sale_median_sqm": sale_stats.get("median"),
            "sale_count": data.sale_count,
            "rent_median": rent_stats.get("median"),
            "rent_min": rent_stats.get("min"),
            "rent_max": rent_stats.get("max"),
            "rent_count": data.rent_count,
            "year_built": data.project.completion_year if data.project else None,
            "total_units": data.project.total_units if data.project else None,
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


def _compute_consensus(*source_values: Optional[int]) -> tuple[Optional[int], str]:
    """Compute consensus price/sqm and confidence level from multiple sources."""
    values = [v for v in source_values if v]

    if not values:
        return None, "low"

    if len(values) == 1:
        return values[0], "low"

    median = sorted(values)[len(values) // 2]

    # Check agreement: if all within 15% of median, high confidence
    if all(abs(v - median) / median < 0.15 for v in values):
        confidence = "high" if len(values) >= 3 else "medium"
    else:
        confidence = "medium" if len(values) >= 2 else "low"

    return median, confidence


def _first_valid(*values: Optional[int]) -> Optional[int]:
    for v in values:
        if v is not None:
            return v
    return None


async def check_market(
    project_name: str,
    name_th: Optional[str] = None,
    name_en: Optional[str] = None,
    include_ddproperty: bool = True,
    verbose: bool = True,
) -> MarketResult:
    """
    Query all sources in parallel and return unified MarketResult.

    Args:
        project_name: Primary project name (Thai or English)
        name_th: Optional Thai name for better search (from NPA database)
        name_en: Optional English name for better search
        include_ddproperty: Set False to skip DDProperty (avoids Camoufox dependency)
        verbose: Print progress
    """
    # Build comprehensive name variants from all available names
    all_names = [project_name]
    if name_th and name_th != project_name:
        all_names.append(name_th)
    if name_en and name_en != project_name:
        all_names.append(name_en)

    variants: list[str] = []
    for n in all_names:
        variants.extend(_generate_name_variants(n))
    # Deduplicate
    seen: set[str] = set()
    unique_variants: list[str] = []
    for v in variants:
        if v.lower() not in seen:
            seen.add(v.lower())
            unique_variants.append(v)

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Market Check: {project_name}")
        if len(unique_variants) > 1:
            print(f"  Search variants: {unique_variants[:5]}")
        print(f"{'='*60}")

    # Launch queries in parallel
    tasks = {
        "hipflat": asyncio.create_task(_query_hipflat(project_name, unique_variants)),
        "zmyhome": asyncio.create_task(_query_zmyhome(project_name, unique_variants)),
        "propertyhub": asyncio.create_task(_query_propertyhub(project_name, unique_variants)),
    }
    if include_ddproperty:
        tasks["ddproperty"] = asyncio.create_task(_query_ddproperty(project_name))

    results = {}
    for name, task in tasks.items():
        try:
            results[name] = await task
            status = "found" if results[name].get("found") else "not found"
            if verbose:
                error = results[name].get("error", "")
                err_str = f" ({error})" if error else ""
                print(f"  [{name}] {status}{err_str}")
        except Exception as e:
            results[name] = {"found": False, "error": str(e)}
            if verbose:
                print(f"  [{name}] error: {e}")

    h = results.get("hipflat", {})
    z = results.get("zmyhome", {})
    p = results.get("propertyhub", {})
    d = results.get("ddproperty", {})

    # Compute consensus price from all available sources
    consensus_sqm, confidence = _compute_consensus(
        h.get("avg_sale_sqm") or h.get("avg_sold_sqm"),
        z.get("sale_median_sqm"),
        p.get("sale_median_sqm"),
        d.get("sale_median_sqm"),
    )

    # Merge rent data from all sources
    rent_values = [
        v for v in [
            h.get("rent_min"), h.get("rent_max"),
            z.get("rent_min"), z.get("rent_max"),
            p.get("rent_min"), p.get("rent_max"),
            d.get("rent_min"), d.get("rent_max"),
        ] if v
    ]
    rent_medians = [v for v in [
        p.get("rent_median"), z.get("rent_median"), d.get("rent_median"),
    ] if v]

    result = MarketResult(
        project_name=project_name,
        # Sale prices per source
        sale_price_sqm_hipflat=h.get("avg_sale_sqm"),
        sale_price_sqm_zmyhome_median=z.get("sale_median_sqm"),
        sale_price_sqm_propertyhub_median=p.get("sale_median_sqm"),
        sale_price_sqm_ddproperty_median=d.get("sale_median_sqm"),
        sale_price_sqm_consensus=consensus_sqm,
        # Historical/appraisal
        sold_price_sqm_hipflat=h.get("avg_sold_sqm"),
        govt_appraisal_sqm=z.get("govt_appraisal_sqm"),
        # Rental
        rent_min=min(rent_values) if rent_values else None,
        rent_max=max(rent_values) if rent_values else None,
        rent_median=rent_medians[0] if rent_medians else None,
        # Specs (first valid from any source)
        year_built=_normalize_year(_first_valid(
            h.get("year_completed"), p.get("year_built"), z.get("year_built"), d.get("year_built"),
        )),
        total_units=_first_valid(
            p.get("total_units"), h.get("total_units"), z.get("total_units"), d.get("total_units"),
        ),
        developer=p.get("developer") or z.get("developer"),
        # Liquidity
        units_for_sale=_first_valid(
            h.get("units_for_sale"), d.get("sale_count"), p.get("sale_count"), z.get("sale_count"),
        ),
        units_for_rent=_first_valid(
            h.get("units_for_rent"), d.get("rent_count"), p.get("rent_count"), z.get("rent_count"),
        ),
        # Trends (Hipflat only)
        yoy_change_pct=h.get("yoy_change_pct"),
        price_trend=h.get("price_trend"),
        # District (Hipflat only)
        district_avg_sale_sqm=h.get("district_avg_sale_sqm"),
        district_avg_rent_sqm=h.get("district_avg_rent_sqm"),
        # PropertyHub extras
        utility_fee_sqm=p.get("utility_fee_sqm"),
        # Source flags
        hipflat_found=h.get("found", False),
        zmyhome_found=z.get("found", False),
        propertyhub_found=p.get("found", False),
        ddproperty_found=d.get("found", False),
        confidence=confidence,
    )

    if verbose:
        print_result(result)

    return result


def npa_discount(npa_price_sqm: int, market: MarketResult) -> Optional[float]:
    """Calculate real discount vs market consensus. Returns percentage."""
    if market.sale_price_sqm_consensus is None:
        return None
    return (market.sale_price_sqm_consensus - npa_price_sqm) / market.sale_price_sqm_consensus * 100


def npa_yield(npa_price: int, market: MarketResult) -> Optional[float]:
    """Calculate gross rental yield using market rental data."""
    if market.rent_median:
        return market.rent_median * 12 / npa_price * 100
    if market.rent_min:
        return market.rent_min * 12 / npa_price * 100
    return None


def print_result(r: MarketResult) -> None:
    sources = []
    if r.hipflat_found:
        sources.append("Hipflat")
    if r.zmyhome_found:
        sources.append("ZMyHome")
    if r.propertyhub_found:
        sources.append("PropertyHub")
    if r.ddproperty_found:
        sources.append("DDProperty")

    print(f"\n  Sources: {', '.join(sources) or 'NONE'} | Confidence: {r.confidence.upper()}")

    print("\n  --- SALE PRICE/SQM ---")
    if r.sale_price_sqm_hipflat:
        print(f"  Hipflat listing avg : ฿{r.sale_price_sqm_hipflat:,}")
    if r.sold_price_sqm_hipflat:
        print(f"  Hipflat SOLD avg    : ฿{r.sold_price_sqm_hipflat:,}  <- historical txn")
    if r.sale_price_sqm_zmyhome_median:
        print(f"  ZMyHome median      : ฿{r.sale_price_sqm_zmyhome_median:,}")
    if r.sale_price_sqm_propertyhub_median:
        print(f"  PropertyHub median  : ฿{r.sale_price_sqm_propertyhub_median:,}")
    if r.sale_price_sqm_ddproperty_median:
        print(f"  DDProperty median   : ฿{r.sale_price_sqm_ddproperty_median:,}")
    if r.sale_price_sqm_consensus:
        print(f"  >>> CONSENSUS       : ฿{r.sale_price_sqm_consensus:,}/sqm ({r.confidence})")
    if r.govt_appraisal_sqm:
        print(f"  กรมธนารักษ์ appraisal: ฿{r.govt_appraisal_sqm:,}/sqm")

    print("\n  --- RENTAL ---")
    if r.rent_median:
        print(f"  Median rent         : ฿{r.rent_median:,}/mo")
    if r.rent_min and r.rent_max:
        print(f"  Range               : ฿{r.rent_min:,} - ฿{r.rent_max:,}/mo")

    print("\n  --- PROJECT ---")
    if r.year_built:
        age = 2026 - r.year_built
        flag = " OK" if 2008 <= r.year_built <= 2018 else (" OLD" if r.year_built < 2006 else "")
        print(f"  Year built          : {r.year_built} ({age} years){flag}")
    if r.developer:
        print(f"  Developer           : {r.developer}")
    if r.total_units:
        print(f"  Total units         : {r.total_units}")
    if r.utility_fee_sqm:
        print(f"  CAM fee             : {r.utility_fee_sqm} THB/sqm/mo")

    print("\n  --- LIQUIDITY ---")
    if r.units_for_sale is not None:
        print(f"  Units for sale      : {r.units_for_sale}")
    if r.units_for_rent is not None:
        print(f"  Units for rent      : {r.units_for_rent}")

    if r.yoy_change_pct is not None or r.price_trend is not None:
        print("\n  --- TREND ---")
    if r.yoy_change_pct is not None:
        direction = "up" if r.yoy_change_pct >= 0 else "down"
        print(f"  YoY change          : {direction} {r.yoy_change_pct:+.1f}%")
    if r.price_trend is not None:
        trend_en = "uptrend" if r.price_trend == "ขาขึ้น" else "downtrend"
        print(f"  Long-term trend     : {trend_en} ({r.price_trend})")

    if r.district_avg_sale_sqm:
        print("\n  --- DISTRICT ---")
        print(f"  District sale avg   : ฿{r.district_avg_sale_sqm:,}/sqm")
        if r.district_avg_rent_sqm:
            print(f"  District rent avg   : ฿{r.district_avg_rent_sqm:,}/sqm/mo")

    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified Market Price Checker",
        epilog="Examples:\n"
               "  python market_checker.py 'esta phahol'\n"
               "  python market_checker.py 'esta condo' --thai 'เอสต้า พหล-สะพานใหม่'\n"
               "  python market_checker.py 'inspire place abac' --no-ddproperty\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("name", nargs="+", help="Project name to search")
    parser.add_argument("--thai", dest="name_th", help="Thai name (improves ZMyHome search)")
    parser.add_argument("--english", dest="name_en", help="English name (improves Hipflat search)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-ddproperty", action="store_true",
                        help="Skip DDProperty (avoids Camoufox dependency)")
    args = parser.parse_args()

    project_name = " ".join(args.name)
    result = await check_market(
        project_name,
        name_th=args.name_th,
        name_en=args.name_en,
        include_ddproperty=not args.no_ddproperty,
        verbose=not args.json,
    )

    if args.json:
        out = {k: v for k, v in asdict(result).items() if v is not None}
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

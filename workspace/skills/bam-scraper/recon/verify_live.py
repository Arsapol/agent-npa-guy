"""Verify models against live API data with diverse asset types."""
import asyncio
import json
import sys

import httpx

sys.path.insert(0, "../scripts")
from models import BamAssetDetail, BamAssetSearch

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://www.bam.co.th",
    "referer": "https://www.bam.co.th/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


async def main():
    errors_search = []
    errors_detail = []
    unknown_keys_search = set()
    unknown_keys_detail = set()

    # Get model field names + aliases
    search_known = set()
    for name, field in BamAssetSearch.model_fields.items():
        search_known.add(name)
        if field.alias:
            search_known.add(field.alias)

    detail_known = set()
    for name, field in BamAssetDetail.model_fields.items():
        detail_known.add(name)
        if field.alias:
            detail_known.add(field.alias)

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch page 1 from 5 different provinces for diversity
        provinces = ["กรุงเทพมหานคร", "เชียงใหม่", "ภูเก็ต", "ชลบุรี", "นครราชสีมา"]
        all_items = []

        for prov in provinces:
            r = await client.post(
                "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search",
                json={
                    "pageSize": 10, "pageNumber": 1, "inputText": "",
                    "assetType": "", "bedroom": "", "bathroom": "",
                    "startMeter": "", "endMeter": "", "province": prov,
                    "district": "", "firstPriceRange": "", "secondPriceRange": "",
                    "thirdPriceRange": "", "fourthPriceRange": "", "sortby": "",
                    "startTwoMeter": "", "endTwoMeter": "", "nearby": [],
                    "isHotDeal": "", "isCampaign": "", "campaignName": "",
                    "stars": "", "isCenterPrice": "", "isSpecialPrice": "",
                    "isShockPrice": "", "isFourthPrice": "",
                    "userKey": "", "smartSearch": None, "semanticSearch": None,
                },
                headers=BASE_HEADERS,
            )
            data = r.json()
            items = data.get("data", [])
            all_items.extend(items)
            print(f"{prov}: {len(items)} items")

        # Test search parsing
        for item in all_items:
            # Check for unknown keys
            for k in item.keys():
                if k not in search_known and k != "raw_json":
                    unknown_keys_search.add(k)

            try:
                BamAssetSearch.model_validate(item)
            except Exception as e:
                errors_search.append((item.get("id"), str(e)[:200]))

        print(f"\nSearch: {len(all_items)} items tested, {len(errors_search)} errors")
        if unknown_keys_search:
            print(f"  UNKNOWN KEYS: {unknown_keys_search}")
        for aid, err in errors_search[:5]:
            print(f"  Error {aid}: {err}")

        # Test detail parsing (sample 10)
        sample_ids = [item["id"] for item in all_items[:10]]
        for aid in sample_ids:
            r = await client.get(
                f"https://bam-bo-api-prd.bam.co.th/property-detail/getExpiredSubscriptionDateTimeByAssetId/{aid}",
                headers=BASE_HEADERS,
            )
            detail = r.json()

            for k in detail.keys():
                if k not in detail_known:
                    unknown_keys_detail.add(k)

            try:
                BamAssetDetail.model_validate(detail)
            except Exception as e:
                errors_detail.append((aid, str(e)[:200]))

        print(f"\nDetail: {len(sample_ids)} items tested, {len(errors_detail)} errors")
        if unknown_keys_detail:
            print(f"  UNKNOWN KEYS: {unknown_keys_detail}")
        for aid, err in errors_detail[:5]:
            print(f"  Error {aid}: {err}")

    total_errors = len(errors_search) + len(errors_detail)
    total_unknown = len(unknown_keys_search) + len(unknown_keys_detail)
    print(f"\n=== VERDICT ===")
    print(f"Parse errors: {total_errors}")
    print(f"Unknown keys: {total_unknown}")
    if total_errors == 0 and total_unknown == 0:
        print("ALL FIELDS CAPTURED, NO PARSE ERRORS!")


asyncio.run(main())

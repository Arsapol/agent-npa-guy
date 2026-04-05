"""Test BAM detail + campaign endpoints."""
import asyncio
import json
import httpx

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://www.bam.co.th",
    "referer": "https://www.bam.co.th/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

# Use the asset ID from earlier search result (154304) + the one from user (136725)
TEST_IDS = [154304, 136725]


async def fetch_detail(client: httpx.AsyncClient, asset_id: int) -> dict:
    r = await client.get(
        f"https://bam-bo-api-prd.bam.co.th/property-detail/getExpiredSubscriptionDateTimeByAssetId/{asset_id}",
        headers=BASE_HEADERS,
    )
    return {"asset_id": asset_id, "status": r.status_code, "data": r.json()}


async def fetch_campaign(client: httpx.AsyncClient, asset_id: int) -> dict:
    r = await client.get(
        f"https://bam-bo-api-prd.bam.co.th/cmk-v2/getCampaignCondition/{asset_id}",
        headers=BASE_HEADERS,
    )
    return {"asset_id": asset_id, "status": r.status_code, "data": r.json()}


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        tasks = []
        for aid in TEST_IDS:
            tasks.append(fetch_detail(client, aid))
            tasks.append(fetch_campaign(client, aid))
        results = await asyncio.gather(*tasks)

    details = [r for r in results if "getExpired" not in str(r)]
    # Group by type
    detail_results = results[::2]  # even indices
    campaign_results = results[1::2]  # odd indices

    with open("detail_responses.json", "w", encoding="utf-8") as f:
        json.dump(detail_results, f, ensure_ascii=False, indent=2)
    with open("campaign_responses.json", "w", encoding="utf-8") as f:
        json.dump(campaign_results, f, ensure_ascii=False, indent=2)

    print("=== DETAIL RESPONSES ===")
    for r in detail_results:
        print(f"\nAsset {r['asset_id']} (status {r['status']}):")
        print(json.dumps(r["data"], ensure_ascii=False, indent=2)[:2000])

    print("\n=== CAMPAIGN RESPONSES ===")
    for r in campaign_results:
        print(f"\nAsset {r['asset_id']} (status {r['status']}):")
        print(json.dumps(r["data"], ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    asyncio.run(main())

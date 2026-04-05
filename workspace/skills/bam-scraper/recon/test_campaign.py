"""Find assets with campaigns and check campaign endpoint."""
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


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # Search for campaign assets
        r = await client.post(
            "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search",
            json={
                "pageSize": 5, "pageNumber": 1, "inputText": "",
                "assetType": "", "bedroom": "", "bathroom": "",
                "startMeter": "", "endMeter": "", "province": "",
                "district": "", "firstPriceRange": "", "secondPriceRange": "",
                "thirdPriceRange": "", "fourthPriceRange": "", "sortby": "",
                "startTwoMeter": "", "endTwoMeter": "", "nearby": [],
                "isHotDeal": "", "isCampaign": "true", "campaignName": "",
                "stars": "", "isCenterPrice": "", "isSpecialPrice": "",
                "isShockPrice": "", "isFourthPrice": "",
                "userKey": "8qovak2zgv6mmxjsslc",
                "smartSearch": None, "semanticSearch": None,
            },
            headers=BASE_HEADERS,
        )
        search = r.json()
        print(f"Campaign assets total: {search.get('totalData', 0)}")

        # Check campaign endpoint for first few
        for asset in search.get("data", [])[:3]:
            aid = asset["id"]
            cr = await client.get(
                f"https://bam-bo-api-prd.bam.co.th/cmk-v2/getCampaignCondition/{aid}",
                headers=BASE_HEADERS,
            )
            cdata = cr.json()
            print(f"\nAsset {aid} ({asset.get('assetNo')}) campaign={asset.get('isCampaign')} campaignName={asset.get('campaignName')}:")
            print(json.dumps(cdata, ensure_ascii=False, indent=2)[:1500])

        # Also save a campaign asset's full search data
        if search.get("data"):
            with open("campaign_asset_sample.json", "w", encoding="utf-8") as f:
                json.dump(search["data"][0], f, ensure_ascii=False, indent=2)
            print(f"\nSaved campaign_asset_sample.json")


if __name__ == "__main__":
    asyncio.run(main())

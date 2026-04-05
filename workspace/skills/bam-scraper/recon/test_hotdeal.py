"""Find hot deal / shock price assets."""
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

BASE_BODY = {
    "pageSize": 3, "pageNumber": 1, "inputText": "",
    "assetType": "", "bedroom": "", "bathroom": "",
    "startMeter": "", "endMeter": "", "province": "",
    "district": "", "firstPriceRange": "", "secondPriceRange": "",
    "thirdPriceRange": "", "fourthPriceRange": "", "sortby": "",
    "startTwoMeter": "", "endTwoMeter": "", "nearby": [],
    "isHotDeal": "", "isCampaign": "", "campaignName": "",
    "stars": "", "isCenterPrice": "", "isSpecialPrice": "",
    "isShockPrice": "", "isFourthPrice": "",
    "userKey": "8qovak2zgv6mmxjsslc",
    "smartSearch": None, "semanticSearch": None,
}


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # Try different filters
        for label, overrides in [
            ("hotDeal", {"isHotDeal": "true"}),
            ("shockPrice", {"isShockPrice": "true"}),
            ("specialPrice", {"isSpecialPrice": "true"}),
            ("centerPrice", {"isCenterPrice": "true"}),
            ("stars=5", {"stars": "5"}),
        ]:
            body = {**BASE_BODY, **overrides}
            r = await client.post(
                "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search",
                json=body, headers=BASE_HEADERS,
            )
            d = r.json()
            total = d.get("totalData", 0)
            print(f"{label}: {total} assets")
            if d.get("data") and total > 0:
                a = d["data"][0]
                print(f"  sample: {a.get('assetNo')} sell={a.get('sellPrice')} discount={a.get('discountPrice')} shock={a.get('shockPrice')} stars={a.get('stars')}")

        # Total assets across all provinces
        body = {**BASE_BODY, "pageSize": 1}
        r = await client.post(
            "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search",
            json=body, headers=BASE_HEADERS,
        )
        print(f"\nTotal assets (all provinces): {r.json().get('totalData', 0)}")


if __name__ == "__main__":
    asyncio.run(main())

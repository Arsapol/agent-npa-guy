"""Test BAM API endpoints and save responses as JSON."""
import asyncio
import json
import httpx

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.bam.co.th",
    "referer": "https://www.bam.co.th/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}


async def test_provinces(client: httpx.AsyncClient) -> dict:
    r = await client.post(
        "https://bam-bo-api-prd.bam.co.th/master/province/filter",
        json={"text": ""},
        headers=BASE_HEADERS,
    )
    return r.json()


async def test_districts(client: httpx.AsyncClient) -> dict:
    r = await client.post(
        "https://bam-bo-api-prd.bam.co.th/master/District/Dropdown/find",
        json={"province": "กรุงเทพมหานคร"},
        headers=BASE_HEADERS,
    )
    return r.json()


async def test_search(client: httpx.AsyncClient) -> dict:
    r = await client.post(
        "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search",
        json={
            "pageSize": 2,
            "pageNumber": 1,
            "inputText": "",
            "assetType": "",
            "bedroom": "",
            "bathroom": "",
            "startMeter": "",
            "endMeter": "",
            "province": "กรุงเทพมหานคร",
            "district": "",
            "firstPriceRange": "",
            "secondPriceRange": "",
            "thirdPriceRange": "",
            "fourthPriceRange": "",
            "sortby": "",
            "startTwoMeter": "",
            "endTwoMeter": "",
            "nearby": [],
            "isHotDeal": "",
            "isCampaign": "",
            "campaignName": "",
            "stars": "",
            "isCenterPrice": "",
            "isSpecialPrice": "",
            "isShockPrice": "",
            "isFourthPrice": "",
            "userKey": "8qovak2zgv6mmxjsslc",
            "smartSearch": None,
            "semanticSearch": None,
        },
        headers=BASE_HEADERS,
    )
    return r.json()


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        provinces, districts, search = await asyncio.gather(
            test_provinces(client),
            test_districts(client),
            test_search(client),
        )

    out_dir = "."
    for name, data in [
        ("provinces", provinces),
        ("districts_bangkok", districts),
        ("search_bangkok", search),
    ]:
        path = f"{out_dir}/{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {path} ({len(json.dumps(data))} bytes)")


if __name__ == "__main__":
    asyncio.run(main())

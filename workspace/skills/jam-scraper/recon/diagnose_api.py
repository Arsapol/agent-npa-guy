"""
Diagnose why JAM API requests fail.
Tests: rate limits, response codes, timeouts, connection issues.
"""

import asyncio
import json
import time

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = b"QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf"
BASE_URL = "https://www.jjpropertythai.com/api/proxy/v1"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.jjpropertythai.com/Search",
}


def decrypt(data: dict) -> dict:
    if "_encrypted" not in data:
        return data
    parts = data["_encrypted"].split(":")
    iv = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ct = bytes.fromhex(parts[2])
    return json.loads(AESGCM(KEY).decrypt(iv, ct + tag, None).decode("utf-8"))


async def test_single_request(client: httpx.AsyncClient, page: int) -> dict:
    """Test a single request and capture full diagnostic info."""
    start = time.time()
    result = {
        "page": page,
        "status": None,
        "elapsed_ms": None,
        "error": None,
        "response_size": None,
        "items_count": None,
        "headers": None,
    }
    try:
        resp = await client.get(
            f"{BASE_URL}/assets",
            params={
                "freeText": "",
                "page": page,
                "user_code": "521789",
                "limit": 50,
                "SellingStart": 0,
                "SellingEnd": 100000000,
            },
            headers=HEADERS,
        )
        result["status"] = resp.status_code
        result["elapsed_ms"] = round((time.time() - start) * 1000)
        result["response_size"] = len(resp.content)
        result["headers"] = dict(resp.headers)

        if resp.status_code == 200:
            data = decrypt(resp.json())
            result["items_count"] = len(data.get("data", []))
            result["total_from_api"] = data.get("count")
        else:
            result["body_preview"] = resp.text[:500]

    except httpx.ReadTimeout:
        result["error"] = "ReadTimeout"
        result["elapsed_ms"] = round((time.time() - start) * 1000)
    except httpx.ConnectTimeout:
        result["error"] = "ConnectTimeout"
        result["elapsed_ms"] = round((time.time() - start) * 1000)
    except httpx.ConnectError as e:
        result["error"] = f"ConnectError: {e}"
        result["elapsed_ms"] = round((time.time() - start) * 1000)
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["elapsed_ms"] = round((time.time() - start) * 1000)

    return result


async def main():
    print("=== JAM API Diagnostics ===\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Sequential single requests (pages 1-5)
        print("Test 1: Sequential requests (1s apart)")
        for page in [1, 2, 3, 10, 50, 100]:
            r = await test_single_request(client, page)
            status = r["status"] or r["error"]
            items = r.get("items_count", "?")
            ms = r["elapsed_ms"]
            size = r.get('response_size') or 0
            print(f"  Page {page:3d}: {status} | {ms:4d}ms | {items} items | {size:,}b")
            await asyncio.sleep(1.0)

        # Test 2: Burst — 5 concurrent requests
        print("\nTest 2: 5 concurrent requests")
        tasks = [test_single_request(client, p) for p in range(1, 6)]
        results = await asyncio.gather(*tasks)
        for r in results:
            status = r["status"] or r["error"]
            items = r.get("items_count", "?")
            ms = r["elapsed_ms"]
            print(f"  Page {r['page']:3d}: {status} | {ms:4d}ms | {items} items")

        await asyncio.sleep(3.0)

        # Test 3: Burst — 10 concurrent requests
        print("\nTest 3: 10 concurrent requests")
        tasks = [test_single_request(client, p) for p in range(1, 11)]
        results = await asyncio.gather(*tasks)
        for r in results:
            status = r["status"] or r["error"]
            items = r.get("items_count", "?")
            ms = r["elapsed_ms"]
            print(f"  Page {r['page']:3d}: {status} | {ms:4d}ms | {items} items")

        await asyncio.sleep(3.0)

        # Test 4: Rapid sequential (no delay)
        print("\nTest 4: 10 rapid sequential (no delay)")
        for page in range(1, 11):
            r = await test_single_request(client, page)
            status = r["status"] or r["error"]
            items = r.get("items_count", "?")
            ms = r["elapsed_ms"]
            print(f"  Page {page:3d}: {status} | {ms:4d}ms | {items} items")

        await asyncio.sleep(3.0)

        # Test 5: Check response headers for rate limit info
        print("\nTest 5: Response headers inspection")
        r = await test_single_request(client, 1)
        if r["headers"]:
            interesting = {k: v for k, v in r["headers"].items()
                          if any(x in k.lower() for x in ["rate", "limit", "retry", "x-", "cf-", "server"])}
            if interesting:
                print("  Rate-limit related headers:")
                for k, v in interesting.items():
                    print(f"    {k}: {v}")
            else:
                print("  No rate-limit headers found. All headers:")
                for k, v in r["headers"].items():
                    print(f"    {k}: {v}")

        # Test 6: Different timeout values
        print("\nTest 6: Timeout sensitivity")
        for timeout in [5, 10, 20, 30]:
            async with httpx.AsyncClient(timeout=float(timeout)) as tc:
                r = await test_single_request(tc, 1)
                status = r["status"] or r["error"]
                ms = r["elapsed_ms"]
                print(f"  Timeout={timeout:2d}s: {status} | {ms:4d}ms")

    print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())

"""
Test JAM API decryption.

Encryption: AES-256-GCM
Key: QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf (32 bytes = 256-bit)
Format: iv_hex:tag_hex:ciphertext_hex

The JS concatenates ciphertext + tag before decrypting:
  i = new Uint8Array([...o, ...s])  // [...ciphertext, ...tag]
Then: crypto.subtle.decrypt({name:"AES-GCM", iv: r}, key, i)
"""

import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = b"QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf"  # 32 bytes = AES-256


def decrypt_response(encrypted_str: str) -> dict:
    """Decrypt a JAM API encrypted response."""
    parts = encrypted_str.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts separated by ':', got {len(parts)}")

    iv = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ciphertext = bytes.fromhex(parts[2])

    # AES-GCM: the tag is appended to the ciphertext
    # JS does: new Uint8Array([...ciphertext, ...tag])
    aesgcm = AESGCM(KEY)
    plaintext = aesgcm.decrypt(iv, ciphertext + tag, None)

    return json.loads(plaintext.decode("utf-8"))


def main():
    # Test with a sample encrypted response
    # Fetch from the API first
    import httpx

    print("Fetching encrypted data from JAM API...")
    resp = httpx.get(
        "https://www.jjpropertythai.com/api/proxy/v1/assets",
        params={
            "freeText": "",
            "page": 1,
            "user_code": "521789",
            "limit": 2,
            "SellingStart": 0,
            "SellingEnd": 100000000,
            "typeSaleIn[]": "3",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.jjpropertythai.com/Search",
        },
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()

    if "_encrypted" in data:
        encrypted = data["_encrypted"]
        print(f"Encrypted data length: {len(encrypted):,} chars")
        print(f"IV: {encrypted[:32]}")
        print(f"Tag: {encrypted[33:65]}")
        print(f"Ciphertext preview: {encrypted[66:130]}...")

        print("\nDecrypting...")
        decrypted = decrypt_response(encrypted)
        print(f"Decrypted type: {type(decrypted)}")

        if isinstance(decrypted, dict):
            print(f"Keys: {list(decrypted.keys())}")
            # Pretty print first item if it's a list of properties
            if "data" in decrypted:
                items = decrypted["data"]
                if isinstance(items, list) and items:
                    print(f"\nTotal items: {len(items)}")
                    print(f"First item keys: {list(items[0].keys())}")
                    print(f"\nFirst item:")
                    print(json.dumps(items[0], ensure_ascii=False, indent=2)[:2000])
            else:
                print(json.dumps(decrypted, ensure_ascii=False, indent=2)[:3000])
        elif isinstance(decrypted, list):
            print(f"List with {len(decrypted)} items")
            if decrypted:
                print(f"First item keys: {list(decrypted[0].keys()) if isinstance(decrypted[0], dict) else 'not a dict'}")
                print(json.dumps(decrypted[0], ensure_ascii=False, indent=2)[:2000])

        # Save full decrypted response
        with open("decrypted_sample.json", "w", encoding="utf-8") as f:
            json.dump(decrypted, f, ensure_ascii=False, indent=2)
        print("\nSaved full response to decrypted_sample.json")
    else:
        print("Response is NOT encrypted!")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    main()

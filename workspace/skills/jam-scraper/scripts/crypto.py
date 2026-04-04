"""AES-256-GCM encryption/decryption for JAM API responses."""

import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Hardcoded in jjpropertythai.com/_nuxt/tVx1KLp4.js
_KEY = b"QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf"
_AESGCM = AESGCM(_KEY)


def decrypt(encrypted_str: str) -> dict:
    """Decrypt JAM API response. Format: iv_hex:tag_hex:ciphertext_hex"""
    parts = encrypted_str.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 hex parts separated by ':', got {len(parts)}")
    iv = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ciphertext = bytes.fromhex(parts[2])
    plaintext = _AESGCM.decrypt(iv, ciphertext + tag, None)
    return json.loads(plaintext.decode("utf-8"))


def decrypt_response(data: dict) -> dict:
    """Decrypt if encrypted, pass through otherwise."""
    if "_encrypted" in data:
        return decrypt(data["_encrypted"])
    return data

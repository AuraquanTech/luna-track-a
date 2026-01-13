\
from __future__ import annotations

import hmac
import hashlib
from typing import Optional


def hmac_sha256(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

def verify_hmac(secret: str, body: bytes, signature_hex: Optional[str]) -> bool:
    if not secret or not signature_hex:
        return False
    expected = hmac_sha256(secret, body)
    return hmac.compare_digest(expected, signature_hex.strip())

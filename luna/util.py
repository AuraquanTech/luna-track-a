\
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Tuple

# Heuristic: flag likely specific venue/proper noun names.
# Goal: prevent "Mario's Wine Bar" style hallucinations in Track A.
_CAP_WORD = re.compile(r"\b[A-Z][a-z]{2,}\b")
_APOSTROPHE = re.compile(r"[’']")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def stable_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def stable_hash(*parts: str, length: int = 64) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()[:length]

def stable_hash_json(prefix: str, obj: Any) -> str:
    return stable_hash(prefix, stable_json_dumps(obj))

def looks_like_specific_venue(text: str) -> bool:
    """
    Conservative heuristic:
    - multiple capitalized words (proper nouns)
    - apostrophes (common in venue names)
    - URLs/@ handles
    """
    if not text:
        return False
    if "http://" in text or "https://" in text or "@" in text:
        return True
    if _APOSTROPHE.search(text):
        return True
    caps = _CAP_WORD.findall(text)
    # allow first word capitalization; flag if >=2 capitalized words
    return len(caps) >= 2

def redact_if_needed(text: str) -> Tuple[str, bool]:
    """Return (possibly redacted) text and whether it was modified."""
    if not text:
        return text, False
    if looks_like_specific_venue(text):
        # Minimal redaction: lower-case and remove apostrophes
        t = text.replace("’", "").replace("'", "")
        t = re.sub(r"\b([A-Z][a-z]{2,})\b", lambda m: m.group(1).lower(), t)
        return t, True
    return text, False

class SimpleTTLCache:
    """Tiny TTL cache to avoid extra deps."""
    def __init__(self, ttl_seconds: int = 60, max_items: int = 5000):
        self.ttl = ttl_seconds
        self.max = max_items
        self._d: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Any:
        v = self._d.get(key)
        if not v:
            return None
        exp, val = v
        if exp < time.time():
            self._d.pop(key, None)
            return None
        return val

    def set(self, key: str, value: Any) -> None:
        if len(self._d) >= self.max:
            # naive eviction: clear
            self._d.clear()
        self._d[key] = (time.time() + self.ttl, value)

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

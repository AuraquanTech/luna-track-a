\
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional

from .util import clamp_int


@dataclass
class Bucket:
    tokens: float
    last: float


class RateLimiter:
    """
    Lightweight in-memory token bucket.
    For Track A, this is enough; add Redis if you see abuse.
    """
    def __init__(self, *, rate_per_minute: int = 60, burst: int = 30):
        self.rate = max(1, rate_per_minute) / 60.0
        self.burst = max(1, burst)
        self._buckets: Dict[str, Bucket] = {}

    def allow(self, key: str, cost: int = 1) -> bool:
        cost = clamp_int(cost, 1, 50)
        now = time.time()
        b = self._buckets.get(key)
        if b is None:
            b = Bucket(tokens=float(self.burst), last=now)
            self._buckets[key] = b
        # refill
        elapsed = max(0.0, now - b.last)
        b.tokens = min(float(self.burst), b.tokens + elapsed * self.rate)
        b.last = now
        if b.tokens >= cost:
            b.tokens -= cost
            return True
        return False

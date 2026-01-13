\
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List

from .util import utc_now_iso, stable_json_dumps


class Spooler:
    """
    Auto-healing fallback: if DB writes fail, enqueue a JSONL record locally.
    When DB is healthy again, we replay the queue.
    """
    def __init__(self, spool_dir: str = "/tmp/luna_spool", max_bytes: int = 8_000_000):
        self.dir = Path(spool_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self.dir / "queue.jsonl"

    def _current_size(self) -> int:
        try:
            return self.path.stat().st_size
        except FileNotFoundError:
            return 0

    def enqueue(self, kind: str, payload: Dict[str, Any], *, error: Optional[str] = None) -> None:
        rec = {
            "ts": utc_now_iso(),
            "kind": kind,
            "payload": payload,
            "error": error,
        }
        line = stable_json_dumps(rec) + "\n"
        with self._lock:
            if self._current_size() + len(line.encode("utf-8")) > self.max_bytes:
                # Best-effort: rotate (drop old)
                self.rotate()
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)

    def rotate(self) -> None:
        with self._lock:
            if self.path.exists():
                rot = self.dir / f"queue.{utc_now_iso().replace(':','-')}.jsonl"
                self.path.rename(rot)

    def drain(self, apply_fn: Callable[[str, Dict[str, Any]], None], max_records: int = 200) -> int:
        """
        Replay queued writes. apply_fn(kind, payload) must raise on failure.
        Returns count applied.
        """
        with self._lock:
            if not self.path.exists():
                return 0
            lines = self.path.read_text(encoding="utf-8").splitlines()

        if not lines:
            return 0

        applied = 0
        remaining: List[str] = []
        for line in lines:
            if applied >= max_records:
                remaining.append(line)
                continue
            try:
                rec = json.loads(line)
                apply_fn(rec.get("kind",""), rec.get("payload",{}))
                applied += 1
            except Exception:
                remaining.append(line)

        with self._lock:
            if remaining:
                self.path.write_text("\n".join(remaining) + "\n", encoding="utf-8")
            else:
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass
        return applied

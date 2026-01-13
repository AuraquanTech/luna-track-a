\
from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Callable, Tuple

from .errors import LunaError
from .util import utc_now_iso

try:
    from supabase import create_client  # type: ignore
except Exception as e:  # pragma: no cover
    create_client = None  # type: ignore


def _retry(fn: Callable[[], Any], *, attempts: int = 3, base_delay: float = 0.25, max_delay: float = 2.0) -> Any:
    last = None
    delay = base_delay
    for _ in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            time.sleep(delay)
            delay = min(max_delay, delay * 2)
    raise last  # type: ignore


class SupabaseDB:
    def __init__(self, url: str, key: str):
        if create_client is None:
            raise RuntimeError("supabase client not installed. Add `supabase` to requirements.txt.")
        self.url = url
        self.key = key
        self.sb = create_client(url, key)

    def ping(self) -> bool:
        # Lightweight read from schema_version
        def _do():
            self.sb.table("schema_version").select("version").limit(1).execute()
            return True
        try:
            return bool(_retry(_do, attempts=2))
        except Exception:
            return False

    def upsert_user(self, user_ref: str) -> str:
        def _do():
            res = self.sb.table("users").upsert(
                {"chatgpt_user_ref": user_ref, "last_seen_at": utc_now_iso(), "updated_at": utc_now_iso()},
                on_conflict="chatgpt_user_ref"
            ).execute()
            # supabase-py returns list in data
            return res.data[0]["id"]
        try:
            return _retry(_do, attempts=3)
        except Exception as e:
            raise LunaError("DB_UPSERT_USER_FAILED", "Unable to create/update user", {"cause": str(e)}, retryable=True)

    def set_opt_out(self, user_id: str, opt_out: bool) -> None:
        def _do():
            self.sb.table("users").update({"data_opt_out": opt_out, "updated_at": utc_now_iso()}).eq("id", user_id).execute()
        try:
            _retry(_do, attempts=3)
        except Exception as e:
            raise LunaError("DB_OPT_OUT_FAILED", "Unable to update opt-out", {"cause": str(e)}, retryable=True)

    def insert_archetype(self, *, user_id: str, level: str, source_hash: str, archetype_json: Dict[str, Any], model_version: Optional[str] = None) -> None:
        row = {
            "user_id": user_id,
            "level": level,
            "source_hash": source_hash,
            "archetype_json": archetype_json,
            "model_version": model_version,
        }
        def _do():
            self.sb.table("archetypes").upsert(row, on_conflict="user_id,level,source_hash").execute()
        try:
            _retry(_do, attempts=3)
        except Exception as e:
            raise LunaError("DB_STORE_ARCHETYPE_FAILED", "Unable to store archetype", {"cause": str(e)}, retryable=True)

    def insert_date_plan(self, *, user_id: str, source_hash: str, city: str, plan_json: Dict[str, Any]) -> None:
        row = {"user_id": user_id, "source_hash": source_hash, "city": city, "plan_json": plan_json}
        def _do():
            self.sb.table("date_plans").upsert(row, on_conflict="user_id,source_hash").execute()
        try:
            _retry(_do, attempts=3)
        except Exception as e:
            raise LunaError("DB_STORE_DATEPLAN_FAILED", "Unable to store date plan", {"cause": str(e)}, retryable=True)

    def insert_event(self, *, user_id: str, event_name: str, event_id: str, properties: Dict[str, Any], occurred_at: str) -> None:
        row = {"user_id": user_id, "event_name": event_name, "event_id": event_id, "properties": properties, "occurred_at": occurred_at}
        def _do():
            self.sb.table("event_log").insert(row).execute()
        try:
            # events are best-effort; ignore duplicates
            _retry(_do, attempts=2)
        except Exception:
            # swallow: metrics should never break UX
            return

    def insert_feedback(self, *, user_id: str, date_plan_id: Optional[str], rating: Optional[int], tags: Optional[list], notes: Optional[str]) -> None:
        row = {"user_id": user_id, "date_plan_id": date_plan_id, "rating": rating, "tags": tags, "notes": notes}
        def _do():
            self.sb.table("feedback").insert(row).execute()
        try:
            _retry(_do, attempts=2)
        except Exception:
            return

    def get_latest(self, *, user_id: str) -> Dict[str, Any]:
        """
        Returns latest archetype (lite/deep) and most recent date plan count.
        """
        out: Dict[str, Any] = {}
        def _do_arche(level: str):
            res = self.sb.table("archetypes").select("archetype_json,created_at,level").eq("user_id", user_id).eq("level", level).order("created_at", desc=True).limit(1).execute()
            return res.data[0] if res.data else None

        def _do_plans():
            res = self.sb.table("date_plans").select("id", count="exact").eq("user_id", user_id).execute()
            # supabase returns count in res.count
            return getattr(res, "count", None)

        try:
            out["latest_lite"] = _do_arche("lite")
            out["latest_deep"] = _do_arche("deep")
            out["date_plan_count"] = _do_plans()
        except Exception:
            return out
        return out

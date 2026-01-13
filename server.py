\
"""
Luna Track A — MCP server (FastMCP v2)

Positioning (CRITICAL):
- NOT a dating app, NOT a matchmaker.
- Relationship chief-of-staff coach that improves outcomes on ANY dating app or IRL.
- Track A: self-knowledge + DateOps. No monetization. No venue hallucinations.

Cost strategy:
- ChatGPT does the reasoning.
- This server only VALIDATES + STORES structured outputs (plus best-effort metrics).
"""

from __future__ import annotations

import os
import json
import logging
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP, Context

from luna.db import SupabaseDB
from luna.errors import LunaError, error_payload
from luna.models import ArchetypeProfile, DateOpsPlan, LunaEvent, ToolMeta, model_dump
from luna.ratelimit import RateLimiter
from luna.spool import Spooler
from luna.util import (
    env_bool,
    stable_hash_json,
    stable_json_dumps,
    utc_now_iso,
    looks_like_specific_venue,
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(message)s")
logger = logging.getLogger("luna")

# ---- Config ----
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
LUNA_SPOOL_DIR = os.getenv("LUNA_SPOOL_DIR", "/tmp/luna_spool")
LUNA_RATE_LIMIT_PER_MIN = int(os.getenv("LUNA_RATE_LIMIT_PER_MIN", "60"))
LUNA_RATE_LIMIT_BURST = int(os.getenv("LUNA_RATE_LIMIT_BURST", "30"))

REQUIRE_CONSENT = env_bool("LUNA_REQUIRE_CONSENT", False)

# ---- Runtime ----
mcp = FastMCP("Luna Relationship OS (Track A)")
spool = Spooler(spool_dir=LUNA_SPOOL_DIR)
rl = RateLimiter(rate_per_minute=LUNA_RATE_LIMIT_PER_MIN, burst=LUNA_RATE_LIMIT_BURST)

db: Optional[SupabaseDB] = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    db = SupabaseDB(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def _log_json(event: str, **fields: Any) -> None:
    payload = {"event": event, "ts": utc_now_iso(), **fields}
    logger.info(stable_json_dumps(payload))


def _require_db() -> SupabaseDB:
    if db is None:
        raise LunaError("DB_NOT_CONFIGURED", "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    return db


def _check_rate_limit(user_ref: str, cost: int = 1) -> None:
    if not rl.allow(user_ref, cost=cost):
        raise LunaError("RATE_LIMITED", "Too many requests. Try again in a minute.", retryable=True)


def _spool_apply(kind: str, payload: Dict[str, Any]) -> None:
    """
    Replayer for auto-healing queue. This MUST be deterministic and safe to repeat.
    """
    d = _require_db()
    if kind == "archetype":
        d.insert_archetype(**payload)
    elif kind == "dateplan":
        d.insert_date_plan(**payload)
    elif kind == "optout":
        d.set_opt_out(payload["user_id"], payload["opt_out"])
    elif kind == "event":
        d.insert_event(**payload)
    elif kind == "feedback":
        d.insert_feedback(**payload)
    else:
        # unknown record type: drop
        return


def _maybe_drain_spool(ctx: Optional[Context] = None) -> None:
    """
    Best-effort drain; never throw.
    """
    try:
        drained = spool.drain(_spool_apply, max_records=100)
        if drained and ctx:
            # low-noise: only tell client when meaningful
            ctx.info(f"Recovered and replayed {drained} queued writes.")  # type: ignore
    except Exception:
        return


def _ensure_user(user_ref: str) -> str:
    d = _require_db()
    user_id = d.upsert_user(user_ref)
    return user_id


def _consent_gate(user_row: Dict[str, Any], user_ref: str) -> None:
    if not REQUIRE_CONSENT:
        return
    if user_row.get("data_opt_out"):
        raise LunaError("USER_OPTED_OUT", "User opted out of data storage.")
    if not user_row.get("consent_version"):
        raise LunaError("CONSENT_REQUIRED", "User consent required before storing data.", {"how": "Call accept_consent tool"})


# ----------------------------
# Tools (ChatGPT does reasoning; server validates + stores)
# ----------------------------

@mcp.tool
async def health(ctx: Context) -> Dict[str, Any]:
    """
    Health status. Use this in deployment verification.
    """
    ok = bool(db and db.ping())
    _maybe_drain_spool(ctx)
    return {
        "structuredContent": {
            "type": "luna_health",
            "ok": ok,
            "db_configured": bool(db),
            "spool_path": str(spool.path),
        },
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="health"))
    }


@mcp.tool
async def accept_consent(user_ref: str, consent_version: str, ctx: Context) -> Dict[str, Any]:
    """
    Record user consent for data storage. Use ONLY when user explicitly agrees.
    """
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    # Update consent_version via direct update
    def _do():
        d.sb.table("users").update({"consent_version": consent_version, "updated_at": utc_now_iso()}).eq("id", user_id).execute()
    try:
        _do()
    except Exception as e:
        spool.enqueue("optout", {"user_id": user_id, "opt_out": False}, error=str(e))
    _maybe_drain_spool(ctx)
    _log_json("consent", user_ref=user_ref, consent_version=consent_version)
    return {
        "structuredContent": {"type": "luna_consent", "status": "accepted", "consent_version": consent_version},
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="consent"))
    }


@mcp.tool
async def set_data_opt_out(user_ref: str, opt_out: bool, ctx: Context) -> Dict[str, Any]:
    """
    Opt-out switch. If opt_out=true, future calls will still work but will NOT store new records.
    """
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)
    try:
        d.set_opt_out(user_id, opt_out)
    except LunaError as e:
        spool.enqueue("optout", {"user_id": user_id, "opt_out": opt_out}, error=str(e))
    _maybe_drain_spool(ctx)

    return {
        "structuredContent": {"type": "luna_opt_out", "opt_out": opt_out},
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="settings"))
    }


@mcp.tool
async def store_archetype(
    user_ref: str,
    archetype: ArchetypeProfile,
    ctx: Context,
) -> Dict[str, Any]:
    """
    Store a validated archetype (Lite or Deep).
    IMPORTANT:
      - ChatGPT must generate the archetype content.
      - This server only validates + stores. It does not call OpenAI.
    """
    _check_rate_limit(user_ref, cost=2)
    d = _require_db()

    user_id = d.upsert_user(user_ref)

    # Opt-out gate
    try:
        # Fetch opt-out quickly (best-effort; if fails, proceed but avoid storing)
        res = d.sb.table("users").select("data_opt_out,consent_version").eq("id", user_id).limit(1).execute()
        user_row = res.data[0] if res.data else {}
    except Exception:
        user_row = {}

    if user_row.get("data_opt_out"):
        return {
            "structuredContent": {
                "type": "luna_archetype",
                "stored": False,
                "reason": "opted_out",
                "profile": model_dump(archetype),
            },
            "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="archetype_card"))
        }

    # Consent gate (optional)
    if REQUIRE_CONSENT and not user_row.get("consent_version"):
        return {
            "structuredContent": {
                "type": "luna_archetype",
                "stored": False,
                "reason": "consent_required",
                "profile": model_dump(archetype),
            },
            "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="archetype_card", warnings=["consent_required"]))
        }

    archetype_dict = model_dump(archetype)
    # Deterministic idempotency key: hash of structured payload (not raw transcript)
    source_hash = stable_hash_json(f"{user_ref}:{archetype.level}", archetype_dict)

    payload = {
        "user_id": user_id,
        "level": archetype.level,
        "source_hash": source_hash,
        "archetype_json": archetype_dict,
        "model_version": archetype.model_version,
    }

    try:
        d.insert_archetype(**payload)
    except LunaError as e:
        # auto-healing fallback
        spool.enqueue("archetype", payload, error=e.message)
        return {
            "structuredContent": {
                "type": "luna_archetype",
                "stored": False,
                "profile": archetype_dict,
            },
            "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="archetype_card", warnings=["spooled_write"]))
        }

    _maybe_drain_spool(ctx)

    # best-effort metrics
    try:
        d.insert_event(
            user_id=user_id,
            event_name="archetype_stored",
            event_id=f"archetype:{source_hash}",
            properties={"level": archetype.level, "source": archetype.source},
            occurred_at=utc_now_iso(),
        )
    except Exception:
        pass

    return {
        "structuredContent": {
            "type": "luna_archetype",
            "stored": True,
            "profile": archetype_dict,
            "card_copy": archetype.share_card_copy,
        },
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="archetype_card"))
    }


@mcp.tool
async def store_dateops_plan(
    user_ref: str,
    city: str,
    plan: DateOpsPlan,
    ctx: Context,
) -> Dict[str, Any]:
    """
    Store a DateOps plan (criteria-only).
    Safety constraints:
      - MUST NOT contain specific venue names (Track A).
      - If detected, returns an error so ChatGPT can regenerate.
    """
    _check_rate_limit(user_ref, cost=2)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    # Opt-out gate
    try:
        res = d.sb.table("users").select("data_opt_out").eq("id", user_id).limit(1).execute()
        if res.data and res.data[0].get("data_opt_out"):
            return {
                "structuredContent": {"type": "luna_dateops", "stored": False, "reason": "opted_out", "plan": model_dump(plan)},
                "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="dateops_plan")),
            }
    except Exception:
        pass

    plan_dict = model_dump(plan)

    # Hard guardrails against venue hallucinations / proper nouns
    suspicious = []
    for field_path, text in [
        ("primary_criteria.category", plan.primary_criteria.category),
        ("primary_criteria.vibe_required", plan.primary_criteria.vibe_required),
        ("backup_criteria.category", plan.backup_criteria.category),
        ("backup_criteria.vibe_required", plan.backup_criteria.vibe_required),
        ("invite_text", plan.invite_text),
        ("backup_plan", plan.backup_plan or ""),
    ]:
        if looks_like_specific_venue(text):
            suspicious.append(field_path)

    if suspicious:
        return {
            "structuredContent": {
                "type": "luna_dateops",
                "stored": False,
                "reason": "venue_name_detected",
                "fields": suspicious,
                "instructions": "Regenerate using ONLY generic criteria. No business names, no URLs, no @handles, no apostrophes.",
            },
            "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="dateops_plan", warnings=["venue_name_detected"]))
        }

    source_hash = stable_hash_json(f"{user_ref}:dateops:{city}", plan_dict)
    payload = {"user_id": user_id, "source_hash": source_hash, "city": city, "plan_json": plan_dict}

    try:
        d.insert_date_plan(**payload)
    except LunaError as e:
        spool.enqueue("dateplan", payload, error=e.message)
        return {
            "structuredContent": {"type": "luna_dateops", "stored": False, "plan": plan_dict},
            "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="dateops_plan", warnings=["spooled_write"]))
        }

    _maybe_drain_spool(ctx)

    # best-effort metrics
    try:
        d.insert_event(
            user_id=user_id,
            event_name="dateops_stored",
            event_id=f"dateops:{source_hash}",
            properties={"city": city},
            occurred_at=utc_now_iso(),
        )
    except Exception:
        pass

    return {
        "structuredContent": {
            "type": "luna_dateops",
            "stored": True,
            "city": city,
            "plan": plan_dict,
            "display_text": _render_dateops_markdown(plan_dict, city),
        },
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="dateops_plan"))
    }


def _render_dateops_markdown(plan: Dict[str, Any], city: str) -> str:
    p = plan
    pc = p.get("primary_criteria", {})
    bc = p.get("backup_criteria", {})
    hooks = p.get("conversation_hooks", []) or []
    hooks_md = "\n".join([f"- {h}" for h in hooks[:6]]) if hooks else "- (none)"
    return f"""\
## 🗓️ {p.get('plan_name','Date Plan')} ({city})

**Time:** {p.get('suggested_time','')}

### Primary criteria
- Category: **{pc.get('category','')}**
- Vibe: {pc.get('vibe_required','')}
- Noise: {pc.get('noise_level','')}
- Price: {pc.get('price_tier','')}

### Backup criteria
- Category: **{bc.get('category','')}**
- Vibe: {bc.get('vibe_required','')}
- Noise: {bc.get('noise_level','')}
- Price: {bc.get('price_tier','')}

### Invite text
> {p.get('invite_text','').strip()}

### Conversation hooks
{hooks_md}
"""


@mcp.tool
async def log_event(user_ref: str, event: LunaEvent, ctx: Context) -> Dict[str, Any]:
    """
    Best-effort analytics logging (never breaks UX).
    Use for:
      - app_open
      - quiz_started
      - quiz_completed
      - share_clicked
      - deep_started / deep_completed
      - dateops_started / dateops_completed
    """
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    occurred_at = event.occurred_at or utc_now_iso()
    payload = {
        "user_id": user_id,
        "event_name": event.event_name,
        "event_id": event.event_id,
        "properties": event.properties,
        "occurred_at": occurred_at,
    }

    try:
        d.insert_event(**payload)
    except Exception as e:
        spool.enqueue("event", payload, error=str(e))

    _maybe_drain_spool(ctx)

    return {
        "structuredContent": {"type": "luna_event", "ok": True},
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="event_ack"))
    }


@mcp.tool
async def submit_feedback(
    user_ref: str,
    rating: Optional[int],
    tags: Optional[list],
    notes: Optional[str],
    date_plan_id: Optional[str],
    ctx: Context,
) -> Dict[str, Any]:
    """
    Best-effort feedback logging (Track A learning loop).
    """
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    payload = {
        "user_id": user_id,
        "date_plan_id": date_plan_id,
        "rating": rating,
        "tags": tags,
        "notes": notes,
    }

    try:
        d.insert_feedback(**payload)
    except Exception as e:
        spool.enqueue("feedback", payload, error=str(e))

    _maybe_drain_spool(ctx)

    return {
        "structuredContent": {"type": "luna_feedback", "ok": True},
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="feedback_ack"))
    }


@mcp.tool
async def get_user_snapshot(user_ref: str, ctx: Context) -> Dict[str, Any]:
    """
    Retrieve latest stored outputs for continuity across sessions.
    """
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)
    snap = d.get_latest(user_id=user_id)
    _maybe_drain_spool(ctx)
    return {
        "structuredContent": {"type": "luna_snapshot", "snapshot": snap},
        "_meta": model_dump(ToolMeta(generated_at=utc_now_iso(), widget_view="snapshot"))
    }


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    # For local dev: `fastmcp run server.py`
    # For cloud: see DEPLOY.md
    _log_json("startup", db_configured=bool(db), spool_dir=LUNA_SPOOL_DIR)
    mcp.run()

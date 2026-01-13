"""
OpenAPI REST wrapper for Luna Track A MCP Server.
This allows ChatGPT Custom GPTs to call Luna tools via Actions.

Run with: uvicorn openapi_wrapper:app --host 0.0.0.0 --port 8001
"""

import os
import json
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from luna.db import SupabaseDB
from luna.models import ArchetypeProfile, DateOpsPlan, LunaEvent, ToolMeta, model_dump
from luna.ratelimit import RateLimiter
from luna.util import utc_now_iso, env_bool, looks_like_specific_venue

# ---- Config ----
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
LUNA_RATE_LIMIT_PER_MIN = int(os.getenv("LUNA_RATE_LIMIT_PER_MIN", "60"))
LUNA_RATE_LIMIT_BURST = int(os.getenv("LUNA_RATE_LIMIT_BURST", "30"))

# Initialize
db: Optional[SupabaseDB] = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    db = SupabaseDB(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

rate_limiter = RateLimiter(LUNA_RATE_LIMIT_PER_MIN, LUNA_RATE_LIMIT_BURST)

app = FastAPI(
    title="Luna Track A API",
    description="Relationship OS API - Store archetypes, DateOps plans, and track events. ChatGPT does reasoning; this API validates and stores.",
    version="1.0.0",
    servers=[{"url": "https://luna-track-a-production.up.railway.app"}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_db() -> SupabaseDB:
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    return db


def _check_rate_limit(user_ref: str, cost: int = 1):
    if not rate_limiter.allow(user_ref, cost):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


# ---- Request Models ----
class HealthResponse(BaseModel):
    ok: bool
    db_configured: bool


class ConsentRequest(BaseModel):
    user_ref: str
    consent_version: str


class OptOutRequest(BaseModel):
    user_ref: str
    opt_out: bool


class StoreArchetypeRequest(BaseModel):
    user_ref: str
    archetype: ArchetypeProfile


class StoreDateOpsRequest(BaseModel):
    user_ref: str
    plan: DateOpsPlan


class LogEventRequest(BaseModel):
    user_ref: str
    event: LunaEvent


# ---- Endpoints ----
@app.get("/api/health", tags=["Health"])
async def health() -> Dict[str, Any]:
    """Check server health and database connection."""
    ok = bool(db and db.ping())
    return {
        "ok": ok,
        "db_configured": bool(db),
        "generated_at": utc_now_iso()
    }


@app.post("/api/consent", tags=["User"])
async def accept_consent(req: ConsentRequest) -> Dict[str, Any]:
    """Record user consent for data storage."""
    _check_rate_limit(req.user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(req.user_ref)
    d.sb.table("users").update({
        "consent_version": req.consent_version,
        "updated_at": utc_now_iso()
    }).eq("id", user_id).execute()

    return {
        "status": "accepted",
        "consent_version": req.consent_version,
        "generated_at": utc_now_iso()
    }


@app.post("/api/opt-out", tags=["User"])
async def set_opt_out(req: OptOutRequest) -> Dict[str, Any]:
    """Set data opt-out preference."""
    _check_rate_limit(req.user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(req.user_ref)
    d.set_opt_out(user_id, req.opt_out)

    return {
        "opt_out": req.opt_out,
        "generated_at": utc_now_iso()
    }


@app.post("/api/archetype", tags=["Archetype"])
async def store_archetype(req: StoreArchetypeRequest) -> Dict[str, Any]:
    """
    Store a validated archetype profile (Lite or Deep).
    ChatGPT generates the archetype; this endpoint validates and stores it.
    """
    _check_rate_limit(req.user_ref, cost=2)
    d = _require_db()
    user_id = d.upsert_user(req.user_ref)

    # Check opt-out
    res = d.sb.table("users").select("data_opt_out").eq("id", user_id).limit(1).execute()
    user_row = res.data[0] if res.data else {}

    if user_row.get("data_opt_out"):
        return {
            "stored": False,
            "reason": "opted_out",
            "profile": model_dump(req.archetype),
            "generated_at": utc_now_iso()
        }

    # Store archetype
    archetype_id = d.upsert_archetype(user_id, model_dump(req.archetype))

    return {
        "stored": True,
        "archetype_id": archetype_id,
        "profile": model_dump(req.archetype),
        "generated_at": utc_now_iso()
    }


@app.post("/api/dateops", tags=["DateOps"])
async def store_dateops_plan(req: StoreDateOpsRequest) -> Dict[str, Any]:
    """
    Store a DateOps plan with venue criteria.
    ChatGPT generates the plan; this endpoint validates and stores it.
    """
    _check_rate_limit(req.user_ref, cost=2)
    d = _require_db()
    user_id = d.upsert_user(req.user_ref)

    # Check for specific venue names (not allowed)
    plan_dict = model_dump(req.plan)
    if looks_like_specific_venue(json.dumps(plan_dict)):
        raise HTTPException(
            status_code=400,
            detail="Plan contains specific venue names. Use criteria only, not venue names."
        )

    # Check opt-out
    res = d.sb.table("users").select("data_opt_out").eq("id", user_id).limit(1).execute()
    user_row = res.data[0] if res.data else {}

    if user_row.get("data_opt_out"):
        return {
            "stored": False,
            "reason": "opted_out",
            "plan": plan_dict,
            "generated_at": utc_now_iso()
        }

    plan_id = d.upsert_dateops_plan(user_id, plan_dict)

    return {
        "stored": True,
        "plan_id": plan_id,
        "plan": plan_dict,
        "generated_at": utc_now_iso()
    }


@app.post("/api/event", tags=["Events"])
async def log_event(req: LogEventRequest) -> Dict[str, Any]:
    """
    Log a relationship event (date, conversation milestone, etc.).
    """
    _check_rate_limit(req.user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(req.user_ref)

    # Check opt-out
    res = d.sb.table("users").select("data_opt_out").eq("id", user_id).limit(1).execute()
    user_row = res.data[0] if res.data else {}

    if user_row.get("data_opt_out"):
        return {
            "stored": False,
            "reason": "opted_out",
            "event": model_dump(req.event),
            "generated_at": utc_now_iso()
        }

    event_id = d.insert_event(user_id, model_dump(req.event))

    return {
        "stored": True,
        "event_id": event_id,
        "event": model_dump(req.event),
        "generated_at": utc_now_iso()
    }


@app.get("/api/archetype/{user_ref}", tags=["Archetype"])
async def get_archetype(user_ref: str) -> Dict[str, Any]:
    """Retrieve the latest archetype for a user."""
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    res = d.sb.table("archetypes").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()

    if not res.data:
        return {"found": False, "archetype": None}

    return {
        "found": True,
        "archetype": res.data[0].get("profile_json", {}),
        "generated_at": utc_now_iso()
    }


@app.get("/api/dateops/{user_ref}", tags=["DateOps"])
async def get_dateops(user_ref: str) -> Dict[str, Any]:
    """Retrieve the latest DateOps plan for a user."""
    _check_rate_limit(user_ref, cost=1)
    d = _require_db()
    user_id = d.upsert_user(user_ref)

    res = d.sb.table("dateops_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()

    if not res.data:
        return {"found": False, "plan": None}

    return {
        "found": True,
        "plan": res.data[0].get("plan_json", {}),
        "generated_at": utc_now_iso()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)

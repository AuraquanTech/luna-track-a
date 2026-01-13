\
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

try:
    # Pydantic v2
    from pydantic import BaseModel, Field, ConfigDict
    _V2 = True
except Exception:  # pragma: no cover
    # Pydantic v1 fallback (best-effort)
    from pydantic import BaseModel, Field  # type: ignore
    ConfigDict = dict  # type: ignore
    _V2 = False


def model_dump(obj: BaseModel) -> Dict[str, Any]:
    """Compatibility wrapper for Pydantic v1/v2."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore
    return obj.dict()  # type: ignore


# ----------------------------
# Archetype (Lite / Deep)
# ----------------------------

class Trait(BaseModel):
    label: str = Field(..., min_length=1, max_length=64)
    score: int = Field(..., ge=1, le=10)
    evidence: str = Field(..., min_length=1, max_length=280)


class BlindSpots(BaseModel):
    patterns: List[str] = Field(default_factory=list, description="Recurring patterns hurting the user's dating outcomes")
    self_sabotage: List[str] = Field(default_factory=list, description="Likely self-sabotage behaviors")
    triggers: List[str] = Field(default_factory=list, description="Situations that reliably spike conflict/avoidance")
    repairs: List[str] = Field(default_factory=list, description="Simple repairs to try next time")


class Compatibility(BaseModel):
    green_flags: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    dealbreakers: List[str] = Field(default_factory=list)
    best_fit_environments: List[str] = Field(default_factory=list, description="Contexts where user dates best")


class ArchetypeProfile(BaseModel):
    """
    IMPORTANT POSITIONING:
    - This is NOT matchmaking output.
    - It's self-knowledge + practical scripts. (Track A)
    """
    model_config = ConfigDict(extra="forbid") if _V2 else None  # type: ignore

    level: Literal["lite", "deep"] = "lite"
    archetype_name: str = Field(..., min_length=2, max_length=64)
    tagline: str = Field(..., min_length=2, max_length=120)

    # Psycholinguistic reads (from text/voice transcript)
    energy_level: Literal["Low-Key", "Moderate", "High-Voltage"] = "Moderate"
    communication_style: Literal["Direct", "Storyteller", "Reflective", "Debater", "Avoidant"] = "Reflective"
    conflict_style: Literal["Repair-Fast", "Slow-to-Warm", "Avoidant", "Escalator", "Stonewall"] = "Slow-to-Warm"

    traits: List[Trait] = Field(default_factory=list)

    blind_spots: BlindSpots = Field(default_factory=BlindSpots)
    compatibility: Compatibility = Field(default_factory=Compatibility)

    # Output surfaces
    share_card_copy: str = Field(..., min_length=20, max_length=2500, description="Markdown text user can copy/paste")

    # Provenance (non-PII)
    source: Optional[str] = Field(default=None, description="Optional user-provided label (e.g., 'text_quiz', 'voice')")
    created_from: Optional[str] = Field(default=None, description="Optional: short note of what input type was used")

    # Forward-compat
    schema_version: str = Field(default="2026-01-12.archetype.v1")
    model_version: Optional[str] = Field(default=None, description="Optional: model version tag used by ChatGPT reasoning")


# ----------------------------
# DateOps (criteria-only)
# ----------------------------

class VenueCriteria(BaseModel):
    model_config = ConfigDict(extra="forbid") if _V2 else None  # type: ignore

    category: str = Field(..., min_length=2, max_length=64, description="Generic type, e.g., 'jazz lounge', 'wine bar'")
    vibe_required: str = Field(..., min_length=2, max_length=180)
    noise_level: Literal["Quiet", "Moderate", "Loud"] = "Moderate"
    price_tier: Literal["$", "$$", "$$$", "$$$$"] = "$$"
    accessibility_notes: Optional[str] = Field(default=None, max_length=200)


class DateOpsPlan(BaseModel):
    model_config = ConfigDict(extra="forbid") if _V2 else None  # type: ignore

    plan_name: str = Field(..., min_length=2, max_length=80)
    suggested_time: str = Field(..., min_length=2, max_length=60)
    constraints_summary: str = Field(..., min_length=2, max_length=400, description="What constraints were optimized for")
    primary_criteria: VenueCriteria
    backup_criteria: VenueCriteria

    invite_text: str = Field(..., min_length=10, max_length=900)
    conversation_hooks: List[str] = Field(default_factory=list, max_length=12)

    # Optional execution ops
    checklist: List[str] = Field(default_factory=list, description="Step-by-step execution checklist")
    backup_plan: str = Field(default="", max_length=500)

    # Forward-compat
    schema_version: str = Field(default="2026-01-12.dateops.v1")
    model_version: Optional[str] = Field(default=None)


# ----------------------------
# Analytics
# ----------------------------

class LunaEvent(BaseModel):
    model_config = ConfigDict(extra="allow") if _V2 else None  # type: ignore

    event_name: str = Field(..., min_length=1, max_length=64)
    event_id: str = Field(..., min_length=8, max_length=128, description="Client-generated idempotency key")
    properties: Dict[str, Any] = Field(default_factory=dict)
    occurred_at: Optional[str] = Field(default=None, description="ISO timestamp; server will set if missing")


class ToolMeta(BaseModel):
    model_config = ConfigDict(extra="forbid") if _V2 else None  # type: ignore
    generated_at: str
    widget_view: str
    warnings: List[str] = Field(default_factory=list)
    request_id: Optional[str] = None

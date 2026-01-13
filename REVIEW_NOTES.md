# REVIEW_NOTES — “4 runs” hardening pass

This repo was built as if you asked for a post-mortem *before* you ship.

## Run 1 — Correctness + protocol hygiene
- Moved from “server does reasoning” to **ChatGPT does reasoning → server validates + stores**.
- Strict Pydantic schemas (extra=forbid where possible).
- Deterministic idempotency keys via stable JSON hashing.
- RLS enabled (no public policies).

## Run 2 — Reliability + auto-healing
- DB writes wrapped with retries.
- **Spooler**: if Supabase fails, writes queue.jsonl locally; replays later.
- Metrics writes are best-effort (never break UX).
- `health()` tool for deployment checks.

## Run 3 — Safety + trust
- **Venue hallucination guard**: rejects DateOps outputs that look like specific venues.
- Data minimization rules embedded in SYSTEM_PROMPT + PRIVACY.md.
- Optional consent gate via `LUNA_REQUIRE_CONSENT`.

## Run 4 — Operability + future-proofing
- `event_log` table + metric queries for D1/D7 retention, deepening, share rate.
- Dockerfile for Railway.
- Snapshot tool for continuity across sessions.
- Guardrails documented in SECURITY.md.

If you want “Run 5”: add Places API (Track B), embeddings pipeline, and a signed-auth proxy.

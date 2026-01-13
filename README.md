# Luna Track A — Relationship Chief-of-Staff (ChatGPT App + MCP)

**Track A = distribution + data moat.**  
Luna is **not** a dating app and **not** a matchmaker. She’s a *coach* that makes you better at dating **anywhere** (Hinge/Bumble/Tinder/IRL) via:

- **Psycholinguistic archetypes** (Lite text quiz → optional Deep read)
- **DateOps** (constraints → criteria-based plan → invite script → backup plan → debrief)
- **Zero venue hallucinations** (criteria-only until Places API in Track B)
- **Zero OpenAI API cost** (ChatGPT does reasoning; server only validates + stores)

## Repo contents

- `server.py` — FastMCP server (Track A tools)
- `schema.sql` — Supabase/Postgres schema
- `SYSTEM_PROMPT.md` — the “frontend” (ChatGPT behavior)
- `METRICS_DASHBOARD.sql` — retention + funnel queries
- `DEPLOY.md` — Railway deploy steps
- `SHIP_NOW.md` — 3-week ship checklist
- `SECURITY.md` / `PRIVACY.md` — guardrails

## Quickstart (local)

```bash
cp .env.example .env
# fill SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Apply schema.sql in Supabase SQL Editor first
fastmcp run server.py --transport http --host 0.0.0.0 --port 8000
```

Verify:

```bash
# In ChatGPT MCP dev tools, call tool: health
```

## Core tools

- `store_archetype(user_ref, archetype)` — validate + store Lite/Deep archetype
- `store_dateops_plan(user_ref, city, plan)` — validate + store DateOps plan (**criteria-only**)
- `log_event(user_ref, event)` — best-effort analytics
- `get_user_snapshot(user_ref)` — latest stored outputs
- `set_data_opt_out(user_ref, opt_out)` — opt-out toggle
- `submit_feedback(...)` — best-effort feedback
- `health()` — deploy check

## Design constraints (non-negotiable)

- **No factual venue names** in Track A. The server rejects suspicious proper nouns.
- **No OpenAI API calls** from the server. ChatGPT generates content; tools store it.
- **Service-role only** DB access (RLS enabled, no public policies).

## License

Internal prototype; choose a license before public launch.

# SHIP NOW — 3 Week Plan (Track A)

This is the minimum path to “in store” without scope creep.

## RIGHT NOW (2 hours)

1) **Create Supabase project**
- Copy `schema.sql` into Supabase SQL Editor → Run.
- Confirm tables: `users, archetypes, date_plans, event_log`.

2) **Configure env**
```bash
cp .env.example .env
# set:
# SUPABASE_URL=
# SUPABASE_SERVICE_ROLE_KEY=
```

3) **Run server locally**
```bash
pip install -r requirements.txt
fastmcp run server.py --transport http --host 0.0.0.0 --port 8000
```

4) **Smoke test in ChatGPT MCP dev mode**
- Call `health()`
- Then have ChatGPT generate a dummy Lite archetype (per SYSTEM_PROMPT) and call `store_archetype(...)`
- Verify `archetypes` has a row.

## WEEK 1 (8–10 hours)

- Finish prompt polish (`SYSTEM_PROMPT.md`)
- Add app icon + listing copy (see `EXECUTION_SUMMARY.md`)
- Add 10 friends as beta testers → get 20 archetypes

## WEEK 2 (6–8 hours)

- Deploy to Railway (see `DEPLOY.md`)
- Register MCP server + tools in ChatGPT
- Start collecting: **Lite quiz completions** + **share rate**

## WEEK 3 (10–12 hours)

- Add Deep flow prompts (voice transcript)
- Add DateOps flow prompts
- Submit to ChatGPT App Store

## Guardrails (don’t break these)

- No venue names. Criteria only.
- No matching loop in Track A.
- No OpenAI API calls from server.
- Track metrics weekly (see `METRICS_DASHBOARD.sql`).

## Go/No-Go signals (Week 4)

Targets:
- 1,000 archetypes stored
- 25% share rate
- 50% D7 retention
- 20% DateOps attach rate

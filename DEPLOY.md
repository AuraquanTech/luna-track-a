# DEPLOY.md — Railway (Track A)

## 1) Create Railway service

- New Project → Deploy from GitHub repo.
- Use Dockerfile: `docker/Dockerfile`.

## 2) Set env vars

Required:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional:
- `LOG_LEVEL=INFO`
- `LUNA_RATE_LIMIT_PER_MIN=60`
- `LUNA_RATE_LIMIT_BURST=30`
- `LUNA_SPOOL_DIR=/tmp/luna_spool`
- `LUNA_REQUIRE_CONSENT=false`

## 3) Start command

Dockerfile already runs:

```bash
fastmcp run server.py --transport http --host 0.0.0.0 --port $PORT
```

## 4) Verify

In ChatGPT MCP dev tools (or whatever runner you use):
- Call `health()`
- Confirm `ok=true`

Then run one test flow:
- Generate a Lite archetype
- Call `store_archetype(...)`
- Confirm a row is added to `archetypes`

## 5) Troubleshooting

- `DB_NOT_CONFIGURED` → env vars missing
- `DB_*_FAILED` with warnings `spooled_write` → Supabase transient; will auto-replay later
- `venue_name_detected` → your DateOps output included a specific venue name; regenerate with criteria-only

## 6) Rollback strategy

- Railway: redeploy previous build
- Supabase: schema changes are additive; no destructive migrations in Track A

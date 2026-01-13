# SECURITY.md

## Threat model (Track A)

- Unauthorized tool calls / abuse
- PII leakage into stored JSON
- Hallucinated venue names (trust risk)
- Database outages causing data loss

## Implemented controls

- **Rate limiting** (in-memory token bucket per `user_ref`)
- **Data minimization**: prompts forbid storing transcripts, names, phone numbers
- **Venue hallucination guard**: server rejects suspicious proper nouns in DateOps output
- **Auto-healing DB fallback**: local JSONL spool + replay when DB is healthy
- **Service-role only DB access**: RLS enabled, no public policies

## Recommended hardening (optional)

- Put server behind a reverse proxy that enforces:
  - IP allowlist (OpenAI egress IPs if available)
  - Bearer token
  - Request body size limits
- Add WAF rules for burst abuse

## Incident playbook

- Abuse spike → lower `LUNA_RATE_LIMIT_PER_MIN` and rotate endpoint
- DB outage → server will spool; watch logs for `spooled_write`
- Data incident → set `data_opt_out=true` for impacted users, rotate keys

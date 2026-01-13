# PRIVACY.md (Track A)

## What is stored

- Pseudonymous `chatgpt_user_ref` (as provided by ChatGPT/OpenAI tooling)
- Structured archetype JSON (traits, blind spots, share card copy)
- Structured DateOps JSON (criteria + scripts)
- Anonymous event analytics (funnel + retention)
- Optional feedback notes (user-provided)

## What is NOT stored

- Raw audio
- Full transcripts (unless you intentionally include them — don’t)
- Phone numbers / addresses / real names
- Exact venue names

## Opt-out

Users can opt out at any time via `set_data_opt_out(user_ref, true)`.

When opted out:
- Tools still return results (ChatGPT output), but server stops storing new rows.

# 🚀 DEPLOYMENT LOCKED: Week 1–3 (Jan 12–Feb 2, 2026)

**Status:** Go/no-go. Code locked. Positioning locked. Scope locked.  
**Last Updated:** January 12, 2026, 7:35 AM EST

---

## SCOPE (LOCKED)

### What Luna Does

**Tier 1: Text Quiz (~5 min)**
- 5 yes/no or short-answer questions
- Output: Lite archetype card (name + 3 traits + 2 blind spots + 1 green flag + 1 red flag)
- CTA: "Copy this. Share it. See what friends think."

**Tier 2: Voice Deepening (Optional, ~1–3 min if user opts in)**
- User uploads voice transcript OR speaks via ChatGPT's transcriber
- Output: Deep dossier (full archetype + conflict style + roastable traits + romantic patterns)
- CTA: "Post your archetype. Tag me. Use this when refining profiles or planning dates."

**Retention: DateOps Loop**
- User: "I already have a date this week. Help me plan it."
- You: Constraints in → Criteria filter → Scripts → Backup plans → Debrief after
- **No venue names.** You output criteria + templates only.

---

## MCP TOOLS (LOCKED, No Changes)

### 1. `store_archetype(kind='lite' | 'deep')`
**Purpose:** Validate + store archetype to Supabase.

**Input:**
```json
{
  "user_id": "string",
  "kind": "lite" | "deep",
  "archetype": {
    "name": "string",
    "traits": ["string", "string", "string"],
    "blind_spots": ["string", "string"],
    "green_flags": ["string"],
    "red_flags": ["string"],
    "conflict_style": "string (optional, deep only)",
    "roastable": ["string"] (optional, deep only)
  }
}
```

**Output:**
```json
{
  "status": "stored",
  "user_id": "...",
  "archetype_id": "...",
  "created_at": "ISO timestamp"
}
```

---

### 2. `store_dateops_plan()`
**Purpose:** Store date planning constraints → output criteria + scripts (no venue names).

**Input:**
```json
{
  "user_id": "string",
  "date_constraints": {
    "when": "this_week | this_month | specific_date",
    "venue_vibe": "casual | upscale | outdoorsy | cultural",
    "person_style": "string (e.g., 'creative, introverted, loves music')",
    "your_goals": "string (e.g., 'show I'm thoughtful without trying too hard')"
  }
}
```

**Output:**
```json
{
  "status": "planned",
  "plan_id": "...",
  "criteria": {
    "things_to_look_for": ["string", "string"],
    "things_to_avoid": ["string", "string"]
  },
  "scripts": {
    "opening": "string",
    "conversation_starters": ["string", "string"],
    "if_awkward": "string",
    "closing": "string"
  },
  "backup_plan": "string",
  "debrief_prompt": "string"
}
```

---

### 3. `log_event()`
**Purpose:** Track user actions for metrics + moat building.

**Input:**
```json
{
  "user_id": "string",
  "event_type": "quiz_started | lite_completed | deep_completed | shared | dateops_used | feedback_submitted",
  "timestamp": "ISO timestamp",
  "metadata": {}
}
```

**Output:**
```json
{
  "status": "logged",
  "event_id": "..."
}
```

---

### 4. `submit_feedback()`
**Purpose:** User reports outcome (helps refine archetype).

**Input:**
```json
{
  "user_id": "string",
  "archetype_id": "string",
  "feedback": {
    "outcome": "went_well | went_ok | didn't_click | learned_something",
    "what_worked": "string (optional)",
    "what_didn't": "string (optional)",
    "new_insight": "string (optional)"
  }
}
```

**Output:**
```json
{
  "status": "submitted",
  "feedback_id": "..."
}
```

---

## SUPABASE SCHEMA (LOCKED)

### Table: `users`
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP,
  region TEXT,
  source TEXT DEFAULT 'chatgpt_app_store'
);
```

### Table: `archetypes`
```sql
CREATE TABLE archetypes (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  kind TEXT NOT NULL CHECK (kind IN ('lite', 'deep')),
  name TEXT NOT NULL,
  traits JSONB,
  blind_spots JSONB,
  green_flags JSONB,
  red_flags JSONB,
  conflict_style TEXT,
  roastable JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, kind)
);
```

### Table: `dateops_plans`
```sql
CREATE TABLE dateops_plans (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  venue_vibe TEXT,
  person_style TEXT,
  goals TEXT,
  criteria JSONB,
  scripts JSONB,
  backup_plan TEXT,
  debrief_prompt TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `events`
```sql
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  event_type TEXT NOT NULL,
  archetype_id TEXT REFERENCES archetypes(id),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX(user_id, event_type)
);
```

### Table: `feedback`
```sql
CREATE TABLE feedback (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  archetype_id TEXT REFERENCES archetypes(id),
  outcome TEXT CHECK (outcome IN ('went_well', 'went_ok', 'didn't_click', 'learned_something')),
  what_worked TEXT,
  what_didn't TEXT,
  new_insight TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## WEEK 1: SETUP (8–10 hours)

### Monday–Tuesday (Jan 12–13)

- [ ] **Supabase Account** (5 min)
- [ ] **Run Schema SQL** (1 min)
- [ ] **Update SYSTEM_PROMPT.md lines 1–20** (5 min)
- [ ] **Copy server.py Locally** (2 min)
- [ ] **Install Dependencies** (5 min)
- [ ] **Test with curl** (30 min)
- [ ] **Verify data saves to Supabase** (10 min)

**Deliverable:** Working MCP server + database + updated messaging

---

## WEEK 2: HOSTING + REGISTRATION (6–8 hours)

### Wednesday–Thursday (Jan 15–16)

- [ ] **Push to GitHub** (10 min)
- [ ] **Deploy to Railway** (5 min)
- [ ] **Test health endpoint** (5 min)
- [ ] **Register MCP app in OpenAI** (10 min)
- [ ] **Invite 10 beta testers** (30 min)
- [ ] **Collect feedback** (30 min)

**Deliverable:** Public MCP server + beta access

---

## WEEK 3: BETA + SUBMIT (10–12 hours)

### Friday–Sunday (Jan 17–19)

- [ ] **Test all flows** (1.5 hrs)
- [ ] **Verify no PII** (20 min)
- [ ] **Monitor logs** (15 min)
- [ ] **Iterate on UX** (30 min)
- [ ] **Design app icon (512x512)** (1 hr)
- [ ] **Write App Store listing** (1 hr)
- [ ] **Submit to ChatGPT** (15 min)

**Deliverable:** App submitted to ChatGPT App Store

---

## WEEKS 4–13: GROWTH + METRICS (5–8 hrs/week)

### Every Friday (Jan 24, Jan 31, etc.)

- [ ] **Run weekly metrics**
- [ ] **Track 6 KPIs** (archetypes, deepening %, share rate, D7, DateOps attach, feedback)
- [ ] **Iterate on prompts**
- [ ] **Announce in communities**
- [ ] **Gather qualitative feedback**

---

## SUCCESS METRICS (WEEK 4)

By Friday, Jan 24, all 6 must be green to continue:

| Metric | Target |
|--------|--------|
| Archetypes Stored | ≥ 1,000 |
| Deepening % | ≥ 40% |
| Share Rate | ≥ 25% |
| D7 Retention | ≥ 50% |
| DateOps Attach | ≥ 20% |
| Feedback Signal | ≥ 30% |

**Green → Continue. Red → Pivot.**

---

## GO / NO-GO

**Status: GO ✅**

You have:
- ✅ Clear positioning (coach, not competitor)
- ✅ Clear timeline (3 weeks to launch)
- ✅ Clear metrics (6 KPIs by Week 4)
- ✅ Clear code (no changes needed)
- ✅ Clear optionality (Track B contingent)

Ship Track A immediately. Start Week 1 TODAY.

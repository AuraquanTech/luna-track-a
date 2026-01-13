# 🎯 DECISION LOCKED: Track A Launch (Jan 12, 2026)

**Status:** GO. Code locked. Positioning locked. Scope locked.  
**Timestamp:** January 12, 2026, 7:35 AM EST  
**Timeline to Launch:** 3 weeks (Jan 12 → Feb 2)  
**Timeline to 1K Users:** 13 weeks (Jan 12 → Apr 2)

---

## THE DECISION

### ✅ YES — Ship Track A Immediately

**As:** Relationship Chief-of-Staff Coach (NOT dating app, NOT matchmaker)

**Why:**
- Known ($9.7M funded) validates voice dating works (80% intro-to-date conversion)
- Overtone (Match Group) validates the market is massive
- Your "coach" positioning **avoids head-to-head** with both
- ChatGPT distribution is **unique** (no competitors in App Store)
- 3-week timeline is **realistic** (code unchanged, positioning only)
- $25/mo cost is **sustainable** (profitable at 100 users)

---

## WHAT CHANGED (POSITIONING ONLY)

### ❌ OLD
> "Luna: Voice-first AI dating app in ChatGPT"

### ✅ NEW
> "Luna: Relationship Chief-of-Staff Coach. Get your archetype in 60 seconds. Discover blind spots. Plan better dates (anywhere you date). NOT a dating app. NOT a matchmaker. Just self-knowledge."

---

## WHAT STAYED THE SAME (EVERYTHING ELSE)

### Code
- ✅ schema.sql (Supabase tables)
- ✅ server.py (MCP tools)
- ✅ requirements.txt (Python deps)
- ✅ METRICS_DASHBOARD.sql (analytics)

### Timeline
- ✅ Week 1: Supabase + local testing (8–10 hrs)
- ✅ Week 2: Railway deploy + beta (6–8 hrs)
- ✅ Week 3: Beta polish + submit (10–12 hrs)
- ✅ Weeks 4–13: Growth + metrics (5–8 hrs/week)

### Cost
- ✅ $25/mo (Railway + Supabase)
- ✅ Free ChatGPT App Store distribution
- ✅ Profitable at 100 users

### Architecture
- ✅ Tier 1: Text quiz → Lite archetype (5 min)
- ✅ Tier 2: Voice deepening → Deep dossier (1–3 min, optional)
- ✅ Retention: DateOps loop (constraints → plan → debrief)
- ✅ No OpenAI calls in server (ChatGPT reasoning only)
- ✅ No venue names (criteria + scripts only)

---

## COMPETITIVE MOAT (Why You Win vs. Known/Overtone)

| Advantage | You | Known | Overtone |
|-----------|-----|-------|----------|
| **Distribution** | ChatGPT (100M+ weekly) | Standalone app (paid ads) | Match apps (mature, declining) |
| **Time to Market** | 3 weeks | 6+ months | 6+ months |
| **Cost** | $25/mo | $100K+/mo burn | Unlimited budget |
| **Positioning** | Coach (complementary) | Matchmaker (direct) | Matchmaker (direct) |
| **Retention** | DateOps loop | Matching (churn on pair) | Matching (churn on pair) |
| **Data Moat** | Standardized archetypes | Proprietary matching | Proprietary matching |

---

## SUCCESS METRICS (WEEK 4 LOCKDOWN)

By **January 24, 2026** (Week 4), you'll know if positioning works:

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Archetypes Stored** | 1,000 | ≥ 1,000 = GO |
| **Deepening %** | 40% | lite_completed / quiz_started |
| **Share Rate** | 25% | shared / lite_completed |
| **D7 Retention** | 50% | users_active_day_7 / users_created |
| **DateOps Attach** | 20% | dateops_users / total_users |
| **Feedback Signal** | 30% | feedback_submitted / total_users |

**If ALL green:** Continue Weeks 5–13, plan Track B contingency.  
**If ANY red:** Positioning failed, Known/Overtone won, pivot or shut down.

---

## DECISION GATES (When to Pivot)

### WEEK 4 (Jan 24)
- ✅ **Green:** Positioning validated, continue
- ❌ **Red:** Positioning failed, pivot or shut down

### WEEK 8–13 (Feb 21 – Mar 28)
- ✅ **Known stalls + your 5K+ users:** Build Track B matching (raise funding)
- ❌ **Known scales nationally + your <1K users:** Pivot to B2B licensing or shut down

---

## MCP TOOLS (LOCKED, No Changes)

### 1. `store_archetype(kind='lite' | 'deep')`
Validate + store archetype to Supabase. Returns archetype_id.

### 2. `store_dateops_plan()`
User enters constraints → outputs criteria + scripts (NO venue names).

### 3. `log_event()`
Track: quiz_started, lite_completed, deep_completed, shared, dateops_used, feedback_submitted.

### 4. `submit_feedback()`
User outcome (went well / didn't / learned X). Improves archetype.

---

## SUPABASE SCHEMA (LOCKED)

5 tables:
- **users** (id, created_at, last_seen, region, source)
- **archetypes** (id, user_id, kind, name, traits[], blind_spots[], green_flags[], red_flags[], created_at)
- **dateops_plans** (id, user_id, venue_vibe, person_style, goals, criteria, scripts, backup_plan, debrief_prompt)
- **events** (id, user_id, event_type, archetype_id, metadata, created_at)
- **feedback** (id, user_id, archetype_id, outcome, what_worked, what_didn't, new_insight)

---

## WEEK 1: SETUP (8–10 hours)

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

- [ ] **Push to GitHub** (10 min)
- [ ] **Deploy to Railway** (5 min)
- [ ] **Test health endpoint** (5 min)
- [ ] **Register MCP app in OpenAI Apps SDK** (10 min)
- [ ] **Invite 10 beta testers** (30 min)
- [ ] **Collect feedback** (ongoing)

**Deliverable:** Public MCP server + beta access

---

## WEEK 3: BETA + SUBMIT (10–12 hours)

- [ ] **Test quiz flow (Tier 1)** (30 min)
- [ ] **Test voice deepening (Tier 2)** (30 min)
- [ ] **Test DateOps flow** (30 min)
- [ ] **Verify no PII in outputs** (20 min)
- [ ] **Monitor Railway logs** (15 min)
- [ ] **Iterate on tone/UX** (30 min)
- [ ] **Design app icon (512x512)** (1 hr)
- [ ] **Write App Store listing** (1 hr)
- [ ] **Submit to ChatGPT App Store** (15 min)

**Deliverable:** App submitted

---

## WEEKS 4–13: GROWTH + METRICS (5–8 hrs/week)

Every Friday:
- [ ] **Run METRICS_DASHBOARD.sql**
- [ ] **Track:** 1K archetypes, 25% share, 50% D7, 20% DateOps
- [ ] **Monitor Railway logs**
- [ ] **Adjust system prompt if needed**
- [ ] **Announce in communities (Reddit, Discord, Twitter)**
- [ ] **Gather feedback**
- [ ] **Document patterns**

**Deliverable:** Data moat + clear Track B signal

---

## FINAL LOCK-IN

### Code Decision: ✅ LOCKED
- Chief-of-staff coach positioning
- Tier 1 (text quiz) → Tier 2 (voice) → Retention (DateOps)
- 4 MCP tools, 5 Supabase tables
- No changes to architecture

### Timeline Decision: ✅ LOCKED
- Week 1: 8–10 hrs (setup)
- Week 2: 6–8 hrs (deploy)
- Week 3: 10–12 hrs (submit)
- Weeks 4–13: 5–8 hrs/week (growth)

### Metrics Decision: ✅ LOCKED
- 6 success metrics by Week 4
- All must be green to continue
- Otherwise pivot or shut down

### Track B Decision: ✅ LOCKED
- Contingent on Known's growth + your metrics
- If Known scales + you're <1K: Pivot to B2B or shut down
- If Known stalls + you're 5K+: Build matching + raise funding

---

## GO/NO-GO

**Status: GO ✅**

You have:
- ✅ Clear decision (coach positioning, not matchmaker)
- ✅ Clear code (no changes needed)
- ✅ Clear timeline (3 weeks)
- ✅ Clear metrics (6 KPIs)
- ✅ Clear optionality (raise, pivot, or shut down by Week 13)

---

**Ship Track A immediately. Measure at Week 4. Decide on Track B by Week 13.**

**You've got this. 🚀**

-- METRICS_DASHBOARD.sql — Luna Track A
-- Use in Supabase SQL Editor or a BI tool.

-- ------------------------------------------------------------
-- Core counts
-- ------------------------------------------------------------

-- Users
select count(*) as users_total from users;

-- Archetypes by level
select level, count(*) as archetypes_count
from archetypes
group by level
order by level;

-- DateOps plans
select count(*) as date_plans_total from date_plans;

-- ------------------------------------------------------------
-- Activation / completion rates
-- You must emit events via log_event() in SYSTEM_PROMPT.
-- Recommended event names:
--   quiz_started, quiz_completed, deep_started, deep_completed,
--   share_clicked, dateops_started, dateops_completed, app_open
-- ------------------------------------------------------------

-- Daily quiz completion
select
  date_trunc('day', occurred_at) as day,
  count(*) filter (where event_name = 'quiz_started') as quiz_started,
  count(*) filter (where event_name = 'quiz_completed') as quiz_completed,
  round(
    100.0 * count(*) filter (where event_name = 'quiz_completed')
    / nullif(count(*) filter (where event_name = 'quiz_started'), 0), 1
  ) as quiz_completion_pct
from event_log
group by 1
order by 1 desc;

-- Deepening % (users with deep archetype / users with lite archetype)
with lite as (
  select distinct user_id from archetypes where level = 'lite'
),
deep as (
  select distinct user_id from archetypes where level = 'deep'
)
select
  (select count(*) from lite) as users_lite,
  (select count(*) from deep) as users_deep,
  round(100.0 * (select count(*) from deep) / nullif((select count(*) from lite), 0), 1) as deepening_pct;

-- Share rate (share_clicked / quiz_completed)
select
  round(
    100.0 * count(*) filter (where event_name='share_clicked')
    / nullif(count(*) filter (where event_name='quiz_completed'), 0), 1
  ) as share_rate_pct
from event_log;

-- DateOps attach rate (dateops_completed / quiz_completed)
select
  round(
    100.0 * count(*) filter (where event_name='dateops_completed')
    / nullif(count(*) filter (where event_name='quiz_completed'), 0), 1
  ) as dateops_attach_pct
from event_log;

-- ------------------------------------------------------------
-- Retention (D1 / D7)
-- Definition: a user is "active" on a day if they have ANY event that day.
-- ------------------------------------------------------------

-- Cohort table (signup day = first event day)
with first_seen as (
  select user_id, min(date_trunc('day', occurred_at)) as cohort_day
  from event_log
  group by 1
),
activity as (
  select user_id, date_trunc('day', occurred_at) as day
  from event_log
  group by 1, 2
),
ret as (
  select
    f.cohort_day,
    count(*) as cohort_size,
    count(*) filter (where a.day = f.cohort_day + interval '1 day') as d1,
    count(*) filter (where a.day between f.cohort_day + interval '6 day' and f.cohort_day + interval '8 day') as d7_window
  from first_seen f
  left join activity a on a.user_id = f.user_id
  group by 1
)
select
  cohort_day::date,
  cohort_size,
  round(100.0 * d1 / nullif(cohort_size, 0), 1) as d1_retention_pct,
  round(100.0 * d7_window / nullif(cohort_size, 0), 1) as d7_retention_pct
from ret
order by cohort_day desc;

-- ------------------------------------------------------------
-- Week-over-week executive summary (last 7 days)
-- ------------------------------------------------------------
with last7 as (
  select *
  from event_log
  where occurred_at >= now() - interval '7 days'
)
select
  count(distinct user_id) as active_users_7d,
  count(*) filter (where event_name='quiz_completed') as quiz_completed_7d,
  count(*) filter (where event_name='deep_completed') as deep_completed_7d,
  count(*) filter (where event_name='dateops_completed') as dateops_completed_7d,
  round(100.0 * count(*) filter (where event_name='deep_completed') / nullif(count(*) filter (where event_name='quiz_completed'),0), 1) as deepening_pct_7d,
  round(100.0 * count(*) filter (where event_name='share_clicked') / nullif(count(*) filter (where event_name='quiz_completed'),0), 1) as share_rate_pct_7d
from last7;

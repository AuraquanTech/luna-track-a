-- Luna Track A (Chief-of-Staff Coach) — Supabase/Postgres schema
-- Purpose: store standardized archetypes + DateOps plans + analytics events.
-- NOTE: This schema is designed for service_role access (server-side). No client access assumed.

begin;

-- Extensions
create extension if not exists "uuid-ossp";
create extension if not exists "vector";

-- ------------------------------------------------------------
-- 0) Schema versioning
-- ------------------------------------------------------------
create table if not exists schema_version (
  id uuid primary key default uuid_generate_v4(),
  version text not null unique,
  applied_at timestamptz not null default now()
);

-- ------------------------------------------------------------
-- 1) Users (pseudonymous)
-- ------------------------------------------------------------
create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  chatgpt_user_ref text unique not null, -- pseudonymous stable ref (hash) from OpenAI/ChatGPT
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  data_opt_out boolean not null default false,
  consent_version text, -- optional, set when user explicitly consents
  last_seen_at timestamptz
);

create index if not exists idx_users_created_at on users(created_at);
create index if not exists idx_users_last_seen_at on users(last_seen_at);

-- ------------------------------------------------------------
-- 2) Archetypes (the moat)
-- ------------------------------------------------------------
do $$ begin
  create type archetype_level as enum ('lite', 'deep');
exception when duplicate_object then null;
end $$;

create table if not exists archetypes (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  level archetype_level not null default 'lite',
  source_hash text not null, -- idempotency key
  archetype_json jsonb not null,
  embedding vector(1536), -- optional; Track B
  model_version text, -- optional; for future compatibility
  created_at timestamptz not null default now(),

  unique(user_id, level, source_hash)
);

create index if not exists idx_archetypes_user_created on archetypes(user_id, created_at desc);
create index if not exists idx_archetypes_level on archetypes(level);

-- ------------------------------------------------------------
-- 3) DateOps plans (retention loop; criteria-only, no venues)
-- ------------------------------------------------------------
create table if not exists date_plans (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  source_hash text not null, -- idempotency key
  city text not null,
  plan_json jsonb not null,
  created_at timestamptz not null default now(),

  unique(user_id, source_hash)
);

create index if not exists idx_date_plans_user_created on date_plans(user_id, created_at desc);
create index if not exists idx_date_plans_city on date_plans(city);

-- ------------------------------------------------------------
-- 4) Feedback (learning loop, still Track A-safe)
-- ------------------------------------------------------------
create table if not exists feedback (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  date_plan_id uuid references date_plans(id) on delete set null,
  rating int check (rating between 1 and 5),
  tags text[],
  notes text,
  created_at timestamptz not null default now()
);

create index if not exists idx_feedback_user_created on feedback(user_id, created_at desc);

-- ------------------------------------------------------------
-- 5) Event log (metrics & funnels)
-- ------------------------------------------------------------
create table if not exists event_log (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references users(id) on delete cascade,
  event_name text not null,
  event_id text not null, -- idempotency for event (client generated)
  properties jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now(),

  unique(user_id, event_id)
);

create index if not exists idx_event_log_user_time on event_log(user_id, occurred_at desc);
create index if not exists idx_event_log_name_time on event_log(event_name, occurred_at desc);

-- ------------------------------------------------------------
-- RLS (locked down; server uses service_role anyway)
-- ------------------------------------------------------------
alter table users enable row level security;
alter table archetypes enable row level security;
alter table date_plans enable row level security;
alter table feedback enable row level security;
alter table event_log enable row level security;

-- Deny everything by default (no policies) - intended for service_role access only.

insert into schema_version(version) values ('2026-01-12.luna_track_a.v1')
on conflict (version) do nothing;

commit;

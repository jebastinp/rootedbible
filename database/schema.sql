-- =====================================================================
-- Rooted — Bible Reading Tracker 2026
-- Production PostgreSQL / Supabase Schema
-- =====================================================================
-- Run this whole file once against a fresh Supabase project
-- (Supabase SQL Editor -> New query -> paste -> Run)
-- =====================================================================

create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------
-- ENUM TYPES
-- ---------------------------------------------------------------------
do $$ begin
  create type user_role as enum ('member', 'leader', 'admin', 'super_admin');
exception when duplicate_object then null; end $$;

do $$ begin
  create type user_status as enum ('active', 'inactive', 'suspended');
exception when duplicate_object then null; end $$;

do $$ begin
  create type announcement_visibility as enum ('all', 'members', 'leaders', 'admins');
exception when duplicate_object then null; end $$;

do $$ begin
  create type import_status as enum ('pending', 'processing', 'success', 'failed', 'rolled_back');
exception when duplicate_object then null; end $$;

-- ---------------------------------------------------------------------
-- USERS
-- ---------------------------------------------------------------------
create table if not exists users (
    id              uuid primary key default uuid_generate_v4(),
    user_id         varchar(20) not null unique,      -- e.g. REH001, legacy/admin login
    supabase_user_id varchar(50) unique,                -- Supabase Auth user id (Google sign-in via Supabase)
    email           varchar(255) unique,               -- Google account email
    name            varchar(150) not null,
    phone           varchar(20),
    role            user_role not null default 'member',
    status          user_status not null default 'active',
    photo_url       text,
    joined_date     date not null default current_date,
    date_of_birth   date,
    auth_provider   varchar(20),                        -- 'google' | 'email' | 'legacy'
    last_login_at   timestamptz,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    deleted_at      timestamptz
);

create index if not exists idx_users_user_id on users (user_id) where deleted_at is null;
create index if not exists idx_users_supabase_user_id on users (supabase_user_id) where deleted_at is null;
create index if not exists idx_users_email on users (email) where deleted_at is null;
create index if not exists idx_users_role on users (role) where deleted_at is null;
create index if not exists idx_users_status on users (status) where deleted_at is null;

-- ---------------------------------------------------------------------
-- READING PLAN (single church-wide plan, one row per day)
-- ---------------------------------------------------------------------
create table if not exists reading_plan (
    id                  uuid primary key default uuid_generate_v4(),
    day_number          integer not null unique,
    reading_date        date not null unique,
    old_testament       text,           -- e.g. "Genesis 1-3"
    new_testament       text,           -- e.g. "Matthew 1"
    estimated_minutes   integer not null default 15,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),
    deleted_at          timestamptz,
    constraint chk_day_number_positive check (day_number > 0)
);

create index if not exists idx_reading_plan_date on reading_plan (reading_date) where deleted_at is null;
create index if not exists idx_reading_plan_day on reading_plan (day_number) where deleted_at is null;

create table if not exists reading_plan_passage (
    id                  uuid primary key default uuid_generate_v4(),
    reading_plan_id     uuid not null references reading_plan(id) on delete cascade,
    testament           varchar(3) not null,
    book_name           varchar(60) not null,
    chapter_start       integer not null,
    chapter_end         integer not null,
    sort_order          integer not null default 0,
    constraint chk_passage_testament check (testament in ('OT','NT')),
    constraint chk_passage_chapter_range check (chapter_end >= chapter_start)
);

create index if not exists idx_passage_plan on reading_plan_passage (reading_plan_id);

-- ---------------------------------------------------------------------
-- READING PROGRESS (one row per user per day)
-- ---------------------------------------------------------------------
create table if not exists reading_progress (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    reading_plan_id     uuid not null references reading_plan(id) on delete cascade,
    day_number          integer not null,
    completed           boolean not null default false,
    completed_at        timestamptz,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),
    unique (user_id, reading_plan_id)
);

create index if not exists idx_progress_user on reading_progress (user_id);
create index if not exists idx_progress_plan on reading_progress (reading_plan_id);
create index if not exists idx_progress_completed on reading_progress (completed);
create index if not exists idx_progress_user_day on reading_progress (user_id, day_number);

-- ---------------------------------------------------------------------
-- USER STATS (denormalized, recalculated on every progress change / import)
-- ---------------------------------------------------------------------
create table if not exists user_stats (
    user_id             uuid primary key references users(id) on delete cascade,
    current_streak      integer not null default 0,
    longest_streak      integer not null default 0,
    days_completed      integer not null default 0,
    ot_days_completed    integer not null default 0,
    nt_days_completed    integer not null default 0,
    overall_percentage  numeric(5,2) not null default 0,
    last_completed_date date,
    updated_at          timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- ANNOUNCEMENTS
-- ---------------------------------------------------------------------
create table if not exists announcements (
    id              uuid primary key default uuid_generate_v4(),
    title           varchar(200) not null,
    description     text not null,
    publish_date    date not null default current_date,
    expiry_date     date,
    visibility      announcement_visibility not null default 'all',
    is_active       boolean not null default true,
    created_by      uuid references users(id),
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now(),
    deleted_at      timestamptz
);

create index if not exists idx_announcements_active on announcements (is_active, publish_date, expiry_date) where deleted_at is null;

-- ---------------------------------------------------------------------
-- CHURCH SETTINGS (single row config)
-- ---------------------------------------------------------------------
create table if not exists church_settings (
    id                  uuid primary key default uuid_generate_v4(),
    church_name         varchar(200) not null default 'Rooted Church',
    church_logo_url     text,
    reading_year        integer not null default 2026,
    verse_of_the_day    text,
    updated_at          timestamptz not null default now()
);

-- ---------------------------------------------------------------------
-- AUDIT LOGS
-- ---------------------------------------------------------------------
create table if not exists audit_logs (
    id              uuid primary key default uuid_generate_v4(),
    actor_id        uuid references users(id),
    action          varchar(100) not null,        -- e.g. "USER_CREATED", "PROGRESS_MARKED"
    entity_type     varchar(50) not null,
    entity_id       uuid,
    metadata        jsonb,
    ip_address      varchar(50),
    created_at      timestamptz not null default now()
);

create index if not exists idx_audit_actor on audit_logs (actor_id);
create index if not exists idx_audit_entity on audit_logs (entity_type, entity_id);
create index if not exists idx_audit_created on audit_logs (created_at desc);

-- ---------------------------------------------------------------------
-- CSV IMPORT HISTORY
-- ---------------------------------------------------------------------
create table if not exists import_history (
    id                  uuid primary key default uuid_generate_v4(),
    file_type           varchar(30) not null,      -- users | reading_plan | progress
    file_name           varchar(255) not null,
    status              import_status not null default 'pending',
    total_rows          integer not null default 0,
    inserted_rows       integer not null default 0,
    updated_rows        integer not null default 0,
    skipped_rows        integer not null default 0,
    failed_rows         integer not null default 0,
    error_log           jsonb,
    imported_by         uuid references users(id),
    created_at          timestamptz not null default now(),
    completed_at        timestamptz
);

create index if not exists idx_import_status on import_history (status);
create index if not exists idx_import_type on import_history (file_type);

-- ---------------------------------------------------------------------
-- BIBLE CONTENT (versions/books/chapters) - structured so licensed
-- translations can be added later without any code changes. Only
-- license_status IN ('public_domain','licensed') is ever shown to users;
-- 'pending' versions exist as placeholders until a church has a signed
-- license (see README section on Bible content licensing).
-- ---------------------------------------------------------------------
create table if not exists bible_version (
    id              uuid primary key default uuid_generate_v4(),
    code            varchar(20) not null unique,
    language        varchar(40) not null,
    version_name    varchar(120) not null,
    license_status  varchar(20) not null default 'pending',
    is_active       boolean not null default true,
    created_at      timestamptz not null default now()
);

create table if not exists bible_book (
    id                  uuid primary key default uuid_generate_v4(),
    bible_version_id    uuid not null references bible_version(id) on delete cascade,
    name                varchar(60) not null,
    testament           varchar(3) not null check (testament in ('OT', 'NT')),
    sort_order          integer not null,
    chapter_count       integer not null,
    unique (bible_version_id, name)
);

create table if not exists bible_chapter (
    id                  uuid primary key default uuid_generate_v4(),
    book_id             uuid not null references bible_book(id) on delete cascade,
    chapter_number      integer not null,
    unique (book_id, chapter_number)
);

create index if not exists idx_bible_chapter_book on bible_chapter (book_id);

-- Each verse individually addressable - highlights/notes/bookmarks reference
-- verse_id, never verse text (different translations have different text).
create table if not exists bible_verse (
    id                  uuid primary key default uuid_generate_v4(),
    chapter_id          uuid not null references bible_chapter(id) on delete cascade,
    verse_number        integer not null,
    text                text not null,
    unique (chapter_id, verse_number)
);

create index if not exists idx_verse_chapter on bible_verse (chapter_id);

create table if not exists bookmark (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    verse_id            uuid not null references bible_verse(id) on delete cascade,
    translation_id      uuid not null references bible_version(id) on delete cascade,
    created_at          timestamptz not null default now(),
    unique (user_id, verse_id)
);

create index if not exists idx_bookmark_user on bookmark (user_id);

-- One row per user - always the single latest reading position.
create table if not exists reading_position (
    user_id             uuid primary key references users(id) on delete cascade,
    translation_id      uuid not null references bible_version(id) on delete cascade,
    book_id             uuid not null references bible_book(id) on delete cascade,
    chapter_number      integer not null,
    verse_number        integer not null default 1,
    updated_at          timestamptz not null default now()
);

-- Standalone chapter completion, independent of any reading plan.
create table if not exists reading_completion (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    translation_id      uuid not null references bible_version(id) on delete cascade,
    book_id             uuid not null references bible_book(id) on delete cascade,
    chapter_number      integer not null,
    completed_at        timestamptz not null default now(),
    unique (user_id, translation_id, book_id, chapter_number)
);

create index if not exists idx_completion_user on reading_completion (user_id);

-- Placeholder rows for every version named in the product plan. All rows
-- start 'pending' and empty (no books/chapters) until licensed - at which
-- point an admin flips license_status and runs the XML import for that
-- version (backend/scripts/import_bible_xml.py). Note: 'kjv1769' is the
-- internal code but the only English KJV-family source file actually on
-- disk is the 21st Century King James Version (KJ21, 1994) - a distinct,
-- copyrighted edition, NOT the genuine public-domain 1769 KJV. Never mark
-- this 'public_domain' - it isn't.
insert into bible_version (code, language, version_name, license_status)
values
    ('kjv1769', 'English', '21st Century King James Version (KJ21)', 'pending'),
    ('nkjv', 'English', 'New King James Version', 'pending'),
    ('ta_bsi', 'Tamil', 'Tamil Bible (Bible Society of India)', 'pending'),
    ('te_bsi', 'Telugu', 'Telugu Bible (Bible Society of India)', 'pending'),
    ('kn_bsi', 'Kannada', 'Kannada Bible (Bible Society of India)', 'pending'),
    ('hi_bsi', 'Hindi', 'Hindi Bible (Bible Society of India)', 'pending')
on conflict (code) do nothing;

-- ---------------------------------------------------------------------
-- QUIZ
-- ---------------------------------------------------------------------
create table if not exists quiz_question (
    id                  uuid primary key default uuid_generate_v4(),
    chapter_id          uuid not null references bible_chapter(id) on delete cascade,
    question            text not null,
    options             jsonb not null,
    correct_index       integer not null,
    verse_reference     varchar(60) not null,
    age_group           varchar(10) not null default 'adult'
);

create index if not exists idx_quiz_question_chapter on quiz_question (chapter_id);

create table if not exists quiz_attempt (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    reading_plan_id     uuid not null references reading_plan(id) on delete cascade,
    chapter_id          uuid references bible_chapter(id) on delete set null,
    score               integer not null default 0,
    total_questions     integer not null default 0,
    passed              boolean not null default false,
    attempt_count       integer not null default 1,
    created_at          timestamptz not null default now()
);

create index if not exists idx_quiz_attempt_user on quiz_attempt (user_id, reading_plan_id);

-- ---------------------------------------------------------------------
-- NOTES & HIGHLIGHTS
-- ---------------------------------------------------------------------
create table if not exists note (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    verse_reference     varchar(60) not null,
    verse_id            uuid references bible_verse(id) on delete cascade,
    translation_id      uuid references bible_version(id) on delete cascade,
    note_text           text not null,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_note_user on note (user_id);

create table if not exists highlight (
    id                  uuid primary key default uuid_generate_v4(),
    user_id             uuid not null references users(id) on delete cascade,
    verse_reference     varchar(60) not null,
    color               varchar(10) not null default 'yellow' check (color in ('yellow','blue','green','red','purple')),
    verse_id            uuid references bible_verse(id) on delete cascade,
    translation_id      uuid references bible_version(id) on delete cascade,
    verse_start         integer,
    verse_end           integer,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_highlight_user on highlight (user_id);

-- ---------------------------------------------------------------------
-- CHURCH CHALLENGE: the parent container for Family / Buddy Group community.
-- There is no global community - a Family or Buddy Group always belongs to
-- exactly one Church Challenge, and only ACTIVE participants of that
-- challenge may belong to its groups.
-- ---------------------------------------------------------------------
create table if not exists church_challenge (
    id                  uuid primary key default uuid_generate_v4(),
    name                varchar(200) not null,
    church_name         varchar(200) not null,
    description         text,
    reading_plan_id     uuid references reading_plan(id) on delete set null,
    start_date          date,
    end_date            date,
    participant_limit   integer not null default 100,
    status              varchar(20) not null default 'draft' check (status in ('draft','active','completed','archived')),
    allow_families      boolean not null default true,
    family_limit        integer not null default 4,
    allow_buddies       boolean not null default true,
    buddy_limit         integer not null default 5,
    quiz_enabled        boolean not null default true,
    rewards_enabled     boolean not null default true,
    created_by          uuid references users(id) on delete set null,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),
    deleted_at          timestamptz
);

create table if not exists challenge_member (
    id                  uuid primary key default uuid_generate_v4(),
    challenge_id        uuid not null references church_challenge(id) on delete cascade,
    user_id             uuid not null references users(id) on delete cascade,
    status              varchar(20) not null default 'pending' check (status in ('pending','active','removed')),
    role                varchar(20) not null default 'participant' check (role in ('participant','admin')),
    requested_at        timestamptz not null default now(),
    joined_at           timestamptz,
    unique (challenge_id, user_id)
);

create index if not exists idx_challenge_member_challenge on challenge_member (challenge_id);
create index if not exists idx_challenge_member_user on challenge_member (user_id);

create table if not exists family (
    id                  uuid primary key default uuid_generate_v4(),
    challenge_id        uuid not null references church_challenge(id) on delete cascade,
    name                varchar(120) not null,
    owner_id            uuid not null references users(id) on delete cascade,
    description         text,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_family_challenge on family (challenge_id);

create table if not exists family_member (
    id                  uuid primary key default uuid_generate_v4(),
    family_id           uuid not null references family(id) on delete cascade,
    user_id             uuid not null references users(id) on delete cascade,
    role                varchar(10) not null default 'member' check (role in ('owner','member')),
    status              varchar(10) not null default 'active' check (status in ('active','removed','left')),
    joined_at           timestamptz not null default now(),
    unique (family_id, user_id)
);

create index if not exists idx_family_member_family on family_member (family_id);
create index if not exists idx_family_member_user on family_member (user_id);

create table if not exists buddy_group (
    id                  uuid primary key default uuid_generate_v4(),
    challenge_id        uuid not null references church_challenge(id) on delete cascade,
    name                varchar(120) not null,
    owner_id            uuid not null references users(id) on delete cascade,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_buddy_group_challenge on buddy_group (challenge_id);

create table if not exists buddy_member (
    id                  uuid primary key default uuid_generate_v4(),
    buddy_group_id      uuid not null references buddy_group(id) on delete cascade,
    user_id             uuid not null references users(id) on delete cascade,
    role                varchar(10) not null default 'member' check (role in ('owner','member')),
    status              varchar(10) not null default 'active' check (status in ('active','removed','left')),
    joined_at           timestamptz not null default now(),
    unique (buddy_group_id, user_id)
);

create index if not exists idx_buddy_member_group on buddy_member (buddy_group_id);
create index if not exists idx_buddy_member_user on buddy_member (user_id);

create table if not exists join_request (
    id                  uuid primary key default uuid_generate_v4(),
    type                varchar(20) not null check (type in ('challenge','family','buddy')),
    requester_id        uuid not null references users(id) on delete cascade,
    target_user_id      uuid references users(id) on delete cascade,
    challenge_id        uuid references church_challenge(id) on delete cascade,
    family_id           uuid references family(id) on delete cascade,
    buddy_group_id      uuid references buddy_group(id) on delete cascade,
    status              varchar(10) not null default 'pending' check (status in ('pending','approved','declined','cancelled')),
    created_at          timestamptz not null default now(),
    responded_at        timestamptz,
    responded_by_id     uuid references users(id) on delete set null
);

create index if not exists idx_request_requester on join_request (requester_id);
create index if not exists idx_request_target on join_request (target_user_id);
create index if not exists idx_request_challenge on join_request (challenge_id);
create index if not exists idx_request_family on join_request (family_id);
create index if not exists idx_request_buddy_group on join_request (buddy_group_id);

create table if not exists challenge_reward (
    id                  uuid primary key default uuid_generate_v4(),
    challenge_id        uuid not null references church_challenge(id) on delete cascade,
    name                varchar(120) not null,
    description         text,
    requirement_type    varchar(20) not null check (requirement_type in ('streak','completion')),
    requirement_value   integer not null,
    badge_icon          varchar(40),
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

create index if not exists idx_reward_challenge on challenge_reward (challenge_id);

create table if not exists encouragement (
    id                  uuid primary key default uuid_generate_v4(),
    from_user_id        uuid not null references users(id) on delete cascade,
    to_user_id          uuid references users(id) on delete cascade,
    family_id           uuid references family(id) on delete cascade,
    buddy_group_id      uuid references buddy_group(id) on delete cascade,
    message             varchar(120) not null,
    created_at          timestamptz not null default now(),
    check ((family_id is not null and buddy_group_id is null) or (family_id is null and buddy_group_id is not null))
);

create index if not exists idx_encouragement_family on encouragement (family_id);
create index if not exists idx_encouragement_buddy_group on encouragement (buddy_group_id);

-- ---------------------------------------------------------------------
-- TRIGGERS: auto-update updated_at
-- ---------------------------------------------------------------------
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_users_updated_at on users;
create trigger trg_users_updated_at before update on users
  for each row execute function set_updated_at();

drop trigger if exists trg_reading_plan_updated_at on reading_plan;
create trigger trg_reading_plan_updated_at before update on reading_plan
  for each row execute function set_updated_at();

drop trigger if exists trg_progress_updated_at on reading_progress;
create trigger trg_progress_updated_at before update on reading_progress
  for each row execute function set_updated_at();

drop trigger if exists trg_announcements_updated_at on announcements;
create trigger trg_announcements_updated_at before update on announcements
  for each row execute function set_updated_at();

drop trigger if exists trg_church_challenge_updated_at on church_challenge;
create trigger trg_church_challenge_updated_at before update on church_challenge
  for each row execute function set_updated_at();

drop trigger if exists trg_family_updated_at on family;
create trigger trg_family_updated_at before update on family
  for each row execute function set_updated_at();

drop trigger if exists trg_buddy_group_updated_at on buddy_group;
create trigger trg_buddy_group_updated_at before update on buddy_group
  for each row execute function set_updated_at();

drop trigger if exists trg_challenge_reward_updated_at on challenge_reward;
create trigger trg_challenge_reward_updated_at before update on challenge_reward
  for each row execute function set_updated_at();

-- ---------------------------------------------------------------------
-- SEED: default church settings row
-- ---------------------------------------------------------------------
insert into church_settings (church_name, reading_year, verse_of_the_day)
select 'Rooted Church', 2026, 'Blessed is the one... whose delight is in the law of the LORD. (Psalm 1:1-2)'
where not exists (select 1 from church_settings);

-- ---------------------------------------------------------------------
-- SEED: a super admin so the app is usable on first boot
-- ---------------------------------------------------------------------
insert into users (user_id, name, role, status)
select 'ADMIN001', 'Super Admin', 'super_admin', 'active'
where not exists (select 1 from users where user_id = 'ADMIN001');

insert into user_stats (user_id)
select id from users where user_id = 'ADMIN001'
on conflict (user_id) do nothing;

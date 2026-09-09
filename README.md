# Rooted 🌱
### Rooted in God's Word. Growing Every Day.

Rooted is being developed as a Scripture-first reading companion for individuals
and churches. The [new product foundation](docs/rooted/README.md) is authoritative
for the MVP; it includes the PRD, backlog, design, architecture, rights inventory
and release gates. Individual sign-in is requested but not yet implemented.

The existing app is a church-tracker prototype. Its member-code login, quizzes,
rankings and plan-day statistics are legacy behavior, not the new MVP definition.
No Bible edition is currently cleared for this release.
---

## 0. Quick Start (one click, after Supabase is set up)

```bash
# Mac/Linux
./run.sh

# Windows
run.bat
```

This installs dependencies on first run (Python venv + npm) and starts
both the backend (`http://localhost:8001`) and frontend
(`http://localhost:5173`) together. Ctrl+C stops both.

**You still need to do this once first** — the script can't do it for you:
1. Create a free [Supabase](https://supabase.com) project.
2. Open its **SQL Editor**, paste all of `database/schema.sql`, run it.
3. Copy the connection string into `backend/.env`'s `DATABASE_URL` (the
   script creates `backend/.env` from `.env.example` on first run if it
   doesn't exist yet — edit it, then run `./run.sh` again).
4. Complete the [edition licensing and source workflow](docs/rooted/07-bible-licensing.md).
   The legacy automatic KJV importer is disabled. Do not substitute another
   translation or mark an edition approved without evidence and content QA.
5. In the Admin Panel → **Plan Generator**, generate your first reading
   plan (e.g. "New Testament, 90 days, Sunday rest") so Home has
   something to link to.

First login (seeded automatically by `schema.sql`): **`ADMIN001`** (no
password — see section 3.5 below for why).

---

## 1. Architecture

```
bible-reading-tracker/
├── backend/            FastAPI + SQLAlchemy + Alembic (Python 3.12)
│   ├── app/
│   │   ├── core/       config, security (JWT), custom exceptions
│   │   ├── db/         SQLAlchemy engine/session
│   │   ├── models/     ORM models (Users, ReadingPlan, Progress, ...)
│   │   ├── schemas/    Pydantic request/response DTOs
│   │   ├── repositories/  thin DB-access layer (no business logic)
│   │   ├── services/   business logic (streaks, CSV import, auth, reports)
│   │   ├── api/v1/     FastAPI routers (controllers - thin, delegate to services)
│   │   └── main.py     app factory, middleware, exception handlers
│   ├── alembic/        DB migrations
│   └── tests/          pytest unit tests
├── frontend/           React 19 + Vite + TypeScript + Tailwind
│   └── src/
│       ├── features/   member-facing pages (home, progress, community, profile, auth)
│       ├── admin/       admin panel pages (dashboard, members, reading plan, reports, CSV import, settings)
│       ├── components/ shared layout + UI pieces
│       ├── store/      Zustand auth store (persisted)
│       └── lib/        axios client with auto token refresh
├── database/schema.sql  Full Postgres/Supabase schema (run this in Supabase SQL editor)
├── supabase/schema.sql  Same file, kept here too since Supabase tooling often looks here
├── sample-csv/          Example users.csv / reading_plan.csv / progress.csv
└── docker-compose.yml
```

**Layering rule that was followed throughout:** controllers (`api/v1/*.py`)
never contain business logic — they validate input via Pydantic, call a
service, and return the result. All calculation (streaks, percentages,
CSV validation/upsert, dashboard aggregation) lives in `services/`.

---

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Frontend | React 19, Vite, TypeScript, TailwindCSS, Framer Motion, TanStack Query, Zustand, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | Supabase (hosted PostgreSQL) |
| Auth | JWT (User-ID-only login, no password/OTP/email) |
| CSV Import | pandas, with preview → validate → confirm → rollback flow |

---

## 3. Getting Started

### 3.1 Prerequisites
- Node.js 20+
- Python 3.12+
- A free [Supabase](https://supabase.com) project

### 3.2 Set up the database (Supabase)
1. Create a new Supabase project.
2. Open **SQL Editor** → paste the entire contents of `database/schema.sql` → **Run**.
   This creates every table, enum, index, trigger, and seeds a default
   `ADMIN001` super-admin account plus default church settings.
3. Copy your **Project Settings → Database → Connection string (URI)** —
   you'll need it for the backend `.env`.

### 3.3 Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL to your Supabase connection string,
# and set JWT_SECRET_KEY to a long random string.

# Optional but recommended: run Alembic migrations instead of / in addition
# to schema.sql if you prefer migration-driven schema management:
alembic upgrade head

uvicorn app.main:app --reload --port 8001
```
API docs are then available at `http://localhost:8001/api/docs` (Swagger)
and `http://localhost:8001/api/redoc`.

### 3.4 Frontend setup
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Visit `http://localhost:5173`. The Vite dev server proxies `/api` to
`http://localhost:8001` automatically (see `vite.config.ts`).

### 3.5 First login
Use the seeded super admin to get in and start adding real members:
```
User ID: ADMIN001
```
(No password — this app is User-ID-only login by design.) From the
Admin Panel → Members, add your real church members, or use
**CSV Import** with the sample files in `sample-csv/`.

---

## 4. Environment Variables

### Backend (`backend/.env`)
| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase Postgres connection string |
| `JWT_SECRET_KEY` | Long random secret used to sign JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default 7 days, so members stay logged in |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | Only needed if you extend the app to use Supabase Storage/Auth directly |
| `CORS_ORIGINS` | JSON array of allowed frontend origins |

### Frontend (`frontend/.env`)
| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Defaults to `/api/v1` (proxied in dev) |

---

## 5. CSV Import Guide

Admin Panel → **CSV Import**. The wizard is a two-step flow:

1. **Preview** — upload the file; the backend parses it with pandas,
   validates every row (missing required fields, invalid roles/dates,
   references to users/plan-days that don't exist yet), and returns a
   row-by-row preview with a short-lived `import_token` (30 min TTL).
2. **Confirm** — re-sends the `import_token`; the backend runs the actual
   insert/update inside a DB transaction. If anything throws mid-import,
   the whole transaction rolls back and the import is logged as
   `rolled_back` in **Import History**.

### Required columns

| File | Required columns | Notes |
|---|---|---|
| `users.csv` | `user_id`, `name` | Optional: `role`, `phone`, `joined_date`. Existing `user_id` → updated, not duplicated. |
| `reading_plan.csv` | `day`, `date` | Optional: `old_testament`, `new_testament`, `estimated_minutes`. |
| `progress.csv` | `user_id`, `day` | Optional: `completed` (true/false), `completed_date`. Requires the referenced user and plan day to already exist — import `users.csv` and `reading_plan.csv` first. |

After every `progress.csv` import, streaks/longest-streak/completion % are
**automatically recalculated** for every affected member — no manual
recompute step needed.

Sample files to try immediately are in `sample-csv/`.

---

## 6. The Streak / Progress Engine

All of a member's stats (`current_streak`, `longest_streak`,
`days_completed`, OT/NT breakdown, `overall_percentage`) are derived purely
from their `reading_progress` rows joined against `reading_plan`, recomputed
by `ProgressService.recalculate_stats()`:

- **Longest streak** — the longest run of consecutive completed day-numbers
  across the whole plan.
- **Current streak** — counts backwards from today's day-number (or from
  yesterday's, if today isn't marked complete yet) for as long as each day
  was completed.

This is triggered after every **Mark as Completed** action and after every
**progress.csv** import, so numbers are always in sync — there's no
separate "recalculate" button needed.

Unit tests for this logic (including the streak-broken-by-a-missed-day
case) are in `backend/tests/test_progress_service.py`.

---

## 7. Deployment

### Docker Compose (both services)
```bash
docker compose up --build
```
This builds and runs `backend` (port 8000) and `frontend` (port 5173,
served via nginx which proxies `/api` to the backend container). Point
`backend/.env`'s `DATABASE_URL` at Supabase — there's no local Postgres
container, since Supabase **is** the database.

### Separately
- **Backend**: any host that runs a Python ASGI app (Render, Railway, Fly.io,
  a VM behind nginx, etc). Run `alembic upgrade head` once, then
  `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- **Frontend**: `npm run build` produces `dist/` — deploy as a static site
  (Vercel, Netlify, Cloudflare Pages) or behind the included nginx config.
  It's PWA-ready (`vite-plugin-pwa`), so it can be "installed" to a phone's
  home screen.

---

## 8. Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401 Unauthorized` on every request | Access token expired and refresh token missing/expired — log in again. |
| Login says "User ID not found" | The `user_id` must match exactly what's in the `users` table (case-insensitive); add the member first via Admin → Members or CSV import. |
| CSV import preview shows all rows invalid | Check the column headers match exactly (case-insensitive, spaces become underscores) — see the required columns table above. |
| `psycopg2` connection errors | Double-check `DATABASE_URL`'s password/host from Supabase — it's easy to copy the pooler URL by mistake; use the direct connection URI for migrations. |
| Streaks look wrong after a bulk import | Recalculation only runs for users referenced in the `progress.csv` you just imported — if you edited `reading_plan.csv` afterward with new dates, re-import `progress.csv` (upsert is safe, it won't duplicate) to force a recalculation. |

---

## 9. Roadmap / Future Extensibility

The architecture (service layer + repository layer + typed DTOs) was built
so these can be added without a rewrite:
- Push notifications (Firebase/OneSignal) — hook into `mark_today_completed`
  and `AnnouncementService.create`.
- Attendance, Events, Prayer Requests, Church Groups, Donations — new
  `models/`, `schemas/`, `services/`, `api/v1/` modules following the same
  pattern as `announcements`.
- Multi-church support — add a `church_id` FK to `users`/`reading_plan` and
  scope repository queries by it.

---

## 10. What's implemented vs. what's a starting point

Fully implemented and working end-to-end: User-ID login + JWT refresh,
Home (today's reading with a real **Read Now** flow into the Bible
text, manual mark-completed fallback, streak, top 5, verse of the day,
announcements), the **Reading screen** (distraction-free, dark mode,
font size, tap-a-verse to highlight or add a note, prev/next chapter),
the **Quiz screen** (retry-friendly, 70% pass threshold, wrong-answer
verse hints, auto-marks the day complete on pass), Progress (stats,
heatmap, monthly chart, achievement badges), Community (leaderboard,
announcements, today's-readers count), Profile, and the full Admin
panel (dashboard, members CRUD, reading-plan CRUD, **Plan Generator**
that auto-distributes chapters across a chosen duration/rest-day
pattern, announcements CRUD, CSV import wizard with preview/rollback/
history, member reports + Excel export, settings) — including a phone-
width nav drawer for Admin, not just tablet/desktop.

Bible content is blocked pending reviewed rights and source QA. The machine
inventory at `licensing/translations.json` records the requested editions as
pending. The existing database labels alone do not grant content access.

Intentionally left as a documented starting point rather than built out
further in this pass: quiz questions only exist for 3 sample chapters
(Genesis 1, Psalm 23, John 3) — a pastor/admin needs to author the rest
(there's no admin UI for writing quiz questions yet, only direct DB
inserts matching the `quiz_question` table shape); family/children-
specific reading views and multi-language UI switching are not built;
and a full automated test suite for every endpoint
(a representative set covering the trickiest logic — streaks and CSV
validation — is included), Firebase/OneSignal push wiring, and true
offline-first PWA background sync. The service-layer architecture makes
all three straightforward to add without touching existing code.

---

## 11. Bible content licensing and validation

See [the licensing matrix](docs/rooted/07-bible-licensing.md) and
[canonical data schema](docs/rooted/08-bible-data-schema.md).
Both catalog and direct book/chapter/navigation lookup require an active,
reviewed registry approval as well as the database visibility classification.
All supplied registry records are pending, including legacy KJV.

The current guard supports only reviewed worldwide, unlimited-user, stored-text
web use. Restricted territories, API metering, native distribution and licensed
offline support need their own enforcement before release. A missing or malformed
registry denies access. Container deployments must make the reviewed registry
available at the configured path; no approvals are included in this repository.

Validate a local canonical package against an independently approved source
manifest (this neither downloads text nor writes to the database):

```bash
cd backend
venv/bin/python scripts/validate_bible.py /path/to/dataset.json /path/to/manifest.json
DEBUG=false venv/bin/python -m pytest tests -q
```

The report includes checksum and structural counts, never verse text. Passing
structural validation is not content QA or a license. Release readiness remains
false until written scope, manifest provenance and human language review are
verified. Keep signed agreements and licensed source files outside public Git.

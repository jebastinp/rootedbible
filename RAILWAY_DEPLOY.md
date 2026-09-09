# Deploying Rooted to Railway

This repo supports either a single Railway service or two independently deployable services.

## Single-service deployment (recommended for a simple Railway setup)

Create one Railway service from `jebastinp/rootedbible` with the repository root as its
Root Directory. Railway will use the root `Dockerfile`, which builds the React frontend,
runs the FastAPI backend, and serves both through Nginx on Railway's `$PORT`.

Set these Variables on the service:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`
- `CORS_ORIGINS` containing the generated Railway domain, for example
   `["https://rootedbible-production.up.railway.app"]`
- `APP_ENV=production` and `DEBUG=false`

For the frontend build, set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to the same
public Supabase URL and anon key. Leave `VITE_API_BASE_URL` unset (or set it to
`/api/v1`); the combined image proxies that path to the local FastAPI process.

Generate one public domain under **Networking** and use that domain for `CORS_ORIGINS`.

## Two-service deployment

If you prefer independent scaling, use the setup below:

- `backend/` - FastAPI, `Dockerfile` present. Listens on `$PORT`, runs `alembic upgrade head` on every start.
- `frontend/` - React/Vite, built to static files and served by nginx, `Dockerfile` present. Listens on `$PORT`.

Railway needs **two separate services** in the same project, both pointed at this GitHub repo with a different **Root Directory** each. There is no single-click monorepo deploy - do the following once in the Railway dashboard.

## 1. Backend service

1. Railway dashboard -> New Project -> Deploy from GitHub repo -> select `jebastinp/rootedbible`.
2. In the new service's **Settings -> Source**, set **Root Directory** to `backend`. Railway will detect the `Dockerfile` automatically.
3. **Settings -> Networking** -> Generate a public domain (e.g. `rooted-backend-production.up.railway.app`). Railway injects `PORT` automatically - the Dockerfile already binds to it.
4. **Variables** - add everything from `backend/.env.example` with real values:
   - `JWT_SECRET_KEY` - generate a new long random string (do **not** reuse the example placeholder)
   - `SUPABASE_JWT_SECRET`
   - `DATABASE_URL` - your Supabase Postgres connection string
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
   - `CORS_ORIGINS` - JSON array containing your frontend's Railway domain once you have it, e.g. `["https://rooted-frontend-production.up.railway.app"]`
   - `APP_ENV=production`, `DEBUG=false`
5. Deploy. Watch the build logs - `alembic upgrade head` runs before the server starts, so the first deploy also creates the schema. Confirm `GET /api/health` returns 200 on the public domain.

## 2. Frontend service

1. Same project -> New Service -> GitHub repo -> same repo again.
2. **Settings -> Source** -> Root Directory: `frontend`.
3. **Settings -> Build** -> add a build argument (Railway calls these "Build-time variables" under the Dockerfile build settings, or set them as regular service Variables - Railway passes service Variables through as Docker build args automatically):
   - `VITE_API_BASE_URL=https://<your-backend-domain>/api/v1` (the backend domain from step 1.3, **with** `/api/v1`)
   - `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` - same values as the backend's Supabase project
4. **Settings -> Networking** -> Generate a public domain.
5. Deploy. Once live, go back to the **backend** service and update `CORS_ORIGINS` to include this frontend domain, then redeploy the backend.

## 3. Supabase Auth redirect URLs

In Supabase Dashboard -> Authentication -> URL Configuration, add the frontend's Railway domain to **Redirect URLs** (e.g. `https://rooted-frontend-production.up.railway.app/auth/callback`), or Google sign-in / email verification links will bounce.

## Notes

- The `bible/` directory (licensed Bible XML source files) is intentionally excluded from git via `.gitignore` and is **not** pushed to GitHub. If you need it on the backend service for `scripts/import_bible_xml.py`, upload it separately (Railway volume, or run the import once against the Supabase DB from your machine) - never commit it to a public repo.
- Local `docker compose up` still works unchanged - both Dockerfiles default `PORT` to their original local ports (`8000` backend, `80` frontend) when Railway's `$PORT` isn't present.
- Rotate `JWT_SECRET_KEY` and any Supabase keys that were ever committed to `.env` files before this repo was pushed - check `git log` if in doubt.

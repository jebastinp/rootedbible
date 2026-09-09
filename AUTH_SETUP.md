# Rooted Authentication Setup

Rooted's authentication is handled by **Supabase Auth**. The backend never sees a
Google password or a Rooted password directly — it only verifies the session
token Supabase issues once *it* has finished authenticating the user (via
Google OAuth, or via email + password with Supabase's own email verification).

Two sign-in methods are supported, and a user can use either (or both, if the
emails match — see "Account linking" below):

- **Google** — `supabase.auth.signInWithOAuth({ provider: 'google' })`
- **Email + password** — `supabase.auth.signUp` / `signInWithPassword`, with
  Supabase's built-in email confirmation flow

## How it fits together

```
Frontend (supabase-js)              Backend (FastAPI)
─────────────────────               ─────────────────
signInWithOAuth('google')  ──►  Google  ──►  Supabase  ──►  redirects to
                                                             /auth/callback
                                                             with a Supabase
                                                             session in the URL
                                                                    │
signUp() / signInWithPassword()  ──►  Supabase  ──►  session (or a
                                        confirmation email first)
                                                                    │
                                                                    ▼
                            POST /auth/supabase { access_token }
                                                                    │
                                                                    ▼
                    Backend verifies the token's signature against
                    SUPABASE_JWT_SECRET, finds/creates the Rooted user,
                    issues Rooted's own access + refresh JWT
                                                                    │
                                                                    ▼
                         Frontend stores the Rooted JWT and discards
                         the Supabase session (supabase.auth.signOut())
```

From that point on, every API call uses Rooted's own JWT (`Authorization:
Bearer ...`), exactly as before — Supabase is only involved during the
sign-in moment itself.

## Required setup (do this once per environment)

### 1. Google Cloud Console

1. Create (or reuse) an OAuth 2.0 Client ID of type **Web application**.
2. Under **Authorized redirect URIs**, add your Supabase project's auth
   callback:
   ```
   https://YOUR_PROJECT.supabase.co/auth/v1/callback
   ```
3. Note the **Client ID** and **Client Secret** — these go into Supabase, not
   into Rooted's own `.env` files.

### 2. Supabase Dashboard

- **Authentication → Providers → Google**: enable it, paste the Client ID and
  Client Secret from step 1.
- **Authentication → URL Configuration**: add your app's origins to the
  allow-list so redirects are accepted, e.g.:
  - `http://localhost:5173` (local dev)
  - `https://app.yourchurch.org` (production)
- **Authentication → Providers → Email**: leave "Confirm email" **on** for
  production (Rooted's UI assumes email confirmation is required — the
  verify-email screen and cooldown timer only matter when this is on; if it's
  off, sign-up completes immediately instead, which the code also handles).
- **Project Settings → API → JWT Settings → JWT Secret**: copy this value —
  it's the one real secret this integration needs (only used as a fallback,
  see the note below).

> **Two verification modes, handled automatically.** Newer Supabase projects
> (and any project with "JWT Signing Keys" enabled) sign session tokens with
> an asymmetric key (ES256) and publish the public half at
> `/auth/v1/.well-known/jwks.json` — the backend fetches and verifies against
> that automatically, and `SUPABASE_JWT_SECRET` isn't actually used for these
> projects. Older projects sign with a single shared secret (HS256) — that's
> what `SUPABASE_JWT_SECRET` is for. `app/core/supabase_auth.py` reads the
> token's own header to pick the right verification path, so nothing needs to
> be configured differently either way — just set `SUPABASE_JWT_SECRET`
> regardless of which kind of project you have, and it's used only if needed.

### 3. Environment variables

**Backend** (`backend/.env`, never commit real values):
```
SUPABASE_JWT_SECRET=<the JWT Secret from Supabase Project Settings -> API>
```

**Frontend** (`frontend/.env`, safe to expose client-side by design):
```
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=<the anon/public key from Supabase Project Settings -> API>
```

The anon key and project URL are public identifiers, not secrets — Supabase
is designed so the anon key alone can't do anything sensitive. The **JWT
Secret** is the only value that must stay server-side.

### 4. Database migration

Run the latest migrations so the `users` table has the columns this
integration needs (`supabase_user_id`, `email`, `auth_provider`,
`last_login_at`):
```bash
cd backend && alembic upgrade head
```

## Routes

| Route | Purpose |
|---|---|
| `/login` | Landing screen: Google, or continue with email |
| `/signup` | Create an account (name, email, password) |
| `/signin` | Sign in with email + password (or Google) |
| `/forgot-password` | Request a password reset email |
| `/reset-password` | Set a new password (opened from the reset email link) |
| `/verify-email` | Shown after sign-up if email confirmation is required |
| `/auth/callback` | Landing point for both the Google redirect and the email confirmation link |
| `/onboarding` | One-time welcome screen for brand-new accounts |
| `/staff-login` | Legacy User-ID login, unlinked from any nav — admin/manager fallback only |

## Account linking

If someone signs up with email/password and later uses "Continue with
Google" with the *same* email (or vice versa), the backend links them to the
same Rooted account by email rather than creating a duplicate — see
`AuthService.login_with_supabase` in `backend/app/services/auth_service.py`.

## What's intentionally not built yet

- Preferred language / Bible translation selection isn't part of onboarding
  yet, because no translation is actually licensed and seeded in the database
  beyond the placeholder catalog rows (see `licensing/README.md`) — showing a
  picker with translations that don't have real text would be misleading.
- `church_id` / `family_id` aren't on the `users` table yet, since the
  church/family data model doesn't exist in this codebase yet. Add them when
  that feature is actually built, rather than as unused speculative columns
  now.

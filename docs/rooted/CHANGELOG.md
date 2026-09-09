# Changelog

## 0.1 foundation work — 2026-09-08

- Added all 16 required foundation artifacts and preserved the source brief.
- Recorded owner request for individual sign-in alongside church accounts. Secure identity implementation remains planned, not delivered.
- Recorded all requested languages; no written permissions or source packages supplied.
- Added a pending-only edition registry and conservative catalog/direct-lookup controls.
- Retired automatic KJV download/import; no translation substitution or real-content import performed.
- Added canonical JSON/manifest structural validation with strict UTF-8, duplicate and Unicode checks, source hashes and synthetic multilingual regression tests.
- Removed raw errors from startup/render fallback UI; restored browser zoom in viewport metadata.

Validation: 63 backend tests passed, including synthetic content and rights-access tests. Frontend production build passed (existing large-bundle warning remains). The validator CLI passed a synthetic multilingual package and explicitly returned release_ready=false; the legacy importer exited before any download. All 16 artifact links were checked. No real-dataset, native-device, accessibility audit, identity-provider, database migration or production release approval is claimed.

Known issues: secure individual/church identity not implemented; current member-code auth is prototype-only; production database/identity configuration remains unresolved; no licensed dataset; canonical schema not migrated into runtime storage; legacy plan-day metrics and quiz/social UI differ from the new brief. See the backlog and launch checklist before adding or releasing features.

## Local database setup — 2026-09-08

Created dedicated local PostgreSQL database `rooted_webapp_1`, initialized its 15 tables, configured `backend/.env`, and generated a fresh local JWT signing secret. Existing databases were not changed. The local admin seed is available; no Scripture dataset was imported. Login, profile, home summary and Bible catalog returned HTTP 200 through the frontend proxy. This is local development setup, not cloud deployment.

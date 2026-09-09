# Rooted product foundation

Baseline: 2026-09-08. Authority: [supplied product brief](source-brief.md).

This is a development baseline for the new reading-focused MVP. It is **not a release approval**. The existing church tracker is a prototype with materially different behavior. No Bible edition is approved by this documentation, and no store submission or rights-holder contact has occurred.

| Required artifact | Document |
|---|---|
| 1. Product requirements | [PRD](01-product-requirements.md) |
| 2. Feature backlog | [Backlog](02-feature-backlog.md) |
| 3. User flow | [Flows](03-user-flow.md) |
| 4. Information architecture | [Screen map](04-information-architecture.md) |
| 5. Design system | [Design](05-design-system.md) |
| 6. Technical architecture | [Architecture](06-technical-architecture.md) |
| 7. Bible licensing matrix | [Licensing](07-bible-licensing.md) |
| 8. Bible data schema | [Schema](08-bible-data-schema.md) |
| 9. Privacy/data map | [Data map](09-privacy-data-map.md) |
| 10. Security threat model | [Threats](10-security-threat-model.md) |
| 11. Analytics taxonomy | [Analytics](11-analytics-taxonomy.md) |
| 12. QA test matrix | [QA](12-qa-test-matrix.md) |
| 13. Risk register | [Risks](13-risk-register.md) |
| 14. Decision log | [Decisions](14-decision-log.md) |
| 15. Launch checklist | [Launch](15-launch-checklist.md) |
| 16. Post-launch roadmap | [Roadmap](16-post-launch-roadmap.md) |

## Current blockers

1. Owner confirmed individual sign-in in addition to church accounts. Use secure account-backed reading with optional church membership; identity provider and migration details need configuration. Preserve existing accounts/data.
2. Six XML sources have now been supplied and inventoried. Exact Indic editions and written grants remain unverified; no Malayalam file is present. See bible-file-inventory.md.
3. Local development now uses the dedicated PostgreSQL database `rooted_webapp_1` on this Mac. Schema initialization, admin login, profile and home APIs are verified. Production database/identity configuration and content QA remain unresolved.
4. Native signing, distribution territories, support identity, legal entity and release date are unset.

Independent work may proceed on access controls, canonical validation, tests and design specifications using synthetic fixtures. Substantial replacement screens and real-content integration follow secure identity design and licensing/source validation. Do not treat a generated document, a boolean flag, or a passing synthetic test as content approval.

## Existing-code audit

| Finding | Evidence | Consequence |
|---|---|---|
| Login required for reading | `frontend/src/App.tsx`, backend Bible routes | Conflicts with proposed first-session experience |
| KJV hard-coded | `frontend/src/lib/bible.ts` | Requested NKJV/Tamil must never silently become KJV |
| Chapters stored as newline text | `backend/app/models/bible.py` | No canonical verse IDs or source-specific versification manifest |
| Chapter lookup did not check licensing | `backend/app/repositories/bible_repository.py` | Fixed with shared pending-by-default registry and visibility checks |
| Importer downloaded text and skipped missing books | legacy `scripts/import_kjv.py` | Retired; replacement structural validator uses local synthetic/approved inputs |
| Progress measures plan days | `backend/app/services/progress_service.py` | Cannot label it whole-Bible completion |
| Quiz CTA, rankings, achievements | Reader, Home, Progress | Outside new MVP; do not migrate these into the new core loop |
| Reader font/theme reset on mount | `ReadingScreen.tsx` | Preferences and last position need persistence |
| Member code grants access | `auth_service.py` | Not suitable production authentication for private/cloud data |
| Google Fonts requests | `frontend/index.html` | Disclose current third party; prefer approved self-hosted fonts |
| API keys/config not production-ready | `.env.example`, config defaults | Release gates remain open |

Maintain these documents when decisions or implementation change. Weekly review: completed work, blockers, changed assumptions, largest risk, removed scope and next goal. An owner role is an assignment to be made, not a person already appointed.

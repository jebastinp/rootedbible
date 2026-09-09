# Bible licensing matrix and workflow

Status as of 2026-09-08: **no edition cleared for Rooted**. The machine inventory is [translations.json](../../licensing/translations.json). Null means unknown, not permission. The older `public_domain` or `licensed` database labels alone are insufficient. KJV is not an approved substitute for NKJV or the requested Tamil edition.

| Requested language / edition | Candidate rights/provider lead | Current evidence | Product status |
|---|---|---|---|
| English / NKJV | Thomas Nelson / HarperCollins Christian Publishing; API.Bible as a potential delivery provider | Public API.Bible terms identify NKJV-specific licensing conditions; no Rooted agreement | Requested; unavailable |
| Tamil / exact edition unknown | Bible Society of India Tamil auxiliary, only if that is the selected edition | Official Tamil site provides a contact; does not grant app rights | Edition + rights unresolved |
| Malayalam / exact edition unknown | Owner/provider must be identified after edition selection | None supplied | Unavailable |
| Hindi / exact edition unknown | Same | None supplied | Unavailable |
| Telugu / exact edition unknown | Same | None supplied | Unavailable |
| Legacy KJV 1769 | Legacy source not audited for this release/territory | Code comments are not evidence | Not selected; unavailable |

## Research notes, not grants

API.Bible's published terms distinguish commercial rights for particular editions and include content integrity, attribution and cache-recency conditions. A provider account or public API documentation does not establish Rooted's entitlement. Archive and review the actual applicable contract and edition terms before choosing this integration. Source: [API.Bible terms](https://api.bible/terms-and-conditions), accessed 2026-09-08.

The [BSI Tamil site](https://tamil.bible/) lists `bsitam@biblesociety.in`. This is a candidate contact for edition identification and rights inquiries, not evidence that the requested edition is theirs or that permission exists. Accessed 2026-09-08.

The [HCCP permissions endpoint](https://www.harpercollinschristian.com/sales-and-rights/permissions/) returned HTTP 403 to the research tool. Its current request process must be confirmed directly. Do not derive full-app permission from quotation allowances or third-party downloadable Bibles.

## Record fields

Every edition record includes identity/language, copyright owner, provider, license type, API availability; explicit display/mobile/commercial/offline/bundling/caching/storage/distribution/iOS/Android/marketing permissions; attribution requirements and exact notice; territories; user/API limits; validity/expiration/renewal; contact and restricted evidence location; reviewer/date; source/checksum/dataset version and QA status. Limits and unknowns cannot be encoded as unlimited.

Restricted evidence belongs outside the repository and client bundle. Store a reference and verified checksum in the approval record, not the signed contract, keys or personal contact details in public code. A reviewer must match the grant to the legal entity, edition, delivery mode, users and territories. Do not mark records approved just to make tests pass.

## Workflow and outreach draft

Owner selects exact edition → identifies holder → sends an authorized inquiry → receives written grant/source → stores restricted evidence → records scoped rights → source validation → independent content QA → release review. No outreach has been sent.

Draft inquiry for the owner to review and send: “We are developing Rooted, a Bible-reading application. Please confirm the rights holder and licensing options for [exact edition/language/year]. We request terms for full-text display on web, iOS and Android; commercial and noncommercial use; API access and limits; offline use, local storage, caching, bundling; international distribution and territories; attribution, screenshots and marketing; expected users [TBD]; fees, expiry and renewal; source format and integrity manifest. Please identify which permissions are granted and excluded in writing.”

Do not commit a new licensed dataset until the grant permits that distribution. Release review must re-check expiration, revocation, limits, notices and every platform. Revocation stops new content delivery; purge caches only as required by the grant while preserving user-owned progress references.

# Security threat model

Assets: user progress and optional legacy private data, credentials, Scripture integrity, license evidence, publishing/signing keys. Boundaries: browser ↔ local storage, browser ↔ backend, backend ↔ database/provider, importer ↔ untrusted files, CI ↔ release assets.

| Threat | Existing exposure / scenario | Required control | Verification |
|---|---|---|---|
| Identity impersonation | Member code alone creates tokens | Verified identity for individual and church accounts; never ship seeded admin login | Unauthorized/role/escalation tests |
| Direct content bypass | Known edition URL bypasses catalog filter | Central deny policy for inactive/unapproved editions and all content endpoints | Catalog + direct books/chapter/nav tests |
| Forged licensing label | DB `licensed` value without evidence | Reviewed registry plus source QA and release rights audit; no client toggle | Pending/unknown/expired/missing evidence tests |
| XSS/token theft | localStorage tokens, user content | React escaped text; no HTML insertion; CSP after required asset review; secure identity redesign | Script-like fixture renders as text |
| Data tampering/loss | Device clock, storage failure, multiple tabs | Explicit timestamps, idempotent atomic writes, export/migrations | Quota, rollback, DST, race tests |
| Secrets disclosure | Env defaults, logs, bundles | Server-only keys; fail release for defaults; no payloads/tokens in logs | Scoped secret and built-asset scan |
| Import corruption | Malformed Unicode, missing/duplicate verses | Strict offline validator, independent manifest, checksum, staged promotion | Negative synthetic fixtures |
| Provider abuse/SSRF | Arbitrary source URLs, unbounded fetching | Only approved adapters; no arbitrary fetch in importer; size/time/rate limits | Reject unknown adapters and oversized inputs |
| Content leakage via cache | PWA/React Query retains API text | Per-edition scoped cache policy; no cache by default | Offline/service-worker inspection |
| Supply-chain compromise | Dependency updates | Lockfile, reviewed upgrades, scan before release | CI report and risk disposition |
| Destructive migrations | Plan days converted to chapters | Keep old data; reversible mapping, backup and count checks | Upgrade/failure/rollback fixtures |

No security-review completion is claimed. Threat testing, dependency scans, production CSP/HTTPS and native secure storage are release gates. Keep the prototype local until identity, data and deployment choices are resolved.

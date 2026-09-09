# Launch checklist — NO-GO

No production distribution, store submission, rights contact or deployment is authorized by this checklist alone. Public launch is blocked by missing licensed datasets, product decisions and release evidence.

## Foundation and content

- [ ] Owner confirms scope/platform/account mode and design.
- [ ] Every edition has exact identity, written evidence and scoped rights.
- [ ] Commercial, API, caching, storage, offline, bundling and territory permissions checked.
- [ ] Expiry/renewal and provider user/rate limits enforced.
- [ ] Complete source manifest/checksum and independent multilingual QA passed.
- [ ] Correct attribution shown in reader/settings/store wherever required.

## Product and QA

- [ ] First reading, continue, completion, edition switch and all routes tested.
- [ ] Chapter denominator, history, streak/timezones and plan coverage verified.
- [ ] Persistence/export/delete/migrations and failed-storage recovery verified.
- [ ] Reminder permissions, time changes and cancellations work on supported platforms.
- [ ] No P0; critical P1 resolved; accessibility and performance evidence signed off.
- [ ] No debug messages, stack traces, test data/accounts or development endpoints in release.

## Security and privacy

- [ ] Secure verified auth if accounts retained; no member-code-only admin access.
- [ ] Secrets, dependencies, bundle, logs, endpoints and HTTPS reviewed.
- [ ] Privacy/data map matches actual implementation and third parties.
- [ ] Legal entity, privacy/terms/support URLs and retention/delete process confirmed.
- [ ] Analytics and crash reporting explicitly selected or declared absent; payloads reviewed.
- [ ] Backup/recovery tested for server data if retained.

## Store and operations

- [ ] App ID/name/version, signing identities, icons and device screenshots verified.
- [ ] Description/keywords/age rating/data declarations/permission explanations accurate.
- [ ] No unsubstantiated official/authorized/all-translations/privacy claims.
- [ ] License notices for Scripture, fonts and shipped software included.
- [ ] Beta feedback triaged and release notes/known issues finalized.
- [ ] Owner approves exact build/hash, distribution and rollback plan.
- [ ] Support contact, response target, content escalation and first-day monitoring assigned.

Before generating a release candidate, inspect compiled assets and licensed-data manifest. Development `npm run build` is a verification artifact, not a public release candidate. Never upload real user data, grants or private notes as test/store assets.

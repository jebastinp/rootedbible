# Privacy and data map

This describes current behavior and the proposed MVP, not a published privacy policy. Confirm legal entity, contact, jurisdictions and final architecture before publishing.

| Data | Why | Current storage/access | Proposed MVP retention and deletion |
|---|---|---|---|
| Member ID/name/phone/birthday/photo/role | Legacy church administration | Postgres; authorized app/admin routes; schema includes optional personal fields | Collect only account identity for individual users; church profile fields remain optional/justified; preserve existing records until approved migration |
| Access/refresh tokens and user snapshot | Legacy sign-in | `rooted-auth` localStorage; readable by same-origin script | Redesign verified identity and token handling; do not keep member-code authentication in production |
| Chapter history/completion/timezone | Continue and progress | Not yet canonical; legacy server stores plan-day completion | Account-scoped Postgres, user export/delete; retention policy and backups must be confirmed |
| Plan enrollment/status | Today's reading | Legacy shared schedule in Postgres | Account-scoped Postgres until delete; no telemetry of passages |
| Reader font/theme/edition | Comfortable reading | Current reader component state | Device until reset/delete |
| Reminder time/permission | Opt-in reminder | Not implemented | Device/OS; clear and cancel on disable/delete |
| Notes/highlights | Legacy reflection | Backend note/highlight routes | Deferred; do not copy into analytics or discard during migration |
| Bible text | Reading | Postgres if imported | Only locations/retention permitted by edition grant |
| Font network requests | Current typography | Browser requests Google Fonts; provider receives request metadata | Prefer self-hosted approved fonts; until then disclose accurately |
| Server logs/IP/path/errors | Operation/security | Hosting/console; existing logging includes exception context | Minimize and redact; provisional seven-day operational retention subject to host config |
| Analytics | None necessary for local MVP | No new SDK introduced | Off; taxonomy is a design only |
| License agreements | Establish content rights | None supplied | Restricted owner storage; not client/public Git; retain per contract/legal policy |

Local data can be accessed by people/scripts with access to that browser profile. Do not describe it as encrypted or backed up unless implemented. Browser data clearing may remove progress; explain export and recovery truthfully. Device-only state is not automatically synchronized.

Delete flow must list actual affected data, request confirmation, cancel reminders, remove owned keys/stores only, and verify reload is empty. Do not clear unrelated origin storage, legacy accounts or server records without a selected scope. Cloud deletion needs server authorization, documented backup retention and verification.

No reading text, notes, raw search history or member identifiers in diagnostics/analytics. Error reports require redaction and user consent if manually shared. Formal privacy-request channel, response target and retention policy remain owner decisions.

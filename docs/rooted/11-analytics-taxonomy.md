# Analytics event taxonomy

Decision proposal: **no analytics collection in MVP by default**. This is a future opt-in contract, not an instruction to install a tracker. Aggregate product research can begin with consented beta interviews and local benchmark scripts.

| Event | Meaning | Allowed candidate fields |
|---|---|---|
| app_open | App became usable, once per session | app version, coarse platform |
| onboarding_complete | Required preferences saved | app version, duration bucket |
| chapter_open | Chapter successfully displayed | load latency bucket, local/API mode |
| chapter_complete | Completion committed | app version; no reference/text |
| plan_started | Enrollment saved | approved catalog plan ID/version |
| plan_day_complete | Assigned units committed | plan ID/version; no passages |
| plan_completed | All required days complete | plan ID/version, duration bucket |
| reminder_enabled | OS-supported schedule succeeded | coarse platform; no exact local time |
| error | Classified operation failed | allowlisted error code, app version; no raw exception |

Never include Bible text, notes, member IDs, tokens, raw URLs, raw search, exact timestamps with location, or sensitive free text. Search is deferred, so `search_used` is not collected. Language/translation preferences can reveal religious behavior and are omitted unless a separately reviewed question justifies collection.

D1/D7/D30 retention needs a longitudinal identifier; do not claim it can be measured anonymously without design work. Before activation: consent model, identifier/retention design, vendor/data residency, payload inspection, deletion/opt-out and accurate policy. Proposed raw-event retention ≤30 days, subject to owner/privacy review. No claims about active readers, retention or crash-free rate before actual measurement.

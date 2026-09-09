# Information architecture

Primary navigation: Home, Bible, Progress, Plans, Settings. Reader is outside the tab shell. Testament, book and chapter selection are coordinated panels in Bible, avoiding three mandatory navigation screens.

| Screen / proposed route | Content and key states |
|---|---|
| Splash | Static startup fallback, timeout recovery; no indefinite logo |
| Individual sign-in `/sign-in` and registration `/sign-up` | Verified identity, confirmation, reset/recovery; no admin role self-assignment |
| Church entry `/church` | Verified identity plus authorized membership/invitation |
| Onboarding `/welcome` | Language → approved edition → optional plan/reminder |
| Home `/` | Today card, continue location, modest chapter progress; no ranks |
| Bible `/bible` | Translation, OT/NT tabs, books, chapter grid, available/empty/error |
| Reader `/bible/:translation/:book/:chapter` | Verses, attribution, appearance, prev/next and completion |
| Today `/today` | Active plan day and individual passage statuses |
| Progress `/progress` | Dataset denominator, OT/NT, current/longest streak, plan summary |
| History `/progress/history` | Date, translation, reference; re-read and undo |
| Plans `/plans` | Coverage, duration, compatibility, startable/unavailable states |
| Plan details `/plans/:id` | Description, day preview, difficulty, duration, start |
| Active plan `/plans/active` | Completed/remaining days, current passages, pause/resume |
| Settings `/settings` | Reading, reminder, data, legal, about |
| Reading settings `/settings/reading` | Font size, spacing, theme, preview |
| Translation `/settings/translations` | Approved editions only, language and attribution |
| Notifications `/settings/reminders` | Enable, time, timezone, OS permission/delivery status |
| About `/about` | Actual version, credits, support contact |
| Privacy `/legal/privacy` | Actual data practices and deletion instructions |
| Terms `/legal/terms` | Owner-approved terms; not generated legal advice |
| Bible attribution `/legal/bible` | Exact active edition notice and permitted-use details |
| Software licenses `/legal/software` | Shipped dependency and font notices |

Legacy `/login`, `/admin`, `/community`, `/profile`, `/read` and `/quiz` remain existing routes pending migration. Do not silently reinterpret old links, auth state or statistics as the new architecture. Link migration needs redirects and tests after product decision.

All primary screens require loading, content, empty and error states. Route titles and focus changes must be announced; back navigation restores scroll. Unknown routes offer Home/Bible without infinite redirects.

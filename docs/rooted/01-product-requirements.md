# Product requirements — internal MVP 0.1

## Outcome and audience

Rooted helps first-time and regular Bible readers open Scripture, complete a chapter, understand progress and return at their own pace. The core loop is Home → Today/Continue → Scripture → Mark chapter complete → Progress. Scripture accuracy and permission precede feature breadth.

## Scope

MVP: approved translation selection; OT/NT book and chapter browser; verse reader; previous/next chapter; last position; chapter completion/history; translation-specific Bible/OT/NT percentages; gentle current/longest streak; one active plan; catalog/details/today/plan progress; persisted reading settings; optional reminders when supported; privacy, terms, about and exact attribution.

Deferred: quizzes, competition, achievements, leaderboards, community, notes, highlights, search, bookmarks, audio, AI, advanced multi-device sync and multi-plan support. Individual sign-in plus church accounts are now explicitly requested; secure authentication is MVP. Existing legacy features are not acceptance evidence for the new MVP and will not be deleted before migration decisions.

## Acceptance criteria

| ID | Requirement | Measurable acceptance |
|---|---|---|
| MVP-01 | Fast first reading | With approved content installed, a new user reaches a chapter within three decisions; individual or church sign-in is clear and requires only necessary credentials |
| MVP-02 | Accurate reader | Every verse equals approved source; numbers/omissions follow source manifest; exact attribution visible |
| MVP-03 | Honest availability | No approved dataset produces an explanatory empty state; never a substituted translation |
| MVP-04 | Completion | Explicit button, repeat-safe chapter completion; no quiz, scrolling or timer requirement |
| MVP-05 | Progress | Unique completed chapter IDs divided by selected validated dataset chapter count; zero denominator displays unavailable |
| MVP-06 | Switching editions | Selected edition has separate progress; switching back restores its state; no implicit cross-edition credit |
| MVP-07 | Continue | Reopening restores translation/book/chapter and verse anchor; unavailable content offers translation selection |
| MVP-08 | Plans | One active enrollment; validated references; completing all assigned chapters completes a day; no skipped-day guilt |
| MVP-09 | Settings | Font/spacing/appearance survive reload; 200% zoom and keyboard navigation usable |
| MVP-10 | Reliability | Loading, no content, failed storage, offline and error states have a clear recovery action |
| MVP-11 | Privacy | No analytics SDK by default; data export/delete behavior tested for selected architecture |
| MVP-12 | Reminders | Off by default; ask permission only after user enables; denied/unsupported delivery explained |

## Progress and streak rules

A qualifying reading unit is an explicit completion of a chapter in the selected approved dataset. A chapter counts once toward completion. Re-reading on a later day may record another history event and qualify that day for a streak; repeated completion on the same date is idempotent. Undo removes the chosen event and recomputes chapter/day aggregates.

Streak: at least one chapter completion on consecutive calendar dates in the user's saved IANA reading timezone. Current streak ends today or yesterday; otherwise zero. Longest streak is independent of the current date. Multiple chapters on one date count as one day; missing a day breaks continuity, with no grace mechanic. Store UTC timestamp plus timezone and derived local date at event creation. Travel does not rewrite history: a deliberate timezone change applies only to future events. No backdating UI or rewards; local device time is not tamper-proof. Account-backed implementation uses server timestamps. Detect obvious clock rollback and explain inconsistent dates without inventing history.

Plan progress is distinct from Bible progress. Completing a plan is not completing the Bible. Pre-enrollment reading does not auto-complete a new plan. Partial days remain partial; plan days do not advance merely because calendar time passed. Pausing preserves progress; switching translation requires explicit restart or compatible new enrollment, preserving the old one.

## Nonfunctional targets, not measured claims

Provisional budgets: interactive shell within 2 seconds on a representative mid-range device; local chapter open under 200 ms p95; API chapter under 2 seconds p95 on a defined test network; no content upload or telemetry of reading text. Test Safari/Chrome and native iOS/Android separately. Release targets and minimum OS versions need owner confirmation.

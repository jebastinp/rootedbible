# Risk register

Scoring: probability 1–5 × impact 1–5. Estimates for prioritization, not measured probabilities. Owners are roles pending assignment. Review weekly and whenever a trigger occurs.

| ID | Risk | P | I | Score | Mitigation | Owner | Trigger | Status |
|---|---|---|---|---|---|---|---|---|
| R01 | Bible licensing unavailable | 5 | 5 | 25 | No-content state; no substitution; early exact-edition inquiry | Rights | No grant/source | Open |
| R02 | Incorrect copyright assumption | 4 | 5 | 20 | Evidence and territory review; disable automatic KJV importer | Rights | Only code flag/comment | Open |
| R03 | API restrictions | 4 | 5 | 20 | Scoped provider adapter and contract review | Engineering | API delivery selected | Open |
| R04 | Offline restrictions | 4 | 5 | 20 | No caching/bundling until permission | Rights | Offline requested | Open |
| R05 | Content corruption | 3 | 5 | 15 | Strict manifest/checksum and human QA | Content QA | New import | Open |
| R06 | Unicode/shaping defects | 3 | 5 | 15 | Script fixtures and native-speaker devices | Language QA | New language/font | Open |
| R07 | Wrong translation/edition | 4 | 5 | 20 | Exact edition selection, immutable IDs | Product | Ambiguous Tamil name | Open |
| R08 | Scope creep | 5 | 4 | 20 | Chapter loop and explicit deferred list | Product | Quiz/social requests | Open |
| R09 | Poor runtime performance | 3 | 4 | 12 | Chapter chunks, lazy routes, device budgets | Engineering | p95 budget exceeded | Open |
| R10 | Search performance | 2 | 3 | 6 | Defer; benchmark index later | Engineering | Search approved | Deferred |
| R11 | Privacy leakage | 3 | 5 | 15 | Data map, no analytics by default, logs review | Privacy | Cloud/vendor addition | Open |
| R12 | Insecure authentication | 5 | 5 | 25 | Decide local mode or replace member-code auth | Security | Public deployment | Open |
| R13 | Store rejection | 3 | 4 | 12 | Signing, rights, metadata and policy review | Release | Store preparation | Open |
| R14 | Reminder permission/delivery | 4 | 3 | 12 | Honest supported/denied states | Engineering | Native/web target chosen | Open |
| R15 | Low retention | 3 | 3 | 9 | Consented beta observation, simplify first reading | Product | Beta friction | Open |
| R16 | Streak dissatisfaction | 3 | 3 | 9 | Explicit local-day rules, neutral wording, no ranks | Design | User confusion | Open |
| R17 | Sync conflicts | 3 | 4 | 12 | Defer sync; idempotent events if chosen | Engineering | Cloud approved | Deferred |
| R18 | Infrastructure cost | 3 | 4 | 12 | Usage forecast and license/API budget | Product | Provider quote | Open |
| R19 | Dependency/provider failure | 3 | 4 | 12 | Lockfiles, timeouts, graceful state, audit | Engineering | Failed build/API | Open |
| R20 | Poor accessibility | 3 | 5 | 15 | Screen-reader and large-text gates | Accessibility QA | Device tests fail | Open |
| R21 | Legacy progress loss | 3 | 5 | 15 | Preserve; no day-to-chapter inference | Engineering | Schema change | Open |
| R22 | Production database setup | 3 | 4 | 12 | Dedicated local database verified; configure production separately | Owner | Deployment planned | Open; local resolved |

Top release blockers: R01/R02/R07/R12. None are resolved by a polished screen or successful compilation.

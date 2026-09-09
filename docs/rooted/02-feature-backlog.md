# Feature backlog

All tasks: baseline 2026-09-08; due date **uncommitted**, start date **unassigned** unless listed below. Owner names must be assigned before scheduling. Priority Critical = release gate, High = core MVP, Medium = follow-up quality. Review is not Done; product approval and QA evidence are required. Dependencies define execution order.

| ID | Task / workstream / area | Deliverable and acceptance | Priority | Status | Owner role | Dependencies | Risk / notes |
|---|---|---|---|---|---|---|---|
| F01 | Foundation / product | 16 linked artifacts, traceable decisions and gap audit | Critical | Review | Product + engineering | brief | Created 2026-09-08; owner approval pending |
| F02 | Architecture / identity | Individual + church account design, identity provider, platforms and territories | Critical | Blocked | Product | provider/platform configuration | Account scope confirmed; preserve legacy data |
| L01 | Rights / editions | Exact editions, rights grants and approved sources | Critical | Blocked | Rights owner | source/evidence from owner | No grant supplied |
| L02 | Rights / controls | Same deny policy for catalog and direct content access | Critical | Review | Engineering | F01 | Implemented 2026-09-08; regression tests; does not establish rights |
| C01 | Content / schema | Canonical verse schema and strict synthetic validator | Critical | Review | Engineering | F01 | Implemented 2026-09-08; synthetic tests pass; no real Scripture import |
| C02 | Content / QA | Compare full source manifests, multilingual samples and attribution | Critical | Blocked | Content QA | L01, C01 | Source-specific omitted verses required |
| D01 | Design / flows | Six main screens and all states reviewed | High | Planned | Design | F02 | Design specs exist; visual approval pending |
| E01 | Reader / navigation | OT/NT/book/chapter and translation selector, last position | High | Planned | Engineering | D01, C02 | No hidden KJV fallback |
| E02 | Reading / progress | Repeat-safe chapter history and timezone rules with tests | High | Planned | Engineering | F02, C01 | Preserve legacy plan data separately |
| E03 | Plans / engine | One enrollment, validated references, pause/resume/completion | High | Planned | Engineering | E02, C02 | Coverage and passage counts checked |
| E04 | Settings / persistence | Font, spacing, theme, language, export/delete | High | Planned | Engineering | F02, D01 | Storage failure and migration tests |
| E05 | Notifications / platform | Opt-in scheduling, denial and cancellation verified | High | Blocked | Engineering | F02 | Web/native delivery differs |
| E06 | UI / localization | Keys, language metadata, shaping/font tests | High | Planned | Engineering + language QA | D01, L01 | Do not machine-substitute Bible text |
| S01 | Security / release | Replace member-code auth if retained, secret/dependency review | Critical | Planned | Security | F02 | Existing auth not production-ready |
| P01 | Privacy / legal | Accurate policies, contact, deletion and retention | Critical | Blocked | Product + legal | F02, entity/contact | No fictional privacy claims |
| Q01 | QA / device | Automated flows + manual accessibility/performance evidence | Critical | Planned | QA | E01–E06 | No physical-device results yet |
| R01 | Release / beta | Signed build, validated content, beta feedback, go/no-go | Critical | Blocked | Release owner | L01, C02, S01, P01, Q01 | No release date assigned |
| X01 | Expansion / features | Evaluate bookmarks/search/notes after retention review | Medium | Deferred | Product | stable release | Do not delay MVP |

Each implementation PR must link an ID, actual start/finish dates, reviewer, test result, remaining risk and migration notes. Split these epics into independently testable tasks after F02/L01; do not invent delivery dates before scope and rights are known.

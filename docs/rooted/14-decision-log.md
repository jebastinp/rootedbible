# Decision log

Date: 2026-09-08. Accepted below means required by the supplied brief or a reversible engineering baseline, not product sign-off on a release. Pending owner choices are not inferred from silence.

| ID | Topic | Decision / proposal | Status | Reason / next evidence |
|---|---|---|---|---|
| D01 | MVP scope | Scripture, chapters, progress, one plan, settings; no rankings/quizzes | Accepted brief | Core loop |
| D02 | Platforms | Retain web/PWA + existing Capacitor foundation; native launch priority/minimum OS TBD | Proposed | Reuse repository; owner must confirm |
| D03 | Editions | NKJV requested; exact Tamil plus Malayalam/Hindi/Telugu unresolved | Blocked | Need editions, grants and source |
| D04 | Ownership | Do not assign rights owner from language alone | Accepted | Exact edition evidence |
| D05 | API/bundle | Per-edition adapter selected only from granted scope | Pending | Contract decides capabilities |
| D06 | Offline | No assumption; only granted installed content | Accepted | Offline tests after L01 |
| D07 | Accounts/sync | Individual sign-in plus church accounts; secure shared identity and optional church membership | Confirmed owner | User: “individual sign-in also”; provider/configuration pending |
| D08 | Read unit | Explicit chapter completion, no quiz requirement | Accepted | Tests per PRD |
| D09 | Denominator | Selected approved dataset chapter count, OT/NT subsets | Accepted | Source manifest |
| D10 | Translation switching | Independent completion by edition/versification | Accepted baseline | No silent credit transfer |
| D11 | Streak | Saved IANA timezone, immutable event local dates, today/yesterday continuity | Accepted baseline | No rewards/clock-proof claims |
| D12 | Launch plans | Propose Proverbs 31 days, Gospels 30 days, NT 90 days; only after reference QA | Proposed | Catalog not published |
| D13 | Analytics | None by default | Proposed | Taxonomy future only |
| D14 | Third parties | Existing toolchain retained; new Bible/notification/analytics providers unselected | Pending | Contracts/platform choice |
| D15 | Privacy | Minimum account data; account-scoped progress and accurate service disclosure | Accepted direction | Final policy after D07 |
| D16 | Support | Owner supplies contact; propose triage within two business days, content issues urgent | Pending owner | No service promise published |
| D17 | Launch date | Unset; gated by rights, content, QA and owner approval | Pending | No fabricated schedule |
| D18 | Device support | Safari/Chrome + selected native devices; actual OS matrix TBD | Pending | Owner/device availability |
| D19 | Roadmap | Stabilize → beta → store → 24h/7d/30d reviews → justified expansion | Accepted brief | No premature expansion |
| D20 | Source control | Create project-scoped repo before CI/release; current parent repo contains unrelated work | Pending | Never commit parent workspace |

Record superseding decisions as new entries with migration consequences. Preserve rejected alternatives only where they explain current tradeoffs.

Owner clarification: all requested languages are wanted (“fully need”). This establishes demand, not exact edition selection or a written license. No source text or grant has been received.

Source update: owner supplied the local `bible/` folder. Six XMLBIBLE sources are inventoried; no license documents were present. KJV 1769 is absent; 21st Century KJV is a distinct supplied edition and is not mapped to that code. Malayalam is absent; Kannada is additional, not a substitute.

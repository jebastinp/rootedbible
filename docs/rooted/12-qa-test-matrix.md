# QA test matrix

Statuses below describe acceptance coverage required, not tests already passed. Synthetic validator/access-control results are recorded in the changelog after execution. Real Bible accuracy remains blocked without approved source and manifest.

| ID | Area | Cases and expected result | Method / gate |
|---|---|---|---|
| QA01 | Rights | Unknown/pending/inactive/version-code URL returns no content; approved records need evidence | Unit + endpoint; Critical |
| QA02 | Structure | Missing/extra/reordered books, chapters, verses, duplicate IDs and invalid numbering rejected | Synthetic unit; Critical |
| QA03 | Unicode | Valid Tamil/Malayalam/Hindi/Telugu; replacement chars, surrogates, controls, empty text rejected | Synthetic unit + native speakers; Critical |
| QA04 | Source fidelity | Checksum, full manifest, every book start/end, random passages/punctuation | Full-source comparison + human; Blocked L01 |
| QA05 | Reader | First/last chapter, cross-book nav, deep links, last verse anchor, no content, failed load | Browser/native; High |
| QA06 | Completion | Repeat click, reread, undo, reload, zero denominator, edition switch, partial dataset | Domain + persistence; High |
| QA07 | Time | Midnight, DST forward/back, today/yesterday/missed days, timezone change, rollback | Fixed clocks/IANA fixtures; High |
| QA08 | Plans | Full reference coverage, invalid bounds, exact duration, partial day, pause/resume, enrollment switch | Domain + UI; High |
| QA09 | Storage | Denied/quota/corrupt state, version migration, interrupted transaction, multi-tab | Integration; High |
| QA10 | Appearance | Small 320 px viewport, large screen, landscape, 200% zoom, font range, all themes | Browser + physical devices; High |
| QA11 | Accessibility | VoiceOver/TalkBack, keyboard, focus restore, targets, contrast, reduced motion | Manual + automated scan; Critical |
| QA12 | Reminder | Permission denied, unsupported web, enabled native, reschedule/timezone, cancel/delete | Platform tests; High |
| QA13 | Privacy/security | No sensitive telemetry/logs; export/delete; unauth/other-user access if retained | Payload/storage and security tests; Critical |
| QA14 | Performance | Cold/warm launch, chapter p50/p95, rapid nav, long verses, large approved dataset | Low/mid/high physical devices; release budgets |
| QA15 | Release | Build/assets/no secrets, rights dates/notices, endpoints, dependency scan, signed native build | CI + owner release review; Critical |

Device matrix: current Safari on macOS/iOS, Chrome on Android/desktop; minimum supported OS versions TBD. At least one older low-memory Android device, one mid-range Android and one iPhone; model/OS/network/build identifier recorded with results. Emulation does not equal physical-device QA.

Manual content QA must use the exact licensed edition and source-native verse labels. Test long mixed-language punctuation, combining marks, selection/copy and reader text reflow. No generated verse text or sample fixture counts count as release Bible verification.

Regression commands: `cd frontend && npm run build && npm test`; `cd backend && DEBUG=false venv/bin/python -m pytest tests -q`. Frontend test coverage must be created for the new domain features; build success alone is not UI QA.

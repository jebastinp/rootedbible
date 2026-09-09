# Canonical Bible and reading schema

Design version 1; additive migration required. Existing tables retain legacy data until tested migration. Source-format adapters may parse JSON/XML/CSV/licensed APIs, but only a canonical validated package reaches the repository.

| Entity | Stable key and fields | Constraints |
|---|---|---|
| Translation | edition ID, BCP-47 language, exact name, provider, copyright, license ID | Never reuse ID for another edition |
| LicenseMetadata | ID, evidence reference/hash, scoped rights, territories, dates, limits, notice | Unknown/expired/withdrawn blocks delivery |
| Dataset | edition ID + dataset version, source/hash/import date, versification ID, QA status | Immutable version, explicit promotion |
| Book | dataset + canonical book ID, localized name, order, testament | Unique order/ID; manifest-defined canon |
| Chapter | dataset + book ID + positive chapter number | Exact manifest chapter set |
| Verse | chapter + source verse label, text, sequence | Exact labels, unique sequence, nonempty valid Unicode |
| ChapterCompletion | user/device + edition + versification + book + chapter | Derived from history; unique chapter credit |
| ReadingHistory | event ID, chapter key, UTC time, IANA timezone, frozen local date | Idempotent daily chapter event; reversible |
| LastPosition | edition key, book, chapter, verse anchor, updated UTC | No provider-specific URL dependency |
| Plan | plan ID/version, title, description, duration, difficulty, languages/compatibility | All references validated |
| PlanDay | plan/version + day number, title, passages, estimated minutes | Contiguous days; nonempty valid references |
| UserPlan | enrollment ID, plan version, edition, start date, status, completed days | One active; state transitions validated |
| Settings | schema version, selected edition, reading timezone, font, spacing, appearance, reminder | Bounded values; explicit capability checks |

Verse labels may contain edition-approved omissions, suffixes or bridges. Do not assume that `max(verse_number)` equals verse count. The approved source manifest defines exact expected labels per chapter and book order. An omitted verse is acceptable only when the manifest and content reviewer explicitly agree. Protestant 66-book metadata in the legacy code is not a universal canon.

Canonical validation input has `schema_version`, `translation_id`, `dataset_version`, `books[]`; each book has `id`, `name`, `testament`, `chapters[]`; each chapter has `number`, `verses[{number,text}]`. A separately reviewed manifest contains the same book/chapter structure with an ordered `verse_numbers[]` list and edition identity. A source adapter must not create that manifest from the dataset it is validating and claim independent accuracy.

Pipeline: strict UTF-8 decode → parser → canonical representation → Unicode/control/whitespace checks → book/chapter/verse sequence comparison → duplicate/empty checks → source checksum → scoped license check → staged dataset → bilingual/manual QA → promotion. Preserve source bytes in restricted storage; do not silently normalize spelling, punctuation, combining characters or verse labels. NFC differences are review flags, not permission to rewrite text.

Runtime progress denominators come only from the approved complete dataset. A partial test fixture or partial import cannot be labeled a whole Bible. Additive dataset version changes do not erase history; incompatible versification requires an approved mapping and user-visible explanation.

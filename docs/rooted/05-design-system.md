# Design system specification

Status: proposed baseline, using the existing Rooted green/cream identity. Visual sign-off and device QA pending. Implementation source today is `frontend/tailwind.config.js`; consolidate into semantic CSS variables during new-shell work.

| Token | Light | Dark / behavior |
|---|---|---|
| canvas | `#F8F4EC` | `#15201A` |
| surface | `#FFFFFF` | `#1D2B23` |
| text.primary | `#1B1B1B` | `#F0F2EB` |
| text.secondary | `#59645E` | `#B9C4BB` |
| action.primary | `#0B5D3B` with white label | `#A8D672` with dark label |
| border | semantic separator, measured contrast where interactive | same rule |
| focus | visible 3 px outline, 2 px offset | never color alone |

Spacing scale: 4/8/12/16/24/32/48 px. Touch targets at least 44×44 CSS px; primary buttons minimum 48 px high. Cards radius 20 px, controls 12 px; subtle single elevation level. No mandatory glass, gold, decorative images or infinite animations.

Reader: maximum line measure 66 characters; default 22 px, range 16–36 px plus browser zoom; line spacing 1.5/1.75/2; paragraph gaps about 0.6 em. Verse numbers remain smaller but legible and individually accessible. Preserve source paragraphs and punctuation; no splitting grapheme clusters or Latin-only line-breaking rules. Use `lang` per edition. Approved Indic fonts must cover Tamil, Malayalam, Devanagari and Telugu and be tested for shaping/selection; system fallback until font rights/files are checked. Do not claim English font coverage.

Theme: system/light/dark; reading appearance may offer paper as an explicit variant. Settings persist. Contrast targets: normal text at least 4.5:1; large text and essential non-text controls at least 3:1. Verify actual combinations and disabled/error states in QA.

Animation: only purposeful state transitions, ≤180 ms; respect reduced motion and never initialize essential Scripture/login content invisibly. Safe areas, keyboard, landscape and 200% zoom must not obscure reader controls.

Components: Button (primary/secondary/destructive/loading), Card, Header, TabBar, ProgressBar/Ring (named and numerically announced), BookSelector, ChapterSelector, Verse, ChapterHeader, TranslationSelector, PlanCard, StatCard, Empty/Error/LoadingState, SettingsRow, Modal/Sheet. Modal/sheet trap and restore focus; Escape closes; loading uses live status. Each component owns semantic states, not duplicate page-specific styling.

Strings use typed localization keys (e.g. `reader.nextChapter`, `progress.completed`). English is initial UI fallback; translated UI requires language review and must not imply availability of a Bible edition.

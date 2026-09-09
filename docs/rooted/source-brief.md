# ROOTED — COMPLETE PRODUCT DEVELOPMENT MASTER PROMPT

## 1. PROJECT IDENTITY

Build a premium Bible reading and spiritual growth application called **Rooted**.

Rooted should help people:

* Read the Bible consistently
* Track Bible-reading progress
* Follow structured reading plans
* Build healthy reading habits
* See meaningful progress toward completing Scripture
* Save important passages
* Reflect on what they read
* Stay consistent without making the experience feel stressful or gamified
* Access Scripture in multiple languages/translations where legally permitted

Rooted should feel:

* Premium
* Peaceful
* Modern
* Minimal
* Trustworthy
* Spiritual
* Fast
* Accessible
* Apple-quality
* Easy for first-time users
* Useful for serious Bible readers

The product should NOT feel like a generic habit tracker with Bible text added to it.

The Bible-reading experience is the heart of Rooted.

---

# 2. CORE PRODUCT PRINCIPLE

The primary experience should be:

OPEN ROOTED
↓
SEE TODAY'S READING / CONTINUE READING
↓
READ SCRIPTURE
↓
MARK PROGRESS
↓
SEE PROGRESS
↓
RETURN TOMORROW

Everything else should support this loop.

Avoid unnecessary features in the MVP.

Prioritize:

1. Scripture accuracy
2. Legal Bible licensing
3. Reading experience
4. Progress tracking
5. Reading plans
6. Reliability
7. Accessibility
8. Privacy
9. Performance
10. Premium design

---

# 3. MVP DEFINITION

The first production version should focus on the following.

## MUST HAVE

### Bible

* Bible book list
* Old Testament
* New Testament
* Books
* Chapters
* Verses
* Verse numbers
* Translation/version selection
* Chapter navigation
* Previous/next chapter
* Continue reading
* Last-read location

### Progress

* Chapters read
* Overall Bible progress
* Old Testament progress
* New Testament progress
* Current reading progress
* Reading history
* Reading streak
* Daily reading status

### Reading Plans

* Plan list
* Plan details
* Start a plan
* Today's reading
* Mark plan reading complete
* Plan progress
* Completed days
* Remaining days

### UI

* Home
* Bible
* Reading
* Progress
* Plans
* Settings

### Settings

* Translation
* Font size
* Reading appearance
* Notifications
* Reminder time
* Theme
* Privacy
* About
* Terms
* Bible attribution/licensing information

---

# 4. FUTURE FEATURES

Do NOT allow these to delay MVP unless specifically approved.

Possible future features:

* Search
* Bookmarks
* Highlights
* Notes
* Cross references
* Verse sharing
* Verse images
* Widgets
* Achievements
* Reading challenges
* Multiple reading plans
* Custom plans
* Cloud sync
* Accounts
* Multi-device synchronization
* Social features
* Community
* Prayer journal
* Prayer reminders
* Audio Bible
* AI Bible study tools
* Devotionals
* Daily verse
* Bible study tools
* Advanced statistics
* Home screen widgets
* Apple Watch support
* Android widgets
* Wearable integrations
* Additional languages
* Additional Bible translations

Every future feature must be evaluated against:

* User value
* Development complexity
* Bible licensing
* Privacy
* Cost
* Maintenance
* Performance

---

# 5. BIBLE CONTENT & LICENSING

THIS IS A CRITICAL PART OF ROOTED.

Never assume that Bible text is free to redistribute.

Do not:

* Scrape Bible.com
* Scrape YouVersion
* Copy copyrighted Bible text from websites
* Download copyrighted translations and bundle them without permission
* Circumvent API restrictions
* Use an API outside its permitted terms
* Store/cache content beyond the provider's license
* Publish copyrighted translations without written authorization

Every Bible version must have a licensing record.

Track:

* Translation name
* Language
* Copyright owner
* Provider
* License type
* API availability
* Commercial use permission
* Offline use permission
* Bundling permission
* Caching permission
* Storage permission
* Distribution permission
* Attribution requirements
* Required copyright notice
* Territory restrictions
* User limits
* API rate limits
* Contract expiration
* Renewal requirements
* Contact person
* Contract/evidence location

---

# 6. TARGET BIBLE LANGUAGES

Initial target languages:

1. Tamil
2. English
3. Malayalam
4. Hindi
5. Telugu

The requested English translation includes:

* NKJV

Tamil should use the specifically approved/licensed Tamil edition.

Do not substitute a different translation simply because it is technically easier.

The final translation list must be determined by actual licensing rights.

---

# 7. BIBLE RIGHTS WORKFLOW

For every translation:

STEP 1
Identify copyright owner/provider.

STEP 2
Contact rights holder/provider.

STEP 3
Ask specifically for:

* Mobile app usage
* Commercial usage
* Display rights
* API rights
* Offline rights
* Local database storage
* Caching
* Number of users
* Number of API calls
* Attribution requirements
* Screenshots/marketing usage
* International distribution
* iOS distribution
* Android distribution

STEP 4
Receive written agreement.

STEP 5
Store license evidence securely.

STEP 6
Record license information in Rooted's internal licensing registry.

STEP 7
Only then implement that translation.

---

# 8. BIBLE DATA ARCHITECTURE

Use a canonical internal structure.

Example:

Translation
→ Book
→ Chapter
→ Verse

Conceptually:

translation_id
language
translation_name
copyright
provider

book_id
book_name
book_number
testament

chapter_number

verse_number
verse_text

Do not make the UI dependent on one specific Bible source's raw format.

Create an import layer.

Possible source formats:

* XML
* JSON
* API response
* CSV
* licensed database

All sources should be converted into a canonical Rooted Bible schema.

---

# 9. BIBLE IMPORT PIPELINE

Create a reliable pipeline:

SOURCE
↓
IMPORT
↓
PARSER
↓
NORMALIZATION
↓
UNICODE VALIDATION
↓
STRUCTURE VALIDATION
↓
VERSE COUNT VALIDATION
↓
DUPLICATE CHECK
↓
MISSING VERSE CHECK
↓
BOOK/CHAPTER VALIDATION
↓
LICENSE CHECK
↓
BUILD DATASET
↓
QA
↓
APP

The pipeline must detect:

* Missing books
* Missing chapters
* Missing verses
* Duplicate verses
* Incorrect verse numbering
* Incorrect chapter numbering
* Invalid Unicode
* Broken Tamil characters
* Broken Malayalam characters
* Broken Hindi characters
* Broken Telugu characters
* Encoding problems
* Unexpected whitespace
* Corrupted text
* Empty verses
* Duplicate IDs

---

# 10. MULTILINGUAL SUPPORT

Rooted must properly support:

Tamil
Malayalam
Hindi
Telugu
English

Use Unicode correctly.

Test:

* Rendering
* Font availability
* Line wrapping
* Character shaping
* Text selection
* Search
* Accessibility
* Large fonts
* Small screens
* Long verses
* Mixed punctuation

Never assume English typography rules work for every language.

---

# 11. HOME SCREEN

The Home screen should immediately answer:

"What should I do now?"

Recommended structure:

TOP:
Rooted greeting / calm header

MAIN CARD:
Today's Reading

Show:

* Plan name
* Today's passage
* Estimated reading time
* Progress
* Continue Reading button

SECONDARY:
Continue Reading

Show:

* Last book
* Chapter
* Translation
* Progress

PROGRESS CARD:

* Overall Bible progress
* Current streak
* Chapters read

OPTIONAL:
Quick access:

* Bible
* Plans
* Progress

Keep the screen uncluttered.

---

# 12. BIBLE SCREEN

Bible navigation should be extremely simple.

Allow:

* Testament selection
* Book selection
* Chapter selection

Do not make the user repeatedly tap through unnecessary screens.

Potential structure:

Bible
→ Old Testament / New Testament
→ Book
→ Chapter

Include:

* Translation selector
* Chapter selector
* Previous chapter
* Next chapter
* Continue reading

---

# 13. READING SCREEN

This is the most important screen in Rooted.

Prioritize readability.

Requirements:

* Large comfortable typography
* Good line spacing
* Clear verse numbers
* Minimal visual distraction
* Smooth scrolling
* Fast rendering
* Dark mode
* Light mode
* Adjustable font size
* Adjustable reading appearance
* Translation indicator
* Chapter title
* Navigation

Avoid excessive UI around Scripture.

The Bible should visually dominate the screen.

---

# 14. READING PROGRESS

Define exactly what "read" means.

Recommended MVP model:

A chapter can be marked complete.

Track:

* Translation
* Book
* Chapter
* Completion status
* Completed timestamp

Avoid ambiguous progress.

If verse-level progress is later introduced, design the database so it can support it without breaking chapter-level progress.

---

# 15. BIBLE COMPLETION CALCULATION

Define the denominator clearly.

For example:

Total chapters in selected Bible dataset.

Then:

Progress =
completed chapters / total chapters

Also show:

* Chapters completed
* Chapters remaining
* Percentage
* Testament progress

Never show misleading progress when a user has changed translation unless the product explicitly defines how translation switching affects progress.

Define this behavior before implementation.

---

# 16. READING STREAK

Streak logic must be explicitly defined.

Example:

A day counts when the user completes at least one qualifying reading unit.

Define:

* User timezone
* Day boundary
* Missed days
* Multiple readings in one day
* Travel across timezones
* Manual date changes
* Device clock manipulation
* Reset behavior
* Grace periods, if any

Do not create confusing streak behavior.

Rooted should encourage Scripture reading rather than make users feel guilty.

---

# 17. READING PLANS

Each plan should contain:

plan_id
title
description
duration
difficulty
language
translation compatibility
days
passages

Each day:

day_number
title
passages
estimated_minutes

User plan state:

user_plan_id
plan_id
start_date
current_day
completed_days
status

Possible states:

* Not Started
* Active
* Completed
* Paused
* Abandoned

---

# 18. INITIAL READING PLANS

Possible launch plans:

* Read the Bible in 1 Year
* New Testament in 90 Days
* Gospels in 30 Days
* Psalms in 30 Days
* Proverbs in 31 Days
* 30-Day Gospel Journey
* Bible Foundations

Before publishing any plan:

* Verify every reference
* Verify chapter numbers
* Verify translation compatibility
* Verify duration
* Test completion logic

---

# 19. PROGRESS DASHBOARD

Show meaningful statistics:

Primary:

* Overall Bible progress
* Chapters completed
* Chapters remaining

Secondary:

* Current streak
* Longest streak
* Reading days
* Current plan progress

Optional:

* Old Testament %
* New Testament %
* Books completed
* Monthly activity

Avoid turning the app into a competition.

---

# 20. SETTINGS

Settings should include:

Reading:

* Translation
* Font size
* Line spacing
* Theme
* Reading appearance

Notifications:

* Enable reminders
* Reminder time
* Reading reminder behavior

Data:

* Export data, if supported
* Delete data, if applicable
* Sync settings, if applicable

Legal:

* Privacy Policy
* Terms of Use
* Bible copyright information
* Licenses
* Open-source licenses

About:

* Rooted version
* Contact
* Credits

---

# 21. NOTIFICATIONS

Notifications must be:

* Optional
* User-controlled
* Respectful
* Not manipulative

Examples:

* "Your reading for today is ready."
* "Continue your reading journey."
* "You have a reading planned for today."

Avoid guilt-based notifications.

Do not imply spiritual judgment because the user missed a day.

---

# 22. DESIGN SYSTEM

Rooted should use a premium, calm design language.

Visual characteristics:

* Clean
* Spacious
* Elegant
* Soft
* Minimal
* Premium
* Modern
* Spiritual without looking old-fashioned

Potential visual inspiration:

* Apple-quality interaction
* Liquid glass-inspired surfaces where appropriate
* Elegant typography
* Subtle gradients
* Soft shadows
* Refined cards
* Beautiful Bible imagery only when useful

Do not overuse:

* Gradients
* Glass effects
* Shadows
* Animations
* Gold
* Decorative religious imagery

The Scripture should remain the focus.

---

# 23. DESIGN TOKENS

Create centralized design tokens for:

Colors
Typography
Spacing
Corner radius
Elevation
Icons
Buttons
Cards
Navigation
Dividers
Animations

Do not hard-code random values throughout the app.

---

# 24. ACCESSIBILITY

Rooted must support:

* Dynamic font sizing
* Screen readers
* VoiceOver / TalkBack
* Sufficient contrast
* Large touch targets
* Reduced motion
* Semantic labels
* Keyboard navigation where applicable
* Accessible controls
* Accessible progress indicators

Test multiple font sizes.

The reading screen must remain usable with large text.

---

# 25. PERFORMANCE

Target:

* Fast cold launch
* Fast chapter loading
* Smooth scrolling
* Low memory usage
* Fast book/chapter navigation
* Efficient local Bible storage
* Efficient search architecture if search is included

Benchmark:

* Low-end device
* Mid-range device
* High-end device

Test large Bible datasets.

---

# 26. OFFLINE ARCHITECTURE

Decide explicitly whether Rooted supports offline reading.

If licensed bundled content is allowed:

App
→ Local Bible database
→ Local reading
→ Local progress

If API-based:

App
→ Secure API
→ Bible provider

Do not cache API content unless the license permits it.

A hybrid model may be used if legally permitted.

---

# 27. ACCOUNT ARCHITECTURE

Make an explicit decision:

OPTION A:
Local-only MVP

Advantages:

* Simple
* Private
* Fast
* Less infrastructure
* Less legal complexity

OPTION B:
Account + cloud sync

Advantages:

* Multi-device
* Backup
* Sync

Disadvantages:

* Authentication
* Backend
* Security
* Privacy
* Data deletion
* Infrastructure
* Cost

Do not introduce accounts unless the user value justifies them.

---

# 28. PRIVACY

Collect the minimum necessary data.

Potential data:

* Reading progress
* Plan progress
* Settings
* Bookmarks
* Notes
* Account data, only if accounts exist
* Analytics events, only if justified

Never unnecessarily collect:

* Bible note contents
* Sensitive personal information
* Full reading text in analytics
* Raw search history without justification

Create a data map for every data field.

For every field ask:

WHY?
WHERE STORED?
WHO CAN ACCESS?
HOW LONG?
CAN USER DELETE IT?
IS IT NECESSARY?

---

# 29. SECURITY

Requirements:

* No production API keys in source code
* No secrets in client bundle
* Secure API communication
* Secure authentication if used
* Secure storage for sensitive credentials
* Dependency scanning
* Secret scanning
* Secure build pipeline
* Logging without sensitive data
* Minimal analytics payloads

Before release:

* Inspect production bundle
* Scan repository
* Check environment variables
* Check API keys
* Check debug logs
* Check endpoints

---

# 30. ANALYTICS

Analytics should measure product health, not spy on users.

Potential events:

app_open
onboarding_complete
chapter_open
chapter_complete
plan_started
plan_day_complete
plan_completed
reminder_enabled
search_used
error

Do not send:

* Full Bible verse text
* User notes
* Sensitive content

Useful metrics:

Activation:

* Onboarding completion
* First chapter opened
* First chapter completed

Engagement:

* Reading days
* Chapters completed
* Plan starts

Retention:

* D1
* D7
* D30

Quality:

* Crash-free sessions
* Chapter load time
* Search latency

---

# 31. ERROR HANDLING

Create friendly error states.

Examples:

Bible unavailable:
"Your Bible content couldn't be loaded. Please try again."

Network unavailable:
"You're offline. Available downloaded content is still accessible."

Unexpected error:
"Something went wrong. Please try again."

Never expose:

* Stack traces
* API secrets
* Internal IDs
* Technical errors to users

---

# 32. QA

Create automated and manual tests.

Bible tests:

* All books exist
* All chapters exist
* Verse counts match source
* No duplicate verses
* No missing verses
* Unicode valid
* Translation metadata correct

Functional tests:

* Navigation
* Progress
* Plans
* Settings
* Notifications
* Persistence

UI tests:

* Small screen
* Large screen
* Large fonts
* Dark mode
* Light mode

Accessibility tests:

* VoiceOver
* TalkBack
* Dynamic type
* Contrast

Performance tests:

* Startup
* Chapter loading
* Scrolling
* Search
* Memory

Security tests:

* Secrets
* Authentication
* Network
* Storage
* Logs

---

# 33. BIBLE CONTENT QA

This deserves separate QA.

For each translation:

1. Compare imported data against licensed source.
2. Validate book order.
3. Validate chapter order.
4. Validate verse numbers.
5. Validate verse count.
6. Validate Unicode.
7. Check random passages manually.
8. Check beginning of every book.
9. Check end of every book.
10. Check chapter boundaries.
11. Check punctuation.
12. Check special characters.
13. Check language rendering.
14. Verify copyright notice.
15. Verify attribution.

Never assume successful import means correct Bible content.

---

# 34. RELEASE BUILD

Before generating production build:

* Remove debug code
* Remove test data
* Remove test accounts
* Remove development API endpoints
* Remove secrets
* Verify production environment
* Verify analytics
* Verify crash reporting
* Verify privacy settings
* Verify Bible licenses
* Verify attribution
* Verify app icon
* Verify screenshots
* Verify metadata

---

# 35. APP STORE PREPARATION

Prepare:

* App name
* Subtitle
* Description
* Keywords
* Screenshots
* App icon
* Promotional artwork
* Privacy URL
* Terms URL
* Support URL
* Copyright information
* Age rating
* Data declarations
* Permissions explanations

Review every claim in marketing copy.

Do not claim:

* "Official"
* "Authorized"
* "Free Bible"
* "All Bible translations"
* "No tracking"
* "Completely private"

unless those claims are actually true.

---

# 36. BIBLE ATTRIBUTION

For every translation, determine exact required copyright/attribution language from the rights holder.

Display it where required.

Possible locations:

* Translation information
* About
* Settings
* Legal page
* App store description if required

Do not invent copyright notices.

---

# 37. SUPPORT

Create a support process.

Support categories:

* Bible content issue
* Translation issue
* Progress issue
* Reading plan issue
* Account issue
* Notification issue
* Crash
* Performance
* Privacy request
* Licensing/content concern

Define:

* Contact method
* Response target
* Escalation path
* Bug reporting process

---

# 38. VERSIONING

Use semantic/product release discipline.

Example:

0.1
Prototype

0.5
Internal MVP

0.9
Beta

1.0
Public launch

1.1
Bug fixes / polish

1.2
First meaningful feature expansion

Maintain:

* Changelog
* Release notes
* Known issues
* Migration notes

---

# 39. DEVELOPMENT ENVIRONMENT

Set up:

* Source repository
* Branch strategy
* Development environment
* Staging environment if backend exists
* Production environment
* Environment variables
* CI/CD
* Automated tests
* Build signing
* Release process

Never put production secrets into Git.

---

# 40. GIT / SOURCE CONTROL

Recommended branches:

main
develop
feature/*
fix/*
release/*

Use meaningful commits.

Examples:

feat: add chapter reader
feat: add reading progress
fix: correct streak timezone logic
fix: repair Tamil Unicode rendering
chore: update Bible data schema

---

# 41. CI/CD

Automate:

* Build
* Unit tests
* UI tests
* Lint
* Formatting
* Dependency checks
* Secret scanning
* Release build

Before merging:

* Tests pass
* No critical security issue
* No licensing issue
* No regression

---

# 42. PROJECT STRUCTURE

Organize the application into logical modules.

Suggested conceptual structure:

Core

* Theme
* Utilities
* Constants
* Error handling

Bible

* Models
* Repository
* Import
* Reader
* Translation management

Reading

* Reader UI
* Progress
* History

Plans

* Plan catalog
* Plan engine
* User plan state

Settings

* Preferences
* Notifications
* Privacy

Analytics

* Events
* Tracking abstraction

Infrastructure

* Database
* Network
* Storage
* Security

Do not tightly couple UI to the Bible provider.

---

# 43. DATABASE DESIGN

Potential entities:

Translation
Book
Chapter
Verse

ReadingProgress
ReadingHistory
ReadingPlan
ReadingPlanDay
UserPlan

Bookmark
Highlight
Note

User
Settings

Analytics configuration

LicenseMetadata

Design for future migration.

Use stable IDs.

---

# 44. DATA MIGRATION

Whenever Bible data schema changes:

* Version database schema
* Provide migration
* Test migration
* Backup where applicable
* Verify reading progress survives migration

Never destroy user progress during an update.

---

# 45. ONBOARDING

Onboarding should be short.

Possible flow:

Screen 1:
Welcome to Rooted

Screen 2:
Choose preferred language

Screen 3:
Choose Bible translation from available licensed versions

Screen 4:
Choose reading goal / plan

Screen 5:
Optional reminder

Screen 6:
Start reading

Do not force unnecessary account creation.

---

# 46. FIRST-TIME USER EXPERIENCE

First session should reach Scripture quickly.

Goal:

Install
→ Open
→ Choose basics
→ Read first passage

Avoid:

* Long tutorials
* Excessive permissions
* Forced registration
* Complex setup
* Too many questions

---

# 47. EMPTY STATES

Design empty states for:

No reading history
No plan
No bookmarks
No notes
No search results
No network
No downloaded content
No reminders

Every empty state should explain:

* What happened
* What the user can do next

---

# 48. LOADING STATES

Use polished loading states.

Avoid blank screens.

Use:

* Skeletons
* Progress indicators
* Subtle transitions

Do not overanimate Scripture content.

---

# 49. ANIMATION

Animations should be:

* Fast
* Subtle
* Meaningful
* Optional where possible

Respect reduced-motion settings.

Do not animate every interaction.

---

# 50. INTERNATIONALIZATION

Do not hard-code UI strings.

Use localization keys.

Example:

home.todayReading
home.continueReading
reader.nextChapter
reader.previousChapter
progress.completed
plans.startPlan

This makes future languages easier.

---

# 51. CONTENT MANAGEMENT

Bible content should not be manually edited inside application code.

Create a controlled content pipeline.

Every dataset should have:

* Version
* Source
* License
* Import date
* Checksum/version identifier
* QA status

---

# 52. LICENSE AUDIT

Before every release:

Check:

[ ] Every Bible version licensed
[ ] API usage permitted
[ ] Offline use permitted
[ ] Caching permitted
[ ] Attribution correct
[ ] Commercial use permitted
[ ] Distribution territory permitted
[ ] Contract active
[ ] No unauthorized content

Do not ship if a critical rights item is unresolved.

---

# 53. SECURITY AUDIT

Before every release:

[ ] No API keys in app
[ ] No secrets in Git
[ ] HTTPS enabled
[ ] Production endpoints correct
[ ] Debug logging removed
[ ] Dependency vulnerabilities reviewed
[ ] Authentication secure if applicable
[ ] Sensitive data protected
[ ] Analytics reviewed
[ ] Privacy policy matches implementation

---

# 54. PRIVACY AUDIT

Before every release:

[ ] Data inventory updated
[ ] Privacy policy accurate
[ ] Analytics reviewed
[ ] Third-party services reviewed
[ ] Data deletion works
[ ] Data retention defined
[ ] Permissions justified
[ ] No unnecessary personal data
[ ] Bible notes not accidentally transmitted
[ ] Search data handling documented

---

# 55. BETA

Beta goals:

* Find crashes
* Find Bible data problems
* Test reading flow
* Test progress accuracy
* Test plans
* Test accessibility
* Test different devices
* Test different languages
* Test performance

Recruit testers representing:

* New Bible readers
* Regular Bible readers
* Users reading in Tamil
* Users reading in English
* Users reading other supported languages
* Accessibility users

---

# 56. BETA FEEDBACK

Collect:

* What confused you?
* What was difficult?
* What felt slow?
* What did you expect?
* What feature did you want?
* Did progress feel accurate?
* Did the reading experience feel comfortable?
* Did you trust the app?
* Did anything feel unnecessary?

Categorize:

P0 = launch blocker
P1 = serious
P2 = important
P3 = improvement

---

# 57. LAUNCH GO / NO-GO

Rooted can launch only if:

[ ] Bible rights cleared
[ ] Bible data validated
[ ] MVP complete
[ ] No P0 bugs
[ ] Critical P1 bugs resolved
[ ] Security review complete
[ ] Privacy review complete
[ ] Accessibility review complete
[ ] Performance acceptable
[ ] Store assets complete
[ ] Legal pages live
[ ] Production monitoring active
[ ] Support process ready
[ ] Backup/recovery ready where relevant

---

# 58. POST-LAUNCH — FIRST 24 HOURS

Monitor:

* Crash rate
* App launch success
* Bible loading
* Chapter loading
* Progress saving
* API failures
* Authentication failures if applicable
* User support
* Store reviews
* Critical legal/licensing issues

Do not immediately add features.

Stabilize first.

---

# 59. FIRST 7 DAYS

Review:

* Downloads
* Activation
* First reading
* First chapter completion
* D1 retention
* D7 retention
* Reading frequency
* Plan starts
* Plan completion
* Crashes
* Support issues

Identify the biggest user problem.

Fix that first.

---

# 60. FIRST 30 DAYS

Perform a product review.

Questions:

1. Are users actually reading Scripture?
2. Do users return?
3. Where do they stop?
4. Is onboarding causing friction?
5. Is the reading screen comfortable?
6. Are plans useful?
7. Is progress motivating?
8. Are notifications useful?
9. Which translation/language is most requested?
10. What causes users to leave?

Then prioritize the next release.

---

# 61. PRODUCT METRICS

North Star concept:

Meaningful Bible reading sessions.

Track:

* Daily active readers
* Weekly active readers
* Reading sessions
* Chapters completed
* Reading days
* Plan starts
* Plan completions
* D1 retention
* D7 retention
* D30 retention
* Crash-free sessions
* Average chapter load time

Do not optimize purely for:

* App opens
* Notification clicks
* Time spent

The goal is meaningful Scripture engagement.

---

# 62. PRODUCT PHILOSOPHY

Rooted should never make users feel:

"An app is controlling my spiritual life."

Instead it should feel like:

"Rooted helps me stay consistent in God's Word."

Avoid:

* Shame
* Fear
* Aggressive streak mechanics
* Excessive notifications
* Competitive spirituality
* Manipulative engagement

Encourage:

* Consistency
* Reflection
* Peace
* Scripture
* Progress
* Personal discipline

---

# 63. MASTER DEVELOPMENT PHASES

PHASE 1 — FOUNDATION

* Product vision
* Target audience
* MVP scope
* Platform decision
* Architecture decision
* Bible licensing research
* Translation inventory
* Legal requirements

EXIT:
Scope and legal architecture understood.

---

PHASE 2 — DESIGN

* Information architecture
* User flows
* Wireframes
* Visual design
* Design system
* Accessibility design
* Reading experience

EXIT:
All MVP screens designed.

---

PHASE 3 — BIBLE CONTENT

* Licensing
* Source acquisition
* Data import
* Normalization
* Unicode validation
* Content QA
* Attribution

EXIT:
Approved Bible datasets ready.

---

PHASE 4 — ENGINEERING

* Project setup
* Database
* Bible repository
* Reader
* Navigation
* Progress
* Plans
* Settings
* Notifications if MVP
* Analytics
* Error handling

EXIT:
MVP feature complete.

---

PHASE 5 — QA

* Unit tests
* Integration tests
* UI tests
* Bible validation
* Accessibility
* Security
* Performance
* Device testing

EXIT:
Release candidate.

---

PHASE 6 — BETA

* Test users
* Feedback
* Bug fixing
* UX refinement
* Performance fixes

EXIT:
Beta acceptance.

---

PHASE 7 — STORE

* Store listing
* Screenshots
* Privacy
* Terms
* Attribution
* App signing
* Build validation
* Submission

EXIT:
Store approval.

---

PHASE 8 — LAUNCH

* Production release
* Monitoring
* Support
* First 24-hour review

EXIT:
Stable production.

---

PHASE 9 — GROWTH

* 7-day review
* 30-day review
* Retention analysis
* Feature prioritization
* Additional translations
* Search
* Bookmarks
* Notes
* Advanced features

---

# 64. MASTER RISK REGISTER

Track at minimum:

1. Bible licensing unavailable
2. Incorrect copyright assumptions
3. API restrictions
4. Offline restrictions
5. Content corruption
6. Unicode problems
7. Translation quality problems
8. Scope creep
9. Performance problems
10. Search performance
11. Privacy issues
12. Security vulnerabilities
13. App store rejection
14. Notification permission issues
15. Poor retention
16. Streak dissatisfaction
17. Sync conflicts
18. Infrastructure costs
19. Third-party dependency failure
20. Poor accessibility

Every risk needs:

* Probability
* Impact
* Score
* Mitigation
* Owner
* Trigger
* Status

---

# 65. MASTER DECISIONS TO MAKE

Before serious development, explicitly decide:

1. Which platforms?
2. Which Bible versions?
3. Who owns the rights?
4. API or bundled content?
5. Is offline reading supported?
6. Is cloud sync needed?
7. Are accounts required?
8. What counts as "read"?
9. How is progress calculated?
10. How do translation changes affect progress?
11. How does streak logic work?
12. Which reading plans launch?
13. Which features are MVP?
14. Which analytics are necessary?
15. Which third-party services are used?
16. What is the privacy model?
17. What is the support model?
18. What is the launch date?
19. What devices/OS versions are supported?
20. What is the post-launch roadmap?

---

# 66. ROOTED MVP SCREEN MAP

Create these screens first:

1. Splash
2. Onboarding
3. Home
4. Bible
5. Testament selection
6. Book selection
7. Chapter selection
8. Bible Reader
9. Today's Reading
10. Progress
11. Reading History
12. Plans
13. Plan Details
14. Active Plan
15. Settings
16. Reading Settings
17. Translation Selection
18. Notification Settings
19. About
20. Privacy
21. Terms
22. Bible Copyright / Attribution

---

# 67. COMPONENT LIBRARY

Create reusable components:

* RootedButton
* RootedCard
* RootedHeader
* RootedTabBar
* RootedProgressBar
* RootedProgressRing
* RootedBookSelector
* RootedChapterSelector
* RootedVerse
* RootedChapterHeader
* RootedTranslationSelector
* RootedPlanCard
* RootedStatCard
* RootedEmptyState
* RootedErrorState
* RootedLoadingState
* RootedSettingsRow
* RootedModal
* RootedSheet

Do not duplicate UI code unnecessarily.

---

# 68. CODE QUALITY

Require:

* Clear architecture
* Small reusable components
* Strong typing where applicable
* Error handling
* Testability
* Documentation
* No dead code
* No duplicated logic
* No magic numbers
* Centralized configuration
* Clear naming

---

# 69. DOCUMENTATION

Maintain:

README
Architecture documentation
Bible licensing documentation
Data schema documentation
API documentation
Privacy/data map
Release checklist
QA checklist
Known issues
Changelog
Decision log

---

# 70. DEFINITION OF DONE

A task is not "Done" merely because code exists.

A feature is Done when:

[ ] Requirement understood
[ ] Design approved
[ ] Code implemented
[ ] Unit tests completed
[ ] Integration tested
[ ] UI tested
[ ] Accessibility checked
[ ] Error states handled
[ ] Performance checked
[ ] Privacy implications checked
[ ] Security implications checked
[ ] Documentation updated
[ ] QA passed
[ ] Product owner approved

---

# 71. PRIORITY SYSTEM

CRITICAL:
Must work before launch.

HIGH:
Important for launch quality.

MEDIUM:
Useful but can be deferred.

LOW:
Future enhancement.

MVP:
Required for first public release.

LATER:
Do not block launch.

---

# 72. ROOTED MASTER TASK MANAGEMENT

Every task should have:

Task ID
Task name
Workstream
Area
Description
Deliverable
Acceptance criteria
Priority
Status
Owner
Start date
Due date
Dependencies
Risk
Notes

Statuses:

Not Started
Planned
In Progress
Blocked
Review
Done
Deferred

---

# 73. WEEKLY MANAGEMENT

Every week review:

1. What was completed?
2. What is blocked?
3. What changed?
4. What decision is needed?
5. What is the biggest risk?
6. What should be removed from scope?
7. What is next week's top goal?

Keep the team focused on the highest-value work.

---

# 74. FINAL ROOTED SUCCESS CRITERIA

Rooted succeeds if a new user can:

Install Rooted
↓
Open the app
↓
Choose a permitted Bible translation
↓
Start reading within minutes
↓
Understand where they are
↓
Complete a reading
↓
See meaningful progress
↓
Return the next day
↓
Continue their journey

The experience should be so simple that the user does not need to think about the technology.

They should simply be able to open Rooted and read God's Word.

---

# 75. IMPORTANT IMPLEMENTATION RULE

Before writing substantial production code, create and maintain these artifacts:

1. Product Requirements Document
2. Feature Backlog
3. User Flow
4. Information Architecture
5. Design System
6. Technical Architecture
7. Bible Licensing Matrix
8. Bible Data Schema
9. Privacy/Data Map
10. Security Threat Model
11. Analytics Event Taxonomy
12. QA Test Matrix
13. Risk Register
14. Decision Log
15. Launch Checklist
16. Post-launch Roadmap

Do not skip the Bible licensing and content validation stages.

---

# 76. FINAL INSTRUCTION TO THE DEVELOPMENT AI / TEAM

Build Rooted systematically.

Do not jump directly into coding screens without resolving:

* Product scope
* Bible licensing
* Data architecture
* Translation architecture
* Progress rules
* Privacy
* Security
* Platform requirements

When making technical decisions, prefer:

* Simple
* Reliable
* Maintainable
* Private
* Fast
* Scalable enough for the expected audience

When making design decisions, prefer:

* Calm
* Premium
* Readable
* Minimal
* Accessible

When making product decisions, prefer:

* Scripture reading
* Consistency
* User trust
* Simplicity

When making content decisions:

* Never assume copyright permission.
* Never scrape copyrighted Bible content.
* Never bypass provider restrictions.
* Use only legally authorized Scripture content.

When uncertain about a Bible translation, API, license, store policy, or legal requirement, flag it as a decision/risk instead of assuming.

The ultimate goal is to build **Rooted as a trustworthy, beautiful, premium Bible reading companion that makes consistent Scripture reading simple.**

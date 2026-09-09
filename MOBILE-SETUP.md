# Turning Rooted into iOS + Android apps (Capacitor)

Capacitor wraps your existing React frontend in a real native shell, so
you write the app once and ship it to both the App Store and Play Store.
Everything below runs on **your own computer** (this can't be done inside
the chat), because it needs to reach the npm registry and, for iOS,
Xcode.

Runs on: iPhone, iPad, Android phones, Android tablets - all from the
same `frontend/` codebase you already have.

---

## 0. What you need before starting

| Requirement | For | Cost |
|---|---|---|
| A Mac | Building/submitting the iOS app (Apple requires Xcode, Mac-only) | — (or rent a cloud Mac, e.g. [MacinCloud](https://www.macincloud.com), [Codemagic](https://codemagic.io) ~$0-30/mo) |
| [Xcode](https://apps.apple.com/app/xcode/id497799835) | Building the iOS app | Free |
| [Android Studio](https://developer.android.com/studio) | Building the Android app | Free, any OS |
| Node.js 20+ | Already needed for the web app | Free |
| Apple Developer account | Publishing to the App Store | $99/year |
| Google Play Console account | Publishing to Play Store | $25 one-time |
| Your backend already deployed somewhere public | The native app can't talk to `localhost` | Varies (Render/Railway/Fly.io) |

You do **not** need a Mac to write code or test on Android - only for
the final iOS build/submit step.

---

## 1. Deploy your backend first

The native app has no dev-server proxy, so it needs a real public URL.
Deploy `backend/` (FastAPI) to Render, Railway, or Fly.io - anything that
runs a Python ASGI app - pointed at your Supabase database, same as the
README's deployment section describes. Note the resulting URL, e.g.
`https://rooted-api.onrender.com`.

## 2. Point the frontend at it

```bash
cd frontend
cp .env.example .env
```

Edit `.env` and set:
```
VITE_API_BASE_URL=https://rooted-api.onrender.com/api/v1
```

## 3. Install dependencies (Capacitor packages are already in package.json)

```bash
npm install
```

## 4. Initialize the native projects (one-time)

```bash
npx cap add ios
npx cap add android
```

This creates `frontend/ios/` and `frontend/android/` - full native
Xcode/Android Studio projects. They get committed to your repo like any
other source.

## 5. Build the web app and sync it into the native shells

Every time you change frontend code, re-run this before testing on
device:

```bash
npm run cap:sync
```

(This runs `npm run build` then `npx cap sync`, copying your `dist/`
into both native projects.)

## 6. Open and run each platform

```bash
npm run cap:ios       # opens Xcode
npm run cap:android   # opens Android Studio
```

- **iOS**: in Xcode, pick a simulator (or your plugged-in iPhone/iPad)
  and hit ▶ Run. Universal iPad + iPhone support is on by default -
  just confirm under the project's *General* tab that both
  **iPhone** and **iPad** are checked under "Supported Destinations".
- **Android**: in Android Studio, pick an emulator (phone or tablet
  profile) or a plugged-in device and hit ▶ Run.

---

## 7. App icons and splash screen

Use your existing `frontend/public/logo-512.png` as the source image.
Easiest path - the community tool `@capacitor/assets`:

```bash
npm install @capacitor/assets --save-dev
npx capacitor-assets generate --iconBackgroundColor '#0B5D3B' --splashBackgroundColor '#F8F4EC'
```

This generates every required icon size for both platforms from one
source image and drops them into `ios/` and `android/` automatically.
Re-run `npm run cap:sync` afterward.

---

## 8. Before you submit: known gaps to close

These aren't Capacitor-specific, but they'll matter for a real store
submission:

- **Admin panel has no phone navigation.** `AdminLayout.tsx`'s sidebar
  is `hidden` below the `md` breakpoint with no replacement nav, so a
  pastor opening Admin on a phone currently sees no menu. Fine on iPad
  (shows the sidebar), but worth a mobile nav drawer before launch if
  pastors will use phones.
- **Bible text licensing** (see the plan doc, section 11, and my
  earlier message) - don't ship the NKJV/Tamil/Telugu/Kannada/Hindi
  files from `allbib.zip` without written permission. Do not substitute another edition. Follow `docs/rooted/07-bible-licensing.md`;
  every requested edition remains unavailable until rights and source QA are cleared.
- **Push notifications** aren't wired up yet (README section 9) - the
  plan's reminder system (section 13) will need `@capacitor/push-notifications`
  wired to Firebase Cloud Messaging (Android) and APNs (iOS) - a
  follow-up task, not part of this Capacitor setup.

---

## 9. Submitting to the stores (once you're happy with testing)

**iOS (App Store):**
1. In Xcode: Product → Archive.
2. Upload through Xcode's Organizer, or Transporter.
3. Fill out the listing in [App Store Connect](https://appstoreconnect.apple.com) (screenshots, description, privacy details).
4. Submit for review (usually 1-3 days).

**Android (Play Store):**
1. In Android Studio: Build → Generate Signed Bundle/APK → Android App Bundle.
2. Create the app listing in [Google Play Console](https://play.google.com/console).
3. Upload the `.aab` file to a release track (start with Internal Testing).
4. Submit for review (usually a few hours to a couple days).

Both stores will ask about data collection/privacy practices - be ready
to describe what Rooted stores (names/user IDs, reading progress) since
this involves children's data per the product plan - that triggers
extra requirements (Apple's "Made for Kids" rules, Google Play's
Families policies) if children ever log in directly rather than
through a parent's account.

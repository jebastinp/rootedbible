import type { CapacitorConfig } from '@capacitor/cli'

// appId: reverse-domain style, unique to you. Changing this later means
// re-creating the app listing on both stores, so pick it carefully now.
// Replace "org.yourchurch" with your own domain/org before first release.
const config: CapacitorConfig = {
  appId: 'org.yourchurch.rooted',
  appName: 'Rooted',
  webDir: 'dist',
  backgroundColor: '#F8F4EC',
  ios: {
    contentInset: 'automatic',
    backgroundColor: '#F8F4EC',
  },
  android: {
    backgroundColor: '#F8F4EC',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
      backgroundColor: '#F8F4EC',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
  },
}

export default config

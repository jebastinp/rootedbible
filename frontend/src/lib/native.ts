import { Capacitor } from '@capacitor/core'
import { StatusBar, Style } from '@capacitor/status-bar'
import { SplashScreen } from '@capacitor/splash-screen'
import { App as CapacitorApp } from '@capacitor/app'

/**
 * Everything in here is a no-op when running in a normal browser or as a
 * PWA - it only does anything inside the Capacitor-wrapped iOS/Android app.
 * Call initNativeApp() once, from main.tsx, before the app renders its
 * first route.
 */
export async function initNativeApp() {
  if (!Capacitor.isNativePlatform()) return

  // Match the status bar to the app's cream background instead of the OS default.
  try {
    await StatusBar.setOverlaysWebView({ overlay: false })
    await StatusBar.setStyle({ style: Style.Light })
    if (Capacitor.getPlatform() === 'android') {
      await StatusBar.setBackgroundColor({ color: '#F8F4EC' })
    }
  } catch {
    // StatusBar plugin can throw on some tablet/foldable configs - never block app start on it.
  }

  // Android hardware/gesture back button: go back in-app instead of
  // exiting the app when there's history to go back to.
  CapacitorApp.addListener('backButton', ({ canGoBack }) => {
    if (canGoBack) {
      window.history.back()
    } else {
      CapacitorApp.exitApp()
    }
  })

  // Hide the native splash screen once React has mounted, so the user never
  // sees a flash of blank white before the app's own UI is ready.
  await SplashScreen.hide()
}

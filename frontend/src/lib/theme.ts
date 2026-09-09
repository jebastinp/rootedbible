import { useEffect, useSyncExternalStore } from 'react'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'rooted-theme'
const listeners = new Set<() => void>()
let current: Theme = readStored()

function readStored(): Theme {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

function apply(theme: Theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

// Applied once at module load too, but main.tsx's inline head script already
// prevents a flash-of-wrong-theme before React even mounts.
apply(current)

function setTheme(theme: Theme) {
  current = theme
  try {
    localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // best-effort only
  }
  apply(theme)
  listeners.forEach((l) => l())
}

/** Only Light and Dark are supported - deliberately no "System" option. */
export function useTheme() {
  const theme = useSyncExternalStore(
    (onChange) => {
      listeners.add(onChange)
      return () => listeners.delete(onChange)
    },
    () => current
  )

  useEffect(() => {
    apply(theme)
  }, [theme])

  return {
    theme,
    setTheme,
    toggle: () => setTheme(current === 'dark' ? 'light' : 'dark'),
  }
}

import { useEffect, useState } from 'react'

export type FontSize = 'small' | 'medium' | 'large' | 'xlarge'
export type LineSpacing = 'compact' | 'comfortable' | 'relaxed'
export type ReaderFont = 'system' | 'serif'

export interface ReaderSettings {
  fontSize: FontSize
  lineSpacing: LineSpacing
  font: ReaderFont
}

const DEFAULT_SETTINGS: ReaderSettings = {
  fontSize: 'medium',
  lineSpacing: 'comfortable',
  font: 'serif',
}

const STORAGE_KEY = 'rooted-reader-settings'

export const FONT_SIZE_PX: Record<FontSize, number> = {
  small: 16,
  medium: 19,
  large: 22,
  xlarge: 26,
}

export const LINE_HEIGHT: Record<LineSpacing, number> = {
  compact: 1.5,
  comfortable: 1.8,
  relaxed: 2.15,
}

function loadSettings(): ReaderSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return DEFAULT_SETTINGS
    return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }
  } catch {
    return DEFAULT_SETTINGS
  }
}

function saveSettings(settings: ReaderSettings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {
    // best-effort only
  }
}

/** Font size, line spacing, and reading font - separate from the app's
 * global Light/Dark appearance (see lib/theme.ts), which the reader also uses. */
export function useReaderSettings() {
  const [settings, setSettings] = useState<ReaderSettings>(loadSettings)

  useEffect(() => {
    saveSettings(settings)
  }, [settings])

  function update(partial: Partial<ReaderSettings>) {
    setSettings((s) => ({ ...s, ...partial }))
  }

  return { settings, update }
}

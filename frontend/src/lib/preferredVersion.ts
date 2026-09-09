const KEY = 'rooted-preferred-bible-version'

/** So a reader who already picked a translation isn't asked again on the
 * next plan day or app open - deep links and the reader default to this. */
export function getPreferredVersion(): string | null {
  try {
    return localStorage.getItem(KEY)
  } catch {
    return null
  }
}

export function setPreferredVersion(code: string): void {
  try {
    localStorage.setItem(KEY, code)
  } catch {
    // best-effort only (private browsing, storage disabled, etc.)
  }
}

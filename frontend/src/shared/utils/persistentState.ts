import { useEffect, useRef, useState, type Dispatch, type SetStateAction } from 'react'

// Every persisted UI preference lives under this namespace so it is easy to spot
// (and clear) in devtools, and never collides with auth/session keys.
const PREFERENCE_PREFIX = 'git-it:pref:'

function browserStorage(): Storage | null {
  if (typeof window === 'undefined') return null
  try {
    const storage = window.localStorage
    return storage && typeof storage.getItem === 'function' ? storage : null
  } catch {
    // Accessing localStorage can throw in private-mode / sandboxed iframes.
    return null
  }
}

/** Read and JSON-parse a stored preference. Returns `undefined` when absent or corrupt. */
function readRawPreference(key: string): unknown {
  const storage = browserStorage()
  const raw = storage?.getItem(PREFERENCE_PREFIX + key)
  if (raw == null) return undefined
  try {
    return JSON.parse(raw)
  } catch {
    // Drop unreadable values so a single bad write can't wedge a preference forever.
    storage?.removeItem(PREFERENCE_PREFIX + key)
    return undefined
  }
}

/** Read a stored preference, falling back to `fallback` when absent or corrupt. */
export function readPreference<T>(key: string, fallback: T): T {
  const raw = readRawPreference(key)
  return raw === undefined ? fallback : (raw as T)
}

/** Best-effort write of a JSON-serialisable preference. Silently no-ops when storage is unavailable. */
export function writePreference<T>(key: string, value: T): void {
  const storage = browserStorage()
  if (!storage) return
  try {
    storage.setItem(PREFERENCE_PREFIX + key, JSON.stringify(value))
  } catch {
    // Storage may be full or disabled; preferences are best-effort, never critical.
  }
}

/**
 * `useState`, but the value is hydrated from `localStorage` on mount and written
 * back whenever it changes. Defaults are never written, so untouched preferences
 * leave storage clean.
 *
 * `sanitize` runs on the hydrated value and should coerce anything unexpected
 * (out-of-range numbers, stale shapes) back into a safe `T`.
 */
export function usePersistentState<T>(
  key: string,
  defaultValue: T,
  sanitize?: (value: T) => T,
): readonly [T, Dispatch<SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => {
    const raw = readRawPreference(key)
    if (raw === undefined) return defaultValue
    return sanitize ? sanitize(raw as T) : (raw as T)
  })

  // Skip the initial run so we don't persist the default for users who never
  // touched the setting.
  const hydrated = useRef(false)
  useEffect(() => {
    if (!hydrated.current) {
      hydrated.current = true
      return
    }
    writePreference(key, value)
  }, [key, value])

  return [value, setValue] as const
}

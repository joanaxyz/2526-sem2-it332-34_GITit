export type MotionMode = 'system' | 'reduced' | 'full'

export type PlayerPreferences = {
  motion_mode: MotionMode
}

const storageKey = 'git-it-preferences'
export const defaultPreferences: PlayerPreferences = { motion_mode: 'system' }

export function readStoredPreferences(): PlayerPreferences {
  if (typeof window === 'undefined') return defaultPreferences
  try {
    const raw = window.localStorage.getItem(storageKey)
    if (!raw) return defaultPreferences
    const parsed = JSON.parse(raw) as Partial<PlayerPreferences>
    return {
      motion_mode: parsed.motion_mode === 'reduced' || parsed.motion_mode === 'full' ? parsed.motion_mode : 'system',
    }
  } catch {
    return defaultPreferences
  }
}

export function persistPreferences(preferences: PlayerPreferences) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(storageKey, JSON.stringify(preferences))
}

export function applyPreferences(preferences: PlayerPreferences) {
  if (typeof window === 'undefined') return
  const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  const resolvedMotion = preferences.motion_mode === 'system' ? (prefersReduced ? 'reduced' : 'full') : preferences.motion_mode
  document.documentElement.dataset.motion = resolvedMotion
}

export function initializePreferences() {
  applyPreferences(readStoredPreferences())
}

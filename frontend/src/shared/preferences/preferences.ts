export type MotionMode = 'system' | 'reduced' | 'full'
export type OnboardingPhase = 'stories' | 'shop' | 'purchase' | 'home' | 'equip' | 'done'

export const onboardingPhases: readonly OnboardingPhase[] = ['stories', 'shop', 'purchase', 'home', 'equip', 'done']

/** What this browser stores and applies to the document. */
export type PlayerPreferences = {
  motion_mode: MotionMode
}

/** What the API reports for the signed-in account. */
export type PlayerAccountPreferences = PlayerPreferences & {
  onboarding_phase: OnboardingPhase
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
  // Only browser-wide settings go here: the onboarding phase is account-scoped
  // and stays on the server (mirrored per user by the onboarding feature).
  window.localStorage.setItem(storageKey, JSON.stringify({ motion_mode: preferences.motion_mode }))
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

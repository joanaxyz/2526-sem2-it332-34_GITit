export type LevelTourMode = 'adventure' | 'challenge' | 'tier'

// Versioned per mode so a tour change replays only the affected onboarding.
const LEVEL_TOUR_VERSIONS: Record<LevelTourMode, string> = {
  adventure: 'v5',
  challenge: 'v6',
  tier: 'v6',
}
const levelTourModes: readonly LevelTourMode[] = ['adventure', 'challenge', 'tier']

export function levelTourStorageKey(
  userId?: number | null,
  mode: LevelTourMode = 'challenge',
) {
  return `git-it-practice-workspace-tour:${LEVEL_TOUR_VERSIONS[mode]}:${userId ?? 'guest'}:${mode}`
}

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

/** Reopen every level tour for one account on this browser. */
export function resetLevelTours(userId?: number | null): boolean {
  const storage = safeStorage()
  if (!storage) return false
  try {
    levelTourModes.forEach((mode) => storage.removeItem(levelTourStorageKey(userId, mode)))
    return true
  } catch {
    return false
  }
}

export function hasSeenLevelTour(
  userId?: number | null,
  mode: LevelTourMode = 'challenge',
) {
  const storage = safeStorage()
  if (!storage) return true
  try {
    return storage.getItem(levelTourStorageKey(userId, mode)) === 'seen'
  } catch {
    return true
  }
}

export function markLevelTourSeen(
  userId?: number | null,
  mode: LevelTourMode = 'challenge',
) {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(levelTourStorageKey(userId, mode), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the tour must not crash the app.
  }
}

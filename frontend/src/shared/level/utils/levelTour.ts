export type LevelTourMode = 'adventure' | 'challenge'

const LEVEL_TOUR_VERSION = 'v3'

export function levelTourStorageKey(
  userId?: number | null,
  mode: LevelTourMode = 'challenge',
) {
  return `git-it-practice-workspace-tour:${LEVEL_TOUR_VERSION}:${userId ?? 'guest'}:${mode}`
}

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
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

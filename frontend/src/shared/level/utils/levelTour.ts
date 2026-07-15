export function levelTourStorageKey(userId?: number | null) {
  return `git-it-practice-workspace-tour:${userId ?? 'guest'}`
}

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

export function hasSeenLevelTour(userId?: number | null) {
  const storage = safeStorage()
  if (!storage) return true
  try {
    return storage.getItem(levelTourStorageKey(userId)) === 'seen'
  } catch {
    return true
  }
}

export function markLevelTourSeen(userId?: number | null) {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(levelTourStorageKey(userId), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the tour must not crash the app.
  }
}

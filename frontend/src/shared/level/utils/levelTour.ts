export function levelTourStorageKey(userId?: number | null) {
  return `git-it-practice-workspace-tour:${userId ?? 'guest'}`
}

export function hasSeenLevelTour(userId?: number | null) {
  if (typeof window === 'undefined') return true
  return localStorage.getItem(levelTourStorageKey(userId)) === 'seen'
}

export function markLevelTourSeen(userId?: number | null) {
  if (typeof window === 'undefined') return
  localStorage.setItem(levelTourStorageKey(userId), 'seen')
}

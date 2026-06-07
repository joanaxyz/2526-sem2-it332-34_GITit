export function practiceTourStorageKey(userId?: number | null) {
  return `git-it-practice-workspace-tour:${userId ?? 'guest'}`
}

export function hasSeenPracticeTour(userId?: number | null) {
  if (typeof window === 'undefined') return true
  return localStorage.getItem(practiceTourStorageKey(userId)) === 'seen'
}

export function markPracticeTourSeen(userId?: number | null) {
  if (typeof window === 'undefined') return
  localStorage.setItem(practiceTourStorageKey(userId), 'seen')
}

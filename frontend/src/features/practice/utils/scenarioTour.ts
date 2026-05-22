export function scenarioTourStorageKey(userId?: number | null) {
  return `git-it-scenario-workspace-tour:${userId ?? 'guest'}`
}

export function hasSeenScenarioTour(userId?: number | null) {
  if (typeof window === 'undefined') return true
  return localStorage.getItem(scenarioTourStorageKey(userId)) === 'seen'
}

export function markScenarioTourSeen(userId?: number | null) {
  if (typeof window === 'undefined') return
  localStorage.setItem(scenarioTourStorageKey(userId), 'seen')
}

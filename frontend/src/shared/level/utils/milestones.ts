const MILESTONE_KEY_PREFIX = 'git-it:milestone:'

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

function milestoneKey(name: string, userId?: number | null) {
  return `${MILESTONE_KEY_PREFIX}${name}:${userId ?? 'guest'}`
}

function hasSeen(name: string, userId?: number | null): boolean {
  const storage = safeStorage()
  if (!storage) return true
  try {
    return storage.getItem(milestoneKey(name, userId)) === 'seen'
  } catch {
    return true
  }
}

function markSeen(name: string, userId?: number | null): void {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(milestoneKey(name, userId), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the milestone must not crash the app.
  }
}

function firstCommandKey(userId?: number | null) {
  return `${MILESTONE_KEY_PREFIX}first-command:${userId ?? 'guest'}`
}

export function hasSeenFirstCommandMilestone(userId?: number | null): boolean {
  const storage = safeStorage()
  if (!storage) return true
  try {
    return storage.getItem(firstCommandKey(userId)) === 'seen'
  } catch {
    return true
  }
}

export function markFirstCommandMilestoneSeen(userId?: number | null): void {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(firstCommandKey(userId), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the milestone must not crash the app.
  }
}

export function hasSeenChapterNavCoachmark(userId?: number | null): boolean {
  return hasSeen('chapter-nav-coachmark', userId)
}

export function markChapterNavCoachmarkSeen(userId?: number | null): void {
  markSeen('chapter-nav-coachmark', userId)
}

export function hasSeenWorldMascotCoachmark(userId?: number | null): boolean {
  return hasSeen('world-mascot-coachmark', userId)
}

export function markWorldMascotCoachmarkSeen(userId?: number | null): void {
  markSeen('world-mascot-coachmark', userId)
  window.dispatchEvent(new CustomEvent('milestone:world-mascot-coachmark-seen'))
}

export function hasSeenAskBlueCoachmark(userId?: number | null): boolean {
  return hasSeen('ask-blue-coachmark', userId)
}

export function markAskBlueCoachmarkSeen(userId?: number | null): void {
  markSeen('ask-blue-coachmark', userId)
}

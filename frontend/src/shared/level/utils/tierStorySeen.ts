// v2 reopens the modal once so existing players receive the revised scenario bank.
const TIER_STORY_VERSION = 'v2'

/**
 * One remembered introduction per user, level and difficulty. The level key is
 * an adventure level id, or `challenge:<trial id>` for a Challenge Gate trial.
 * Variants are deliberately not part of the key: a retry draws a new variant
 * of the same level and must not reopen the introduction.
 */
function tierStoryStorageKey(
  userId: number | null | undefined,
  levelKey: number | string,
  difficulty: string,
) {
  return `git-it-tier-story:${TIER_STORY_VERSION}:${userId ?? 'guest'}:${levelKey}:${difficulty}`
}

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

/** Clear this account's remembered level introductions on the current browser. */
export function resetTierStories(userId: number | null | undefined): boolean {
  const storage = safeStorage()
  if (!storage) return false
  const prefix = `git-it-tier-story:${TIER_STORY_VERSION}:${userId ?? 'guest'}:`
  try {
    const keys = Array.from({ length: storage.length }, (_, index) => storage.key(index))
    keys.forEach((key) => {
      if (key?.startsWith(prefix)) storage.removeItem(key)
    })
    return true
  } catch {
    return false
  }
}

export function hasSeenTierStory(
  userId: number | null | undefined,
  levelKey: number | string,
  difficulty: string,
) {
  const storage = safeStorage()
  // Same rule as the level tour: without storage, never auto-open on every visit.
  if (!storage) return true
  try {
    return storage.getItem(tierStoryStorageKey(userId, levelKey, difficulty)) === 'seen'
  } catch {
    return true
  }
}

export function markTierStorySeen(
  userId: number | null | undefined,
  levelKey: number | string,
  difficulty: string,
) {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(tierStoryStorageKey(userId, levelKey, difficulty), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the introduction must not crash the level.
  }
}

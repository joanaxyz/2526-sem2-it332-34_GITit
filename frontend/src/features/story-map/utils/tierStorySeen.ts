import type { TierDifficulty } from '@/features/story-map/components/tierWorkspaceTypes'

// v2 reopens the modal once so existing players receive the revised scenario bank.
const TIER_STORY_VERSION = 'v2'

/**
 * One "story seen" flag per user, adventure level and difficulty. Variants are
 * deliberately not part of the key: a retry draws a new variant of the same
 * level and must not reopen the story.
 */
function tierStoryStorageKey(
  userId: number | null | undefined,
  adventureLevelId: number,
  difficulty: TierDifficulty,
) {
  return `git-it-tier-story:${TIER_STORY_VERSION}:${userId ?? 'guest'}:${adventureLevelId}:${difficulty}`
}

function safeStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

export function hasSeenTierStory(
  userId: number | null | undefined,
  adventureLevelId: number,
  difficulty: TierDifficulty,
) {
  const storage = safeStorage()
  // Same rule as the level tour: without storage, never auto-open on every visit.
  if (!storage) return true
  try {
    return storage.getItem(tierStoryStorageKey(userId, adventureLevelId, difficulty)) === 'seen'
  } catch {
    return true
  }
}

export function markTierStorySeen(
  userId: number | null | undefined,
  adventureLevelId: number,
  difficulty: TierDifficulty,
) {
  const storage = safeStorage()
  if (!storage) return
  try {
    storage.setItem(tierStoryStorageKey(userId, adventureLevelId, difficulty), 'seen')
  } catch {
    // Storage can be blocked in privacy modes; the story must not crash the level.
  }
}

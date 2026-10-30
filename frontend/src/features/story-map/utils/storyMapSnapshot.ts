import { useAuthStore } from '@/shared/auth/useAuth'

/**
 * Last-known story map payloads, kept per player so a return visit paints the
 * real chapter path at once instead of greyed placeholder nodes. The seeded
 * data is always marked stale and revalidated on mount; the backend stays
 * authoritative, so a node that unlocked or locked since the snapshot is
 * corrected by that refetch and refused by the run start if it was wrong.
 */
const SNAPSHOT_PREFIX = 'git-it:story-map-snapshot:'
const SNAPSHOT_TTL_MS = 7 * 24 * 60 * 60 * 1000
// Bump when the cached payload shape changes, so an older snapshot is dropped
// instead of seeding the map with fields it no longer has.
const SNAPSHOT_VERSION = 2

type SnapshotEntry<T> = {
  version: number
  userId: number
  storedAt: number
  data: T
}

function confirmedUserId() {
  const { accessToken, user, sessionUserId } = useAuthStore.getState()
  return accessToken && user && user.id === sessionUserId ? user.id : undefined
}

function snapshotKey(userId: number, key: string) {
  return `${SNAPSHOT_PREFIX}${userId}:${key}`
}

export const storyMapSnapshotKeys = {
  chapters: (storySlug: string) => `chapters:${storySlug}`,
  chapterOverview: (chapterId: number) => `chapter-overview:${chapterId}`,
}

export function readStoryMapSnapshot<T>(key: string): T | undefined {
  if (typeof window === 'undefined') return undefined
  const userId = confirmedUserId()
  if (userId === undefined) return undefined
  const storageKey = snapshotKey(userId, key)
  try {
    const raw = window.localStorage.getItem(storageKey)
    if (!raw) return undefined
    const entry = JSON.parse(raw) as SnapshotEntry<T>
    if (
      entry?.version !== SNAPSHOT_VERSION
      || entry.userId !== userId
      || !Number.isFinite(entry.storedAt)
      || Date.now() - entry.storedAt > SNAPSHOT_TTL_MS
      || entry.data == null
    ) {
      window.localStorage.removeItem(storageKey)
      return undefined
    }
    return entry.data
  } catch {
    return undefined
  }
}

export function writeStoryMapSnapshot<T>(key: string, data: T) {
  if (typeof window === 'undefined') return
  const userId = confirmedUserId()
  if (userId === undefined) return
  try {
    const entry: SnapshotEntry<T> = { version: SNAPSHOT_VERSION, userId, storedAt: Date.now(), data }
    window.localStorage.setItem(snapshotKey(userId, key), JSON.stringify(entry))
  } catch {
    // localStorage may be unavailable in private mode or quota exceeded.
  }
}

export type OrientationDraft = {
  completedStepIds: string[]
  stepIndex: number
}

const ORIENTATION_PROGRESS_PREFIX = 'git-it:orientation-progress:v1'

function storageKey(userId: number, lessonId: number) {
  return `${ORIENTATION_PROGRESS_PREFIX}:${userId}:${lessonId}`
}

function browserStorage(): Storage | null {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

function removeStoredDraft(storage: Storage, key: string) {
  try {
    storage.removeItem(key)
  } catch {
    // Storage is best-effort; an unavailable browser store must not block a lesson.
  }
}

export function readOrientationDraft(
  userId: number,
  lessonId: number,
  stepIds: string[],
): OrientationDraft | null {
  const storage = browserStorage()
  if (!storage) return null

  const key = storageKey(userId, lessonId)
  let parsed: unknown
  try {
    const raw = storage.getItem(key)
    if (raw === null) return null
    parsed = JSON.parse(raw)
  } catch {
    removeStoredDraft(storage, key)
    return null
  }

  if (!parsed || typeof parsed !== 'object') {
    removeStoredDraft(storage, key)
    return null
  }

  const candidate = parsed as Partial<OrientationDraft>
  if (
    typeof candidate.stepIndex !== 'number'
    || !Number.isInteger(candidate.stepIndex)
    || !Array.isArray(candidate.completedStepIds)
  ) {
    removeStoredDraft(storage, key)
    return null
  }

  const validStepIds = new Set(stepIds)
  const completedStepIds = [
    ...new Set(candidate.completedStepIds.filter((stepId): stepId is string => (
      typeof stepId === 'string' && validStepIds.has(stepId)
    ))),
  ]
  const finalIndex = Math.max(stepIds.length - 1, 0)

  return {
    completedStepIds,
    stepIndex: Math.min(Math.max(candidate.stepIndex, 0), finalIndex),
  }
}

export function writeOrientationDraft(userId: number, lessonId: number, draft: OrientationDraft) {
  const storage = browserStorage()
  if (!storage) return
  try {
    const key = storageKey(userId, lessonId)
    const current = storage.getItem(key)
    let completedStepIds = draft.completedStepIds
    let stepIndex = draft.stepIndex
    if (current !== null) {
      try {
        const parsed = JSON.parse(current) as Partial<OrientationDraft>
        if (Array.isArray(parsed.completedStepIds)) {
          completedStepIds = [...new Set([
            ...parsed.completedStepIds.filter((stepId): stepId is string => typeof stepId === 'string'),
            ...draft.completedStepIds,
          ])]
        }
        if (typeof parsed.stepIndex === 'number' && Number.isInteger(parsed.stepIndex)) {
          // Treat this as a monotonic resume cursor. A stale second tab may add
          // checkpoints, but it must never move the next resume point backward.
          stepIndex = Math.max(parsed.stepIndex, stepIndex)
        }
      } catch {
        // The new write replaces corrupt data below.
      }
    }
    // A draft checkpoints completed interactions. The active, unfinished
    // interaction intentionally restarts cleanly instead of persisting all of
    // its temporary selections and partially assembled answers.
    storage.setItem(key, JSON.stringify({ completedStepIds, stepIndex }))
  } catch {
    // Private browsing and full/blocked storage should degrade to in-memory progress.
  }
}

export function clearOrientationDraft(userId: number, lessonId: number) {
  const storage = browserStorage()
  if (storage) removeStoredDraft(storage, storageKey(userId, lessonId))
}

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { useAuthStore } from '@/shared/auth/useAuth'

const BOOTSTRAP_PREFIX = 'git-it:tier-run-bootstrap:'
const BOOTSTRAP_TTL_MS = 60_000

type BootstrapEntry = {
  userId: number
  run: TierRun
  storedAt: number
}

function confirmedUserId() {
  const { accessToken, user, sessionUserId } = useAuthStore.getState()
  return accessToken && user && user.id === sessionUserId ? user.id : undefined
}

function bootstrapKey(userId: number, runId: number) {
  return `${BOOTSTRAP_PREFIX}${userId}:${runId}`
}

export function writeTierRunBootstrap(run: TierRun) {
  if (typeof window === 'undefined') return
  const userId = confirmedUserId()
  if (userId === undefined) return
  try {
    const entry: BootstrapEntry = { userId, run, storedAt: Date.now() }
    window.sessionStorage.setItem(bootstrapKey(userId, run.id), JSON.stringify(entry))
  } catch {
    // sessionStorage may be unavailable in private mode or quota exceeded.
  }
}

export function readTierRunBootstrap(runId: number): TierRun | undefined {
  if (typeof window === 'undefined') return undefined
  const userId = confirmedUserId()
  if (userId === undefined) return undefined
  try {
    const raw = window.sessionStorage.getItem(bootstrapKey(userId, runId))
    if (!raw) return undefined
    const entry = JSON.parse(raw) as BootstrapEntry
    if (!entry?.run || entry.run.id !== runId || entry.userId !== userId || !Number.isFinite(entry.storedAt)) {
      clearTierRunBootstrap(runId)
      return undefined
    }
    if (Date.now() - entry.storedAt > BOOTSTRAP_TTL_MS) {
      clearTierRunBootstrap(runId)
      return undefined
    }
    return entry.run
  } catch {
    clearTierRunBootstrap(runId)
    return undefined
  }
}

export function clearTierRunBootstrap(runId: number) {
  if (typeof window === 'undefined') return
  const userId = confirmedUserId()
  if (userId === undefined) return
  try {
    window.sessionStorage.removeItem(bootstrapKey(userId, runId))
  } catch {
    // Ignore storage errors.
  }
}

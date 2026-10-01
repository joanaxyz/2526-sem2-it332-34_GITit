import type { ChallengeRun } from '@/features/challenges/types'
import { useAuthStore } from '@/shared/auth/useAuth'

const BOOTSTRAP_PREFIX = 'git-it:challenge-run-bootstrap:'
const BOOTSTRAP_TTL_MS = 60_000

type BootstrapEntry = {
  userId: number
  run: ChallengeRun
  storedAt: number
}

function confirmedUserId() {
  const { accessToken, user, sessionUserId } = useAuthStore.getState()
  return accessToken && user && user.id === sessionUserId ? user.id : undefined
}

function bootstrapKey(userId: number, runId: number) {
  return `${BOOTSTRAP_PREFIX}${userId}:${runId}`
}

export function writeChallengeRunBootstrap(run: ChallengeRun) {
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

export function readChallengeRunBootstrap(runId: number): ChallengeRun | undefined {
  if (typeof window === 'undefined') return undefined
  const userId = confirmedUserId()
  if (userId === undefined) return undefined
  try {
    const raw = window.sessionStorage.getItem(bootstrapKey(userId, runId))
    if (!raw) return undefined
    const entry = JSON.parse(raw) as BootstrapEntry
    if (!entry?.run || entry.run.id !== runId || entry.userId !== userId || !Number.isFinite(entry.storedAt)) {
      clearChallengeRunBootstrap(runId)
      return undefined
    }
    if (Date.now() - entry.storedAt > BOOTSTRAP_TTL_MS) {
      clearChallengeRunBootstrap(runId)
      return undefined
    }
    return entry.run
  } catch {
    clearChallengeRunBootstrap(runId)
    return undefined
  }
}

export function clearChallengeRunBootstrap(runId: number) {
  if (typeof window === 'undefined') return
  const userId = confirmedUserId()
  if (userId === undefined) return
  try {
    window.sessionStorage.removeItem(bootstrapKey(userId, runId))
  } catch {
    // Ignore storage errors.
  }
}

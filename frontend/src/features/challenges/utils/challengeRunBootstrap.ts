import type { ChallengeRun } from '@/features/challenges/types'

const BOOTSTRAP_PREFIX = 'git-it:challenge-run-bootstrap:'
const BOOTSTRAP_TTL_MS = 60_000

type BootstrapEntry = {
  run: ChallengeRun
  storedAt: number
}

function bootstrapKey(runId: number) {
  return `${BOOTSTRAP_PREFIX}${runId}`
}

export function writeChallengeRunBootstrap(run: ChallengeRun) {
  if (typeof window === 'undefined') return
  try {
    const entry: BootstrapEntry = { run, storedAt: Date.now() }
    window.sessionStorage.setItem(bootstrapKey(run.id), JSON.stringify(entry))
  } catch {
    // sessionStorage may be unavailable in private mode or quota exceeded.
  }
}

export function readChallengeRunBootstrap(runId: number): ChallengeRun | undefined {
  if (typeof window === 'undefined') return undefined
  try {
    const raw = window.sessionStorage.getItem(bootstrapKey(runId))
    if (!raw) return undefined
    const entry = JSON.parse(raw) as BootstrapEntry
    if (!entry?.run || entry.run.id !== runId) {
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
  try {
    window.sessionStorage.removeItem(bootstrapKey(runId))
  } catch {
    // Ignore storage errors.
  }
}

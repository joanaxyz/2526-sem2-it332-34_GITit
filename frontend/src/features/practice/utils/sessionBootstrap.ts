import type { PracticeSession } from '@/features/practice/types'

const BOOTSTRAP_PREFIX = 'git-it:session-bootstrap:'
const BOOTSTRAP_TTL_MS = 60_000

type BootstrapEntry = {
  session: PracticeSession
  storedAt: number
}

function bootstrapKey(sessionId: number) {
  return `${BOOTSTRAP_PREFIX}${sessionId}`
}

export function writeSessionBootstrap(session: PracticeSession) {
  if (typeof window === 'undefined') return
  try {
    const entry: BootstrapEntry = { session, storedAt: Date.now() }
    window.sessionStorage.setItem(bootstrapKey(session.id), JSON.stringify(entry))
  } catch {
    // sessionStorage may be unavailable in private mode or quota exceeded.
  }
}

export function readSessionBootstrap(sessionId: number): PracticeSession | undefined {
  if (typeof window === 'undefined') return undefined
  try {
    const raw = window.sessionStorage.getItem(bootstrapKey(sessionId))
    if (!raw) return undefined
    const entry = JSON.parse(raw) as BootstrapEntry
    if (!entry?.session || entry.session.id !== sessionId) {
      clearSessionBootstrap(sessionId)
      return undefined
    }
    if (Date.now() - entry.storedAt > BOOTSTRAP_TTL_MS) {
      clearSessionBootstrap(sessionId)
      return undefined
    }
    return entry.session
  } catch {
    clearSessionBootstrap(sessionId)
    return undefined
  }
}

export function clearSessionBootstrap(sessionId: number) {
  if (typeof window === 'undefined') return
  try {
    window.sessionStorage.removeItem(bootstrapKey(sessionId))
  } catch {
    // Ignore storage errors.
  }
}

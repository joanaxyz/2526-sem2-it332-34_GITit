import { useMemo, useSyncExternalStore } from 'react'
import type { QueryKey } from '@tanstack/react-query'

import { effectiveCwd } from '@/shared/git/simulator/shell'
import { normalizeState } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import type { RepositorySnapshot } from '@/shared/level/types'

/**
 * Where each run's terminal stands, keyed by the run's query key: a folder
 * inside the project (`cwd`, `''` is the project root), or the workspace
 * folder above it (`outside`), where `git init <dir>` / `git clone` leave the
 * learner until they `cd` in.
 *
 * It lives outside repository state on purpose: `cd` moves the learner, not
 * the repository, so it must never change what evaluation compares. A new
 * run (or a page reload) opens the terminal at the project root, like a
 * fresh shell.
 */
export type TerminalLocation = { cwd: string; outside: boolean }

const PROJECT_ROOT: TerminalLocation = { cwd: '', outside: false }
const locations = new Map<string, TerminalLocation>()
const listeners = new Set<() => void>()

function storeKey(queryKey: QueryKey) {
  return JSON.stringify(queryKey)
}

export function terminalLocation(queryKey: QueryKey): TerminalLocation {
  return locations.get(storeKey(queryKey)) ?? PROJECT_ROOT
}

export function setTerminalLocation(queryKey: QueryKey, location: TerminalLocation) {
  const key = storeKey(queryKey)
  const current = terminalLocation(queryKey)
  const next = location.outside ? { cwd: '', outside: true } : { cwd: location.cwd, outside: false }
  if (current.cwd === next.cwd && current.outside === next.outside) return
  if (next.cwd || next.outside) locations.set(key, next)
  else locations.delete(key)
  listeners.forEach((listener) => listener())
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

/** The terminal's location for display, falling back if its folder no longer exists. */
export function useTerminalLocation(
  queryKey: QueryKey,
  repositoryState: RepositorySnapshot | undefined,
): TerminalLocation {
  const location = useSyncExternalStore(subscribe, () => terminalLocation(queryKey))
  return useMemo(() => {
    if (location.outside || !location.cwd || !repositoryState) return location
    const cwd = effectiveCwd(normalizeState(repositoryState as MutableRepositoryState), location.cwd)
    return cwd === location.cwd ? location : { cwd, outside: false }
  }, [location, repositoryState])
}

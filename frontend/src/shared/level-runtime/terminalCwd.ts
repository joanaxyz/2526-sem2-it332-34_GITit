import { useMemo, useSyncExternalStore } from 'react'
import type { QueryKey } from '@tanstack/react-query'

import { effectiveCwd } from '@/shared/git/simulator/shell'
import { normalizeState } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import type { RepositorySnapshot } from '@/shared/level/types'

/**
 * Working directory of each run's terminal, keyed by the run's query key.
 * It lives outside repository state on purpose: `cd` moves the learner, not
 * the repository, so it must never change what evaluation compares. A new
 * run (or a page reload) opens the terminal at the project root, like a
 * fresh shell.
 */
const directories = new Map<string, string>()
const listeners = new Set<() => void>()

function storeKey(queryKey: QueryKey) {
  return JSON.stringify(queryKey)
}

export function terminalCwd(queryKey: QueryKey) {
  return directories.get(storeKey(queryKey)) ?? ''
}

export function setTerminalCwd(queryKey: QueryKey, cwd: string) {
  const key = storeKey(queryKey)
  if ((directories.get(key) ?? '') === cwd) return
  if (cwd) directories.set(key, cwd)
  else directories.delete(key)
  listeners.forEach((listener) => listener())
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

/** The terminal's folder for display, falling back if it no longer exists. */
export function useTerminalCwd(queryKey: QueryKey, repositoryState: RepositorySnapshot | undefined) {
  const cwd = useSyncExternalStore(subscribe, () => terminalCwd(queryKey))
  return useMemo(() => {
    if (!cwd || !repositoryState) return cwd
    return effectiveCwd(normalizeState(repositoryState as MutableRepositoryState), cwd)
  }, [cwd, repositoryState])
}

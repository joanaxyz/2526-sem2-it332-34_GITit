import { entryStatus, isDeleteMarker, visibleProjectTree } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

/**
 * Filesystem view of the learner's working copy.
 *
 * Files come from the visible project tree minus deleted entries (a deleted
 * file is gone from disk even while `git status` still reports it). Folders
 * are implied by file paths, plus the optional `directories` list, which keeps
 * folders that hold no files. Git never tracks those, so they stay out of every
 * commit, index, and status view, exactly like an empty folder on disk.
 * `directories` is omitted when empty so states without empty folders keep
 * their existing shape and hashes.
 */

export type WorkspaceEntryKind = 'file' | 'directory'

export type WorkspaceEntry = {
  name: string
  path: string
  kind: WorkspaceEntryKind
}

export function liveFilePaths(state: MutableRepositoryState) {
  const paths = new Set<string>()
  for (const [path, value] of Object.entries(visibleProjectTree(state, true))) {
    if (!isDeleteMarker(entryStatus(value))) paths.add(path)
  }
  return paths
}

export function explicitDirectories(state: MutableRepositoryState): string[] {
  const value = state.directories
  if (!Array.isArray(value)) return []
  return value.filter((path): path is string => typeof path === 'string' && path.length > 0)
}

export function directoryPaths(state: MutableRepositoryState, files = liveFilePaths(state)) {
  const directories = new Set<string>()
  for (const path of [...files, ...explicitDirectories(state).map((directory) => `${directory}/`)]) {
    const parts = path.split('/').slice(0, -1)
    for (let index = 1; index <= parts.length; index += 1) {
      directories.add(parts.slice(0, index).join('/'))
    }
  }
  return directories
}

/** Kind of `path` in the working copy; `''` is the project root. */
export function pathKind(state: MutableRepositoryState, path: string): WorkspaceEntryKind | null {
  if (path === '') return 'directory'
  const files = liveFilePaths(state)
  if (files.has(path)) return 'file'
  return directoryPaths(state, files).has(path) ? 'directory' : null
}

export function directoryEntries(state: MutableRepositoryState, directory: string): WorkspaceEntry[] {
  const files = liveFilePaths(state)
  const directories = directoryPaths(state, files)
  const prefix = directory ? `${directory}/` : ''
  const entries = new Map<string, WorkspaceEntry>()
  for (const [kind, paths] of [['file', files], ['directory', directories]] as const) {
    for (const path of paths) {
      if (!path.startsWith(prefix)) continue
      const rest = path.slice(prefix.length)
      if (!rest || rest.includes('/')) continue
      entries.set(rest, { name: rest, path, kind })
    }
  }
  return [...entries.values()].sort((left, right) => compareNames(left.name, right.name))
}

/** Live files and folders strictly inside `directory`, sorted by path. */
export function descendantPaths(state: MutableRepositoryState, directory: string) {
  const files = liveFilePaths(state)
  const prefix = `${directory}/`
  return {
    files: [...files].filter((path) => path.startsWith(prefix)).sort(compareNames),
    directories: [...directoryPaths(state, files)].filter((path) => path.startsWith(prefix)).sort(compareNames),
  }
}

/**
 * Store the minimal folder list: only folders that contain no files and no
 * other listed folder. Every other folder is already implied by a path.
 */
export function setExplicitDirectories(state: MutableRepositoryState, candidates: Iterable<string>) {
  const files = liveFilePaths(state)
  const unique = [...new Set([...candidates].filter(Boolean))]
  const kept = unique.filter((directory) => {
    const prefix = `${directory}/`
    if (files.has(directory)) return false
    if ([...files].some((path) => path.startsWith(prefix))) return false
    return !unique.some((other) => other.startsWith(prefix))
  })
  if (kept.length) state.directories = kept.sort(compareNames)
  else delete state.directories
}

export function parentPath(path: string) {
  return path.split('/').slice(0, -1).join('/')
}

function compareNames(left: string, right: string) {
  if (left === right) return 0
  return left < right ? -1 : 1
}

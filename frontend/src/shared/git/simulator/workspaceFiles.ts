import type { RepositoryValue } from '@/shared/level/types'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'
import {
  clone,
  changeType,
  entryContent,
  entryStatus,
  headTree,
  isDeleteMarker,
  normalizeState,
  setOperationMetadata,
  visibleProjectTree,
} from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import {
  descendantPaths,
  directoryPaths,
  explicitDirectories,
  liveFilePaths,
  parentPath,
  setExplicitDirectories,
} from '@/shared/git/simulator/workspaceTree'

export class WorkspaceFileError extends Error {}

type VisibleProjectEntry = {
  status?: string
  content?: RepositoryValue
}

/**
 * Create a file, or a folder when `path` ends with `/`. A file may reuse the
 * path of a deleted tracked file: it then shows as modified, like restoring
 * the file by hand.
 */
export function createWorkspaceFile(
  repositoryState: MutableRepositoryState,
  { path, content = '' }: WorkspaceFileInput,
) {
  if (isDirectoryInput(path)) return createWorkspaceDirectory(repositoryState, { path })
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(path)
  validateNewPath(nextState, normalizedPath)
  const stagedDelete = isDeleteMarker(entryStatus(nextState.staging?.[normalizedPath]))
  nextState.working_tree ??= {}
  nextState.working_tree[normalizedPath] = {
    status: normalizedPath in headTree(nextState) && !stagedDelete ? 'modified' : 'untracked',
    content,
  }
  refreshIgnoredPaths(nextState)
  setExplicitDirectories(nextState, explicitDirectories(nextState))
  setOperationMetadata(nextState, { last_workspace_file_created: normalizedPath })
  return normalizeState(nextState)
}

/** Create an empty folder. Git ignores it until a file is added inside. */
export function createWorkspaceDirectory(repositoryState: MutableRepositoryState, { path }: { path: string }) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(trimTrailingSlashes(path))
  validateNewPath(nextState, normalizedPath)
  setExplicitDirectories(nextState, [...explicitDirectories(nextState), normalizedPath])
  setOperationMetadata(nextState, { last_workspace_directory_created: normalizedPath })
  return normalizeState(nextState)
}

export function writeWorkspaceFile(
  repositoryState: MutableRepositoryState,
  { path, content = '' }: WorkspaceFileInput,
) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(path)
  validateKnownPath(nextState, normalizedPath)
  const baseTree = headTree(nextState)
  nextState.working_tree ??= {}
  nextState.working_tree[normalizedPath] = {
    status: normalizedPath in baseTree ? 'modified' : 'untracked',
    content,
  }
  refreshIgnoredPaths(nextState)
  setOperationMetadata(nextState, { last_workspace_file_written: normalizedPath })
  return normalizeState(nextState)
}

/**
 * Delete a file or a whole folder from the working copy. The containing folder
 * stays on disk even when this removes its last file.
 */
export function deleteWorkspaceFile(repositoryState: MutableRepositoryState, { path }: { path: string }) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(trimTrailingSlashes(path))
  const targetPaths = targetFilePaths(nextState, normalizedPath)
  const keptDirectories = [
    ...explicitDirectories(nextState).filter((directory) => !isSameOrInside(directory, normalizedPath)),
    parentPath(normalizedPath),
  ]
  const baseTree = headTree(nextState)
  const conflicts = new Set(nextState.conflicts ?? [])

  nextState.working_tree ??= {}
  nextState.staging ??= {}
  for (const targetPath of targetPaths) {
    delete nextState.staging[targetPath]
    if (targetPath in baseTree) nextState.working_tree[targetPath] = 'deleted'
    else delete nextState.working_tree[targetPath]
    conflicts.delete(targetPath)
    delete nextState.conflict_details?.[targetPath]
  }
  nextState.conflicts = [...conflicts].sort()
  refreshIgnoredPaths(nextState)
  setExplicitDirectories(nextState, keptDirectories)
  setOperationMetadata(nextState, {
    last_workspace_file_deleted: normalizedPath,
    last_workspace_file_deleted_paths: targetPaths,
  })
  return normalizeState(nextState)
}

/**
 * Rename or move a file or folder (with everything inside it). The source's
 * containing folder stays on disk, and empty folders move along.
 */
export function renameWorkspaceFile(
  repositoryState: MutableRepositoryState,
  { path, newPath }: WorkspaceFileRenameInput,
) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(trimTrailingSlashes(path))
  const normalizedNewPath = normalizePath(trimTrailingSlashes(newPath))
  if (normalizedPath === normalizedNewPath) throw new WorkspaceFileError('Choose a different name.')
  if (normalizedNewPath.startsWith(`${normalizedPath}/`)) {
    throw new WorkspaceFileError('A folder cannot be moved inside itself.')
  }

  const sourcePaths = targetFilePaths(nextState, normalizedPath)
  validateNewPath(nextState, normalizedNewPath)
  const destinations = renameDestinations(normalizedPath, normalizedNewPath, sourcePaths)
  const explicit = explicitDirectories(nextState)
  const keptDirectories = [
    ...explicit.filter((directory) => !isSameOrInside(directory, normalizedPath)),
    ...explicit
      .filter((directory) => isSameOrInside(directory, normalizedPath))
      .map((directory) => `${normalizedNewPath}${directory.slice(normalizedPath.length)}`),
    parentPath(normalizedPath),
  ]

  const baseTree = headTree(nextState)
  const visibleTree = visibleProjectTree(nextState) as Record<string, VisibleProjectEntry>
  const conflicts = new Set(nextState.conflicts ?? [])
  const movedEntries = sourcePaths.map((sourcePath, index) => ({
    sourcePath,
    destination: destinations[index],
    content: clone(visibleTree[sourcePath]?.content ?? null),
  }))

  nextState.working_tree ??= {}
  nextState.staging ??= {}
  for (const { sourcePath, destination, content } of movedEntries) {
    delete nextState.staging[sourcePath]
    delete nextState.working_tree[sourcePath]
    if (sourcePath in baseTree) nextState.working_tree[sourcePath] = 'deleted'
    nextState.working_tree[destination] = {
      status: destination in baseTree ? changeType(baseTree[destination], content) : 'untracked',
      content,
    }
    conflicts.delete(sourcePath)
    delete nextState.conflict_details?.[sourcePath]
  }
  nextState.conflicts = [...conflicts].sort()
  refreshIgnoredPaths(nextState)
  setExplicitDirectories(nextState, keptDirectories)
  setOperationMetadata(nextState, {
    last_workspace_file_renamed_from: normalizedPath,
    last_workspace_file_renamed_to: normalizedNewPath,
  })
  return normalizeState(nextState)
}

function isDirectoryInput(path: string) {
  return String(path || '').replaceAll('\\', '/').trim().endsWith('/')
}

function trimTrailingSlashes(path: string) {
  return String(path || '').replaceAll('\\', '/').trim().replace(/\/+$/, '')
}

function isSameOrInside(path: string, directory: string) {
  return path === directory || path.startsWith(`${directory}/`)
}

function normalizePath(path: string) {
  const normalized = String(path || '').replaceAll('\\', '/').trim()
  if (!normalized) throw new WorkspaceFileError('File path is required.')
  if (normalized.endsWith('/')) throw new WorkspaceFileError('File path must include a file name.')
  if (/^[A-Za-z]:/.test(normalized) || normalized.startsWith('/')) {
    throw new WorkspaceFileError('Use a project-relative path.')
  }
  const parts = normalized.split('/').filter((part) => part && part !== '.')
  if (!parts.length || parts.some((part) => part === '..')) {
    throw new WorkspaceFileError('Parent-directory paths are not supported.')
  }
  if (parts[0] === '.git') throw new WorkspaceFileError('Files inside .git cannot be edited here.')
  if (parts.some((part) => /[<>|]/.test(part))) {
    throw new WorkspaceFileError('The file path contains unsupported characters.')
  }
  return parts.join('/')
}

/** A new file or folder needs a free path whose parents are not files. */
function validateNewPath(state: MutableRepositoryState, path: string) {
  const files = liveFilePaths(state)
  if (files.has(path)) throw new WorkspaceFileError(`${path} already exists.`)

  const parentParts = path.split('/').slice(0, -1)
  for (let index = 1; index <= parentParts.length; index += 1) {
    const parent = parentParts.slice(0, index).join('/')
    if (files.has(parent)) throw new WorkspaceFileError(`${parent} is a file, not a folder.`)
  }

  if (directoryPaths(state, files).has(path)) throw new WorkspaceFileError(`${path} is already a folder.`)
}

/**
 * Writing may target a deleted tracked file (that recreates it), so this
 * accepts every path git still knows about, not only files on disk.
 */
function validateKnownPath(state: MutableRepositoryState, path: string) {
  const knownPaths = new Set([
    ...Object.keys(visibleProjectTree(state)),
    ...Object.keys(state.staging ?? {}),
    ...Object.keys(state.working_tree ?? {}),
  ])
  if (!knownPaths.has(path)) throw new WorkspaceFileError(`${path} does not exist.`)
  const prefix = `${path}/`
  if ([...knownPaths].some((known) => known.startsWith(prefix))) {
    throw new WorkspaceFileError(`${path} is a folder, not a file.`)
  }
}

/** Files on disk at `path`: the file itself, or everything inside a folder. */
function targetFilePaths(state: MutableRepositoryState, path: string) {
  const files = liveFilePaths(state)
  if (files.has(path)) return [path]
  if (directoryPaths(state, files).has(path)) return descendantPaths(state, path).files
  throw new WorkspaceFileError(`${path} does not exist.`)
}

function renameDestinations(source: string, destination: string, sourcePaths: string[]) {
  if (sourcePaths.length === 1 && sourcePaths[0] === source) return [destination]
  const prefix = `${source}/`
  return sourcePaths.map((sourcePath) => `${destination}/${sourcePath.slice(prefix.length)}`)
}

function refreshIgnoredPaths(state: MutableRepositoryState) {
  const rules = gitignoreRules(state)
  if (!rules.length) return
  for (const [path, value] of Object.entries(state.working_tree ?? {})) {
    if (path === '.gitignore') continue
    if (entryStatus(value) === 'untracked' && rules.some((rule) => pathMatchesRule(path, rule))) {
      state.working_tree[path] = {
        status: 'ignored',
        content: entryContent(value),
      }
    } else if (entryStatus(value) === 'ignored' && !rules.some((rule) => pathMatchesRule(path, rule))) {
      state.working_tree[path] = {
        status: path in headTree(state) ? 'modified' : 'untracked',
        content: entryContent(value),
      }
    }
  }
}

function gitignoreRules(state: MutableRepositoryState) {
  const gitignore = state.working_tree?.['.gitignore'] ?? headTree(state)['.gitignore']
  const content = String(entryContent(gitignore) ?? '')
  return content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#') && !line.startsWith('!'))
}

function pathMatchesRule(path: string, rule: string) {
  const clean = rule.replace(/^\//, '')
  if (clean.endsWith('/')) return path.startsWith(clean)
  if (clean.includes('*')) {
    const pattern = new RegExp(`^${clean.split('*').map(escapeRegExp).join('.*')}$`)
    return pattern.test(path)
  }
  return path === clean || path.endsWith(`/${clean}`) || path.startsWith(`${clean}/`)
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

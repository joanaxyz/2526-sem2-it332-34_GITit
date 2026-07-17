import type { RepositoryValue } from '@/shared/level/types'
import {
  clone,
  changeType,
  entryContent,
  entryStatus,
  headTree,
  normalizeState,
  setOperationMetadata,
  visibleProjectTree,
} from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

export class WorkspaceFileError extends Error {}

export type WorkspaceFileInput = {
  path: string
  content: string
}

export type WorkspaceFileRenameInput = {
  path: string
  newPath: string
}

type VisibleProjectEntry = {
  status?: string
  content?: RepositoryValue
}

export function createWorkspaceFile(
  repositoryState: MutableRepositoryState,
  { path, content = '' }: WorkspaceFileInput,
) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(path)
  validateNewPath(nextState, normalizedPath)
  nextState.working_tree ??= {}
  nextState.working_tree[normalizedPath] = {
    status: 'untracked',
    content,
  }
  refreshIgnoredPaths(nextState)
  setOperationMetadata(nextState, { last_workspace_file_created: normalizedPath })
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

export function deleteWorkspaceFile(repositoryState: MutableRepositoryState, { path }: { path: string }) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(path)
  const targetPaths = targetFilePaths(nextState, normalizedPath)
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
  setOperationMetadata(nextState, {
    last_workspace_file_deleted: normalizedPath,
    last_workspace_file_deleted_paths: targetPaths,
  })
  return normalizeState(nextState)
}

export function renameWorkspaceFile(
  repositoryState: MutableRepositoryState,
  { path, newPath }: WorkspaceFileRenameInput,
) {
  const nextState = normalizeState(clone(repositoryState))
  const normalizedPath = normalizePath(path)
  const normalizedNewPath = normalizePath(newPath)
  if (normalizedPath === normalizedNewPath) throw new WorkspaceFileError('Choose a different name.')
  if (normalizedNewPath.startsWith(`${normalizedPath}/`)) {
    throw new WorkspaceFileError('A folder cannot be moved inside itself.')
  }

  const sourcePaths = targetFilePaths(nextState, normalizedPath)
  const destinations = renameDestinations(normalizedPath, normalizedNewPath, sourcePaths)
  validateDestinationPaths(nextState, destinations, sourcePaths)

  const baseTree = headTree(nextState)
  const visibleTree = visibleProjectTree(nextState) as Record<string, VisibleProjectEntry>
  const conflicts = new Set(nextState.conflicts ?? [])
  const movedEntries = sourcePaths.map((sourcePath, index) => {
    const visibleEntry = visibleTree[sourcePath]
    if (!visibleEntry || visibleEntry.status === 'deleted') {
      throw new WorkspaceFileError(`${sourcePath} cannot be renamed because it is deleted.`)
    }
    return {
      sourcePath,
      destination: destinations[index],
      content: clone(visibleEntry.content ?? null),
    }
  })

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
  setOperationMetadata(nextState, {
    last_workspace_file_renamed_from: normalizedPath,
    last_workspace_file_renamed_to: normalizedNewPath,
  })
  return normalizeState(nextState)
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

function validateNewPath(state: MutableRepositoryState, path: string) {
  const knownPaths = knownFilePaths(state)
  if (knownPaths.has(path)) throw new WorkspaceFileError(`${path} already exists.`)

  const parentParts = path.split('/').slice(0, -1)
  for (let index = 1; index <= parentParts.length; index += 1) {
    const parentPath = parentParts.slice(0, index).join('/')
    if (knownPaths.has(parentPath)) throw new WorkspaceFileError(`${parentPath} is a file, not a folder.`)
  }

  const prefix = `${path}/`
  if ([...knownPaths].some((known) => known.startsWith(prefix))) {
    throw new WorkspaceFileError(`${path} is already a folder.`)
  }
}

function validateKnownPath(state: MutableRepositoryState, path: string) {
  const knownPaths = knownFilePaths(state)
  if (!knownPaths.has(path)) throw new WorkspaceFileError(`${path} does not exist.`)
  const prefix = `${path}/`
  if ([...knownPaths].some((known) => known.startsWith(prefix))) {
    throw new WorkspaceFileError(`${path} is a folder, not a file.`)
  }
}

function targetFilePaths(state: MutableRepositoryState, path: string) {
  const knownPaths = knownFilePaths(state)
  if (knownPaths.has(path)) return [path]
  const prefix = `${path}/`
  const matches = [...knownPaths].filter((known) => known.startsWith(prefix)).sort()
  if (matches.length) return matches
  throw new WorkspaceFileError(`${path} does not exist.`)
}

function renameDestinations(source: string, destination: string, sourcePaths: string[]) {
  if (sourcePaths.length === 1 && sourcePaths[0] === source) return [destination]
  const prefix = `${source}/`
  return sourcePaths.map((sourcePath) => `${destination}/${sourcePath.replace(prefix, '')}`)
}

function validateDestinationPaths(state: MutableRepositoryState, destinations: string[], sourcePaths: string[]) {
  const occupiedPaths = new Set([...knownFilePaths(state)].filter((path) => !sourcePaths.includes(path)))
  for (const destination of destinations) {
    if (occupiedPaths.has(destination)) throw new WorkspaceFileError(`${destination} already exists.`)

    const parentParts = destination.split('/').slice(0, -1)
    for (let index = 1; index <= parentParts.length; index += 1) {
      const parentPath = parentParts.slice(0, index).join('/')
      if (occupiedPaths.has(parentPath)) throw new WorkspaceFileError(`${parentPath} is a file, not a folder.`)
    }

    const prefix = `${destination}/`
    if ([...occupiedPaths].some((known) => known.startsWith(prefix))) {
      throw new WorkspaceFileError(`${destination} is already a folder.`)
    }
  }
}

function knownFilePaths(state: MutableRepositoryState) {
  return new Set([
    ...Object.keys(visibleProjectTree(state)),
    ...Object.keys(state.staging ?? {}),
    ...Object.keys(state.working_tree ?? {}),
  ])
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

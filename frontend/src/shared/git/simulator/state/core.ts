import type { RepositoryCommit, RepositoryValue } from '@/shared/level/types'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

const DELETE_MARKERS = new Set(['deleted', 'removed', 'delete', 'remove'])

const DISPLAY_STATUS_ALIASES: Record<string, string> = {
  added: 'added',
  add: 'added',
  new: 'added',
  untracked: 'untracked',
  modified: 'modified',
  changed: 'modified',
  updated: 'modified',
  staged: 'staged',
  ignored: 'ignored',
  conflict: 'conflicted',
  conflicted: 'conflicted',
  clean: 'clean',
  deleted: 'deleted',
  removed: 'deleted',
  delete: 'deleted',
  remove: 'deleted',
}

export function clone<T>(value: T): T {
  return value === undefined ? value : structuredClone(value)
}

export function isRecord(value: unknown): value is Record<string, RepositoryValue> {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value))
}

export function asRecord(value: unknown): Record<string, RepositoryValue> {
  return isRecord(value) ? value : {}
}

export function normalizeState(input?: Partial<MutableRepositoryState> | null): MutableRepositoryState {
  const state = clone((input ?? {}) as MutableRepositoryState)
  delete state.project_tree
  delete state.visible_tree
  ensureShape(state)
  normalizeCommits(state)
  normalizeHead(state)
  return state
}

export function ensureShape(state: MutableRepositoryState) {
  state.repository_initialized ??= true
  state.commits ??= []
  state.branches ??= {}
  state.head = isRecord(state.head) ? state.head : { type: 'branch', name: 'main' }
  state.staging ??= {}
  state.working_tree ??= {}
  state.conflicts ??= []
  state.conflict_details ??= {}
  state.remotes ??= {}
  state.remote_branches ??= {}
  state.upstream_tracking ??= {}
  state.tags ??= {}
  state.remote_tags ??= {}
  state.stash_stack ??= []
  state.reflog ??= []
  state.partial_hunks ??= {}
  state.replaced_commits ??= {}
  state.operation_metadata ??= {}
}

export function normalizeHead(state: MutableRepositoryState) {
  const head = state.head
  if (head?.type === 'branch') {
    head.target = state.branches?.[head.name ?? ''] ?? null
  }
}

export function normalizeCommits(state: MutableRepositoryState) {
  const commits = state.commits ?? []
  const commitsById = new Map<string, RepositoryCommit>()

  commits.forEach((commit, index) => {
    commit.id ||= `c${index}`
    commit.message ||= commit.id
    commit.parents ||= []

    const parentTree = parentTreeFor(commit, commitsById)
    const authoredTree = isRecord(commit.tree)
    const tree = authoredTree ? clone(commit.tree ?? {}) : clone(parentTree)

    if (authoredTree) {
      const inferred = diffTrees(parentTree, tree)
      const authored = normalizeChanges(commit.changes)
      commit.changes = Object.keys(authored).length ? authored : inferred
    } else if (commit.changes && Object.keys(commit.changes).length) {
      const changes = normalizeChanges(commit.changes)
      commit.changes = changes
      commit.tree = applyChanges(parentTree, changes)
    } else {
      const legacyFiles = clone(commit.files ?? {})
      const changes = changesFromEntries(parentTree, legacyFiles)
      commit.changes = changes
      commit.tree = applyChanges(parentTree, changes)
    }

    commit.tree = commit.tree ?? tree
    commit.is_merge = (commit.parents ?? []).length > 1
    commit.files ??= filesFromChanges(commit.changes ?? {})
    commit.order ??= index
    commitsById.set(commit.id, commit)
  })
}

function parentTreeFor(commit: RepositoryCommit, commitsById: Map<string, RepositoryCommit>) {
  const parent = commitsById.get((commit.parents ?? [])[0] ?? '')
  return clone(parent?.tree ?? {})
}

export function normalizeChanges(changes?: Record<string, RepositoryValue>): Record<string, { change_type: string; before: RepositoryValue; after: RepositoryValue }> {
  const normalized: Record<string, { change_type: string; before: RepositoryValue; after: RepositoryValue }> = {}
  for (const [path, payload] of Object.entries(changes ?? {})) {
    if (isRecord(payload)) {
      const before = (payload.before ?? null) as RepositoryValue
      const after = (payload.after ?? null) as RepositoryValue
      normalized[path] = {
        change_type: String(payload.change_type ?? changeType(before, after)),
        before,
        after,
      }
    } else {
      const before = null
      const after = isDeleteMarker(payload) ? null : payload
      normalized[path] = {
        change_type: String(payload ?? changeType(before, after)),
        before,
        after,
      }
    }
  }
  return normalized
}

export function changesFromEntries(baseTree: Record<string, RepositoryValue>, entries?: Record<string, RepositoryValue>) {
  const changes: Record<string, { change_type: string; before: RepositoryValue; after: RepositoryValue }> = {}
  for (const [path, marker] of Object.entries(entries ?? {})) {
    const before = baseTree[path] ?? null
    const after = isDeleteMarker(marker) || isDeleteMarker(entryStatus(marker)) ? null : entryContent(marker)
    changes[path] = {
      change_type: changeType(before, after, marker),
      before,
      after,
    }
  }
  return changes
}

export function diffTrees(before: Record<string, RepositoryValue>, after: Record<string, RepositoryValue>) {
  const changes: Record<string, { change_type: string; before: RepositoryValue; after: RepositoryValue }> = {}
  for (const path of [...new Set([...Object.keys(before ?? {}), ...Object.keys(after ?? {})])].sort()) {
    const oldValue = before[path] ?? null
    const newValue = after[path] ?? null
    if (JSON.stringify(oldValue) === JSON.stringify(newValue)) continue
    changes[path] = {
      change_type: changeType(oldValue, newValue),
      before: oldValue,
      after: newValue,
    }
  }
  return changes
}

export function applyChanges(baseTree: Record<string, RepositoryValue>, changes?: Record<string, { change_type?: string; after?: RepositoryValue }>) {
  const tree = clone(baseTree ?? {})
  for (const [path, payload] of Object.entries(changes ?? {})) {
    if (isDeleteMarker(payload.change_type) || payload.after === null || payload.after === undefined) {
      delete tree[path]
    } else {
      tree[path] = clone(payload.after)
    }
  }
  return tree
}

export function filesFromChanges(changes?: Record<string, { change_type?: string }>) {
  const files: Record<string, RepositoryValue> = {}
  for (const [path, payload] of Object.entries(changes ?? {})) {
    files[path] = payload.change_type ?? 'modified'
  }
  return files
}

export function changeType(before?: RepositoryValue | null, after?: RepositoryValue | null, marker?: RepositoryValue | null) {
  if (isDeleteMarker(marker) || after === null || after === undefined) return 'deleted'
  if (before === null || before === undefined) return 'added'
  return 'modified'
}

export function isDeleteMarker(value: unknown) {
  return DELETE_MARKERS.has(String(value ?? '').toLowerCase())
}

export function entryStatus(value: unknown) {
  if (isRecord(value)) {
    const status = value.status ?? value.state ?? value.change_type
    if (status !== undefined && status !== null) return String(status).toLowerCase()
    if (value.ignored === true) return 'ignored'
    if (value.untracked === true) return 'untracked'
  }
  return String(value ?? '').toLowerCase()
}

export function entryContent(value: unknown): RepositoryValue {
  if (isRecord(value)) {
    if ('content' in value) return clone(value.content)
    if ('after' in value) return clone(value.after)
    if ('value' in value) return clone(value.value)
  }
  return clone(value as RepositoryValue)
}

export function tokenHaystack(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (Array.isArray(value)) return value.map(tokenHaystack).join(' ')
  if (isRecord(value)) return Object.values(value).map(tokenHaystack).join(' ')
  return String(value)
}

export function headBranch(state: MutableRepositoryState) {
  return state.head?.type === 'branch' ? state.head.name : null
}

export function headCommit(state: MutableRepositoryState) {
  if (state.head?.type === 'branch') return state.branches?.[state.head.name ?? ''] ?? null
  return state.head?.target ?? null
}

export function commitById(state: MutableRepositoryState, commitId?: string | null) {
  if (!commitId) return null
  return (state.commits ?? []).find((commit) => commit.id === commitId) ?? null
}

export function treeForCommit(state: MutableRepositoryState, commitId?: string | null) {
  return clone(commitById(state, commitId)?.tree ?? {})
}

export function headTree(state: MutableRepositoryState) {
  return treeForCommit(state, headCommit(state))
}

export function nextCommitId(state: MutableRepositoryState) {
  const existing = new Set((state.commits ?? []).map((commit) => commit.id))
  let index = 0
  while (existing.has(`c${index}`)) index += 1
  return `c${index}`
}

export function commitPayload({
  state,
  commitId,
  message,
  parents,
  tree,
  changes,
}: {
  state: MutableRepositoryState
  commitId: string
  message: string
  parents: string[]
  tree: Record<string, RepositoryValue>
  changes: Record<string, { change_type?: string; before?: RepositoryValue; after?: RepositoryValue }>
}): RepositoryCommit {
  return {
    id: commitId,
    message,
    parents,
    tree: clone(tree),
    changes: clone(changes),
    files: filesFromChanges(changes),
    author: 'GIT it',
    order: state.commits?.length ?? 0,
    is_merge: parents.length > 1,
  }
}

export function setOperationMetadata(state: MutableRepositoryState, metadata: Record<string, RepositoryValue | undefined>) {
  state.operation_metadata ??= {}
  for (const [key, value] of Object.entries(metadata)) {
    if (value === undefined) continue
    state.operation_metadata[key] = clone(value)
    state[key] = clone(value)
  }
}

export function recordReflog(state: MutableRepositoryState, target: string | null | undefined, message: string) {
  if (!target) return
  state.reflog ??= []
  state.reflog.push({
    ref: `HEAD@{${state.reflog.length}}`,
    target,
    message,
  })
}

export function setHeadCommit(state: MutableRepositoryState, commitId: string | null) {
  const branch = headBranch(state)
  if (branch) {
    state.branches ??= {}
    state.branches[branch] = commitId
  } else {
    state.head.target = commitId
  }
  normalizeHead(state)
  recordReflog(state, commitId, 'move HEAD')
}

export function asList(value: unknown): RepositoryValue[] {
  if (value === null || value === undefined || value === '') return []
  return Array.isArray(value) ? value : [value as RepositoryValue]
}

export function entryTokens(value: unknown): string[] {
  if (value === null || value === undefined) return []
  if (isRecord(value)) {
    for (const key of ['hunks', 'tokens', 'target_hunks', 'leftover_hunks']) {
      if (key in value) return asList(value[key]).map(String)
    }
  }
  const haystack = tokenHaystack(value)
  return haystack ? [haystack] : []
}

export function cleanupPartialHunksAfterCommit(state: MutableRepositoryState, stagedEntries: Record<string, RepositoryValue>) {
  state.partial_hunks ??= {}
  for (const [path, stagedValue] of Object.entries(stagedEntries)) {
    if (entryStatus(stagedValue) !== 'partial') continue
    const authored = state.partial_hunks[path]
    if (!isRecord(authored)) continue
    const leftover = asList(authored.leftover_hunks ?? authored.remaining_hunks ?? authored.leftover)
    if (leftover.length) state.partial_hunks[path] = { target_hunks: [], leftover_hunks: leftover }
    else delete state.partial_hunks[path]
  }
}

export function displayStatus(value: unknown, fallback = 'changed') {
  const status = entryStatus(value)
  if (!status || status === 'none') return fallback
  return DISPLAY_STATUS_ALIASES[status] ?? fallback
}


import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import {
  clone,
  displayStatus,
  entryContent,
  entryStatus,
  headTree,
  isDeleteMarker,
  normalizeState,
} from '@/shared/git/simulator/state/core'

export function visibleProjectTree(input: MutableRepositoryState | RepositorySnapshot, assumeNormalized = false) {
  const normalized = assumeNormalized ? (input as MutableRepositoryState) : normalizeState(input)
  const baseTree = headTree(normalized)
  const visible: Record<string, RepositoryValue> = {}

  for (const [path, content] of Object.entries(baseTree)) {
    visible[path] = { status: 'clean', source: 'head', content: clone(content) }
  }

  for (const [path, value] of Object.entries(normalized.staging ?? {})) {
    const status = entryStatus(value)
    if (isDeleteMarker(status) || isDeleteMarker(value)) {
      visible[path] = { status: 'deleted', source: 'staging', content: null }
    } else {
      visible[path] = {
        status: displayStatus(value, path in baseTree ? 'modified' : 'added'),
        source: 'staging',
        content: entryContent(value),
      }
    }
  }

  const stagedPaths = new Set(Object.keys(normalized.staging ?? {}))
  for (const [path, value] of Object.entries(normalized.working_tree ?? {})) {
    const status = entryStatus(value)
    if (isDeleteMarker(status) || isDeleteMarker(value)) {
      visible[path] = { status: 'deleted', source: 'working_tree', content: null }
    } else {
      visible[path] = {
        status: displayStatus(value, path in baseTree || stagedPaths.has(path) ? 'modified' : 'untracked'),
        source: 'working_tree',
        content: entryContent(value),
      }
    }
  }

  return Object.fromEntries(Object.entries(visible).sort(([left], [right]) => left.localeCompare(right)))
}

export function snapshotForCommand(input: MutableRepositoryState, alreadyNormalized = false): RepositorySnapshot {
  const state = alreadyNormalized ? input : normalizeState(input)
  const head = state.head?.type === 'branch'
    ? { ...state.head, target: state.branches?.[state.head.name ?? ''] ?? null }
    : { ...state.head }
  return {
    repository_initialized: state.repository_initialized,
    commits: clone(state.commits ?? []),
    branches: clone(state.branches ?? {}),
    head,
    staging: clone(state.staging ?? {}),
    working_tree: clone(state.working_tree ?? {}),
    conflicts: clone(state.conflicts ?? []),
    conflict_details: clone(state.conflict_details ?? {}),
    remotes: clone(state.remotes ?? {}),
    remote_branches: clone(state.remote_branches ?? {}),
    upstream_tracking: clone(state.upstream_tracking ?? {}),
    tags: clone(state.tags ?? {}),
    remote_tags: clone(state.remote_tags ?? {}),
    stash_stack: clone(state.stash_stack ?? []),
    partial_hunks: clone(state.partial_hunks ?? {}),
    replaced_commits: clone(state.replaced_commits ?? {}),
    reflog: clone(state.reflog ?? []),
    operation_metadata: clone(state.operation_metadata ?? {}),
    config: clone(state.config ?? {}),
    remote_fixtures: clone(state.remote_fixtures),
    remote_updates: clone(state.remote_updates ?? {}),
    merge_abort_state: clone(state.merge_abort_state),
    merge_parent: state.merge_parent ?? null,
    merge_conflicts: clone(state.merge_conflicts),
    merge_resolutions: clone(state.merge_resolutions ?? {}),
    conflict_on_merge: state.conflict_on_merge,
    conflict_files: clone(state.conflict_files ?? []),
    merge_conflict_files: clone(state.merge_conflict_files ?? []),
    cherry_pick_in_progress: state.cherry_pick_in_progress,
    cherry_pick_original_head: state.cherry_pick_original_head ?? null,
    rebase_state: clone(state.rebase_state),
  } as RepositorySnapshot
}

export function snapshot(input: MutableRepositoryState, alreadyNormalized = false): RepositorySnapshot {
  const state = alreadyNormalized ? input : normalizeState(input)
  const projectTree = visibleProjectTree(state, true)
  return {
    ...snapshotForCommand(state, true),
    project_tree: projectTree,
    visible_tree: projectTree,
  }
}

export function stateAffectsVisibleTree(previous: MutableRepositoryState, next: MutableRepositoryState) {
  for (const key of ['commits', 'staging', 'working_tree', 'conflicts', 'branches', 'head'] as const) {
    if (JSON.stringify(previous[key]) !== JSON.stringify(next[key])) return true
  }
  return false
}

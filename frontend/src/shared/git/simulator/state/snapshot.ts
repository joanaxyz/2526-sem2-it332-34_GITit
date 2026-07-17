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
  const state = alreadyNormalized ? clone(input) : normalizeState(input)
  delete state.project_tree
  delete state.visible_tree
  return state
}

export function snapshot(input: MutableRepositoryState, alreadyNormalized = false): RepositorySnapshot {
  const state = alreadyNormalized ? input : normalizeState(input)
  const projectTree = visibleProjectTree(state, true)
  return {
    ...snapshotForCommand(state, true),
    project_tree: projectTree,
    visible_tree: clone(projectTree),
  }
}

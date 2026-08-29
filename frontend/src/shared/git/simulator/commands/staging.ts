import type { RepositoryValue } from '@/shared/level/types'
import { hasOption, optionValues } from '@/shared/git/simulator/parser'
import { asList, changeType, clone, entryStatus, entryTokens, headCommit, headTree, isRecord, recordReflog, setHeadCommit, setOperationMetadata, treeForCommit } from '@/shared/git/simulator/state'
import { resolveRevision } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitAdd(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '-p') || hasOption(parsed, '--patch')) {
    const paths = stagePatch(state, parsed.pathspecs)
    return { command: 'add', details: { paths, mode: 'patch' } }
  }
  const includeTracked = true
  const includeUntracked = !(hasOption(parsed, '-u') || hasOption(parsed, '--update'))
  const selected = selectedPaths(state, parsed.pathspecs, { includeTracked, includeUntracked })
  stageSelected(state, selected)
  return { command: 'add', details: { paths: selected, mode: includeUntracked ? 'all' : 'tracked' } }
}

export function selectedPaths(
  state: MutableRepositoryState,
  paths: string[],
  { includeTracked, includeUntracked }: { includeTracked: boolean; includeUntracked: boolean },
) {
  const workingTree = state.working_tree ?? {}
  const baseTree = headTree(state)
  let requested = paths.filter((path) => path !== '--')
  if (!requested.length || requested.includes('.')) requested = Object.keys(workingTree).sort()
  const selected: string[] = []
  const missing: string[] = []

  for (const requestedPath of requested) {
    const matches = matchingPaths(workingTree, requestedPath)
    if (!matches.length) {
      missing.push(requestedPath)
      continue
    }
    for (const path of matches) {
      const value = workingTree[path]
      const status = entryStatus(value)
      if (status === 'ignored') continue
      const tracked = path in baseTree || ['modified', 'deleted', 'removed'].includes(status)
      const untracked = !tracked || status === 'untracked'
      if ((tracked && includeTracked) || (untracked && includeUntracked)) selected.push(path)
    }
  }
  if (missing.length) {
    throw new SimulatorCommandError(`fatal: pathspec '${missing.join("', '")}' did not match any files`)
  }
  return [...new Set(selected)].sort()
}

function matchingPaths(workingTree: Record<string, RepositoryValue>, requestedPath: string) {
  if (requestedPath.endsWith('/')) return Object.keys(workingTree).filter((path) => path.startsWith(requestedPath)).sort()
  if (requestedPath in workingTree) return [requestedPath]
  const prefix = `${requestedPath.replace(/\/$/, '')}/`
  return Object.keys(workingTree).filter((path) => path.startsWith(prefix)).sort()
}

export function stageSelected(state: MutableRepositoryState, paths: string[]) {
  state.working_tree ??= {}
  state.staging ??= {}
  const conflicts = new Set(state.conflicts ?? [])
  for (const path of paths) {
    if (entryStatus(state.working_tree[path]) === 'ignored') continue
    state.staging[path] = clone(state.working_tree[path] ?? 'updated')
    delete state.working_tree[path]
    conflicts.delete(path)
    delete (state.conflict_details ?? {})[path]
  }
  state.conflicts = [...conflicts].sort()
}

function stagePatch(state: MutableRepositoryState, paths: string[]) {
  state.working_tree ??= {}
  state.partial_hunks ??= {}
  const selected = paths.length
    ? paths
    : Object.keys(state.partial_hunks).length
      ? Object.keys(state.partial_hunks)
      : Object.entries(state.working_tree)
          .filter(([, value]) => !['ignored', 'untracked'].includes(entryStatus(value)))
          .map(([path]) => path)
  if (!selected.length) throw new SimulatorCommandError('No tracked changes available for patch staging.')

  state.staging ??= {}
  const stagedPaths: string[] = []
  for (const path of selected) {
    if (!(path in state.working_tree) && !(path in state.partial_hunks)) continue
    if (entryStatus(state.working_tree[path]) === 'ignored') continue
    const authored = state.partial_hunks[path]
    let targetHunks: RepositoryValue[]
    let leftoverHunks: RepositoryValue[]
    if (isRecord(authored)) {
      targetHunks = asList(authored.target_hunks ?? authored.staged_hunks ?? authored.stage)
      leftoverHunks = asList(authored.leftover_hunks ?? authored.remaining_hunks ?? authored.leftover)
    } else {
      const hunks = asList(authored)
      targetHunks = hunks.slice(0, 1)
      leftoverHunks = hunks.slice(1)
    }
    if (targetHunks.length || leftoverHunks.length) {
      state.staging[path] = { status: 'partial', hunks: targetHunks }
      if (leftoverHunks.length) state.working_tree[path] = { status: 'modified', hunks: leftoverHunks }
      else delete state.working_tree[path]
    } else {
      state.staging[path] = { status: 'partial', hunks: entryTokens(state.working_tree[path]) }
      state.working_tree[path] = 'modified'
    }
    stagedPaths.push(path)
  }
  return stagedPaths
}

export function gitRm(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const cached = hasOption(parsed, '--cached')
  const baseTree = headTree(state)
  const removed: string[] = []
  for (const path of expandPathspecs(baseTree, parsed.pathspecs)) {
    if (!(path in baseTree) && !(path in (state.staging ?? {}))) {
      throw new SimulatorCommandError(`fatal: pathspec '${path}' did not match any files`)
    }
    state.staging ??= {}
    state.staging[path] = 'deleted'
    if (!cached) {
      // `git rm` removes the file from the working tree; the deletion lives in
      // the index (staging). Leaving a tombstone here would wrongly read as an
      // unstaged change still present in the worktree.
      state.working_tree ??= {}
      delete state.working_tree[path]
    } else {
      state.working_tree ??= {}
      state.working_tree[path] = { status: 'untracked', content: baseTree[path] ?? '' }
    }
    removed.push(path)
  }
  setOperationMetadata(state, { last_rm_cached_paths: cached ? removed : [] })
  return { command: 'rm', details: { removed, cached } }
}

function expandPathspecs(baseTree: Record<string, RepositoryValue>, paths: string[]) {
  const expanded: string[] = []
  for (const spec of paths) {
    if (spec.endsWith('/')) expanded.push(...Object.keys(baseTree).filter((path) => path.startsWith(spec)))
    else {
      const prefix = `${spec.replace(/\/$/, '')}/`
      const matches = Object.keys(baseTree).filter((path) => path.startsWith(prefix))
      expanded.push(...(matches.length ? matches : [spec]))
    }
  }
  return [...new Set(expanded)].sort()
}

export function gitRestore(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  let paths = parsed.pathspecs
  const source = String(optionValues(parsed, '--source').at(-1) ?? '')
  if (hasOption(parsed, '--staged')) {
    if (source) throw new SimulatorCommandError('fatal: --source with --staged is not supported in this simulator', 129)
    if (paths.includes('.')) paths = Object.keys(state.staging ?? {}).sort()
    const unstaged: string[] = []
    for (const path of paths) {
      if (path in (state.staging ?? {})) {
        state.working_tree ??= {}
        state.working_tree[path] = clone(state.staging?.[path] ?? 'modified')
        delete state.staging?.[path]
        unstaged.push(path)
      }
    }
    return { command: 'restore', details: { unstaged } }
  }
  const restored: string[] = []
  if (source) {
    const sourceCommit = resolveRevision(state, source)
    if (!sourceCommit) throw new SimulatorCommandError(`fatal: could not resolve ${source}`)
    const sourceTree = treeForCommit(state, sourceCommit)
    for (const path of paths) {
      state.working_tree ??= {}
      if (!(path in sourceTree)) state.working_tree[path] = 'deleted'
      else state.working_tree[path] = { status: changeType(headTree(state)[path] ?? null, sourceTree[path]), content: clone(sourceTree[path]) }
      restored.push(path)
    }
    setOperationMetadata(state, { last_restore_source: sourceCommit, last_restore_paths: restored })
    return { command: 'restore', details: { restored, source: sourceCommit } }
  }
  if (paths.includes('.')) {
    paths = Object.keys(state.working_tree ?? {}).filter((path) => entryStatus(state.working_tree?.[path]) !== 'ignored' && entryStatus(state.working_tree?.[path]) !== 'untracked').sort()
  }
  const conflicts = new Set(state.conflicts ?? [])
  for (const path of paths) {
    if (!(path in (state.working_tree ?? {})) && !(path in headTree(state))) {
      throw new SimulatorCommandError(`error: pathspec '${path}' did not match any file(s) known to git`)
    }
    delete state.working_tree?.[path]
    conflicts.delete(path)
    delete state.conflict_details?.[path]
    restored.push(path)
  }
  state.conflicts = [...conflicts].sort()
  return { command: 'restore', details: { restored } }
}

export function gitReset(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const targetExpr = parsed.args[0]
  const mode = hasOption(parsed, '--soft') ? 'soft' : hasOption(parsed, '--mixed') ? 'mixed' : 'hard'
  const target = resolveRevision(state, targetExpr)
  if (!target) throw new SimulatorCommandError(`fatal: ambiguous argument '${targetExpr}'`)
  const oldHead = headCommit(state)
  const oldTree = treeForCommit(state, oldHead)
  const targetTree = treeForCommit(state, target)
  state.merge_abort_state = clone(state)
  setHeadCommit(state, target)
  if (mode === 'soft') {
    state.staging = entriesFromTreeDiff(targetTree, oldTree)
  } else if (mode === 'mixed') {
    state.staging = {}
    state.working_tree = entriesFromTreeDiff(targetTree, oldTree)
  } else {
    state.staging = {}
    state.working_tree = {}
    state.conflicts = []
    delete state.conflict_details
    delete state.merge_parent
    delete state.cherry_pick_in_progress
    delete state.cherry_pick_original_head
  }
  setOperationMetadata(state, {
    last_reset_mode: mode,
    last_reset_target: target,
    last_reset_target_expr: targetExpr,
    last_reset_previous_head: oldHead,
  })
  recordReflog(state, target, `reset: moving to ${targetExpr}`)
  return {
    command: 'reset',
    stdout: mode === 'hard' ? `HEAD is now at ${target}` : mode === 'mixed' ? 'Unstaged changes after reset' : '',
  }
}

function entriesFromTreeDiff(before: Record<string, RepositoryValue>, after: Record<string, RepositoryValue>) {
  const entries: Record<string, RepositoryValue> = {}
  for (const path of new Set([...Object.keys(before), ...Object.keys(after)])) {
    const oldValue = before[path] ?? null
    const newValue = after[path] ?? null
    if (JSON.stringify(oldValue) === JSON.stringify(newValue)) continue
    entries[path] = newValue === null ? 'deleted' : { status: changeType(oldValue, newValue), content: clone(newValue) }
  }
  return entries
}

import type { RepositoryValue } from '@/shared/level/types'
import { hasOption, optionValues } from '@/shared/git/simulator/parser'
import { applyChanges, changeType, clone, commitById, commitPayload, diffTrees, headBranch, headCommit, isRecord, nextCommitId, setHeadCommit, setOperationMetadata, treeForCommit } from '@/shared/git/simulator/state'
import { createCommit } from '@/shared/git/simulator/commands/commits'
import { commonAncestor, commitsSince, isAncestor, resolveRef } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitMerge(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '--abort')) return abortMerge(state)
  if (hasOption(parsed, '--continue')) return continueMerge(state)
  if (hasOption(parsed, '--squash')) return squashMerge(state, parsed.args[0])
  return mergeBranch(state, parsed.args[0], hasOption(parsed, '--no-ff'))
}

function abortMerge(state: MutableRepositoryState): CommandOutcome {
  if (!state.merge_parent && !state.conflicts?.length) throw new SimulatorCommandError('fatal: There is no merge to abort (MERGE_HEAD missing).')
  const restored = state.merge_abort_state
  if (restored && isRecord(restored) && Object.keys(restored).length > 0) {
    for (const key of Object.keys(state)) delete state[key]
    Object.assign(state, clone(restored))
    setOperationMetadata(state, { last_merge_aborted: true })
    return { command: 'merge', stdout: '' }
  }
  state.conflicts = []
  state.staging = {}
  state.working_tree = {}
  delete state.conflict_details
  delete state.merge_parent
  setOperationMetadata(state, { last_merge_aborted: true })
  return { command: 'merge', stdout: '' }
}

function continueMerge(state: MutableRepositoryState) {
  if (!state.merge_parent) throw new SimulatorCommandError('fatal: There is no merge in progress (MERGE_HEAD missing).')
  if (state.conflicts?.length) throw new SimulatorCommandError('Committing is not possible because you have unmerged files.')
  return createCommit(state, null, [])
}

function squashMerge(state: MutableRepositoryState, branch: string): CommandOutcome {
  if (state.merge_parent || state.conflicts?.length) throw new SimulatorCommandError('error: Merging is not possible because you have unmerged files.')
  const targetId = resolveRef(state, branch)
  if (!targetId) throw new SimulatorCommandError(`merge: ${branch} - not something we can merge`)
  const currentId = headCommit(state)
  if (currentId === targetId) return { command: 'merge', stdout: 'Already up to date.' }
  const currentTree = treeForCommit(state, currentId)
  const targetTree = treeForCommit(state, targetId)
  state.staging ??= {}
  for (const [path, value] of Object.entries(targetTree)) {
    if (JSON.stringify(value) !== JSON.stringify(currentTree[path])) {
      state.staging[path] = { status: changeType(currentTree[path] ?? null, value), content: clone(value ?? null) }
    }
  }
  for (const path of Object.keys(currentTree)) {
    if (!(path in targetTree)) state.staging[path] = 'deleted'
  }
  setOperationMetadata(state, { last_merge_branch: branch, last_merge_target: targetId, squash_merge_staged: true })
  return { command: 'merge', stdout: 'Squash commit -- not updating HEAD\nAutomatic merge went well; stopped before committing as requested' }
}

export function mergeBranch(state: MutableRepositoryState, branch: string, noFf: boolean): CommandOutcome {
  if (state.merge_parent || state.conflicts?.length) throw new SimulatorCommandError('error: Merging is not possible because you have unmerged files.')
  const targetId = resolveRef(state, branch)
  if (!targetId) throw new SimulatorCommandError(`merge: ${branch} - not something we can merge`)
  const currentId = headCommit(state)
  if (currentId === targetId) return { command: 'merge', stdout: 'Already up to date.' }

  const beforeMerge = clone(state)
  const currentTree = treeForCommit(state, currentId)
  const targetTree = treeForCommit(state, targetId)
  const baseId = commonAncestor(state, currentId, targetId)
  const baseTree = treeForCommit(state, baseId)
  const conflictPaths = new Set(authoredConflictPaths(state))
  for (const path of overlappingConflicts(baseTree, currentTree, targetTree)) conflictPaths.add(path)

  const stagedPaths: string[] = []
  for (const path of [...new Set([...Object.keys(currentTree), ...Object.keys(targetTree)])].sort()) {
    if (conflictPaths.has(path) || JSON.stringify(currentTree[path]) === JSON.stringify(targetTree[path])) continue
    const after = targetTree[path] ?? null
    state.staging ??= {}
    state.staging[path] = after === null ? 'deleted' : { status: changeType(currentTree[path] ?? null, after), content: clone(after) }
    stagedPaths.push(path)
  }

  if (conflictPaths.size) {
    state.merge_parent = targetId
    state.merge_abort_state = beforeMerge
    state.conflicts = [...conflictPaths].sort()
    state.conflict_details ??= {}
    state.working_tree ??= {}
    for (const path of state.conflicts) {
      state.conflict_details[path] = {
        base: clone(baseTree[path] ?? null),
        ours: clone(currentTree[path] ?? null),
        theirs: clone(targetTree[path] ?? null),
        resolution: clone(state.merge_resolutions?.[path] ?? null),
        merge_branch: branch,
      }
      state.working_tree[path] = conflictEntry(branch, baseTree[path] ?? null, currentTree[path] ?? null, targetTree[path] ?? null, state.merge_resolutions?.[path] ?? null)
    }
    setOperationMetadata(state, { last_merge_branch: branch, last_merge_target: targetId, last_merge_conflicted: true, last_merge_conflict_paths: state.conflicts })
    return {
      command: 'merge',
      details: { branch, conflicts: state.conflicts },
      exitCode: 1,
      stdout: `Auto-merging ${state.conflicts.join(', ')}\nCONFLICT (content): Merge conflict in ${state.conflicts.join(', ')}\nAutomatic merge failed; fix conflicts and then commit the result.`,
    }
  }

  if (!noFf && isAncestor(state, currentId, targetId)) {
    // A fast-forward only moves the current branch ref. The path differences
    // calculated above describe the new commit tree; they must not remain as
    // staged changes after the ref moves.
    state.staging = {}
    state.working_tree = {}
    setHeadCommit(state, targetId)
    setOperationMetadata(state, { last_merge_branch: branch, last_merge_target: targetId, last_merge_fast_forward: true })
    return { command: 'merge', stdout: `Fast-forward\nMerged ${branch}.` }
  }

  const commitId = nextCommitId(state)
  const changes = diffTrees(currentTree, targetTree)
  state.commits ??= []
  state.commits.push(commitPayload({ state, commitId, message: `Merge branch '${branch}'`, parents: [currentId, targetId].filter(Boolean) as string[], tree: targetTree, changes }))
  state.staging = {}
  setHeadCommit(state, commitId)
  setOperationMetadata(state, {
    last_merge_branch: branch,
    last_merge_target: targetId,
    last_merge_created_commit: commitId,
    last_merge_auto_staged_paths: stagedPaths,
    last_merge_no_ff: noFf,
  })
  const strategy = noFf ? 'ort (no fast-forward)' : 'ort'
  return { command: 'merge', stdout: `Merge made by the '${strategy}' strategy.\n ${Object.keys(changes).length} file(s) changed` }
}

function conflictEntry(branch: string, _base: RepositoryValue, ours: RepositoryValue, theirs: RepositoryValue, resolution: RepositoryValue) {
  return {
    status: 'conflicted',
    content: `<<<<<<< HEAD\n${ours ?? ''}\n=======\n${theirs ?? ''}\n>>>>>>> ${branch}\n`,
    base: _base,
    ours,
    theirs,
    resolution,
  }
}

function authoredConflictPaths(state: MutableRepositoryState) {
  if (!state.conflict_on_merge && !state.merge_conflicts) return []
  let paths = [...(state.conflict_files ?? []), ...(state.merge_conflict_files ?? [])]
  if (isRecord(state.merge_conflicts)) paths = [...paths, ...Object.keys(state.merge_conflicts)]
  return [...new Set(paths.map(String))].sort()
}

function overlappingConflicts(baseTree: Record<string, RepositoryValue>, currentTree: Record<string, RepositoryValue>, targetTree: Record<string, RepositoryValue>) {
  const conflicts = new Set<string>()
  for (const path of new Set([...Object.keys(baseTree), ...Object.keys(currentTree), ...Object.keys(targetTree)])) {
    const base = JSON.stringify(baseTree[path] ?? null)
    const ours = JSON.stringify(currentTree[path] ?? null)
    const theirs = JSON.stringify(targetTree[path] ?? null)
    if (ours !== base && theirs !== base && ours !== theirs) conflicts.add(path)
  }
  return conflicts
}

export function gitMergetool(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const conflicts = state.conflicts ?? []
  if (!conflicts.length) throw new SimulatorCommandError('No files need merging')
  const requested = parsed.pathspecs.length ? parsed.pathspecs : conflicts
  const selected = conflicts.filter((path) => requested.includes(path))
  if (!selected.length) throw new SimulatorCommandError('No files need merging')
  const configuredTool = String(optionValues(parsed, '--tool').at(-1) ?? state.config?.['merge.tool'] ?? state.operation_metadata?.configured_merge_tool ?? 'tool')
  setOperationMetadata(state, {
    last_mergetool_tool: configuredTool,
    last_mergetool_paths: selected,
    last_mergetool_opened: true,
  })
  return {
    command: 'mergetool',
    stdout: `Opened ${configuredTool} for ${selected.join(', ')}.\nResolve the file in the workspace editor, save it, then run git add for the resolved path.`,
  }
}

export function gitRebase(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '--abort')) {
    const rebaseState = isRecord(state.rebase_state) ? state.rebase_state : null
    const abortState = rebaseState?.abort_state
    if (!isRecord(abortState)) throw new SimulatorCommandError('fatal: No rebase in progress?')
    for (const key of Object.keys(state)) delete state[key]
    Object.assign(state, clone(abortState))
    setOperationMetadata(state, { last_rebase_aborted: true })
    return { command: 'rebase', stdout: '' }
  }
  if (hasOption(parsed, '--continue')) {
    if (!isRecord(state.rebase_state)) throw new SimulatorCommandError('fatal: No rebase in progress?')
    if (state.conflicts?.length) throw new SimulatorCommandError('You must edit all merge conflicts and then mark them as resolved using git add')
    const remaining = Array.isArray(state.rebase_state.remaining) ? state.rebase_state.remaining.map(String) : []
    if (!remaining.length) {
      setOperationMetadata(state, { last_rebase_new_head: headCommit(state), last_rebase_replayed_commits: clone((state.rebase_state.applied as RepositoryValue[]) ?? []) })
      delete state.rebase_state
      return { command: 'rebase', stdout: 'Successfully rebased and updated current branch.' }
    }
  }
  const ontoValues = optionValues(parsed, '--onto')
  const hasOnto = ontoValues.length > 0
  // Plain `rebase <upstream>`: newbase == upstream == args[0], rebasing the
  // current branch. `rebase --onto <newbase> <upstream> [<branch>]`: replay the
  // <upstream>..<branch> range onto <newbase>; <branch> defaults to HEAD.
  const newBaseRef = String(hasOnto ? ontoValues.at(-1) : parsed.args[0])
  const upstreamRef = String(parsed.args[0])
  const branchRef = hasOnto ? parsed.args[1] : undefined
  const newBase = resolveRef(state, newBaseRef)
  if (!newBase) throw new SimulatorCommandError(`fatal: invalid upstream '${newBaseRef}'`)
  const upstream = resolveRef(state, upstreamRef)
  if (!upstream) throw new SimulatorCommandError(`fatal: invalid upstream '${upstreamRef}'`)
  // With an explicit <branch>, real git checks it out before rebasing so the
  // replayed commits and the moved ref land on that branch, not on prior HEAD.
  if (branchRef) {
    if (!(branchRef in (state.branches ?? {}))) {
      throw new SimulatorCommandError(`fatal: no such branch/commit '${branchRef}'`)
    }
    state.head = { type: 'branch', name: branchRef, target: state.branches?.[branchRef] ?? null }
  }
  const currentBranch = headBranch(state)
  if (!currentBranch) throw new SimulatorCommandError('fatal: rebase requires a branch checkout')
  const branchTip = headCommit(state)
  if (branchTip === newBase) return { command: 'rebase', stdout: 'Current branch is up to date.' }
  // Cut at the merge-base of the branch and the upstream: only commits the branch
  // has beyond the upstream are replayed onto the new base.
  const commitsToReplay = commitsSince(state, branchTip, commonAncestor(state, branchTip, upstream)).reverse()
  let newHead = newBase
  const applied: string[] = []
  for (const sourceId of commitsToReplay) {
    const source = commitById(state, sourceId)
    if (!source) continue
    const base = treeForCommit(state, newHead)
    const nextTree = applyChanges(base, source.changes ?? {})
    const commitId = nextCommitId(state)
    state.commits ??= []
    state.commits.push(commitPayload({ state, commitId, message: source.message ?? `rebase ${sourceId}`, parents: [newHead].filter(Boolean) as string[], tree: nextTree, changes: diffTrees(base, nextTree) }))
    newHead = commitId
    applied.push(commitId)
  }
  setHeadCommit(state, newHead)
  setOperationMetadata(state, {
    last_rebase_target: newBaseRef,
    last_rebase_onto: hasOnto ? newBase : null,
    last_rebase_upstream: upstream,
    last_rebase_new_head: newHead,
    last_rebase_interactive: hasOption(parsed, '-i') || hasOption(parsed, '--interactive'),
    last_rebase_replayed_commits: applied,
  })
  return { command: 'rebase', stdout: `Successfully rebased and updated ${currentBranch}.` }
}

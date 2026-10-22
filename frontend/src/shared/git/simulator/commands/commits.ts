import type { RepositoryValue } from '@/shared/level/types'
import { hasOption } from '@/shared/git/simulator/parser'
import { applyChanges, changesFromEntries, changeType, cleanupPartialHunksAfterCommit, clone, commitById, commitPayload, diffTrees, headBranch, headCommit, headTree, nextCommitId, recordReflog, setHeadCommit, setOperationMetadata, treeForCommit } from '@/shared/git/simulator/state'
import { resolveRevision } from '@/shared/git/simulator/commands/refs'
import { selectedPaths, stageSelected } from '@/shared/git/simulator/commands/staging'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitCommit(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  let stagedByAll: string[] = []
  if (hasOption(parsed, '-a') || hasOption(parsed, '--all')) {
    stagedByAll = selectedPaths(state, [], { includeTracked: true, includeUntracked: false })
    stageSelected(state, stagedByAll)
  }
  if (hasOption(parsed, '--amend')) return amendCommit(state, parsed, stagedByAll)
  return createCommit(state, parsed.message, stagedByAll)
}

export function createCommit(state: MutableRepositoryState, message: string | null, stagedByAll: string[] = []): CommandOutcome {
  if (state.conflicts?.length) throw new SimulatorCommandError('Committing is not possible because you have unmerged files.')
  if (!Object.keys(state.staging ?? {}).length && !state.merge_parent) {
    throw new SimulatorCommandError('nothing to commit, working tree clean', 1)
  }
  const mergeParent = state.merge_parent ?? null
  delete state.merge_parent
  const mergeBranch = String(state.operation_metadata?.last_merge_branch ?? 'branch')
  const commitMessage = message ?? (mergeParent ? `Merge branch '${mergeBranch}'` : 'commit')
  const current = headCommit(state)
  const parents = [current, mergeParent].filter((value): value is string => Boolean(value))
  const commitId = nextCommitId(state)
  const baseTree = treeForCommit(state, current)
  const stagedEntries = clone(state.staging ?? {})
  const stagedChanges = changesFromEntries(baseTree, stagedEntries)
  const tree = applyChanges(baseTree, stagedChanges)
  state.commits ??= []
  state.commits.push(commitPayload({ state, commitId, message: commitMessage, parents, tree, changes: stagedChanges }))
  state.staging = {}
  delete state.merge_abort_state
  cleanupPartialHunksAfterCommit(state, stagedEntries)
  setHeadCommit(state, commitId)
  if (mergeParent) setOperationMetadata(state, { last_merge_created_commit: commitId })
  return {
    command: 'commit',
    details: {
      commit_id: commitId,
      message: commitMessage,
      changes: stagedChanges,
      branch: headBranch(state) ?? 'HEAD',
      amend: false,
      staged_by_all: stagedByAll,
    },
  }
}

function amendCommit(state: MutableRepositoryState, parsed: ParsedGitCommand, stagedByAll: string[]) {
  const current = headCommit(state)
  const oldCommit = commitById(state, current)
  if (!oldCommit) throw new SimulatorCommandError('fatal: You have nothing to amend.')
  let message = oldCommit.message ?? 'commit'
  if (parsed.message !== null) message = parsed.message
  const parentIds = [...(oldCommit.parents ?? [])]
  const parentId = parentIds[0] ?? null
  const parentTree = treeForCommit(state, parentId)
  const currentTree = clone(oldCommit.tree ?? parentTree)
  const stagedEntries = clone(state.staging ?? {})
  if (!Object.keys(stagedEntries).length && parsed.message === null && !hasOption(parsed, '--no-edit')) {
    throw new SimulatorCommandError('No changes', 1)
  }
  const stagedChanges = changesFromEntries(currentTree, stagedEntries)
  const amendedTree = applyChanges(currentTree, stagedChanges)
  const commitId = nextCommitId(state)
  const changes = diffTrees(parentTree, amendedTree)
  state.commits ??= []
  state.commits.push(commitPayload({ state, commitId, message, parents: parentIds, tree: amendedTree, changes }))
  state.replaced_commits ??= {}
  if (current) state.replaced_commits[current] = commitId
  setOperationMetadata(state, {
    last_amend_replaced_commit: current,
    last_amend_created_commit: commitId,
  })
  state.staging = {}
  cleanupPartialHunksAfterCommit(state, stagedEntries)
  setHeadCommit(state, commitId)
  recordReflog(state, commitId, `commit --amend: replaced ${current}`)
  return {
    command: 'commit',
    details: {
      commit_id: commitId,
      message,
      changes,
      branch: headBranch(state) ?? 'HEAD',
      amend: true,
      replaced: current,
      staged_by_all: stagedByAll,
    },
  }
}

export function gitRevert(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (state.conflicts?.length) throw new SimulatorCommandError('error: revert is not possible because you have unmerged files.')
  const sourceId = resolveRevision(state, parsed.args[0])
  const source = commitById(state, sourceId)
  if (!sourceId || !source) throw new SimulatorCommandError(`fatal: bad revision '${parsed.args[0]}'`)
  const headId = headCommit(state)
  const head = headTree(state)
  const revertedChanges: Record<string, { change_type: string; before: RepositoryValue; after: RepositoryValue }> = {}
  for (const [path, change] of Object.entries(source.changes ?? {})) {
    revertedChanges[path] = {
      change_type: changeType(head[path] ?? null, change.before ?? null),
      before: head[path] ?? null,
      after: change.before ?? null,
    }
  }
  const nextTree = applyChanges(head, revertedChanges)
  const commitId = nextCommitId(state)
  const message = `Revert "${source.message ?? source.id}"`
  state.commits ??= []
  state.commits.push(commitPayload({ state, commitId, message, parents: [headId].filter(Boolean) as string[], tree: nextTree, changes: diffTrees(head, nextTree) }))
  setHeadCommit(state, commitId)
  setOperationMetadata(state, { last_revert_source: sourceId, last_revert_created_commit: commitId, last_revert_no_edit: hasOption(parsed, '--no-edit') })
  recordReflog(state, commitId, `revert: ${sourceId}`)
  return { command: 'revert', stdout: `[${headBranch(state) ?? 'HEAD'} ${commitId}] ${message}` }
}

export function gitCherryPick(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '--abort')) {
    if (!state.cherry_pick_in_progress && !state.cherry_pick_original_head) throw new SimulatorCommandError('error: no cherry-pick or revert in progress')
    const original = state.cherry_pick_original_head ?? null
    if (original) setHeadCommit(state, original)
    state.staging = {}
    state.working_tree = {}
    state.conflicts = []
    delete state.conflict_details
    delete state.cherry_pick_in_progress
    delete state.cherry_pick_original_head
    delete state.cherry_pick_source
    delete state.cherry_pick_message
    setOperationMetadata(state, { last_cherry_pick_aborted: true })
    return { command: 'cherry-pick', stdout: '' }
  }
  if (hasOption(parsed, '--continue')) return continueCherryPick(state)
  if (state.conflicts?.length) throw new SimulatorCommandError('error: cherry-pick is not possible because you have unmerged files.')
  const sourceId = resolveRevision(state, parsed.args[0])
  if (!sourceId) throw new SimulatorCommandError(`fatal: bad revision '${parsed.args[0]}'`)
  const source = commitById(state, sourceId)
  if (!source) throw new SimulatorCommandError(`fatal: bad revision '${parsed.args[0]}'`)
  const headId = headCommit(state)
  const head = headTree(state)
  const forcedConflicts = new Set(
    Array.isArray(state.cherry_pick_conflict_files)
      ? state.cherry_pick_conflict_files.map(String)
      : [],
  )
  const sourceParentTree = treeForCommit(state, source.parents?.[0] ?? null)
  const conflictPaths = Object.entries(source.changes ?? {})
    .filter(([path, change]) => {
      const before = sourceParentTree[path] ?? null
      const after = change.after ?? null
      const current = head[path] ?? null
      return forcedConflicts.has(path)
        || (JSON.stringify(current) !== JSON.stringify(before)
          && JSON.stringify(current) !== JSON.stringify(after))
    })
    .map(([path]) => path)
  if (conflictPaths.length) {
    const conflicts = new Set(conflictPaths)
    const nonConflictingChanges = Object.fromEntries(
      Object.entries(source.changes ?? {}).filter(([path]) => !conflicts.has(path)),
    )
    const stagedTree = applyChanges(head, nonConflictingChanges)
    state.staging = Object.fromEntries(
      Object.entries(diffTrees(head, stagedTree)).map(([path, change]) => [
        path,
        change.after === null
          ? 'deleted'
          : { status: change.change_type, content: clone(change.after) },
      ]),
    )
    state.working_tree ??= {}
    state.conflict_details ??= {}
    for (const path of conflictPaths) {
      const before = sourceParentTree[path] ?? null
      const ours = head[path] ?? null
      const theirs = source.tree?.[path] ?? null
      state.conflict_details[path] = { base: clone(before), ours: clone(ours), theirs: clone(theirs) }
      state.working_tree[path] = {
        status: 'conflicted',
        content: `<<<<<<< HEAD\n${ours ?? ''}\n=======\n${theirs ?? ''}\n>>>>>>> ${sourceId}\n`,
      }
    }
    state.conflicts = [...conflicts].sort()
    state.cherry_pick_in_progress = true
    state.cherry_pick_original_head = headId
    state.cherry_pick_source = sourceId
    // Git prepares the commit message (with any -x note) when it stops, and
    // --continue commits with it.
    state.cherry_pick_message = cherryPickMessage(source.message ?? `cherry-pick ${sourceId}`, sourceId, parsed)
    setOperationMetadata(state, {
      last_cherry_pick_source: sourceId,
      last_cherry_pick_conflicted: true,
      last_cherry_pick_conflict_paths: state.conflicts,
    })
    return {
      command: 'cherry-pick',
      exitCode: 1,
      stdout: `Auto-merging ${conflictPaths.join(', ')}\nCONFLICT (content): Merge conflict in ${conflictPaths.join(', ')}\nerror: could not apply ${sourceId}`,
    }
  }
  const nextTree = applyChanges(head, source.changes ?? {})
  const changes = diffTrees(head, nextTree)
  if (hasOption(parsed, '--no-commit') || hasOption(parsed, '-n')) {
    // Like Git, a --no-commit pick lands on top of whatever is already staged,
    // so several picks can be committed together.
    const index = applyChanges(head, changesFromEntries(head, clone(state.staging ?? {})))
    const staged = diffTrees(head, applyChanges(index, source.changes ?? {}))
    state.staging = Object.fromEntries(
      Object.entries(staged).map(([path, change]) => [path, change.after === null ? 'deleted' : { status: change.change_type, content: clone(change.after) }]),
    )
    setOperationMetadata(state, { cherry_pick_in_progress: true, cherry_pick_original_head: headId, last_cherry_pick_source: sourceId, last_cherry_pick_no_commit: true })
    state.cherry_pick_in_progress = true
    state.cherry_pick_original_head = headId
    return { command: 'cherry-pick', stdout: '' }
  }
  const commitId = nextCommitId(state)
  const message = cherryPickMessage(source.message ?? `cherry-pick ${sourceId}`, sourceId, parsed)
  state.commits ??= []
  state.commits.push(commitPayload({ state, commitId, message, parents: [headId].filter(Boolean) as string[], tree: nextTree, changes }))
  setHeadCommit(state, commitId)
  setOperationMetadata(state, { last_cherry_pick_source: sourceId, last_cherry_pick_created_commit: commitId, last_cherry_pick_no_commit: false })
  return { command: 'cherry-pick', stdout: `[${headBranch(state) ?? 'HEAD'} ${commitId}] ${message}` }
}

function continueCherryPick(state: MutableRepositoryState): CommandOutcome {
  if (!state.cherry_pick_in_progress) {
    throw new SimulatorCommandError('error: no cherry-pick or revert in progress')
  }
  if (state.conflicts?.length) {
    throw new SimulatorCommandError('error: cherry-pick is not possible because you have unmerged files.')
  }
  const sourceId = String(state.cherry_pick_source ?? state.operation_metadata?.last_cherry_pick_source ?? '')
  const source = commitById(state, sourceId)
  if (!source) throw new SimulatorCommandError('fatal: cherry-pick source commit is unavailable')
  const headId = headCommit(state)
  const head = headTree(state)
  const stagedChanges = changesFromEntries(head, clone(state.staging ?? {}))
  if (!Object.keys(stagedChanges).length) {
    throw new SimulatorCommandError('nothing to commit, working tree clean', 1)
  }
  const tree = applyChanges(head, stagedChanges)
  const commitId = nextCommitId(state)
  const message = String(state.cherry_pick_message ?? source.message ?? `cherry-pick ${sourceId}`)
  state.commits ??= []
  state.commits.push(
    commitPayload({
      state,
      commitId,
      message,
      parents: [headId].filter(Boolean) as string[],
      tree,
      changes: diffTrees(head, tree),
    }),
  )
  setHeadCommit(state, commitId)
  state.staging = {}
  state.working_tree = {}
  delete state.cherry_pick_in_progress
  delete state.cherry_pick_original_head
  delete state.cherry_pick_source
  delete state.cherry_pick_message
  setOperationMetadata(state, {
    last_cherry_pick_source: sourceId,
    last_cherry_pick_created_commit: commitId,
    last_cherry_pick_no_commit: false,
  })
  return { command: 'cherry-pick', stdout: `[${headBranch(state) ?? 'HEAD'} ${commitId}] ${message}` }
}

function cherryPickMessage(message: string, sourceId: string, parsed: ParsedGitCommand) {
  return hasOption(parsed, '-x')
    ? `${message}\n\n(cherry picked from commit ${sourceId})`
    : message
}

export function gitTag(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  state.tags ??= {}
  if (hasOption(parsed, '-d') || hasOption(parsed, '--delete')) {
    for (const name of parsed.args) delete state.tags[name]
    setOperationMetadata(state, { last_tags_deleted: parsed.args })
    return { command: 'tag', stdout: parsed.args.map((name) => `Deleted tag '${name}'`).join('\n') }
  }
  if (!parsed.args.length) return { command: 'tag', stdout: Object.keys(state.tags).sort().join('\n') }
  const [name, targetRef = 'HEAD'] = parsed.args
  const target = resolveRevision(state, targetRef)
  if (!target) throw new SimulatorCommandError(`fatal: Failed to resolve '${targetRef}' as a valid ref.`)
  state.tags[name] = { target, annotated: hasOption(parsed, '-a') || hasOption(parsed, '--annotate') || parsed.message !== null, message: parsed.message ?? '' }
  setOperationMetadata(state, { last_tag_created: name, last_tag_target: target })
  return { command: 'tag', stdout: '' }
}

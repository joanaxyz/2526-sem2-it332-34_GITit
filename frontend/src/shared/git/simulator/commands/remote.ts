import { hasOption } from '@/shared/git/simulator/parser'
import { applyChanges, applyRemoteFixtureBranches, clone, commitById, commitPayload, diffTrees, headBranch, headCommit, materializeRemoteCommits, nextCommitId, setHeadCommit, setOperationMetadata, treeForCommit } from '@/shared/git/simulator/state'
import { mergeBranch } from '@/shared/git/simulator/commands/merge'
import { commonAncestor, commitsSince, isAncestor } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitRemote(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (!parsed.args.length) return { command: 'remote', details: { verbose: hasOption(parsed, '-v') || hasOption(parsed, '--verbose') } }
  if (parsed.args[0] === 'add') {
    const [, name, url] = parsed.args
    state.remotes ??= {}
    if (name in state.remotes) throw new SimulatorCommandError(`error: remote ${name} already exists.`, 3)
    state.remotes[name] = url
    setOperationMetadata(state, { last_remote_added: name, last_remote_url: url })
    return { command: 'remote', details: { added: name } }
  }
  if (parsed.args[0] === 'set-url') {
    const [, name, url] = parsed.args
    state.remotes ??= {}
    if (!(name in state.remotes)) throw new SimulatorCommandError(`error: No such remote '${name}'`, 2)
    state.remotes[name] = url
    setOperationMetadata(state, { last_remote_set_url: name, last_remote_url: url })
    return { command: 'remote', details: { set_url: name } }
  }
  throw new SimulatorCommandError('fatal: unsupported remote operation', 129)
}

export function gitFetch(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const allRemotes = hasOption(parsed, '--all')
  const remote = parsed.args[0] ?? 'origin'
  state.remotes ??= {}
  if (!allRemotes && !(remote in state.remotes) && !state.remote_fixtures && !state.remote_updates) {
    throw new SimulatorCommandError(`fatal: '${remote}' does not appear to be a git repository`)
  }
  if (state.remote_updates) {
    state.remote_branches ??= {}
    Object.assign(state.remote_branches, clone(state.remote_updates))
  }
  applyRemoteFixtureBranches(state)
  materializeRemoteCommits(state)
  const pruned: string[] = []
  if (hasOption(parsed, '--prune') || hasOption(parsed, '-p')) {
    const remoteBranches = state.remote_branches ?? {}
    // A ref is pruned when the fixture marks it deleted upstream - either by a
    // null tracking target or by listing it in `remote_stale_branches` (bare or
    // remote-qualified names both accepted).
    const stale = new Set(
      (Array.isArray(state.remote_stale_branches) ? state.remote_stale_branches : []).map((name) => {
        const text = String(name)
        return text.includes('/') ? text : `${remote}/${text}`
      }),
    )
    for (const branch of Object.keys(remoteBranches)) {
      if (branch.startsWith(`${remote}/`) && (remoteBranches[branch] === null || stale.has(branch))) {
        delete remoteBranches[branch]
        pruned.push(branch)
      }
    }
  }
  setOperationMetadata(state, { remote_tracking_updated: true, last_fetch_remote: allRemotes ? '--all' : remote, last_fetch_all: allRemotes, fetch_pruned_refs: pruned.length ? pruned : null })
  const url = state.remotes[remote] ?? `https://example.test/${remote}.git`
  return { command: 'fetch', stdout: `From ${url}` }
}

export function gitPull(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const remote = parsed.args[0] ?? 'origin'
  const branch = parsed.args[1] ?? headBranch(state) ?? 'main'
  gitFetch(state, { ...parsed, args: [remote], pathspecs: [remote] })
  const remoteKey = `${remote}/${branch}`
  const remoteCommit = state.remote_branches?.[remoteKey]
  if (!remoteCommit) throw new SimulatorCommandError(`fatal: couldn't find remote ref ${branch}`)
  setOperationMetadata(state, { remote_tracking_updated: true })
  if (hasOption(parsed, '--ff-only')) {
    const current = headCommit(state)
    if (current === remoteCommit || isAncestor(state, current, remoteCommit)) {
      setHeadCommit(state, remoteCommit)
      setOperationMetadata(state, { pull_strategy: 'ff-only', pull_fast_forwarded: true })
      return { command: 'pull', stdout: current === remoteCommit ? 'Already up to date.' : 'Fast-forward' }
    }
    // Divergent history: --ff-only refuses to create a merge, matching real git.
    // Challenge 7.B hard expects this failure so the learner falls back to fetch + merge.
    throw new SimulatorCommandError('fatal: Not possible to fast-forward, aborting.', 128)
  }
  if (hasOption(parsed, '--rebase')) {
    const currentBranch = headBranch(state)
    if (!currentBranch) throw new SimulatorCommandError('fatal: pull with rebase requires a branch checkout')
    const current = headCommit(state)
    if (current === remoteCommit || isAncestor(state, current, remoteCommit)) {
      setHeadCommit(state, remoteCommit)
      setOperationMetadata(state, { pull_strategy: 'rebase', pull_rebased_onto: remoteCommit })
      return { command: 'pull', stdout: `Successfully rebased and updated refs/heads/${currentBranch}.` }
    }
    // Genuine divergence: replay the local-only commits on top of remoteCommit
    // instead of dropping them - mirrors gitRebase's replay loop.
    const commitsToReplay = commitsSince(state, current, commonAncestor(state, current, remoteCommit)).reverse()
    let newHead = remoteCommit
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
    setOperationMetadata(state, { pull_strategy: 'rebase', pull_rebased_onto: remoteCommit, last_rebase_replayed_commits: applied })
    return { command: 'pull', stdout: `Successfully rebased and updated refs/heads/${currentBranch}.` }
  }
  return mergeBranch(state, remoteKey, false)
}

export function gitPush(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const remote = parsed.args[0] ?? 'origin'
  if (hasOption(parsed, '--tags')) {
    state.remote_tags ??= {}
    Object.assign(state.remote_tags, clone(state.tags ?? {}))
    setOperationMetadata(state, { last_push_remote: remote, last_push_tags: true })
    return { command: 'push', stdout: `To ${state.remotes?.[remote] ?? `https://example.test/${remote}.git`}\n * [new tag] pushed tags` }
  }
  if (hasOption(parsed, '--delete') || hasOption(parsed, '-d')) {
    const branch = parsed.args[1]
    const remoteKey = `${remote}/${branch}`
    if (!(remoteKey in (state.remote_branches ?? {}))) throw new SimulatorCommandError(`error: unable to delete '${branch}': remote ref does not exist`, 1)
    delete state.remote_branches?.[remoteKey]
    for (const [local, upstream] of Object.entries(state.upstream_tracking ?? {})) {
      if (upstream === remoteKey) delete state.upstream_tracking?.[local]
    }
    setOperationMetadata(state, { last_push_deleted_branch: remoteKey, remote_branch_deleted: branch, last_push_remote: remote })
    return { command: 'push', stdout: `To ${state.remotes?.[remote] ?? `https://example.test/${remote}.git`}\n - [deleted] ${branch}` }
  }
  const branch = parsed.args[1] ?? headBranch(state)
  if (!branch) throw new SimulatorCommandError('fatal: You are not currently on a branch.')
  const commitId = state.branches?.[branch]
  const remoteKey = `${remote}/${branch}`
  state.remote_branches ??= {}
  state.remote_branches[remoteKey] = commitId ?? null
  state.remotes ??= {}
  state.remotes[remote] ??= `https://example.test/${remote}.git`
  if (hasOption(parsed, '-u') || hasOption(parsed, '--set-upstream')) {
    state.upstream_tracking ??= {}
    state.upstream_tracking[branch] = remoteKey
  }
  setOperationMetadata(state, { last_push_remote: remote, last_push_branch: branch, last_push_remote_branch: remoteKey, last_push_commit: commitId ?? null, force_with_lease: hasOption(parsed, '--force-with-lease'), force_push_with_lease: hasOption(parsed, '--force-with-lease') })
  return { command: 'push', stdout: `To ${state.remotes[remote]}\n * [new branch] ${branch} -> ${branch}` }
}

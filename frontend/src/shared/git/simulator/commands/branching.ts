import { hasOption } from '@/shared/git/simulator/parser'
import { clone, headBranch, headCommit, isRecord, setOperationMetadata } from '@/shared/git/simulator/state'
import { isAncestor, resolveRef } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitBranch(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '-m') || hasOption(parsed, '--move')) return renameBranch(state, parsed)
  if (hasOption(parsed, '-d') || hasOption(parsed, '-D') || hasOption(parsed, '--delete')) {
    const name = parsed.args[0]
    const target = state.branches?.[name]
    if (!(name in (state.branches ?? {}))) throw new SimulatorCommandError(`error: branch '${name}' not found.`, 1)
    if (headBranch(state) === name) throw new SimulatorCommandError(`error: Cannot delete branch '${name}' checked out`, 1)
    // `-d` (safe delete) refuses a branch whose work is not reachable from HEAD;
    // `-D` forces it. This is what makes the -d vs -D lesson real (curriculum 3.B).
    if (!hasOption(parsed, '-D') && !isAncestor(state, target, headCommit(state))) {
      throw new SimulatorCommandError(
        `error: The branch '${name}' is not fully merged.\nIf you are sure you want to delete it, run 'git branch -D ${name}'.`,
        1,
      )
    }
    delete state.branches?.[name]
    setOperationMetadata(state, { last_branch_deleted: name })
    return { command: 'branch', details: { deleted: name, target: target ?? '' } }
  }
  if (parsed.args.length) {
    const [name, startPoint] = parsed.args
    if (name in (state.branches ?? {})) throw new SimulatorCommandError(`fatal: A branch named '${name}' already exists.`)
    const targetId = startPoint ? resolveRef(state, startPoint) : headCommit(state)
    if (startPoint && !targetId) throw new SimulatorCommandError(`fatal: Not a valid object name: '${startPoint}'.`)
    state.branches ??= {}
    state.branches[name] = targetId ?? null
    setOperationMetadata(state, { last_branch_created: name })
    return { command: 'branch', details: { created: name, target: targetId ?? null } }
  }
  return {
    command: 'branch',
    details: {
      verbose: hasOption(parsed, '-v') || hasOption(parsed, '-vv'),
      all: hasOption(parsed, '-a'),
      merged: hasOption(parsed, '--merged'),
    },
  }
}

function renameBranch(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const oldName = parsed.args.length > 1 ? parsed.args[0] : headBranch(state)
  const newName = parsed.args.length > 1 ? parsed.args[1] : parsed.args[0]
  if (!oldName) throw new SimulatorCommandError('fatal: branch rename requires a current branch')
  if (!newName) throw new SimulatorCommandError('usage: git branch -m [<oldbranch>] <newbranch>', 129)
  if (!(oldName in (state.branches ?? {}))) throw new SimulatorCommandError(`error: refname refs/heads/${oldName} not found`, 1)
  if (newName in (state.branches ?? {})) throw new SimulatorCommandError(`fatal: A branch named '${newName}' already exists.`)
  state.branches ??= {}
  state.branches[newName] = state.branches[oldName]
  delete state.branches[oldName]
  if (headBranch(state) === oldName) state.head = { type: 'branch', name: newName, target: state.branches[newName] ?? null }
  if (oldName in (state.upstream_tracking ?? {})) {
    state.upstream_tracking ??= {}
    state.upstream_tracking[newName] = state.upstream_tracking[oldName]
    delete state.upstream_tracking[oldName]
  }
  setOperationMetadata(state, { last_branch_renamed_from: oldName, last_branch_renamed_to: newName })
  return { command: 'branch', details: { renamed: newName, old_name: oldName } }
}

export function gitSwitch(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '-c') || hasOption(parsed, '--create')) {
    const [name, startPoint] = parsed.args
    return createAndSwitchBranch(state, name, startPoint)
  }
  if (hasOption(parsed, '--detach')) {
    const targetId = resolveRef(state, parsed.args[0] ?? 'HEAD')
    if (!targetId) throw new SimulatorCommandError(`fatal: invalid reference: ${parsed.args[0]}`)
    state.head = { type: 'detached', target: targetId }
    setOperationMetadata(state, { detached_head: true, last_detached_to: targetId })
    return { command: 'switch', stdout: `HEAD is now at ${targetId}` }
  }
  const name = parsed.args[0]
  if (!(name in (state.branches ?? {}))) {
    const remoteKey = `origin/${name}`
    if (remoteKey in (state.remote_branches ?? {})) {
      state.branches ??= {}
      state.branches[name] = state.remote_branches?.[remoteKey] ?? null
      state.upstream_tracking ??= {}
      state.upstream_tracking[name] = remoteKey
    } else {
      throw new SimulatorCommandError(`fatal: invalid reference: ${name}`)
    }
  }
  state.head = { type: 'branch', name, target: state.branches?.[name] ?? null }
  setOperationMetadata(state, { last_switch_branch: name, last_switched_to: name })
  return { command: 'switch', stdout: `Switched to branch '${name}'` }
}

function createAndSwitchBranch(state: MutableRepositoryState, name: string, startPoint?: string) {
  if (name in (state.branches ?? {})) throw new SimulatorCommandError(`fatal: A branch named '${name}' already exists.`)
  const targetId = startPoint ? resolveRef(state, startPoint) : headCommit(state)
  if (startPoint && !targetId) throw new SimulatorCommandError(`fatal: invalid reference: ${startPoint}`)
  state.branches ??= {}
  state.branches[name] = targetId ?? null
  state.head = { type: 'branch', name, target: targetId ?? null }
  setOperationMetadata(state, { last_branch_created: name, last_switch_branch: name, last_switched_to: name })
  return { command: 'switch', stdout: `Switched to a new branch '${name}'` }
}

export function gitCheckout(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  if (hasOption(parsed, '-b')) return createAndSwitchBranch(state, parsed.args[0], parsed.args[1])
  const side = hasOption(parsed, '--ours') ? 'ours' : 'theirs'
  if (!state.conflicts?.length) {
    throw new SimulatorCommandError('fatal: --ours/--theirs can only be used while resolving merge conflicts.')
  }
  const conflicts = new Set(state.conflicts)
  const checkedOut: string[] = []
  for (const path of parsed.pathspecs) {
    if (!conflicts.has(path)) throw new SimulatorCommandError(`error: path '${path}' is not conflicted`, 1)
    const detail = state.conflict_details?.[path]
    const value = isRecord(detail) ? detail[side] : null
    state.working_tree ??= {}
    state.working_tree[path] = {
      status: 'modified',
      content: clone(value ?? null),
      resolution_side: side,
    }
    setOperationMetadata(state, { last_checkout_conflict_side: side, last_checkout_conflict_paths: parsed.pathspecs })
    checkedOut.push(path)
  }
  return { command: 'checkout', details: { checked_out: checkedOut, side } }
}

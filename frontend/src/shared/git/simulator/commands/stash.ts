import { hasOption, optionValues } from '@/shared/git/simulator/parser'
import { clone, entryStatus, headBranch, setOperationMetadata } from '@/shared/git/simulator/state'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitStash(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const subcommand = parsed.args[0] ?? 'push'
  if (subcommand === 'list') return { command: 'stash', stdout: formatStashList(state) }
  if (subcommand === 'show') return showStash(state, stashIndex(parsed.args[1]))
  if (subcommand === 'pop') return applyStash(state, stashIndex(parsed.args[1]), true)
  if (subcommand === 'apply') return applyStash(state, stashIndex(parsed.args[1]), false)
  if (subcommand === 'drop') return dropStash(state, stashIndex(parsed.args[1]))
  return pushStash(state, parsed)
}

function pushStash(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const includeUntracked = hasOption(parsed, '-u') || hasOption(parsed, '--include-untracked')
  const workingTree = Object.fromEntries(
    Object.entries(state.working_tree ?? {}).filter(([, value]) => includeUntracked || entryStatus(value) !== 'untracked'),
  )
  if (!Object.keys(workingTree).length && !Object.keys(state.staging ?? {}).length && !state.conflicts?.length) {
    return { command: 'stash', stdout: 'No local changes to save' }
  }
  const entry = {
    working_tree: clone(workingTree),
    staging: clone(state.staging ?? {}),
    conflicts: clone(state.conflicts ?? []),
    message: String(optionValues(parsed, '-m', '--message').at(-1) ?? 'WIP on ' + (headBranch(state) ?? 'HEAD')),
  }
  state.stash_stack ??= []
  state.stash_stack.push(entry)
  for (const path of Object.keys(workingTree)) delete state.working_tree?.[path]
  state.staging = {}
  state.conflicts = []
  setOperationMetadata(state, { last_stash_action: 'push', last_stash_operation: 'push', stash_count: state.stash_stack.length })
  return { command: 'stash', stdout: 'Saved working directory and index state' }
}

function applyStash(state: MutableRepositoryState, index: number, remove: boolean): CommandOutcome {
  const stack = state.stash_stack ?? []
  if (!stack.length) return { command: 'stash', stdout: 'No stash entries found.' }
  const realIndex = stack.length - 1 - index
  const entry = stack[realIndex]
  if (!entry) throw new SimulatorCommandError(`fatal: log for stash@{${index}} only has ${stack.length} entries`)
  Object.assign(state.working_tree ??= {}, clone(entry.working_tree ?? {}))
  Object.assign(state.staging ??= {}, clone(entry.staging ?? {}))
  state.conflicts = clone(entry.conflicts ?? [])
  if (remove) stack.splice(realIndex, 1)
  setOperationMetadata(state, { last_stash_action: remove ? 'pop' : 'apply', last_stash_operation: remove ? 'pop' : 'apply', stash_count: stack.length })
  return { command: 'stash', stdout: remove ? `Dropped stash@{${index}}` : '' }
}

function dropStash(state: MutableRepositoryState, index: number): CommandOutcome {
  const stack = state.stash_stack ?? []
  if (!stack.length) return { command: 'stash', stdout: 'No stash entries found.' }
  const realIndex = stack.length - 1 - index
  if (!stack[realIndex]) throw new SimulatorCommandError(`fatal: log for stash@{${index}} only has ${stack.length} entries`)
  stack.splice(realIndex, 1)
  setOperationMetadata(state, { last_stash_action: 'drop', last_stash_operation: 'drop', stash_count: stack.length })
  return { command: 'stash', stdout: `Dropped stash@{${index}}` }
}

function showStash(state: MutableRepositoryState, index: number): CommandOutcome {
  const stack = state.stash_stack ?? []
  const entry = stack[stack.length - 1 - index]
  if (!entry) return { command: 'stash', stdout: '' }
  const paths = [...Object.keys(entry.working_tree ?? {}), ...Object.keys(entry.staging ?? {})].sort()
  return { command: 'stash', stdout: paths.join('\n') }
}

function stashIndex(raw?: string) {
  if (!raw) return 0
  const match = raw.match(/stash@\{(\d+)\}/)
  if (match) return Number(match[1])
  return /^\d+$/.test(raw) ? Number(raw) : 0
}

function formatStashList(state: MutableRepositoryState) {
  const stack = state.stash_stack ?? []
  return stack
    .slice()
    .reverse()
    .map((entry, index) => `stash@{${index}}: ${entry.message ?? 'WIP'}`)
    .join('\n')
}

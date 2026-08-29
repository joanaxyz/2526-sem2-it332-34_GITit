import { entryContent, headTree, setOperationMetadata } from '@/shared/git/simulator/state'
import { commonAncestor, commitsSince, resolveRef } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function gitCheckIgnore(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const path = parsed.pathspecs[0]
  const rule = matchingGitignoreRule(state, path)
  if (!rule) return { command: 'check-ignore', stdout: '', exitCode: 1 }
  return { command: 'check-ignore', stdout: `.gitignore:1:${rule}\t${path}` }
}

function matchingGitignoreRule(state: MutableRepositoryState, path: string) {
  const gitignore = state.working_tree?.['.gitignore'] ?? headTree(state)['.gitignore']
  const content = String(entryContent(gitignore) ?? '')
  return content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'))
    .find((rule) => pathMatchesIgnoreRule(path, rule))
}

function pathMatchesIgnoreRule(path: string, rule: string) {
  const clean = rule.replace(/^\//, '').replace(/\/$/, '')
  if (!clean) return false
  if (clean.includes('*')) {
    const pattern = new RegExp(`^${clean.split('*').map(escapeRegExp).join('.*')}$`)
    return pattern.test(path)
  }
  return path === clean || path.startsWith(`${clean}/`) || path.endsWith(`/${clean}`)
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

export function gitMergeBase(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const left = resolveRef(state, parsed.args[0])
  const right = resolveRef(state, parsed.args[1])
  if (!left || !right) throw new SimulatorCommandError('fatal: Not a valid object name')
  const base = commonAncestor(state, left, right)
  if (!base) return { command: 'merge-base', stdout: '', exitCode: 1 }
  setOperationMetadata(state, { last_merge_base: base })
  return { command: 'merge-base', stdout: base }
}

export function gitRevList(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  const [leftRef, rightRef] = parsed.args[0].split('..')
  const left = resolveRef(state, leftRef)
  const right = resolveRef(state, rightRef)
  if (!left || !right) throw new SimulatorCommandError('fatal: Not a valid object name')
  const count = commitsSince(state, right, left).length
  setOperationMetadata(state, { last_rev_list_count: count })
  return { command: 'rev-list', stdout: String(count) }
}

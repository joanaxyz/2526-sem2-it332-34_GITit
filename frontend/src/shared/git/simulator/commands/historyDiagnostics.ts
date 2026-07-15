import type { RepositoryCommit, RepositoryValue } from '@/shared/level/types'
import { hasOption } from '@/shared/git/simulator/parser'
import {
  commitById,
  headCommit,
  headTree,
  isRecord,
  treeForCommit,
} from '@/shared/git/simulator/state'
import {
  commonAncestor,
  history,
  resolveRevision,
} from '@/shared/git/simulator/commands/refs'
import {
  SimulatorCommandError,
  type CommandOutcome,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'

export function gitShortlog(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const commits = reachableCommits(state, parsed.args.at(-1))
  const counts = new Map<string, number>()
  for (const commit of commits) {
    const author = commit.author ?? 'GIT it'
    counts.set(author, (counts.get(author) ?? 0) + 1)
  }
  const summary = hasOption(parsed, '-s') || hasOption(parsed, '-n') || hasOption(parsed, '-sn')
  const rows = [...counts.entries()].sort((left, right) =>
    summary ? right[1] - left[1] || left[0].localeCompare(right[0]) : left[0].localeCompare(right[0]),
  )
  return {
    command: 'shortlog',
    stdout: summary
      ? rows.map(([author, count]) => `${String(count).padStart(6)}\t${author}`).join('\n')
      : rows
          .map(([author]) => {
            const messages = commits
              .filter((commit) => (commit.author ?? 'GIT it') === author)
              .map((commit) => `      ${commit.message}`)
            return `${author} (${messages.length}):\n${messages.join('\n')}`
          })
          .join('\n\n'),
  }
}

export function gitRevParse(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  if (hasOption(parsed, '--show-toplevel')) {
    return { command: 'rev-parse', stdout: '/workspace/repository' }
  }
  const revision = parsed.args[0]
  const resolved = resolveRevision(state, revision)
  if (!resolved) throw new SimulatorCommandError(`fatal: ambiguous argument '${revision}'`)
  return { command: 'rev-parse', stdout: resolved }
}

export function gitBlame(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const path = parsed.args[0]
  const content = headTree(state)[path]
  if (content === undefined) {
    throw new SimulatorCommandError(`fatal: no such path '${path}' in HEAD`)
  }
  const commitId = headCommit(state) ?? '0000000'
  const lines = String(valueContent(content)).split(/\r?\n/)
  return {
    command: 'blame',
    stdout: lines
      .map(
        (line, index) =>
          `${commitId.padEnd(8)} (GIT it ${String(index + 1).padStart(4)}) ${line}`,
      )
      .join('\n'),
  }
}

export function gitGrep(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const [pattern, treeish] = parsed.args
  const tree = treeish
    ? treeForCommit(state, requireRevision(state, treeish))
    : headTree(state)
  let expression: RegExp
  try {
    expression = new RegExp(pattern, 'i')
  } catch {
    expression = new RegExp(escapeRegExp(pattern), 'i')
  }
  const rows: string[] = []
  for (const [path, value] of Object.entries(tree).sort(([left], [right]) =>
    left.localeCompare(right),
  )) {
    for (const line of String(valueContent(value)).split(/\r?\n/)) {
      if (expression.test(line)) rows.push(`${path}:${line}`)
      expression.lastIndex = 0
    }
  }
  return { command: 'grep', stdout: rows.join('\n'), exitCode: rows.length ? 0 : 1 }
}

export function gitDescribe(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const start = resolveRevision(state, parsed.args[0] ?? 'HEAD')
  if (!start) throw new SimulatorCommandError('fatal: No names found, cannot describe anything.')
  const tagsByTarget = new Map<string, string>()
  for (const [name, value] of Object.entries(state.tags ?? {})) {
    const target = isRecord(value) ? String(value.target ?? '') : String(value)
    if (target) tagsByTarget.set(target, name)
  }
  const chain = firstParentHistory(state, start)
  for (let distance = 0; distance < chain.length; distance += 1) {
    const tag = tagsByTarget.get(chain[distance])
    if (!tag) continue
    return {
      command: 'describe',
      stdout: distance === 0 ? tag : `${tag}-${distance}-g${start.slice(0, 7)}`,
    }
  }
  throw new SimulatorCommandError('fatal: No names found, cannot describe anything.')
}

export function gitRangeDiff(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const [oldRange, newRange] = parsed.args
  const oldCommits = commitsForRange(state, oldRange)
  const newCommits = commitsForRange(state, newRange)
  const length = Math.max(oldCommits.length, newCommits.length)
  const rows: string[] = []
  for (let index = 0; index < length; index += 1) {
    const oldCommit = oldCommits[index]
    const newCommit = newCommits[index]
    const marker = oldCommit && newCommit && patchSignature(oldCommit) === patchSignature(newCommit) ? '=' : '!'
    rows.push(
      `${index + 1}: ${oldCommit?.id ?? '-------'} ${marker} ${index + 1}: ${newCommit?.id ?? '-------'} ${newCommit?.message ?? oldCommit?.message ?? ''}`.trimEnd(),
    )
  }
  return { command: 'range-diff', stdout: rows.join('\n') }
}

export function gitMergeTree(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const left = requireRevision(state, parsed.args[0])
  const right = requireRevision(state, parsed.args[1])
  const base = commonAncestor(state, left, right)
  const leftTree = treeForCommit(state, left)
  const rightTree = treeForCommit(state, right)
  const paths = [...new Set([...Object.keys(leftTree), ...Object.keys(rightTree)])].sort()
  const rows = [`base ${base ?? '(none)'}`, `ours ${left}`, `theirs ${right}`]
  for (const path of paths) {
    const ours = leftTree[path]
    const theirs = rightTree[path]
    if (JSON.stringify(ours) === JSON.stringify(theirs)) continue
    rows.push(`changed in both\n  ${path}`)
  }
  if (rows.length === 3) rows.push('clean virtual merge')
  return { command: 'merge-tree', stdout: rows.join('\n') }
}

function requireRevision(state: MutableRepositoryState, revision: string) {
  const resolved = resolveRevision(state, revision)
  if (!resolved) throw new SimulatorCommandError(`fatal: ambiguous argument '${revision}'`)
  return resolved
}

function reachableCommits(state: MutableRepositoryState, revision?: string) {
  const target = revision ? resolveRevision(state, revision) : headCommit(state)
  return history(state, target)
    .map((commitId) => commitById(state, commitId))
    .filter((commit): commit is RepositoryCommit => Boolean(commit))
}

function firstParentHistory(state: MutableRepositoryState, start: string) {
  const result: string[] = []
  let current: string | null = start
  while (current) {
    result.push(current)
    current = commitById(state, current)?.parents?.[0] ?? null
  }
  return result
}

function commitsForRange(state: MutableRepositoryState, range: string) {
  const [baseRef, tipRef] = range.split('..')
  if (!tipRef) throw new SimulatorCommandError(`fatal: invalid revision range '${range}'`)
  const base = requireRevision(state, baseRef)
  const tip = requireRevision(state, tipRef)
  const commits: RepositoryCommit[] = []
  let current: string | null = tip
  while (current && current !== base) {
    const commit = commitById(state, current)
    if (!commit) break
    commits.unshift(commit)
    current = commit.parents?.[0] ?? null
  }
  return commits
}

function patchSignature(commit: RepositoryCommit) {
  return JSON.stringify(commit.changes ?? commit.tree ?? {})
}

function valueContent(value: RepositoryValue) {
  return isRecord(value) && 'content' in value ? value.content : value
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

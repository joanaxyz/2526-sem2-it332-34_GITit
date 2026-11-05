import type { RepositoryCommit, RepositoryValue } from '@/shared/level/types'
import { hasOption, optionValues } from '@/shared/git/simulator/parser'
import { applyChanges, changesFromEntries, commitById, diffTrees, entryStatus, headBranch, headCommit, headTree, isDeleteMarker, treeForCommit } from '@/shared/git/simulator/state'
import { history, isAncestor, resolveRef, resolveRevision } from '@/shared/git/simulator/commands/refs'
import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'

export function formatOutcome(state: MutableRepositoryState, parsed: ParsedGitCommand, outcome: CommandOutcome) {
  switch (outcome.command) {
    case 'branch':
      return formatBranch(state, outcome)
    case 'remote':
      return parsed.args.length ? '' : formatRemote(state, parsed)
    case 'commit': {
      const details = outcome.details ?? {}
      return `[${details.branch ?? 'HEAD'} ${details.commit_id}] ${details.message ?? 'commit'}`
    }
    case 'add':
    case 'restore':
    case 'checkout':
      return ''
    case 'rm':
      return (outcome.details?.removed as string[] ?? []).map((path) => `rm '${path}'`).join('\n')
    default:
      return outcome.stdout ?? ''
  }
}

export function formatStatus(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  const base = headTree(state)
  const staging = state.staging ?? {}
  const working = state.working_tree ?? {}
  const index = applyChanges(base, changesFromEntries(base, staging))
  const conflicts = new Set(state.conflicts ?? [])
  const staged: string[] = []
  const unstaged: string[] = []
  const unmerged: string[] = []
  const untracked: string[] = []
  const ignored: string[] = []
  const rows: string[] = []
  const paths = [...new Set([...Object.keys(staging), ...Object.keys(working), ...conflicts])].sort()
  for (const path of paths) {
    if (conflicts.has(path)) {
      rows.push(`UU ${path}`)
      unmerged.push(`\tboth modified:   ${path}`)
      continue
    }
    const stagedCode = path in staging ? statusCode(staging[path], path in base) : ' '
    let workingCode = ' '
    if (path in working) {
      const status = entryStatus(working[path])
      if (status === 'ignored') {
        if (hasOption(parsed, '--ignored')) {
          ignored.push(`\t${path}`)
        }
        continue
      }
      const tracked = path in index || ['modified', 'deleted', 'removed'].includes(status)
      if (!tracked) {
        untracked.push(`\t${path}`)
      } else {
        workingCode = statusCode(working[path], true)
      }
    }
    if (stagedCode !== ' ') staged.push(`\t${statusLabel(stagedCode).padEnd(12)}${path}`)
    if (workingCode !== ' ') unstaged.push(`\t${statusLabel(workingCode).padEnd(12)}${path}`)
    if (workingCode !== ' ' || stagedCode !== ' ') rows.push(`${stagedCode}${workingCode} ${path}`)
  }
  const short = hasOption(parsed, '-s') || hasOption(parsed, '--short') || hasOption(parsed, '--porcelain') || hasOption(parsed, '-sb')
  if (short) {
    const branch = headBranch(state) ?? 'HEAD (no branch)'
    const header = headCommit(state) ? branch : `No commits yet on ${branch}`
    return [
      ...(hasOption(parsed, '-sb') ? [`## ${header}`] : []),
      ...rows,
      ...untracked.map((path) => `?? ${path.slice(1)}`),
      ...ignored.map((path) => `!! ${path.slice(1)}`),
    ].join('\n')
  }
  const branch = headBranch(state)
  const lines = [branch ? `On branch ${branch}` : `HEAD detached at ${headCommit(state) ?? 'unknown'}`]
  if (!headCommit(state)) lines.push('', 'No commits yet')
  for (const [heading, entries] of [
    ['Changes to be committed:', staged],
    ['Unmerged paths:', unmerged],
    ['Changes not staged for commit:', unstaged],
    ['Untracked files:', untracked],
    ['Ignored files:', ignored],
  ] as const) {
    if (entries.length) lines.push('', heading, ...entries)
  }
  if (!staged.length && !unmerged.length) {
    if (lines.length > 1) lines.push('')
    lines.push(unstaged.length ? 'no changes added to commit' : untracked.length
      ? 'nothing added to commit but untracked files present'
      : headCommit(state) ? 'nothing to commit, working tree clean' : 'nothing to commit')
  }
  return lines.join('\n')
}

function statusCode(value: RepositoryValue, tracked: boolean) {
  const status = entryStatus(value)
  if (isDeleteMarker(status) || isDeleteMarker(value)) return 'D'
  return tracked ? 'M' : 'A'
}

function statusLabel(code: string) {
  return code === 'A' ? 'new file:' : code === 'D' ? 'deleted:' : 'modified:'
}

function formatBranch(state: MutableRepositoryState, outcome: CommandOutcome) {
  const details = outcome.details ?? {}
  if ('created' in details || 'renamed' in details) return ''
  if ('deleted' in details) return `Deleted branch ${details.deleted} (was ${details.target ?? ''}).`
  const verbose = Boolean(details.verbose)
  const showAll = Boolean(details.all)
  const onlyMerged = Boolean(details.merged)
  const current = headBranch(state)
  const currentHead = headCommit(state)
  const lines: string[] = []
  for (const [name, target] of Object.entries(state.branches ?? {}).sort(([left], [right]) => left.localeCompare(right))) {
    if (onlyMerged && !isAncestor(state, target, currentHead)) continue
    const marker = name === current ? '*' : ' '
    if (verbose) {
      const commit = commitById(state, target)
      lines.push(`${marker} ${name} ${target ?? ''} ${commit?.message ?? ''}`.trimEnd())
    } else {
      lines.push(`${marker} ${name}`)
    }
  }
  if (showAll) {
    for (const name of Object.keys(state.remote_branches ?? {}).sort()) lines.push(`  remotes/${name}`)
  }
  return lines.join('\n')
}

function formatRemote(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  const verbose = hasOption(parsed, '-v') || hasOption(parsed, '--verbose')
  return Object.entries(state.remotes ?? {})
    .sort(([left], [right]) => left.localeCompare(right))
    .flatMap(([name, url]) => (verbose ? [`${name}\t${url} (fetch)`, `${name}\t${url} (push)`] : [name]))
    .join('\n')
}

export function formatLog(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  const ids = hasOption(parsed, '--all')
    ? [...new Set(Object.values(state.branches ?? {}).filter(Boolean) as string[])]
    : [headCommit(state)].filter(Boolean) as string[]
  const seen: RepositoryCommit[] = []
  for (const id of ids) {
    for (const commitId of history(state, id)) {
      const commit = commitById(state, commitId)
      if (commit && !seen.some((item) => item.id === commit.id)) seen.push(commit)
    }
  }
  const limitRaw = optionValues(parsed, '-n', '--max-count').at(-1)
  const limit = limitRaw && limitRaw !== true ? Number(limitRaw) : null
  const commits = limit ? seen.slice(0, limit) : seen
  if (hasOption(parsed, '--oneline')) {
    return commits.map((commit) => `${commit.id} ${commit.message}`).join('\n')
  }
  return commits.map((commit) => `commit ${commit.id}\nAuthor: ${commit.author ?? 'GIT it'}\n\n    ${commit.message}`).join('\n\n')
}

export function formatShow(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  const nameOnly = hasOption(parsed, '--name-only')
  const expression = parsed.args.find((arg) => !arg.startsWith('-')) ?? 'HEAD'
  const separator = expression.indexOf(':')
  const ref = separator >= 0 ? expression.slice(0, separator) || 'HEAD' : expression
  const path = separator >= 0 ? expression.slice(separator + 1) : null
  const commit = commitById(state, resolveRevision(state, ref))
  if (!commit) throw new SimulatorCommandError(`fatal: ambiguous argument '${ref}'`)
  if (path !== null) {
    const tree = commit.tree ?? {}
    if (!path || !(path in tree)) {
      throw new SimulatorCommandError(`fatal: path '${path}' does not exist in '${ref}'`)
    }
    const content = tree[path]
    return typeof content === 'string' ? content : JSON.stringify(content, null, 2)
  }
  const header = `commit ${commit.id}\nAuthor: ${commit.author ?? 'GIT it'}\n\n    ${commit.message}`
  if (nameOnly) return [header, ...Object.keys(commit.changes ?? {})].join('\n')
  const body = Object.entries(commit.changes ?? {}).map(([path, change]) => `${path}\n${change.before ?? ''}\n${change.after ?? ''}`).join('\n')
  return [header, body].filter(Boolean).join('\n\n')
}

export function formatDiff(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  const nameOnly = hasOption(parsed, '--name-only')
  let changes: Record<string, { before?: RepositoryValue; after?: RepositoryValue; change_type?: string }>
  if (parsed.args.length === 1 && parsed.args[0].includes('..')) {
    const [left, right] = parsed.args[0].split('..')
    changes = diffTrees(treeForCommit(state, resolveRef(state, left)), treeForCommit(state, resolveRef(state, right)))
  } else if (hasOption(parsed, '--staged') || hasOption(parsed, '--cached')) {
    changes = changesFromEntries(headTree(state), state.staging ?? {})
  } else {
    const indexTree = applyChanges(headTree(state), changesFromEntries(headTree(state), state.staging ?? {}))
    const entries = Object.fromEntries(Object.entries(state.working_tree ?? {}).filter(([, value]) => !['ignored', 'untracked'].includes(entryStatus(value))))
    changes = changesFromEntries(indexTree, entries)
  }
  const paths = parsed.pathspecs.filter((path) => !path.startsWith('-') && path !== 'HEAD')
  if (paths.length) changes = Object.fromEntries(Object.entries(changes).filter(([path]) => paths.includes(path)))
  if (nameOnly) return Object.keys(changes).sort().join('\n')
  return Object.entries(changes)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([path, change]) => `diff --git a/${path} b/${path}\n--- a/${path}\n+++ b/${path}\n-${change.before ?? ''}\n+${change.after ?? ''}`)
    .join('\n')
}

export function formatReflog(state: MutableRepositoryState) {
  return (state.reflog ?? []).map((entry) => `${entry.target} ${entry.ref}: ${entry.message}`).join('\n')
}

export function formatLsFiles(state: MutableRepositoryState, parsed: ParsedGitCommand) {
  if (hasOption(parsed, '-u') || hasOption(parsed, '--unmerged')) {
    return (state.conflicts ?? []).map((path) => `100644 ${path} 1\t${path}`).join('\n')
  }
  return [...new Set([...Object.keys(headTree(state)), ...Object.keys(state.staging ?? {})])].sort().join('\n')
}

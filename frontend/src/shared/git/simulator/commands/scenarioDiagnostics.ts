import { hasOption } from '@/shared/git/simulator/parser'
import { headBranch, headCommit, isRecord } from '@/shared/git/simulator/state'
import {
  SimulatorCommandError,
  type CommandOutcome,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'

export function gitBisect(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const action = parsed.args[0]
  const metadata = state.operation_metadata ?? {}
  if (action === 'run') {
    const testName = parsed.args.slice(1).join(' ') || 'authored-test'
    const firstBad = String(metadata.first_bad_commit ?? headCommit(state) ?? 'HEAD')
    return {
      command: 'bisect',
      stdout: [
        `running ${testName}`,
        `Bisecting: tested the authored history between ${String(metadata.bisect_good ?? 'good')} and ${String(metadata.bisect_bad ?? 'bad')}.`,
        `${firstBad} is the first bad commit`,
      ].join('\n'),
    }
  }
  if (action === 'log') {
    return {
      command: 'bisect',
      stdout: [
        `# bad: [${String(metadata.bisect_bad ?? headCommit(state) ?? 'HEAD')}] known-bad boundary`,
        `# good: [${String(metadata.bisect_good ?? 'root')}] known-good boundary`,
        `# first bad: [${String(metadata.first_bad_commit ?? headCommit(state) ?? 'HEAD')}]`,
      ].join('\n'),
    }
  }
  throw new SimulatorCommandError('fatal: this curriculum tranche supports git bisect run and git bisect log')
}

export function gitRerere(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const action = parsed.args[0]
  const metadata = state.operation_metadata ?? {}
  const paths = asStringList(metadata.rerere_paths ?? state.conflicts ?? [])
  if (action === 'status') {
    return { command: 'rerere', stdout: paths.join('\n') }
  }
  if (action === 'diff') {
    const rows = paths.flatMap((path) => [
      `--- a/${path}`,
      `+++ b/${path}`,
      `@@ recorded resolution for ${path} @@`,
      `-${String(metadata.rerere_before ?? 'conflicted content')}`,
      `+${String(metadata.rerere_after ?? 'recorded resolution')}`,
    ])
    return { command: 'rerere', stdout: rows.join('\n') }
  }
  throw new SimulatorCommandError('usage: git rerere (status | diff)')
}

export function gitWorktree(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  if (parsed.args[0] !== 'list') throw new SimulatorCommandError('usage: git worktree list')
  const authored = state.operation_metadata?.worktrees
  const worktrees = Array.isArray(authored) ? authored : []
  const rows = worktrees
    .filter(isRecord)
    .map((entry) => {
      const path = String(entry.path ?? '/workspace/repository')
      const commit = String(entry.commit ?? headCommit(state) ?? '0000000')
      const branch = String(entry.branch ?? headBranch(state) ?? 'detached')
      return `${path}  ${commit} [${branch}]`
    })
  if (!rows.length) {
    rows.push(`/workspace/repository  ${headCommit(state) ?? '0000000'} [${headBranch(state) ?? 'detached'}]`)
  }
  return { command: 'worktree', stdout: rows.join('\n') }
}

export function gitSparseCheckout(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  if (parsed.args[0] !== 'list') throw new SimulatorCommandError('usage: git sparse-checkout list')
  return {
    command: 'sparse-checkout',
    stdout: asStringList(state.operation_metadata?.sparse_paths).join('\n'),
  }
}

export function gitSubmodule(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  if (parsed.args[0] !== 'status') throw new SimulatorCommandError('usage: git submodule status')
  const authored = state.operation_metadata?.submodules
  const submodules = Array.isArray(authored) ? authored : []
  return {
    command: 'submodule',
    stdout: submodules
      .filter(isRecord)
      .map((entry) => {
        const prefix = entry.initialized === false ? '-' : ' '
        return `${prefix}${String(entry.commit ?? '0000000')} ${String(entry.path ?? 'vendor/module')} (${String(entry.describe ?? 'heads/main')})`
      })
      .join('\n'),
  }
}

export function configGet(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome | null {
  if (!hasOption(parsed, '--get')) return null
  const key = parsed.args[0]
  const value = state.config?.[key]
  return {
    command: 'config',
    stdout: value === undefined ? '' : String(value),
    exitCode: value === undefined ? 1 : 0,
  }
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.map(String)
}

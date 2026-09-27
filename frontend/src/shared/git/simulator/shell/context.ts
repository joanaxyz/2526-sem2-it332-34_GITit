import type { RepositoryValue } from '@/shared/level/types'
import { entryContent, visibleProjectTree } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { WorkspaceFileError } from '@/shared/git/simulator/workspaceFiles'
import { parentPath, pathKind } from '@/shared/git/simulator/workspaceTree'
import { isInsideGitDirectory, resolveShellPath } from '@/shared/git/simulator/shell/syntax'

/** Mutable state for one shell command: the working copy, cwd, and output. */
export type ShellRun = {
  state: MutableRepositoryState
  cwd: string
  projectName: string
  out: string[]
  err: string[]
  exitCode: number
}

export function fail(run: ShellRun, message: string, exitCode = 1) {
  run.err.push(message)
  run.exitCode = Math.max(run.exitCode, exitCode)
}

/** Apply a workspace mutation, reporting a rejected path as a command error. */
export function mutate(run: ShellRun, prefix: string, apply: (state: MutableRepositoryState) => MutableRepositoryState) {
  try {
    run.state = apply(run.state)
    return true
  } catch (error) {
    if (!(error instanceof WorkspaceFileError)) throw error
    fail(run, `${prefix}: ${error.message}`)
    return false
  }
}

/** Resolve an operand, or return the reason it cannot be used. */
export function resolveOperand(run: ShellRun, operand: string): { path: string } | { error: string } {
  const path = resolveShellPath(run.cwd, operand)
  if (path === null) return { error: operand ? 'outside the project folder' : 'No such file or directory' }
  if (isInsideGitDirectory(path)) return { error: 'Permission denied' }
  return { path }
}

/** Why `path` cannot receive a new entry: its parent is missing or is a file. */
export function missingParentReason(state: MutableRepositoryState, path: string) {
  const kind = pathKind(state, parentPath(path))
  if (kind === 'directory') return null
  return kind === 'file' ? 'Not a directory' : 'No such file or directory'
}

export function fileContent(state: MutableRepositoryState, path: string): RepositoryValue {
  const entry = visibleProjectTree(state, true)[path]
  const content = entryContent(entry)
  return content ?? ''
}

export function baseName(path: string) {
  return path.split('/').filter(Boolean).at(-1) ?? path
}

export function joinPath(directory: string, name: string) {
  return directory ? `${directory}/${name}` : name
}

/** `operand` with `name` appended, as the learner would write it. */
export function joinDisplay(operand: string, name: string) {
  return `${operand.replace(/\/+$/, '')}/${name}`
}

export type ParsedFlags = { flags: Set<string>; operands: string[] }

/**
 * Split `-rf`-style short flags and `--long` flags from operands. Unknown flags
 * fail the command the way coreutils does.
 */
export function parseFlags(
  run: ShellRun,
  program: string,
  args: string[],
  known: Record<string, string>,
): ParsedFlags | null {
  const flags = new Set<string>()
  const operands: string[] = []
  let optionsDone = false
  for (const arg of args) {
    if (optionsDone || arg === '-' || !arg.startsWith('-')) {
      operands.push(arg)
      continue
    }
    if (arg === '--') {
      optionsDone = true
      continue
    }
    if (arg.startsWith('--')) {
      const flag = known[arg]
      if (!flag) {
        fail(run, `${program}: unrecognized option '${arg}'`)
        return null
      }
      flags.add(flag)
      continue
    }
    for (const char of arg.slice(1)) {
      const flag = known[char]
      if (!flag) {
        fail(run, `${program}: invalid option -- '${char}'`)
        return null
      }
      flags.add(flag)
    }
  }
  return { flags, operands }
}

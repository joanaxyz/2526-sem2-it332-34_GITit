import { normalizeState } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { parentPath, pathKind } from '@/shared/git/simulator/workspaceTree'
import { fail, projectFolder, type ShellRun } from '@/shared/git/simulator/shell/context'
import { cp, mkdir, mv, rm, rmdir, touch } from '@/shared/git/simulator/shell/fileCommands'
import {
  ShellSyntaxError,
  expandShellWords,
  parseShellCommand,
  type ShellInvocation,
} from '@/shared/git/simulator/shell/syntax'
import { cat, cd, echo, ls, pwd, tree } from '@/shared/git/simulator/shell/viewCommands'

/**
 * Programs the workspace terminal runs besides git. Read-only ones are free
 * diagnostics; file-changing ones edit the working copy like the Project Files
 * panel. The backend keeps the same lists in `common/git/shell_commands.py`.
 */
const READ_ONLY_PROGRAMS = new Set(['pwd', 'ls', 'cd', 'tree', 'cat', 'echo', 'clear'])
const FILE_PROGRAMS = new Set(['touch', 'mkdir', 'rmdir', 'rm', 'mv', 'cp'])
const REDIRECTABLE_PROGRAMS = new Set(['echo', 'cat'])

/** `outside`: the terminal stands in `/workspace`, one level above the project folder. */
export type ShellContext = { cwd?: string; outside?: boolean; projectName?: string }

export type ShellExecution = {
  program: string
  state: MutableRepositoryState
  cwd: string
  outside: boolean
  stdout: string
  stderr: string
  exitCode: number
  /** True when the command may change the working copy (and so is replayed by the backend). */
  changesFiles: boolean
  /** True when a file edit was not run because it was typed from the (unsimulated) workspace folder. */
  refused: boolean
}

/** The shell program a command starts with, or `null` for git and unknown programs. */
export function shellProgram(command: string) {
  const first = command.trim().split(/\s+/)[0] ?? ''
  return READ_ONLY_PROGRAMS.has(first) || FILE_PROGRAMS.has(first) ? first : null
}

function changesFiles(invocation: ShellInvocation | null) {
  if (!invocation) return false
  if (FILE_PROGRAMS.has(invocation.program)) return true
  return REDIRECTABLE_PROGRAMS.has(invocation.program) && invocation.redirect !== null
}

/** Nearest folder at or above `cwd` that still exists in the working copy. */
export function effectiveCwd(state: MutableRepositoryState, cwd = '') {
  let current = cwd
  while (current && pathKind(state, current) !== 'directory') current = parentPath(current)
  return current
}

export function executeShellCommand(
  repositoryState: MutableRepositoryState,
  command: string,
  context: ShellContext = {},
): ShellExecution {
  const state = normalizeState(repositoryState)
  const run: ShellRun = {
    state,
    cwd: context.outside ? '' : effectiveCwd(state, context.cwd ?? ''),
    outside: Boolean(context.outside),
    projectName: context.projectName || 'project',
    out: [],
    err: [],
    exitCode: 0,
  }

  let invocation: ShellInvocation | null = null
  try {
    invocation = parseShellCommand(command)
  } catch (error) {
    if (!(error instanceof ShellSyntaxError)) throw error
    fail(run, `bash: ${error.message}`, 2)
  }
  // Only the project folder is simulated, so a file edit typed from the
  // workspace folder above it is refused instead of guessed at.
  const refused = Boolean(invocation && run.outside && changesFiles(invocation))
  if (invocation && refused) {
    const folder = projectFolder(run)
    fail(run, `${invocation.program}: not run: this terminal only edits files inside ${folder}/ (run 'cd ${folder}' first)`)
  } else if (invocation) {
    runProgram(run, invocation)
  }

  return {
    program: shellProgram(command) ?? '',
    state: run.state,
    cwd: run.outside ? '' : effectiveCwd(run.state, run.cwd),
    outside: run.outside,
    stdout: run.out.join('\n'),
    stderr: run.err.join('\n'),
    exitCode: run.exitCode,
    changesFiles: changesFiles(invocation),
    refused,
  }
}

function runProgram(run: ShellRun, invocation: ShellInvocation) {
  const { program, redirect } = invocation
  if (redirect && !REDIRECTABLE_PROGRAMS.has(program)) {
    return fail(run, `bash: output redirection is only supported for echo and cat in this terminal`)
  }
  // Globs match project paths, so from the workspace folder they stay literal.
  const args = run.outside
    ? invocation.args.map((word) => word.text)
    : expandShellWords(run.state, run.cwd, invocation.args)
  switch (program) {
    case 'pwd':
      return pwd(run)
    case 'cd':
      return cd(run, args)
    case 'ls':
      return ls(run, args)
    case 'tree':
      return tree(run, args)
    case 'cat':
      return cat(run, args, redirect)
    case 'echo':
      return echo(run, args, redirect)
    case 'clear':
      return
    case 'touch':
      return touch(run, args)
    case 'mkdir':
      return mkdir(run, args)
    case 'rmdir':
      return rmdir(run, args)
    case 'rm':
      return rm(run, args)
    case 'mv':
      return mv(run, args)
    case 'cp':
      return cp(run, args)
  }
}

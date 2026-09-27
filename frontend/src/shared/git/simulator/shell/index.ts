import { normalizeState } from '@/shared/git/simulator/state'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { parentPath, pathKind } from '@/shared/git/simulator/workspaceTree'
import { fail, type ShellRun } from '@/shared/git/simulator/shell/context'
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

export type ShellContext = { cwd?: string; projectName?: string }

export type ShellExecution = {
  program: string
  state: MutableRepositoryState
  cwd: string
  stdout: string
  stderr: string
  exitCode: number
  /** True when the command may change the working copy (and so is replayed by the backend). */
  changesFiles: boolean
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
    cwd: effectiveCwd(state, context.cwd ?? ''),
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
  if (invocation) runProgram(run, invocation)

  return {
    program: shellProgram(command) ?? '',
    state: run.state,
    cwd: effectiveCwd(run.state, run.cwd),
    stdout: run.out.join('\n'),
    stderr: run.err.join('\n'),
    exitCode: run.exitCode,
    changesFiles: changesFiles(invocation),
  }
}

function runProgram(run: ShellRun, invocation: ShellInvocation) {
  const { program, redirect } = invocation
  if (redirect && !REDIRECTABLE_PROGRAMS.has(program)) {
    return fail(run, `bash: output redirection is only supported for echo and cat in this terminal`)
  }
  const args = expandShellWords(run.state, run.cwd, invocation.args)
  switch (program) {
    case 'pwd':
      return pwd(run)
    case 'cd':
      return cd(run, args, enterableNames(run))
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

function enterableNames(run: ShellRun) {
  const metadata = run.state.operation_metadata ?? {}
  return [run.projectName, metadata.last_clone_directory, metadata.last_init_directory].filter(
    (name): name is string => typeof name === 'string' && name.length > 0,
  )
}

import type {
  CommandExecutionPayload,
  RepositoryCommandState,
} from '@/shared/level/types'
import { GitCommandParser } from '@/shared/git/simulator/parser'
import {
  SUPPORTED_OPTIONS,
  diagnosticMetadataForCommand,
  isDiagnosticCommand,
  requestsCommandHelp,
  validateCommand,
} from '@/shared/git/simulator/commandMetadata'
import { commandHelpText, gitHelpText } from '@/shared/git/simulator/help'
import { dispatch } from '@/shared/git/simulator/commands'
import { formatOutcome } from '@/shared/git/simulator/commands/formatters'
import {
  GitCommandParseError,
  NonGitCommandError,
  SimulatorCommandError,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'
import { normalizeState } from '@/shared/git/simulator/state'
import { rebaseGitPathspecs } from '@/shared/git/simulator/gitPathspecs'
import { pathKind } from '@/shared/git/simulator/workspaceTree'
import {
  effectiveCwd,
  executeShellCommand,
  shellProgram,
  type ShellContext,
} from '@/shared/git/simulator/shell'

export type TerminalContext = ShellContext

export type TerminalExecution = {
  execution: CommandExecutionPayload
  /** Working directory after the command (project-relative, `''` is the root). */
  cwd: string
  /** True when the terminal now stands in the workspace folder above the project. */
  outside: boolean
}

/**
 * Run one line typed into the workspace terminal: a shell command (`ls`, `cd`,
 * `mkdir`, ...) or a git command. `context.cwd` is the terminal's working
 * directory; git pathspecs are read relative to it like real git. The payload
 * carries the directory the command ran in so the backend can replay it.
 *
 * `context.outside` means the learner stands in the workspace folder above the
 * project, where `git init <dir>` and `git clone` leave them until they `cd`
 * in. Git still runs against the project there (authored scenarios clone and
 * keep going), so this only changes what the shell shows and allows.
 */
export function executeTerminalCommand(
  repositoryState: MutableRepositoryState,
  command: string,
  context: TerminalContext = {},
): TerminalExecution {
  const state = normalizeState(repositoryState)
  const outside = Boolean(context.outside)
  const cwd = outside ? '' : effectiveCwd(state, context.cwd ?? '')
  const withCwd = (execution: CommandExecutionPayload) => (cwd ? { ...execution, cwd } : execution)

  if (shellProgram(command)) {
    const shell = executeShellCommand(state, command, { ...context, cwd, outside })
    const execution = result({
      // A file edit the simulator cannot place (outside the project folder)
      // is not run, so the backend has nothing to replay.
      processed: !shell.refused,
      state: shell.state,
      output: [shell.stdout, shell.stderr].filter(Boolean).join('\n'),
      normalizedCommand: collapseWhitespace(command),
      exitCode: shell.exitCode,
      stdout: shell.stdout,
      stderr: shell.stderr,
      commandFamily: shell.program,
      // Read-only shell commands are free diagnostics. File-changing ones are
      // replayed by the backend and never count against the command budget.
      diagnostic: !shell.changesFiles,
      diagnosticMetadata: shell.program === 'cd' ? ['changed_directory'] : [],
    })
    return { execution: withCwd(execution), cwd: shell.cwd, outside: shell.outside }
  }

  const rootCommand = rebaseGitPathspecs(command, cwd)
  const execution = runGitCommand(state, rootCommand)
  if (rootCommand !== command) execution.normalized_command = normalizedGitCommand(command)
  if (createdNamedRepositoryFolder(state, execution)) return { execution: withCwd(execution), cwd: '', outside: true }
  return { execution: withCwd(execution), cwd, outside }
}

/**
 * `git init <dir>` and `git clone <url> [<dir>]` create the repository in a new
 * folder and leave the shell where it was, one level above it. The simulator
 * shows that new folder as the project, so the terminal moves to the workspace
 * above it. `git init` on a folder already inside the project stays put: that
 * repository really is a subfolder.
 */
function createdNamedRepositoryFolder(before: MutableRepositoryState, execution: CommandExecutionPayload) {
  if (!execution.processed || execution.exit_code !== 0) return false
  if (execution.command_family === 'clone') return true
  if (execution.command_family !== 'init') return false
  const metadata = execution.next_state.operation_metadata
  const directory = metadata && typeof metadata === 'object' && !Array.isArray(metadata)
    ? metadata.last_init_directory
    : null
  if (typeof directory !== 'string') return false
  const folder = directory.replace(/\/+$/, '')
  return folder !== '' && folder !== '.' && pathKind(before, folder) !== 'directory'
}

export function executeGitCommand(
  repositoryState: MutableRepositoryState,
  command: string,
  context: TerminalContext = {},
): CommandExecutionPayload {
  return executeTerminalCommand(repositoryState, command, context).execution
}

function collapseWhitespace(command: string) {
  return command.trim().split(/\s+/).filter(Boolean).join(' ')
}

function normalizedGitCommand(command: string) {
  try {
    return new GitCommandParser().parse(command).normalizedText
  } catch {
    return collapseWhitespace(command)
  }
}

function runGitCommand(
  repositoryState: MutableRepositoryState,
  command: string,
): CommandExecutionPayload {
  const normalizedFallback = collapseWhitespace(command)

  let parsed: ParsedGitCommand
  try {
    parsed = new GitCommandParser().parse(command)
  } catch (error) {
    if (error instanceof NonGitCommandError) {
      return result({
        processed: false,
        state: normalizeState(repositoryState),
        output: error.message,
        normalizedCommand: normalizedFallback,
        exitCode: error.exitCode,
      })
    }
    if (error instanceof GitCommandParseError) {
      return result({
        processed: false,
        state: normalizeState(repositoryState),
        output: error.message,
        normalizedCommand: normalizedFallback,
        exitCode: error.exitCode,
      })
    }
    throw error
  }

  const state = normalizeState(repositoryState)
  const spec = SUPPORTED_OPTIONS[parsed.subcommand]
  if (spec && requestsCommandHelp(parsed)) {
    const help = commandHelpText(parsed.subcommand)!
    // Git's short usage (-h) exits 129 on stdout; help never executes the command.
    return result({
      processed: true, state, output: help, normalizedCommand: parsed.normalizedText,
      exitCode: parsed.options['-h'] ? 129 : 0, stdout: help,
      commandFamily: parsed.subcommand, diagnostic: true,
    })
  }
  if (!spec) {
    if (['', '-h', '--help', 'help'].includes(parsed.subcommand)) {
      const topic = parsed.args[0]
      const helpText = topic ? commandHelpText(topic) : gitHelpText(
        Object.hasOwn(parsed.options, '-a') || Object.hasOwn(parsed.options, '--all'),
      )
      if (helpText === null) {
        return result({ processed: false, state, output: `git: '${topic}' is not a git command. See 'git --help'.`,
          normalizedCommand: parsed.normalizedText, exitCode: 1 })
      }
      return result({
        processed: Boolean(parsed.subcommand),
        state,
        output: helpText,
        normalizedCommand: parsed.normalizedText,
        exitCode: parsed.subcommand ? 0 : 1,
        stdout: helpText,
        commandFamily: parsed.subcommand,
        diagnostic: Boolean(parsed.subcommand),
        diagnosticMetadata: ['inspected_git_help'],
      })
    }
    if (parsed.subcommand === '--version' || parsed.subcommand === 'version') {
      const versionText = 'git version 2.47.3 (simulated)'
      return result({
        processed: true,
        state,
        output: versionText,
        normalizedCommand: parsed.normalizedText,
        exitCode: 0,
        stdout: versionText,
        commandFamily: parsed.subcommand,
        diagnostic: true,
        diagnosticMetadata: ['inspected_git_version'],
      })
    }
    const message = parsed.subcommand.startsWith('-')
      ? `unknown option: ${parsed.subcommand}`
      : `git: '${parsed.subcommand}' is not a git command. See 'git --help'.`
    return result({
      processed: false,
      state,
      output: message,
      normalizedCommand: parsed.normalizedText,
      exitCode: parsed.subcommand.startsWith('-') ? 129 : 1,
    })
  }

  const validationError = validateCommand(parsed)
  if (validationError) {
    return result({
      processed: false,
      state,
      output: validationError,
      normalizedCommand: parsed.normalizedText,
      exitCode: validationError.startsWith('fatal:') ? 128 : 129,
      diagnostic: isDiagnosticCommand(parsed),
      commandFamily: parsed.subcommand,
    })
  }

  const globalConfig = parsed.subcommand === 'config' && Object.hasOwn(parsed.options, '--global')
  if (!state.repository_initialized && !['init', 'clone'].includes(parsed.subcommand) && !globalConfig) {
    const message = 'fatal: not a git repository (or any of the parent directories): .git'
    return result({
      processed: true,
      state,
      output: message,
      normalizedCommand: parsed.normalizedText,
      exitCode: 128,
      stderr: message,
      commandFamily: parsed.subcommand,
      diagnostic: isDiagnosticCommand(parsed),
      diagnosticMetadata: diagnosticMetadataForCommand(parsed),
    })
  }

  try {
    const outcome = dispatch(state, parsed)
    const stdout = outcome.stdout ?? formatOutcome(state, parsed, outcome)
    const stderr = outcome.stderr ?? ''
    return result({
      processed: true,
      state: normalizeState(state),
      output: [stdout, stderr].filter(Boolean).join('\n'),
      normalizedCommand: parsed.normalizedText,
      exitCode: outcome.exitCode ?? 0,
      stdout,
      stderr,
      commandFamily: parsed.subcommand,
      diagnostic: isDiagnosticCommand(parsed),
      diagnosticMetadata: diagnosticMetadataForCommand(parsed),
    })
  } catch (error) {
    if (error instanceof SimulatorCommandError) {
      return result({
        processed: false,
        state: normalizeState(repositoryState),
        output: error.message,
        normalizedCommand: parsed.normalizedText,
        exitCode: error.exitCode,
        stderr: error.message,
        commandFamily: parsed.subcommand,
        diagnostic: isDiagnosticCommand(parsed),
      })
    }
    throw error
  }
}

function result({
  processed,
  state,
  output,
  normalizedCommand,
  exitCode,
  diagnostic = false,
  stdout = '',
  stderr = '',
  commandFamily = '',
  diagnosticMetadata = [],
}: {
  processed: boolean
  state: MutableRepositoryState
  output: string
  normalizedCommand: string
  exitCode: number
  diagnostic?: boolean
  stdout?: string
  stderr?: string
  commandFamily?: string
  diagnosticMetadata?: string[]
}): CommandExecutionPayload {
  return {
    processed,
    // Mutable simulator state is normalized to the JSON-safe repository shape
    // accepted by the generated command contract at this single owner boundary.
    next_state: state as RepositoryCommandState,
    output,
    normalized_command: normalizedCommand,
    exit_code: exitCode,
    diagnostic,
    stdout,
    stderr: stderr || (!stdout && exitCode ? output : ''),
    command_family: commandFamily,
    diagnostic_metadata: diagnosticMetadata,
  }
}

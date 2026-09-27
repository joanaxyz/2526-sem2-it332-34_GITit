import type {
  CommandExecutionPayload,
  RepositoryCommandState,
  RepositorySnapshot,
} from '@/shared/level/types'
import { GitCommandParser } from '@/shared/git/simulator/parser'
import {
  GIT_COMMAND_NAMES,
  SUPPORTED_OPTIONS,
  diagnosticMetadataForCommand,
  isDiagnosticCommand,
  validateCommand,
} from '@/shared/git/simulator/commandMetadata'
import { dispatch } from '@/shared/git/simulator/commands'
import { formatOutcome } from '@/shared/git/simulator/commands/formatters'
import {
  GitCommandParseError,
  NonGitCommandError,
  SimulatorCommandError,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'
import { normalizeState, snapshotForCommand } from '@/shared/git/simulator/state'
import { rebaseGitPathspecs } from '@/shared/git/simulator/gitPathspecs'
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
}

/**
 * Run one line typed into the workspace terminal: a shell command (`ls`, `cd`,
 * `mkdir`, ...) or a git command. `context.cwd` is the terminal's working
 * directory; git pathspecs are read relative to it like real git. The payload
 * carries the directory the command ran in so the backend can replay it.
 */
export function executeTerminalCommand(
  repositoryState: MutableRepositoryState,
  command: string,
  context: TerminalContext = {},
): TerminalExecution {
  const state = normalizeState(repositoryState)
  const cwd = effectiveCwd(state, context.cwd ?? '')
  const withCwd = (execution: CommandExecutionPayload) => (cwd ? { ...execution, cwd } : execution)

  if (shellProgram(command)) {
    const shell = executeShellCommand(state, command, { ...context, cwd })
    const execution = result({
      processed: true,
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
    return { execution: withCwd(execution), cwd: shell.cwd }
  }

  const rootCommand = rebaseGitPathspecs(command, cwd)
  const execution = runGitCommand(state, rootCommand)
  if (rootCommand !== command) execution.normalized_command = normalizedGitCommand(command)
  return { execution: withCwd(execution), cwd }
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
  if (!spec) {
    if (parsed.subcommand === '--global' && parsed.args[0] === 'config') {
      const guidance =
        'error: invalid git config order.\nUse: git config --global <key> <value>\nOr list values with: git config --list'
      return result({
        processed: false,
        state,
        output: guidance,
        normalizedCommand: parsed.normalizedText,
        exitCode: 129,
        stderr: guidance,
      })
    }
    if (parsed.subcommand === '--help' || parsed.subcommand === 'help') {
      const helpText = gitHelpText(parsed)
      return result({
        processed: true,
        state,
        output: helpText,
        normalizedCommand: parsed.normalizedText,
        exitCode: 0,
        stdout: helpText,
        commandFamily: parsed.subcommand,
        diagnostic: true,
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
    const commandName = parsed.subcommand || parsed.normalizedText
    return result({
      processed: false,
      state,
      output: `git: '${commandName}' is not supported in this simulator.`,
      normalizedCommand: parsed.normalizedText,
      exitCode: 129,
    })
  }

  const validationError = validateCommand(parsed)
  if (validationError) {
    return result({
      processed: false,
      state,
      output: validationError,
      normalizedCommand: parsed.normalizedText,
      exitCode: 129,
      diagnostic: isDiagnosticCommand(parsed),
      commandFamily: parsed.subcommand,
    })
  }

  if (!state.repository_initialized && !['init', 'clone'].includes(parsed.subcommand)) {
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

function gitHelpText(parsed: ParsedGitCommand) {
  if (wantsCompleteHelp(parsed)) return completeGitHelpText()
  return [
    'usage: git <command> [<args>]',
    '',
    'Common commands: status, add, commit, log, branch, restore, diff, config',
    '',
    `This simulator supports ${GIT_COMMAND_NAMES.length} commands used by GIT IT lessons.`,
    "Run 'git help -a' to list the supported simulator commands.",
  ].join('\n')
}

function wantsCompleteHelp(parsed: ParsedGitCommand) {
  return (
    Object.hasOwn(parsed.options, '-a') ||
    Object.hasOwn(parsed.options, '--all') ||
    parsed.args.includes('all')
  )
}

function completeGitHelpText() {
  const playableCommands = Object.keys(SUPPORTED_OPTIONS).sort()

  return [
    `Supported simulator commands (${GIT_COMMAND_NAMES.length})`,
    '',
    'Commands:',
    formatCommandList(playableCommands),
  ].join('\n')
}

function formatCommandList(commands: string[]) {
  return commands.map((command) => `  git ${command}`).join('\n')
}

/**
 * Derive the canonical target repository state by replaying an authored
 * solution against an initial state through the same engine learners use. This
 * is the authoring-time counterpart of the runtime submit path: the frontend
 * (not Django) owns command execution, so content authoring computes the target
 * here and ships it in the definition for the backend to persist and hash.
 */
export function computeTargetState(
  initialState: MutableRepositoryState,
  solutionCommands: string[],
): RepositorySnapshot {
  let state = normalizeState(initialState)
  let cwd = ''
  for (const command of solutionCommands) {
    if (!command.trim()) continue
    const terminal = executeTerminalCommand(state, command, { cwd })
    state = terminal.execution.next_state
    cwd = terminal.cwd
  }
  return snapshotForCommand(state, true)
}

/**
 * The state in front of every solution command, in the shape
 * `generate-targets.mjs` emits. The backend fingerprints it into the variant's
 * solution trajectory, which tells the tutor which step a learner is at.
 */
export function replaySolution(initialState: MutableRepositoryState, solutionCommands: string[]) {
  let state = normalizeState(initialState)
  let cwd = ''
  const steps = []
  for (const command of solutionCommands) {
    if (!command.trim()) continue
    const { execution, cwd: nextCwd } = executeTerminalCommand(state, command, { cwd })
    steps.push({ command, diagnostic: Boolean(execution.diagnostic), ready: normalizeState(state) })
    state = execution.next_state
    cwd = nextCwd
  }
  return { steps, final: normalizeState(state) }
}

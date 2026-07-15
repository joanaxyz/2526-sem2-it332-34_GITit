import type { RepositorySnapshot } from '@/shared/level/types'
import { GitCommandParser, normalizeCommand } from '@/shared/git/simulator/parser'
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
  type CommandExecutionPayload,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'
import { normalizeState, snapshotForCommand } from '@/shared/git/simulator/state'

export function executeGitCommand(
  repositoryState: MutableRepositoryState,
  command: string,
): CommandExecutionPayload {
  const normalizedFallback = command.trim().split(/\s+/).filter(Boolean).join(' ')

  // `cd` is shell navigation, not git. This simulator models a single repository
  // (no separate working directory), so `cd` is accepted as a no-op: it lets
  // realistic onboarding flows (clone/init a folder, then `cd` into it) read
  // naturally without changing repository state. Marked diagnostic so it never
  // counts against a level's command budget. `mkdir` is intentionally NOT
  // supported - directories exist implicitly via file paths.
  if (normalizedFallback === 'cd' || normalizedFallback.startsWith('cd ')) {
    return result({
      processed: true,
      state: normalizeState(repositoryState),
      output: '',
      normalizedCommand: normalizedFallback,
      exitCode: 0,
      stdout: '',
      commandFamily: 'cd',
      diagnostic: true,
      diagnosticMetadata: ['changed_directory'],
    })
  }

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
    next_state: state,
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
  for (const command of solutionCommands) {
    if (!command.trim()) continue
    state = executeGitCommand(state, command).next_state
  }
  return snapshotForCommand(state, true)
}

export { normalizeCommand }

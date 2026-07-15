import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'

export type MutableRepositoryState = RepositorySnapshot & {
  config?: Record<string, RepositoryValue>
  remote_fixtures?: RepositoryValue
  remote_updates?: Record<string, string | null>
  merge_abort_state?: MutableRepositoryState
  merge_parent?: string | null
  merge_conflicts?: RepositoryValue
  merge_resolutions?: Record<string, RepositoryValue>
  conflict_on_merge?: boolean
  conflict_files?: string[]
  merge_conflict_files?: string[]
  cherry_pick_in_progress?: boolean
  cherry_pick_original_head?: string | null
  rebase_state?: RepositoryValue
  [key: string]: unknown
}

export type CommandExecutionPayload = {
  processed: boolean
  next_state: MutableRepositoryState
  output: string
  normalized_command: string
  exit_code: number
  diagnostic: boolean
  stdout: string
  stderr: string
  command_family: string
  diagnostic_metadata: string[]
  /** Client-side run revision used to reject stale optimistic submissions. */
  client_run_revision?: number
}

export type ParsedGitCommand = {
  rawText: string
  normalizedText: string
  argv: string[]
  subcommand: string
  originalSubcommand: string
  args: string[]
  options: Record<string, Array<string | true>>
  pathspecs: string[]
  message: string | null
}

export type CommandOutcome = {
  command: string
  details?: Record<string, RepositoryValue>
  stdout?: string
  stderr?: string
  exitCode?: number
}

export class GitCommandParseError extends Error {
  exitCode = 129
}

export class NonGitCommandError extends Error {
  exitCode = 127
  commandName: string

  constructor(commandName: string) {
    super(`${commandName}: command not found`)
    this.commandName = commandName
  }
}

export class SimulatorCommandError extends Error {
  exitCode: number

  constructor(
    message: string,
    exitCode = 128,
  ) {
    super(message)
    this.exitCode = exitCode
  }
}

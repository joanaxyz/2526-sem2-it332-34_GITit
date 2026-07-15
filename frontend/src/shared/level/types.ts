export type RepositoryValue =
  | string
  | number
  | boolean
  | null
  | RepositoryValue[]
  | { [key: string]: RepositoryValue }

export type RepositoryCommit = {
  id: string
  message: string
  parents: string[]
  tree?: Record<string, RepositoryValue>
  changes?: Record<
    string,
    {
      change_type?: string
      before?: RepositoryValue
      after?: RepositoryValue
    }
  >
  files?: Record<string, RepositoryValue>
  author?: string
  order?: number
  is_merge?: boolean
}

export type ConflictDetail = {
  base?: RepositoryValue
  ours?: RepositoryValue
  theirs?: RepositoryValue
  resolution?: RepositoryValue
  merged?: RepositoryValue
  merge_branch?: string
}

export type RepositorySnapshot = {
  repository_initialized?: boolean
  commits: RepositoryCommit[]
  branches: Record<string, string | null>
  head: {
    type: 'branch' | 'detached'
    name?: string
    target?: string | null
  }
  staging: Record<string, RepositoryValue>
  working_tree: Record<string, RepositoryValue>
  conflicts: string[]
  conflict_details?: Record<string, ConflictDetail>
  remotes?: Record<string, string>
  remote_branches?: Record<string, string | null>
  upstream_tracking?: Record<string, string>
  tags?: Record<string, RepositoryValue>
  remote_tags?: Record<string, RepositoryValue>
  stash_stack?: Array<{
    working_tree?: Record<string, RepositoryValue>
    staging?: Record<string, RepositoryValue>
    conflicts?: string[]
    message?: string
  }>
  reflog?: Array<Record<string, string | null>>
  partial_hunks?: Record<string, RepositoryValue>
  replaced_commits?: Record<string, string>
  operation_metadata?: Record<string, RepositoryValue>
  config?: Record<string, RepositoryValue>
  remote_fixtures?: RepositoryValue
  remote_updates?: Record<string, string | null>
  merge_abort_state?: RepositorySnapshot
  merge_parent?: string | null
  merge_conflicts?: RepositoryValue
  merge_resolutions?: Record<string, RepositoryValue>
  conflict_on_merge?: boolean
  conflict_files?: string[]
  merge_conflict_files?: string[]
  cherry_pick_in_progress?: boolean
  cherry_pick_original_head?: string | null
  rebase_state?: RepositoryValue
  project_tree?: Record<string, RepositoryValue>
  visible_tree?: Record<string, RepositoryValue>
}

export type CopyDetail = {
  label: string
  value: string
}

// Strict schema_version 3 story: the backend normalizer whitelists exactly
// these keys, so the frontend never has to guess. The adventure objective
// checklist is NOT part of this shape - it arrives as a separate top-level
// `objective_checks` payload field.
export type LevelScenarioContext = {
  schema_version?: number
  story?: string
  task?: string
  details?: CopyDetail[]
}

export type RepositoryVisualization = {
  schema_version?: number
  commit_dag: Record<string, RepositoryValue>
}

// The minimal shape the shared terminal needs to render a command + its output.
// Both ChallengeStepLog and the adventure step payload satisfy this, so terminal
// line derivation (and the optimistic pending/error placeholders) are shared.
export type TerminalStep = {
  id: number
  command_text: string
  terminal_output: string
  result_category: string
}

export type CommandExecutionPayload = {
  processed: boolean
  next_state: RepositorySnapshot
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

export type TerminalLine = {
  id: string
  kind: 'system' | 'input' | 'output' | 'warning' | 'success'
  text: string
}

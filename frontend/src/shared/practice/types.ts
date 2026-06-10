import type { ChallengeLevelAccess, Difficulty, PracticeCompletion } from '@/features/challenges/types'

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
  stash_stack?: Array<{
    working_tree?: Record<string, RepositoryValue>
    staging?: Record<string, RepositoryValue>
    conflicts?: string[]
  }>
  reflog?: Array<Record<string, string | null>>
  partial_hunks?: Record<string, RepositoryValue>
  replaced_commits?: Record<string, string>
  operation_metadata?: Record<string, RepositoryValue>
  project_tree?: Record<string, RepositoryValue>
  visible_tree?: Record<string, RepositoryValue>
}

export type RequiredDetail = {
  label: string
  value: string
}

// Strict schema_version 3 brief: the backend normalizer whitelists exactly
// these keys, so the frontend never has to guess. The adventure objective
// checklist is NOT part of this shape — it arrives as a separate top-level
// `objective_checks` payload field.
export type PracticeScenarioContext = {
  schema_version?: number
  story?: string
  task?: string
  details?: RequiredDetail[]
  constraints?: string[]
}

export type ChallengeProblem = {
  id: number
  slug: string
  title: string
  summary: string
  narrative: string
  level_id: number
}

export type RepositoryVisualization = {
  schema_version?: number
  commit_dag: Record<string, RepositoryValue>
}

export type ChallengeRun = {
  id: number
  mode: 'primary' | 'review'
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  failure_reason?: string | null
  completed_at: string | null
  first_attempt_star_eligible: boolean
  challenge: ChallengeProblem
  scenario_context?: PracticeScenarioContext
  storey: {
    id: number
    number: number
    title: string
  }
  difficulty: Difficulty | null
  variant: {
    id: number
    label: string
    changed_variant: boolean
    looped_variant?: boolean
  }
  mastery_progress: {
    mastered: number
    required: number
  }
  mastered_records?: {
    mastered: number
    required: number
  }
  policy: {
    min_counted_commands: number
    max_counted_commands: number
  }
  counts: {
    counted_action_total: number
    minimum_counted_commands: number
    maximum_counted_commands: number
    non_counted_diagnostic_total: number
    remaining_counted_commands: number
    max_reached: boolean
    total_attempts: number
  }
  scaffolding: {
    live_dag: boolean
    expected_state: boolean
    contextual_feedback: boolean
  }
  repository_state: RepositorySnapshot
  visualization: RepositoryVisualization
  expected_state: RepositorySnapshot | null
  steps: ChallengeStepLog[]
  review_mode: boolean
  next_difficulty: {
    id: number
    difficulty: Difficulty
  } | null
  completion?: PracticeCompletion | null
  reviewable_difficulties?: ChallengeLevelAccess[]
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

export type ChallengeStepLog = TerminalStep & {
  command_classification: string
  contextual_feedback: string
  visualization_snapshot?: RepositoryVisualization
  created_at: string
}

export type ChallengeCommandResponse = {
  run: ChallengeRunUpdate
  stdout?: string
  stderr?: string
  exit_code?: number
  command_family?: string
  diagnostic_metadata?: string[]
  step: {
    id: number
    command_text: string
    terminal_output: string
    result_category: string
    evaluation_result: string
    command_classification: string
    contextual_feedback: string
    visualization_snapshot?: RepositoryVisualization
    created_at: string
  }
}

export type ChallengeRunUpdate = Pick<
  ChallengeRun,
  | 'id'
  | 'mode'
  | 'status'
  | 'failure_reason'
  | 'completed_at'
  | 'first_attempt_star_eligible'
  | 'counts'
  | 'repository_state'
  | 'visualization'
  | 'review_mode'
> &
  Partial<
    Pick<
      ChallengeRun,
      'mastery_progress' | 'mastered_records' | 'completion' | 'next_difficulty'
    >
  >

export type TerminalLine = {
  id: string
  kind: 'system' | 'input' | 'output' | 'warning' | 'success'
  text: string
}

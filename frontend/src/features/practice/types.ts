import type { Difficulty } from '@/features/scenarios/types'

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

export type ScenarioStudentContext = {
  story?: string
  situation?: string
  current_state?: string[]
  required_details?: Array<{ label: string; value: string }>
  constraints?: string[]
}

export type ScenarioSession = {
  id: number
  mode: 'primary' | 'review'
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  difficulty_instance_id: number
  completed_at: string | null
  first_attempt_star_eligible: boolean
  completion_type: 'state_based' | 'expanded_state_based'
  scenario: {
    id: number
    slug: string
    title: string
    focus: string
    narrative: string
    student_context?: ScenarioStudentContext
  }
  student_context?: ScenarioStudentContext
  module: {
    id: number
    number: number
    title: string
  }
  unit?: {
    id: number
    number: number
    title: string
  }
  difficulty: Difficulty
  variant: {
    id: number
    label: string
    changed_variant: boolean
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
    id: number
    min_counted_commands: number
    max_counted_commands: number
    non_counted_patterns: string[]
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
  expected_state: RepositorySnapshot | null
  steps: ScenarioStepLog[]
  review_mode: boolean
  next_difficulty: {
    id: number
    difficulty: Difficulty
  } | null
  completion?: {
    first_attempt_star: boolean
    counted_action_total: number
    completed_at: string
  } | null
}

export type ScenarioStepLog = {
  id: number
  command_text: string
  terminal_output: string
  result_category: string
  command_classification: string
  contextual_feedback: string
  created_at: string
}

export type CommandResponse = {
  session: ScenarioSession
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
    created_at: string
  }
}

export type TerminalLine = {
  id: string
  kind: 'system' | 'input' | 'output' | 'warning' | 'success'
  text: string
}

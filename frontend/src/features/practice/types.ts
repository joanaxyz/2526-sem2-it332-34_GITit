import type { Difficulty } from '@/features/scenarios/types'

export type RepositoryCommit = {
  id: string
  message: string
  parents: string[]
  tree?: Record<string, string>
  changes?: Record<
    string,
    {
      change_type?: string
      before?: string | null
      after?: string | null
    }
  >
  files?: Record<string, string>
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
  staging: Record<string, string>
  working_tree: Record<string, string>
  conflicts: string[]
  remotes?: Record<string, string>
  remote_branches?: Record<string, string | null>
  upstream_tracking?: Record<string, string>
  stash_stack?: Array<{
    working_tree?: Record<string, string>
    staging?: Record<string, string>
    conflicts?: string[]
  }>
  reflog?: Array<Record<string, string | null>>
  partial_hunks?: Record<string, unknown>
  operation_metadata?: Record<string, unknown>
}

export type ScenarioSession = {
  id: number
  mode: 'primary' | 'review'
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  difficulty_instance_id: number
  completed_at: string | null
  first_attempt_star_eligible: boolean
  scenario: {
    id: number
    slug: string
    title: string
    focus: string
    narrative: string
    task_prompt: string
  }
  unit: {
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
    non_counted_diagnostic_total: number
    remaining_counted_commands: number
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

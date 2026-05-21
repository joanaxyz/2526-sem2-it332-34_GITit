import type { RepositorySnapshot } from '@/features/practice/types'

export type Difficulty = 'easy' | 'medium' | 'hard'
export type DifficultyStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type DifficultyActionIntent = 'start' | 'review' | 'retry'
export type SkillFocusType = 'command_specific' | 'concept_specific' | 'workflow_specific' | 'diagnostic_inspection'

export type CommandPolicy = {
  id: number
  min_counted_commands: number
  max_counted_commands: number
  non_counted_patterns?: string[]
}

export type LatestAttemptStats = {
  id: number
  status: AttemptStatus
  accuracy_rate: number | null
  command_accurate: boolean | null
  counted_action_total: number
  total_attempts: number
  completed_at: string | null
  ended_at: string | null
}

export type DifficultyAccess = {
  id: number
  difficulty: Difficulty
  status: DifficultyStatus
  review_available: boolean
  active_session_id: number | null
  retry_session_id: number | null
  policy: CommandPolicy
  completion: null | {
    first_attempt_star: boolean
    counted_action_total: number
    completed_at: string
  }
  latest_attempt: LatestAttemptStats | null
}

export type DemoExplanationStep = {
  command: string
  explanation: string
  repository_state: RepositorySnapshot
}

export type ScenarioSkillFocus = {
  id: number
  slug: string
  title: string
  focus: string
  summary: string
  short_explanation?: string
  skill_focus_type: SkillFocusType
  primary_focus_commands: string[]
  supporting_inspection_commands?: string[]
  safe_demo_commands?: string[]
  demo_repository_state?: RepositorySnapshot
  demo_dag_config?: Record<string, unknown>
  demo_explanation_steps?: DemoExplanationStep[]
  related_git_concepts?: string[]
  learning_unit_id: number
  lesson_id: number
  difficulties: DifficultyAccess[]
}

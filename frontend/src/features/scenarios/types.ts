import type { RepositorySnapshot } from '@/features/practice/types'

export type Difficulty = 'easy' | 'medium' | 'hard'
export type DifficultyStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type DifficultyActionIntent = 'start' | 'review' | 'retry' | 'continue' | 'resume'
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
  completion_type?: 'state_based' | 'inspection' | 'expanded_state_based'
  status: DifficultyStatus
  review_available: boolean
  mastery_progress: {
    mastered: number
    required: number
  }
  mastered_records?: {
    mastered: number
    required: number
  }
  successful_attempts?: {
    count: number
    required: number
  }
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
  title?: string
  explanation: string
  repository_state: RepositorySnapshot
  common_mistake?: string
  diagnostic?: boolean
  counted?: boolean
}

export type CommandPreviewSection = {
  id?: string
  title: string
  command?: string
  explanation: string
  pages?: CommandPreviewPage[]
  syntax_examples?: string[]
  what_changes?: string[]
  what_does_not_change?: string[]
  common_mistakes?: string[]
  readiness_notes?: string[]
  demo_steps?: DemoExplanationStep[]
}

export type CommandPreviewPage = {
  id?: string
  title: string
  subtitle?: string
  eyebrow?: string
  heading?: string
  body?: string
  blocks?: CommandPreviewBlock[]
  demo_steps?: DemoExplanationStep[]
}

export type CommandPreviewBlock = {
  type?:
    | 'paragraph'
    | 'bullet_list'
    | 'list'
    | 'command'
    | 'code'
    | 'callout'
    | 'warning'
    | 'terminal_output'
    | 'dag_note'
    | 'demo_step_ref'
  title?: string
  subtitle?: string
  body?: string
  text?: string
  items?: string[]
  command?: string
  language?: string
  demo_step_id?: string
}

export type CommandPreviewCommand = {
  id?: string
  key?: string
  title: string
  command?: string
  canonical_command?: string
  aliases?: string[]
  summary?: string
  tags?: string[]
  pages: CommandPreviewPage[]
  demo_steps?: DemoExplanationStep[]
}

export type CommandPreviewMetadata = {
  schema_version?: number
  title: string
  intro?: string
  purpose?: string
  focus_label?: string
  command_title: string
  commands?: CommandPreviewCommand[]
  command_refs?: Array<string | Record<string, unknown>>
  custom_pages?: CommandPreviewPage[]
  sections?: CommandPreviewSection[]
  syntax_examples: string[]
  supported_demo_commands: string[]
  demo_steps: DemoExplanationStep[]
  demo_repository_state?: RepositorySnapshot
  demo_dag_config?: Record<string, unknown>
  before_state: RepositorySnapshot
  after_state: RepositorySnapshot
  short_explanation: string
  what_changes?: string[]
  what_does_not_change?: string[]
  common_mistakes: string[]
  readiness_notes?: string[]
  diagnostic: boolean
  counted: boolean
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
  command_preview?: CommandPreviewMetadata
  related_git_concepts?: string[]
  learning_unit_id: number
  module_id?: number
  lesson_id: number
  difficulties: DifficultyAccess[]
}

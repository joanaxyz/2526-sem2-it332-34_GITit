import type { RepositorySnapshot } from '@/features/practice/types'
import type { KnownDifficulty } from '@/features/scenarios/constants'

export type Difficulty = KnownDifficulty | (string & {})
export type PracticeKind = 'command_drill' | 'workflow_scenario'
export type PracticeStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type PracticeActionIntent = 'start' | 'review' | 'retry' | 'continue' | 'resume'

export type CommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
}

export type LatestAttemptStats = {
  id: number
  status: AttemptStatus
  accuracy_rate: number | null
  command_accurate?: boolean | null
  counted_action_total: number
  total_attempts: number
  completed_at: string | null
  ended_at: string | null
}

export type PracticeCompletion = {
  first_attempt_star: boolean
  counted_action_total: number
  completed_at: string
}

export type PracticeProgress = {
  count: number
  required: number
}

export type PracticeAccess = {
  id: number
  practice_kind: PracticeKind
  status: PracticeStatus
  required_successful_attempts: number
  successful_attempts: PracticeProgress
  active_session_id: number | null
  latest_attempt: LatestAttemptStats | null
  completion: PracticeCompletion | null
  review_available: boolean
  command_budget: CommandBudget
}

export type CommandDrillAccess = PracticeAccess & {
  practice_kind: 'command_drill'
  slug: string
  title: string
  summary: string
}

export type CommandAdventureLevelSummary = {
  id: number
  slug: string
  number: number
  label: string
  status: PracticeStatus
  unlocked: boolean
  usage_count: number
  drill_count: number
  variant_count: number
  progress: {
    value: number
    numerator: number
    denominator: number
  }
  next_practice: CommandDrillAccess | null
}

export type CommandDrillAdventureSummary = {
  item_type: 'command_drill_adventure'
  id: number
  slug: string
  title: string
  description: string
  practice_kind: 'command_drill'
  progress: {
    value: number
    numerator: number
    denominator: number
    levels_completed: number
    level_count: number
  }
  levels: CommandAdventureLevelSummary[]
}

export type CommandUsageSummary = {
  id: number
  slug: string
  usage_form: string
  label: string
  summary: string
  drills: CommandDrillAccess[]
}

export type CommandTopicSummary = {
  item_type: 'command_topic'
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  mental_model: Record<string, unknown>
  progress: {
    value: number
    numerator: number
    denominator: number
  }
  usages: CommandUsageSummary[]
}

export type WorkflowLevelAccess = PracticeAccess & {
  practice_kind: 'workflow_scenario'
  difficulty: Difficulty
}

export type WorkflowScenarioSummary = {
  item_type: 'workflow_scenario'
  id: number
  slug: string
  title: string
  summary: string
  narrative: string
  command_topics: string[]
  levels: WorkflowLevelAccess[]
}

export type ModuleContentSection = 'command_adventures' | 'command_topics' | 'workflow_scenarios'

export type ModuleContentPage<T extends CommandDrillAdventureSummary | CommandTopicSummary | WorkflowScenarioSummary> = {
  section: ModuleContentSection
  results: T[]
  next_cursor: number | null
}

export type CommandPreviewBlock = {
  type?: 'paragraph' | 'bullet_list' | 'list' | 'command' | 'code' | 'callout' | 'warning' | 'terminal_output'
  title?: string
  body?: string
  text?: string
  items?: string[]
  command?: string
  language?: string
}

export type CommandPreviewPage = {
  id?: string
  title: string
  subtitle?: string
  body?: string
  blocks?: CommandPreviewBlock[]
}

export type CommandPreviewMetadata = {
  schema_version?: number
  title?: string
  intro?: string
  purpose?: string
  command_title?: string
  syntax_examples?: string[]
  common_mistakes?: string[]
  readiness_notes?: string[]
  before_state?: RepositorySnapshot
  after_state?: RepositorySnapshot
  pages?: CommandPreviewPage[]
}

export type CommandUsagePreview = {
  id: number
  slug: string
  usage_form: string
  label: string
  summary: string
  topic: {
    id: number
    slug: string
    base_command: string
    title: string
  }
  command_preview: CommandPreviewMetadata
}

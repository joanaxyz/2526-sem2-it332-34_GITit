import type { RepositorySnapshot } from '@/shared/practice/types'
import type { KnownDifficulty } from '@/features/challenges/constants'

export type Difficulty = KnownDifficulty | (string & {})
export type ChallengeStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type ChallengeActionIntent = 'start' | 'review' | 'retry' | 'continue' | 'resume'

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

export type ChallengeProgress = {
  count: number
  required: number
}

export type ChallengeLevelAccess = {
  id: number
  difficulty: Difficulty
  status: ChallengeStatus
  required_successful_attempts: number
  successful_attempts: ChallengeProgress
  active_run_id: number | null
  latest_attempt: LatestAttemptStats | null
  completion: PracticeCompletion | null
  review_available: boolean
  command_budget: CommandBudget
}

export type CommandAdventureSummary = {
  item_type: 'command_adventure'
  id: number
  slug: string
  title: string
  description: string
  status: 'not_started' | 'started' | 'completed' | 'failed' | 'abandoned'
  active_run_id: number | null
  latest_run_id: number | null
  problem_count: number
  progress: {
    value: number
    numerator: number
    denominator: number
  }
}

export type CommandFormSummary = {
  id: number
  slug: string
  usage_form: string
  label: string
  summary: string
  problem_count: number
}

export type CommandSkillSummary = {
  item_type: 'command_skill'
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  mental_model: Record<string, unknown>
  forms: CommandFormSummary[]
}

export type ChallengeSummary = {
  item_type: 'challenge'
  id: number
  slug: string
  title: string
  summary: string
  narrative: string
  command_topics: string[]
  levels: ChallengeLevelAccess[]
}

export type StoreyContentSection = 'command_adventures' | 'command_skills' | 'challenges'

export type StoreyContentPage<T extends CommandAdventureSummary | CommandSkillSummary | ChallengeSummary> = {
  section: StoreyContentSection
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

export type CommandFormPreview = {
  id: number
  slug: string
  usage_form: string
  label: string
  summary: string
  skill: {
    id: number
    slug: string
    base_command: string
    title: string
  }
  command_preview: CommandPreviewMetadata
}

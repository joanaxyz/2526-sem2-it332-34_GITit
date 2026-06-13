import type { RepositorySnapshot } from '@/shared/level/types'
import type { KnownDifficulty } from '@/features/challenges/constants'
import type { BookPage } from '@/features/storeys/book/bookTypes'

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

export type LevelRunCompletion = {
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
  completion: LevelRunCompletion | null
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
  // Stable across re-runs: true once the adventure has ever been passed. Drives
  // the challenge gate and progress so a post-pass replay can't relock anything.
  is_passed: boolean
  active_run_id: number | null
  latest_run_id: number | null
  level_count: number
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
  level_count: number
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
  levels: ChallengeLevelAccess[]
}

// Tower slots a tome can be authored into. Mirrors backend Tome.placement.
export type TomePlacement = 'above_adventure' | 'below_adventure' | 'below_challenges'

export type TomeSummary = {
  item_type: 'tome'
  id: number
  slug: string
  title: string
  summary: string
  placement: TomePlacement
  // Pages ship inline (tomes are small), so opening the reader needs no fetch.
  pages: BookPage[]
}

export type StoreyContentSection = 'command_adventures' | 'command_skills' | 'challenges' | 'tomes'

export type StoreyContentPage<
  T extends CommandAdventureSummary | CommandSkillSummary | ChallengeSummary | TomeSummary,
> = {
  section: StoreyContentSection
  results: T[]
  next_cursor: number | null
}

// Every Tower section for one storey, fetched in a single request. Storeys
// hold only a handful of challenges/tomes, so the lists are returned whole.
export type StoreyContentOverview = {
  storey_id: number
  command_adventure: CommandAdventureSummary | null
  tomes: TomeSummary[]
  challenges: ChallengeSummary[]
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

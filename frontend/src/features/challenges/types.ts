import type { ChapterContentSection } from '@/shared/level/chapterContent'
import type {
  LevelScenarioContext,
  RepositorySnapshot,
  RepositoryVisualization,
  TerminalStep,
} from '@/shared/level/types'
import type { KnownDifficulty } from '@/features/challenges/utils/constants'
import type { BookPage } from '@/features/story-map/components/book/bookTypes'
import type { CommandSubmissionOutcome } from '@/shared/battle/types'

export type Difficulty = KnownDifficulty | (string & {})
export type ChallengeStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type ChallengeActionIntent = 'start' | 'replay' | 'retry' | 'continue'

export type CommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
}

export type LatestAttemptStats = {
  id: number
  status: AttemptStatus
  stars: number
  counted_action_total: number
  total_attempts: number
  completed_at: string | null
  ended_at: string | null
}

export type LevelRunCompletion = {
  stars: number
  counted_action_total: number
  completed_at: string
}

export type ChallengeTrialAccess = {
  id: number
  difficulty: Difficulty
  status: ChallengeStatus
  cleared: boolean
  replay_available: boolean
  latest_attempt: LatestAttemptStats | null
  completion: LevelRunCompletion | null
  command_budget: CommandBudget
}

export type ChallengeLevelAccess = {
  id: number
  slug: string
  title: string
  brief: string
  status: ChallengeStatus
  completed: boolean
  locked: boolean
  trials: ChallengeTrialAccess[]
}

/** One independently launchable adventure level. Its waves are played inside
 *  its own run; levels belong directly to a chapter, not to an adventure wrapper. */
export type AdventureSummary = {
  item_type: 'adventure'
  id: number
  slug: string
  title: string
  description: string
  command: string
  learned: boolean
  completed: boolean
  locked: boolean
  lock_reason: string
  wave_count: number
  completion: LevelRunCompletion | null
  latest_run_id: number | null
  status: 'not_started' | 'started' | 'completed' | 'failed' | 'abandoned'
  // Stable across re-runs: true once the level has ever been passed. Drives
  // the challenge gate and progress so a post-pass replay can't relock anything.
  is_passed: boolean
  progress: {
    value: number
    numerator: number
    denominator: number
  }
}

export type AdventureLevelSummary = AdventureSummary


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
  status: ChallengeStatus
  completed: boolean
  locked: boolean
  trials: ChallengeTrialAccess[]
}


export type ChapterLessonSummary = {
  item_type: 'lesson'
  id: number
  slug: string
  title: string
  summary: string
  // Pages ship inline (lessons are small), so opening the reader needs no fetch.
  pages: BookPage[]
}

export type { ChapterContentSection }

export type ChapterContentPage<
  T extends AdventureSummary | CommandSkillSummary | ChallengeSummary | ChapterLessonSummary,
> = {
  section: ChapterContentSection
  results: T[]
  next_cursor: number | null
}

// Every relic for one chapter, fetched in a single request. Chapters hold only
// a handful of challenges/lessons, so the lists are returned whole.
export type ChapterContentOverview = {
  chapter_id: number
  adventures: AdventureSummary[]
  lessons: ChapterLessonSummary[]
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

export type ChallengeRef = {
  id: number
  slug: string
  title: string
  summary: string
  narrative: string
  level_id: number
  trial_id?: number
  challenge_level_id?: number
  challenge_level_slug?: string
  challenge_level_title?: string
}

export type ChallengeStepLog = TerminalStep & {
  command_classification: string
  contextual_feedback: string
  visualization_snapshot?: RepositoryVisualization
  created_at: string
}

export type ChallengeRun = {
  id: number
  /** True for uncounted free-play replays; false for counted primary runs. */
  replay: boolean
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  stars: number
  failure_reason?: string | null
  completed_at: string | null
  challenge: ChallengeRef
  scenario_context?: LevelScenarioContext
  chapter: {
    id: number
    number: number
    title: string
  }
  story: { id: number; slug: string; title: string; world_slug: string } | null
  /** Authored battle-stage dressing for this chapter (null -> default sky). */
  battle_stage?: import('@/shared/battle/types').BattleStage | null
  difficulty: Difficulty | null
  /** GitCoins paid out on the first completion of this trial (0 = no reward). */
  reward_coins?: number
  variant: {
    id: number
    label: string
  }
  mastery_progress: {
    cleared: boolean
    stars: number
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
  next_difficulty: {
    id: number
    difficulty: Difficulty
  } | null
  /**
   * Every level of this run's challenge (easy-to-hard) with the user's access state.
   * Drives the completion modal's level navigator so learners can jump to any
   * unlocked level - including lower ones - without leaving the modal.
   */
  sibling_levels?: ChallengeTrialAccess[]
  completion?: LevelRunCompletion | null
}

/** `result_category` value the backend sends when the command reached the
 * scenario's target repository state (mirrors RESULT_TARGET_MATCHED in
 * common/constants.py). The solve signal the battle stage keys off of. */
export const RESULT_TARGET_MATCHED = 'TargetMatched'

export type ChallengeCommandResponse = {
  run: ChallengeRunUpdate
  command_outcome: CommandSubmissionOutcome
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
  | 'replay'
  | 'status'
  | 'stars'
  | 'failure_reason'
  | 'completed_at'
  | 'counts'
  | 'repository_state'
  | 'visualization'
> &
  Partial<
    Pick<
      ChallengeRun,
      'mastery_progress' | 'completion' | 'next_difficulty' | 'sibling_levels'
    >
  >

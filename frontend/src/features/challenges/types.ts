import type {
  LevelScenarioContext,
  RepositorySnapshot,
  RepositoryVisualization,
} from '@/shared/level/types'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import type { KnownDifficulty } from '@/features/challenges/utils/constants'
import type { CommandSubmissionOutcome } from '@/shared/level-runtime/commandOutcome'

export type Difficulty = KnownDifficulty | (string & {})
export type ChallengeStatus = 'not_started' | 'locked' | 'in_progress' | 'completed' | 'failed' | 'abandoned'
type AttemptStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type ChallengeActionIntent = 'start' | 'replay' | 'retry' | 'continue'

type CommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
}

type LatestAttemptStats = {
  id: number
  status: AttemptStatus
  stars: number
  counted_action_total: number
  total_attempts: number
  completed_at: string | null
  ended_at: string | null
}

type LevelRunCompletion = {
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

type CommandPreviewBlock = {
  type?: 'paragraph' | 'bullet_list' | 'list' | 'command' | 'code' | 'callout' | 'warning' | 'terminal_output'
  title?: string
  body?: string
  text?: string
  items?: string[]
  command?: string
  language?: string
}

type CommandPreviewPage = {
  id?: string
  title: string
  subtitle?: string
  body?: string
  blocks?: CommandPreviewBlock[]
}

type CommandPreviewMetadata = {
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

type ChallengeRef = {
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

type ChallengeRunStepResponse = Omit<
  ApiSchemas['ChallengeRunStepResponse'],
  'visualization_snapshot'
> & {
  visualization_snapshot: RepositoryVisualization
}

type ChallengeOptimisticStep = Omit<ChallengeRunStepResponse, 'visualization_snapshot'> & {
  visualization_snapshot?: never
}

export type ChallengeStepLog = ChallengeRunStepResponse | ChallengeOptimisticStep

type ChallengeRunRefinementKeys =
  | 'challenge'
  | 'scenario_context'
  | 'chapter'
  | 'story'
  | 'variant'
  | 'mastery_progress'
  | 'policy'
  | 'counts'
  | 'scaffolding'
  | 'repository_state'
  | 'visualization'
  | 'expected_state'
  | 'steps'
  | 'next_difficulty'
  | 'sibling_levels'
  | 'completion'

export type ChallengeRunResponse = Omit<
  ApiSchemas['ChallengeRunResponse'],
  ChallengeRunRefinementKeys
> & {
  challenge: ChallengeRef
  scenario_context: LevelScenarioContext
  chapter: {
    id: number
    number: number
    title: string
  }
  story: { id: number; slug: string; title: string; world_slug: string } | null
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
  steps: ChallengeRunStepResponse[]
  next_difficulty: {
    id: number
    difficulty: Difficulty
  } | null
  /**
   * Every level of this run's challenge (easy-to-hard) with the user's access state.
   * Drives the completion modal's level navigator so learners can jump to any
   * unlocked level - including lower ones - without leaving the modal.
   */
  sibling_levels: ChallengeTrialAccess[]
  completion: LevelRunCompletion | null
}

export type ChallengeRun = Omit<ChallengeRunResponse, 'steps'> & {
  steps: ChallengeStepLog[]
}

/** `result_category` value the backend sends when the command reached the
 * scenario's target repository state (mirrors RESULT_TARGET_MATCHED in
 * common/constants.py). */
export const RESULT_TARGET_MATCHED = 'TargetMatched'

type ChallengeCommandStep = Omit<
  ApiSchemas['ChallengeCommandStepResponse'],
  'visualization_snapshot'
> & {
  visualization_snapshot: RepositoryVisualization
}

export type ChallengeCommandResponse = Omit<
  ApiSchemas['ChallengeCommandResponse'],
  'run' | 'command_outcome' | 'step'
> & {
  run: ChallengeRunUpdate
  command_outcome: CommandSubmissionOutcome
  step: ChallengeCommandStep
}

type ChallengeRunUpdate = Omit<
  ApiSchemas['ChallengeCommandRunResponse'],
  | 'counts'
  | 'repository_state'
  | 'visualization'
  | 'mastery_progress'
  | 'completion'
  | 'next_difficulty'
  | 'sibling_levels'
> & {
  counts: ChallengeRun['counts']
  repository_state: RepositorySnapshot
  visualization: RepositoryVisualization
  mastery_progress?: ChallengeRun['mastery_progress']
  completion?: ChallengeRun['completion']
  next_difficulty?: ChallengeRun['next_difficulty']
  sibling_levels?: ChallengeRun['sibling_levels']
}

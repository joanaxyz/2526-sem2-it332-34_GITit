import type { BattleStage, CommandSubmissionOutcome } from '@/shared/battle/types'
import type { ChapterBook } from '@/features/story-map/components/book/bookTypes'
import type { LevelScenarioContext, RepositorySnapshot, TerminalStep } from '@/shared/level/types'
import type { ObjectiveCheck } from '@/shared/level/utils/levelContext'

type AdventureRunStatus = 'started' | 'completed' | 'failed' | 'abandoned'
type AttemptStatus = 'started' | 'completed' | 'failed'

type AdventureScaffolding = {
  live_dag: boolean
  expected_state: boolean
  contextual_feedback: boolean
}

type AdventureCommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
}

type AdventureAttemptCounts = {
  command_count: number
  counted_command_count: number
}

type AdventureLevelRef = {
  id: number
  slug: string
  title: string
  is_required: boolean
  /** GitCoins paid out on the first completion of this level (0 = no reward). */
  reward_coins?: number
}

/**
 * Adventure attempts carry the same strict schema_version 3 scenario context as
 * challenges (story / task / copyable details), normalized by the backend
 * `ScenarioContextNormalizer`. The live objective checklist arrives separately
 * as the attempt's `objective_checks` field.
 */
type AdventureScenarioContext = LevelScenarioContext

/** One persisted command in an attempt's terminal history. */
export type AdventureStepLog = TerminalStep

export type AdventureAttempt = {
  id: number
  order: number
  /** Zero-based position inside the selected level's authored wave plan. */
  wave: number
  position: number
  status: AttemptStatus
  level: AdventureLevelRef
  variant: { id: number; label: string }
  scenario_context: AdventureScenarioContext
  /**
   * Adventure-only live checklist: each authored check is evaluated server-side
   * against the current repository state, so `satisfied` ticks as the learner
   * progresses. Updated mid-attempt by `AdventureRunPatch.objective_checks`.
   */
  objective_checks: ObjectiveCheck[]
  scaffolding: AdventureScaffolding
  command_budget: AdventureCommandBudget
  counts: AdventureAttemptCounts
  repository_state: RepositorySnapshot
  /** Terminal history for this attempt; the terminal derives its lines from this. */
  steps: AdventureStepLog[]
}

type AdventureAttemptResult = {
  id: number
  order: number
  status: AttemptStatus
  stars: number
  counted_command_count: number
}

export type AdventureMasteryCommand = {
  slug: string
  form_id: number
  form_slug: string
  skill_slug: string
  title: string
  strength: number
  mastered_bar: number
  introduced: boolean
  mastered: boolean
}

type AdventureMastery = {
  commands: AdventureMasteryCommand[]
  commands_mastered: number
  total_commands: number
  total_achievable: number
  passed: boolean
}

export type AdventureRun = {
  id: number
  status: AdventureRunStatus
  /** True for uncounted free-play replays; false for the counted first playthrough. */
  replay: boolean
  stars: number
  library_opened: boolean
  /** Stable across re-runs: true once this adventure has ever been passed. */
  is_passed: boolean
  selected_level: AdventureLevelRef | null
  /** Next published level in this chapter, or null when this is the final level. */
  next_level: AdventureLevelRef | null
  story: { id: number; slug: string; title: string; world_slug: string } | null
  /** The adventure's chapter id, used to navigate back to the story map. */
  chapter_id: number | null
  /** Authored battle-stage dressing for this chapter (null -> default sky). */
  battle_stage?: BattleStage | null
  current_level_index: number
  total_levels: number
  /** One-based wave cursor and total waves in the selected level. */
  current_wave: number
  total_waves: number
  mastery: AdventureMastery
  completed_at: string | null
  current_attempt: AdventureAttempt | null
  results: AdventureAttemptResult[]
  progress: { completed: number; total: number }
}

export type AdventureLevelLibraryResponse = {
  book: ChapterBook
  run: AdventureRun
}

/**
 * Slim per-command patch returned while an attempt is still in progress. The
 * backend sends this instead of the full run (mirroring the challenge
 * command/run payload split); only the live attempt state changes, so the
 * client merges these fields into the cached run. A transition (solved / budget
 * spent) returns a full `AdventureRun` instead, flagged by the absence of
 * `partial`.
 */
export type AdventureRunPatch = {
  partial: true
  id: number
  status: AdventureRunStatus
  current_attempt: {
    id: number
    counts: AdventureAttemptCounts
    repository_state: RepositorySnapshot
    objective_checks: ObjectiveCheck[] | null
  } | null
}

export type AdventureCommandResponse = {
  run: AdventureRun | AdventureRunPatch
  solved: boolean
  stdout: string
  stderr: string
  exit_code: number
  terminal_output: string
  command_classification: string
  /** The persisted step; replaces the client's optimistic pending placeholder. */
  step: AdventureStepLog
  command_outcome: CommandSubmissionOutcome
}

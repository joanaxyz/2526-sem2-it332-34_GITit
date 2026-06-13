import type { BattleBlock } from '@/shared/battle/types'
import type { LevelScenarioContext, RepositorySnapshot, TerminalStep } from '@/shared/level/types'
import type { ObjectiveCheck } from '@/shared/level/utils/levelContext'

export type AdventureRunStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed'

export type AdventureScaffolding = {
  live_dag: boolean
  expected_state: boolean
  contextual_feedback: boolean
  hints: boolean
}

export type AdventureCommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
}

export type AdventureAttemptCounts = {
  command_count: number
  counted_command_count: number
  hint_count: number
}

export type AdventureLevelRef = {
  id: number
  slug: string
  title: string
  is_required: boolean
}

/**
 * Adventure attempts carry the same strict schema_version 3 scenario context as
 * challenges (story / task / details / constraints), normalized by the backend
 * `ScenarioContextNormalizer`. The live objective checklist arrives separately
 * as the attempt's `objective_checks` field.
 */
export type AdventureScenarioContext = LevelScenarioContext

/** One persisted command in an attempt's terminal history. */
export type AdventureStepLog = TerminalStep

export type AdventureAttempt = {
  id: number
  order: number
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
  /** Authoritative encounter state once the backend battle block ships;
   *  absent → the client derives a deterministic roster. */
  battle?: BattleBlock | null
}

export type AdventureAttemptResult = {
  id: number
  order: number
  status: AttemptStatus
  correctness_score: number
  efficiency_score: number
  independence_score: number
  final_score: number
  mastery_gain: number
  hint_count: number
  counted_command_count: number
}

export type AdventureMasteryCommand = {
  slug: string
  title: string
  strength: number
  mastered_bar: number
  introduced: boolean
  mastered: boolean
}

export type AdventureMastery = {
  commands: AdventureMasteryCommand[]
  commands_mastered: number
  total_commands: number
  session_score: number
  pass_bar: number
  total_achievable: number
  passed: boolean
}

export type AdventureRunMode = 'primary' | 'replay'

export type AdventureRun = {
  id: number
  status: AdventureRunStatus
  /** Primary is the counted first playthrough; replay is uncounted free-play. */
  mode: AdventureRunMode
  /** Stable across re-runs: true once this adventure has ever been passed. */
  is_passed: boolean
  command_adventure: { id: number; slug: string; title: string; description: string }
  /** The adventure's storey id, used to navigate back to the Tower. */
  storey_id: number
  current_level_index: number
  total_levels: number
  session_score: number
  passed: boolean
  mastery_progress_gained: number
  mastery: AdventureMastery
  completed_at: string | null
  current_attempt: AdventureAttempt | null
  results: AdventureAttemptResult[]
  progress: { completed: number; total: number }
}

export type AdventureHintResponse = {
  run: AdventureRun
  hint: string
  hint_number: number
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
  /** Authoritative battle outcome of this command; absent → client-derived. */
  battle?: BattleBlock | null
}

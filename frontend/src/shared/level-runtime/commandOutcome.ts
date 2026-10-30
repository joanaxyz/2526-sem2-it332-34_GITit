import type { CommandExecutionPayload } from '@/shared/level/types'

/** Neutral result returned after a Git command is evaluated. */
export type CommandSubmissionOutcome = {
  processed: boolean
  counted: boolean
  solved: boolean
  failed: boolean
  command_family: string
  previous_rules_passing: number
  rules_passing: number
  rules_delta: number
  total_rules: number
  max_counted_commands: number
  counted_command_count: number
  remaining_counted_commands: number
}

/**
 * The outcome of a command the browser can already judge, so the stage can
 * resolve the turn without waiting for the server: input the engine could not
 * run is a counted miss, and a read-only diagnostic is a free look. A command
 * that changes the repository returns `null`; only the server's evaluation
 * knows what it achieved. Mirrors the backend `CommandCountClassifier`.
 */
export function predictLocalOutcome(
  execution: CommandExecutionPayload,
  counts: { counted: number; max: number; scoringPolicyVersion?: number },
): CommandSubmissionOutcome | null {
  if (!execution.normalized_command.trim()) return null
  // A normal negative query is still a valid inspection. Keep this aligned
  // with the backend command boundary, including missing config values.
  const inspectionSucceeded = execution.exit_code === 0 || (
    execution.exit_code === 1 && ['check-ignore', 'grep', 'merge-base', 'config'].includes(execution.command_family ?? '')
  )
  const counted = !execution.processed || ((counts.scoringPolicyVersion ?? 1) >= 2 && execution.diagnostic && !inspectionSucceeded)
  if (!counted && !execution.diagnostic) return null
  const countedCommands = counts.counted + (counted ? 1 : 0)
  return {
    processed: execution.processed,
    counted,
    solved: false,
    failed: counted && countedCommands >= counts.max,
    command_family: execution.command_family ?? '',
    previous_rules_passing: 0,
    rules_passing: 0,
    rules_delta: 0,
    total_rules: 0,
    max_counted_commands: counts.max,
    counted_command_count: countedCommands,
    remaining_counted_commands: Math.max(0, counts.max - countedCommands),
  }
}

/** Whether the server's outcome plays out the turn the prediction already showed. */
export function confirmsPrediction(predicted: CommandSubmissionOutcome, actual: CommandSubmissionOutcome) {
  return (
    actual.processed === predicted.processed &&
    actual.counted === predicted.counted &&
    actual.solved === predicted.solved &&
    actual.failed === predicted.failed &&
    actual.rules_delta === 0 &&
    actual.remaining_counted_commands === predicted.remaining_counted_commands
  )
}

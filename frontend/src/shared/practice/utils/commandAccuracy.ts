export const COMMAND_ACCURACY_PROGRESS_THRESHOLD = 70
export const COMMAND_ACCURACY_MASTERY_THRESHOLD = 100

export type CommandAccuracyInput = {
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  counted_action_total: number
  minimum_counted_commands: number
}

export function meetsProgressAccuracy(accuracy: number | null): boolean {
  return accuracy !== null && accuracy >= COMMAND_ACCURACY_PROGRESS_THRESHOLD
}

export function meetsMasteryAccuracy(accuracy: number | null): boolean {
  return accuracy !== null && accuracy >= COMMAND_ACCURACY_MASTERY_THRESHOLD
}

/** Mirrors the backend command accuracy calculation for practice sessions. */
export function commandAccuracyRate({
  status,
  counted_action_total,
  minimum_counted_commands,
}: CommandAccuracyInput): number | null {
  if (status === 'started') return null
  if (status === 'failed' || status === 'abandoned') return 0
  if (counted_action_total <= minimum_counted_commands) return 100
  if (minimum_counted_commands === 0) return 0
  return Math.round((minimum_counted_commands / counted_action_total) * 100)
}

export function commandAccuracyFromSession(session: {
  status: CommandAccuracyInput['status']
  policy: { min_counted_commands: number }
  counts: { counted_action_total: number }
}): number | null {
  return commandAccuracyRate({
    status: session.status,
    counted_action_total: session.counts.counted_action_total,
    minimum_counted_commands: session.policy.min_counted_commands,
  })
}

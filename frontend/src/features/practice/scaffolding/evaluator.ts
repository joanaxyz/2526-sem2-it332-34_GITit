import { computeBudgetConsumedPct } from './budget'

export type ScaffoldEvaluationInput = {
  session_complete: boolean
  counted_commands_used: number
  min_threshold: number
  max_limit: number
  scaffold_t1_fired: boolean
  scaffold_t2_fired: boolean
  scaffold_t3_fired: boolean
}

/**
 * Evaluates which scaffold trigger (if any) should fire after an action command.
 *
 * Skip behavior: triggers are evaluated from highest (T3) to lowest (T1) and the
 * first applicable unfired trigger is returned. A lower-priority trigger is
 * permanently blocked once a higher-priority trigger has already fired — this is
 * enforced by requiring that no higher trigger has fired as a precondition for each
 * lower trigger. Example: if usage jumps from 30 % to 92 % in a single command, T3
 * fires and T1/T2 can never fire in any future evaluation for this session.
 */
export function evaluateScaffoldTriggers(state: ScaffoldEvaluationInput): 'T1' | 'T2' | 'T3' | null {
  if (state.session_complete) return null

  const pct = computeBudgetConsumedPct(
    state.counted_commands_used,
    state.min_threshold,
    state.max_limit,
  )

  if (pct >= 85 && !state.scaffold_t3_fired) return 'T3'
  // T2 is blocked permanently once T3 has fired (skip behavior — see module docstring)
  if (pct >= 65 && !state.scaffold_t2_fired && !state.scaffold_t3_fired) return 'T2'
  // T1 is blocked permanently once T2 or T3 has fired
  if (pct >= 40 && !state.scaffold_t1_fired && !state.scaffold_t2_fired && !state.scaffold_t3_fired) return 'T1'

  return null
}

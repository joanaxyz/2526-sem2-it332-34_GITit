import { useState } from 'react'
import { toast } from 'sonner'

import type { ScenarioSession } from '@/features/practice/types'
import { computeBudgetConsumedPct } from './budget'
import { evaluateScaffoldTriggers } from './evaluator'
import { logScaffoldTrigger } from './logger'
import { getScaffoldMessage } from './messages'
import { ScaffoldToast } from './ScaffoldToast'
import { readScaffoldTriggers, writeScaffoldTriggers } from './store'
import type { ScaffoldTriggerFlags } from './store'

// Fixed toast ID ensures only one scaffold hint is visible at a time.
// A subsequent trigger replaces the previous toast rather than stacking a second one.
const SCAFFOLD_TOAST_ID = 'scaffold-hint'
type ScaffoldDifficulty = 'easy' | 'medium' | 'hard'

function scaffoldDifficultyFor(difficulty: ScenarioSession['difficulty']): ScaffoldDifficulty {
  if (difficulty === 'easy') return 'easy'
  if (difficulty === 'medium') return 'medium'
  if (difficulty === 'hard') return 'hard'
  return 'hard'
}

export function useScaffolding(sessionId: number) {
  const [flags, setFlags] = useState<ScaffoldTriggerFlags>(() => readScaffoldTriggers(sessionId))

  function clearToast() {
    toast.dismiss(SCAFFOLD_TOAST_ID)
  }

  function markFired(trigger: 'T1' | 'T2' | 'T3') {
    const key = `t${trigger.charAt(1).toLowerCase()}_fired` as keyof ScaffoldTriggerFlags
    const updated = { ...flags, [key]: true }
    setFlags(updated)
    writeScaffoldTriggers(sessionId, updated)
  }

  function showToast(
    trigger: 'T1' | 'T2' | 'T3',
    session: ScenarioSession,
    onProceedToCommandPreview: () => void,
  ) {
    const difficulty = scaffoldDifficultyFor(session.difficulty)
    const message = getScaffoldMessage(trigger, difficulty)

    toast.custom(
      () => (
        <ScaffoldToast
          message={message}
          trigger={trigger}
          difficulty={difficulty}
          onProceedToCommandPreview={() => {
            // Session state is preserved in full while the modal is open:
            // (a) TanStack Query cache (in memory for the tab lifetime)
            // (b) sessionStorage bootstrap written by updateScenarioSessionCache
            // (c) scaffold trigger flags written to sessionStorage by writeScaffoldTriggers
            // The modal renders over the workspace — no navigation occurs, so session is never lost.
            clearToast()
            onProceedToCommandPreview()
          }}
          onContinue={() => {
            clearToast()
            const input = document.querySelector<HTMLInputElement>('[data-command-input]')
            input?.focus()
          }}
        />
      ),
      { id: SCAFFOLD_TOAST_ID, duration: Infinity },
    )
  }

  /**
   * Called after each command submission response (non-review mode only).
   * Evaluates whether a scaffold trigger should fire and, if so, shows the hint toast.
   * onProceedToCommandPreview is called when the student taps "Proceed to Command Preview"
   * — the caller is responsible for opening the correct modal/panel.
   */
  function evaluateAndNotify(
    session: ScenarioSession,
    stepClassification: string,
    onProceedToCommandPreview: () => void,
  ) {
    if (session.status !== 'started') return
    if (stepClassification !== 'counted_action') return

    const trigger = evaluateScaffoldTriggers({
      session_complete: false,
      counted_commands_used: session.counts.counted_action_total,
      min_threshold: session.policy.min_counted_commands,
      max_limit: session.policy.max_counted_commands,
      scaffold_t1_fired: flags.t1_fired,
      scaffold_t2_fired: flags.t2_fired,
      scaffold_t3_fired: flags.t3_fired,
    })

    if (!trigger) return

    logScaffoldTrigger({
      trigger,
      difficulty: session.difficulty,
      counted_commands_used: session.counts.counted_action_total,
      budget_consumed_pct: computeBudgetConsumedPct(
        session.counts.counted_action_total,
        session.policy.min_counted_commands,
        session.policy.max_counted_commands,
      ),
    })

    markFired(trigger)
    showToast(trigger, session, onProceedToCommandPreview)
  }

  return { clearToast, evaluateAndNotify, flags }
}

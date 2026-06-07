import { useState } from 'react'
import { toast } from 'sonner'

import type { ChallengeRun } from '@/shared/practice/types'
import { computeBudgetConsumedPct } from './budget'
import { evaluateScaffoldTriggers } from './evaluator'
import { logScaffoldTrigger } from './logger'
import { getScaffoldMessage } from './messages'
import { ScaffoldToast } from './ScaffoldToast'
import { readScaffoldTriggers, writeScaffoldTriggers } from './store'
import type { ScaffoldTriggerFlags } from './store'

const SCAFFOLD_TOAST_ID = 'scaffold-hint'
type ScaffoldDifficulty = 'easy' | 'medium' | 'hard'

function scaffoldDifficultyFor(difficulty: ChallengeRun['difficulty']): ScaffoldDifficulty {
  if (difficulty === 'easy') return 'easy'
  if (difficulty === 'medium') return 'medium'
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
    run: ChallengeRun,
    onReviewTower: () => void,
  ) {
    const difficulty = scaffoldDifficultyFor(run.difficulty)
    const message = getScaffoldMessage(trigger, difficulty)

    toast.custom(
      () => (
        <ScaffoldToast
          message={message}
          trigger={trigger}
          difficulty={difficulty}
          onReviewTower={() => {
            clearToast()
            onReviewTower()
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

  function evaluateAndNotify(
    run: ChallengeRun,
    stepClassification: string,
    onReviewTower: () => void,
  ) {
    if (run.status !== 'started') return
    if (stepClassification !== 'counted_action') return

    const trigger = evaluateScaffoldTriggers({
      session_complete: false,
      counted_commands_used: run.counts.counted_action_total,
      min_threshold: run.policy.min_counted_commands,
      max_limit: run.policy.max_counted_commands,
      scaffold_t1_fired: flags.t1_fired,
      scaffold_t2_fired: flags.t2_fired,
      scaffold_t3_fired: flags.t3_fired,
    })

    if (!trigger) return

    logScaffoldTrigger({
      trigger,
      difficulty: run.difficulty ?? 'hard',
      counted_commands_used: run.counts.counted_action_total,
      budget_consumed_pct: computeBudgetConsumedPct(
        run.counts.counted_action_total,
        run.policy.min_counted_commands,
        run.policy.max_counted_commands,
      ),
    })

    markFired(trigger)
    showToast(trigger, run, onReviewTower)
  }

  return { clearToast, evaluateAndNotify, flags }
}

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import type { OutcomeNextStep } from '@/shared/level/components/game-outcome/OutcomeNextStepMascot'

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function difficultyLabel(run: TierRun) {
  return run.difficulty ? capitalize(run.difficulty) : 'Adventure'
}

export function tierOutcomeState(run: TierRun) {
  const isFailed = run.status === 'failed'
  const isReplay = run.replay
  const isTransfer = Boolean(run.transfer)
  const canAdvance = !isTransfer && !isReplay && run.status === 'completed' && Boolean(run.next_difficulty)
  const isPartialClear = !isTransfer && !isReplay && run.status === 'completed' && !canAdvance && !run.progress.cleared
  return { isFailed, isReplay, isTransfer, canAdvance, isPartialClear }
}

/** What the workspace mascot offers once a finished tier run's modal is
 * dismissed: the next scenario, the next difficulty, a retry, or the map. */
export function tierOutcomeNextStep({
  run,
  onBackToMap,
  onNextLevel,
  onRetry,
  onContinue,
}: {
  run: TierRun
  onBackToMap: () => void
  onNextLevel?: () => void
  onRetry?: () => void
  /** Starts the next run on the same tier after a scenario clear that left scenarios
   * to play; the server picks the learner's next uncleared scenario. */
  onContinue?: () => void
}): OutcomeNextStep | null {
  if (run.status !== 'completed' && run.status !== 'failed') return null
  const { isFailed, isReplay, isTransfer, canAdvance, isPartialClear } = tierOutcomeState(run)
  const nextScenario = run.progress.next_scenario

  if (isTransfer) {
    return { caption: 'Practice', prompt: 'Click me to keep practicing!', onSelect: onRetry ?? onBackToMap }
  }
  if (canAdvance && onNextLevel && run.next_difficulty) {
    return {
      caption: 'Continue',
      prompt: `Click me to continue to the ${capitalize(run.next_difficulty.difficulty)} tier!`,
      onSelect: onNextLevel,
    }
  }
  if (isPartialClear && onContinue) {
    return {
      caption: 'Continue',
      prompt: 'Click me to continue to the next scenario!',
      detail: nextScenario ? `Next: ${nextScenario.title}` : undefined,
      onSelect: onContinue,
    }
  }
  if (isFailed && onRetry) return { caption: 'Try again', prompt: 'Click me to try again!', onSelect: onRetry }
  if (isReplay && onRetry) return { caption: 'Play again', prompt: 'Click me to play again!', onSelect: onRetry }
  return { caption: 'Map', prompt: 'Click me to head back to the map!', onSelect: onBackToMap }
}

import type { ChallengeRun } from '@/features/challenges/types'
import type { OutcomeNextStep } from '@/shared/level/components/game-outcome/OutcomeNextStepMascot'

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function difficultyLabel(run: ChallengeRun) {
  return run.difficulty ? capitalize(run.difficulty) : 'Challenge'
}

export function canAdvanceFrom(run: ChallengeRun) {
  return !run.replay && run.status === 'completed' && Boolean(run.next_difficulty)
}

/** What the workspace mascot offers once a finished Challenge Gate trial's
 * modal is dismissed: the gate's next trial, a retry, or the map. */
export function challengeOutcomeNextStep({
  run,
  onBackToMap,
  onNextLevel,
  onRetry,
  isStartingNextLevel = false,
  isRetrying = false,
}: {
  run: ChallengeRun
  onBackToMap: () => void
  onNextLevel?: () => void
  onRetry?: () => void
  isStartingNextLevel?: boolean
  isRetrying?: boolean
}): OutcomeNextStep | null {
  if (run.status !== 'completed' && run.status !== 'failed') return null
  if (canAdvanceFrom(run) && onNextLevel && run.next_difficulty) {
    return {
      caption: 'Continue',
      prompt: `Click me to continue to the ${capitalize(run.next_difficulty.difficulty)} trial!`,
      pending: isStartingNextLevel,
      pendingPrompt: 'Opening the next trial…',
      onSelect: onNextLevel,
    }
  }
  if (run.status === 'failed' && onRetry) {
    return {
      caption: 'Try again',
      prompt: 'Click me to try again!',
      pending: isRetrying,
      pendingPrompt: 'Starting a fresh variant…',
      onSelect: onRetry,
    }
  }
  if (run.replay && onRetry) {
    return { caption: 'Play again', prompt: 'Click me to play again!', pending: isRetrying, pendingPrompt: 'Starting…', onSelect: onRetry }
  }
  return { caption: 'Map', prompt: 'Click me to head back to the map!', onSelect: onBackToMap }
}

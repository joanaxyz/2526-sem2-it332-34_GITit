import { Activity, ArrowRight, Award, Castle, RefreshCcw, Send, Sparkles, Stethoscope, Target, Trophy, XCircle } from 'lucide-react'
import type { CSSProperties } from 'react'

import { ChallengeLevelNav } from '@/features/challenges/components/ChallengeLevelNav'
import type { ChallengeRun } from '@/shared/level/types'
import {
  commandAccuracyFromSession,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from '@/shared/level/utils/commandAccuracy'
import { CompletionModal, type CompletionStat } from '@/shared/level/components/completion/CompletionModal'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

function difficultyLabel(run: ChallengeRun) {
  if (!run.difficulty) return 'Challenge'
  return run.difficulty.charAt(0).toUpperCase() + run.difficulty.slice(1)
}

export function ChallengeOutcomeModal({
  open,
  run,
  onClose,
  onBackToTower,
  onNextLevel,
  onContinue,
  onRetry,
  onSelectLevel,
  busyLevelId,
  isStartingNextLevel = false,
  isContinuing = false,
  isRetrying = false,
  nextDifficultyLabel,
}: {
  open: boolean
  run: ChallengeRun
  onClose: () => void
  onBackToTower: () => void
  onNextLevel?: () => void
  onContinue?: () => void
  onRetry?: () => void
  /** Start a fresh run on an arbitrary sibling level from the level navigator. */
  onSelectLevel?: (levelId: number) => void
  busyLevelId?: number | null
  isStartingNextLevel?: boolean
  isContinuing?: boolean
  isRetrying?: boolean
  nextDifficultyLabel?: string | null
}) {
  const accuracy = commandAccuracyFromSession(run)
  const isFailed = run.status === 'failed'
  // Free-play replays are uncounted: no progress, no unlocks, no retry-for-
  // accuracy. They just recap the run and offer "Play again".
  const isReplay = run.review_mode
  const withinMasteryTarget = meetsMasteryAccuracy(accuracy)
  const meetsProgress = meetsProgressAccuracy(accuracy)
  const isNavigating = isStartingNextLevel || isContinuing || isRetrying || Boolean(busyLevelId)
  const requiredAttempts = run.mastery_progress?.required ?? 3
  const hasRequiredAttempts = (run.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const canAdvance = !isReplay && run.status === 'completed' && hasRequiredAttempts && meetsProgress
  const shouldContinueAttempt = !isReplay && run.status === 'completed' && !hasRequiredAttempts && meetsProgress
  const shouldRetryForAccuracy = !isReplay && run.status === 'completed' && !meetsProgress
  const headline = isReplay
    ? isFailed
      ? 'Replay ended'
      : 'Replay complete'
    : isFailed
      ? 'Attempt limit reached'
      : shouldRetryForAccuracy
        ? 'Level cleared, but accuracy needs a retry'
        : canAdvance
          ? 'Level ready'
          : run.first_attempt_star_eligible && withinMasteryTarget
            ? 'Clean run logged'
            : 'Level cleared'
  const hitActionLimit = isFailed && run.counts.max_reached
  const message = isReplay
    ? isFailed
      ? 'This free-play run ended before reaching the target state. It doesn’t affect your saved progress — play again whenever you like.'
      : 'Free play complete. This run is just a replay and doesn’t change your saved progress.'
    : isFailed
      ? hitActionLimit
        ? run.failure_reason ??
          'You used every counted action allowed for this attempt without reaching the target repository state. Check that you chose the correct conflict side, staged the file, and completed the merge commit, then start a fresh variant.'
        : 'This attempt ended before the repository reached the target state. Start a fresh variant and try again with a clean workspace.'
      : shouldRetryForAccuracy
        ? 'The target state was reached, but command accuracy was below 70%. Retry this level to count the run toward progress.'
        : canAdvance
          ? withinMasteryTarget
            ? 'You completed the required successful attempts at 100% accuracy. The next level is ready.'
            : 'You completed the required successful attempts. The next level is ready.'
          : meetsProgress
            ? 'That run counts toward progress. Continue to start a fresh attempt for the remaining successful records.'
            : 'Level cleared.'
  const Icon = isFailed ? XCircle : Sparkles

  const stats: CompletionStat[] = [
    {
      label: 'Accuracy',
      numerator: accuracy ?? 0,
      suffix: '%',
      helper: withinMasteryTarget
        ? 'At mastery target'
        : meetsProgress
          ? 'Counts toward progress'
          : 'Below progress threshold',
      icon: Target,
    },
    {
      label: 'Counted actions',
      numerator: run.counts.counted_action_total,
      denominator: run.policy.min_counted_commands,
      helper: 'Used / mastery target',
      icon: Activity,
    },
    {
      label: 'Submissions',
      numerator: run.counts.total_attempts,
      helper: 'All terminal entries',
      icon: Send,
    },
    {
      label: 'Free diagnostics',
      numerator: run.counts.non_counted_diagnostic_total,
      helper: 'Excluded from accuracy',
      icon: Stethoscope,
    },
    {
      label: 'Successful attempts',
      numerator: run.mastery_progress.mastered,
      denominator: run.mastery_progress.required,
      helper: 'Progress records',
      icon: Trophy,
    },
  ]

  const badges = (
    <>
      <Badge
        variant={isFailed ? 'destructive' : 'default'}
        className="completion-badge"
        style={{ animationDelay: '60ms' } as CSSProperties}
      >
        {difficultyLabel(run)} {isFailed ? 'failed' : 'complete'}
      </Badge>
      {!isFailed && run.first_attempt_star_eligible ? (
        <Badge
          variant="warning"
          className="completion-badge"
          style={{ animationDelay: '140ms' } as CSSProperties}
        >
          <Award className="size-3.5" />
          First-attempt star
        </Badge>
      ) : null}
    </>
  )

  const actions = isReplay ? (
    <>
      {onRetry ? (
        <Button type="button" disabled={isNavigating} onClick={onRetry}>
          <RefreshCcw data-icon="inline-start" />
          {isRetrying ? 'Starting fresh run' : 'Play again'}
        </Button>
      ) : null}
      <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToTower}>
        <Castle data-icon="inline-start" />
        Back to Tower
      </Button>
    </>
  ) : isFailed || shouldRetryForAccuracy ? (
    <>
      {onRetry ? (
        <Button type="button" variant="destructive" disabled={isNavigating} onClick={onRetry}>
          <RefreshCcw data-icon="inline-start" />
          {isRetrying
            ? 'Starting fresh variant'
            : shouldRetryForAccuracy
              ? 'Retry for accuracy'
              : 'Start fresh variant'}
        </Button>
      ) : null}
      <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToTower}>
        <Castle data-icon="inline-start" />
        Back to Tower
      </Button>
    </>
  ) : canAdvance ? (
    <>
      {onNextLevel && nextDifficultyLabel ? (
        <Button type="button" disabled={isNavigating} onClick={onNextLevel}>
          <ArrowRight data-icon="inline-start" />
          {isStartingNextLevel ? 'Opening next level' : `Next: ${nextDifficultyLabel}`}
        </Button>
      ) : null}
      <Button type="button" variant="secondary" disabled={isNavigating} onClick={onClose}>
        Stay in workspace
      </Button>
    </>
  ) : shouldContinueAttempt ? (
    <>
      {onContinue ? (
        <Button type="button" disabled={isNavigating} onClick={onContinue}>
          <ArrowRight data-icon="inline-start" />
          {isContinuing ? 'Continuing' : 'Continue'}
        </Button>
      ) : null}
      <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToTower}>
        <Castle data-icon="inline-start" />
        Back to Tower
      </Button>
    </>
  ) : run.status === 'completed' && meetsProgress ? (
    <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToTower}>
      <Castle data-icon="inline-start" />
      Back to Tower
    </Button>
  ) : null

  return (
    <CompletionModal
      open={open}
      onClose={onClose}
      title={isFailed ? 'Level failed' : 'Level complete'}
      tone={isFailed ? 'failure' : 'success'}
      icon={Icon}
      badges={badges}
      headline={headline}
      message={message}
      note={
        isFailed && run.variant.looped_variant
          ? 'You have cycled through all authored variants. Consider reviewing the command preview or the field guide before this next attempt.'
          : undefined
      }
      stats={stats}
      actions={actions}
    >
      {/* Level navigation is challenge-only — the adventure modal omits it. */}
      {!isReplay && onSelectLevel && run.sibling_levels && run.difficulty ? (
        <ChallengeLevelNav
          levels={run.sibling_levels}
          currentLevelId={run.challenge.level_id}
          onSelectLevel={onSelectLevel}
          busyLevelId={busyLevelId}
          disabled={isNavigating}
        />
      ) : null}
    </CompletionModal>
  )
}

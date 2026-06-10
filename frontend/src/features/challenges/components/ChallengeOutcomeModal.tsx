import { ArrowRight, Award, Castle, RefreshCcw, Sparkles, XCircle } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { ChallengeRun } from '@/shared/practice/types'
import type { ChallengeLevelAccess } from '@/features/challenges/types'
import {
  commandAccuracyFromSession,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from '@/shared/practice/utils/commandAccuracy'
import { CompletionConfetti } from '@/shared/practice/components/completion/CompletionConfetti'
import { CompletionStatTile } from '@/shared/practice/components/completion/CompletionStatTile'
import { TILE_ACCENTS } from '@/shared/practice/components/completion/tileAccents'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

function difficultyLabel(run: ChallengeRun) {
  if (!run.difficulty) return 'Challenge'
  return run.difficulty.charAt(0).toUpperCase() + run.difficulty.slice(1)
}

export function CompletionCelebrationModal({
  open,
  run,
  onClose,
  onBackToTower,
  onNextLevel,
  onContinue,
  onRetry,
  onReviewDifficulty,
  previousDifficulties = [],
  isStartingNextLevel = false,
  isContinuing = false,
  isRetrying = false,
  isReviewing = false,
  nextDifficultyLabel,
}: {
  open: boolean
  run: ChallengeRun
  onClose: () => void
  onBackToTower: () => void
  onNextLevel?: () => void
  onContinue?: () => void
  onRetry?: () => void
  onReviewDifficulty?: (difficulty: ChallengeLevelAccess) => void
  previousDifficulties?: ChallengeLevelAccess[]
  isStartingNextLevel?: boolean
  isContinuing?: boolean
  isRetrying?: boolean
  isReviewing?: boolean
  nextDifficultyLabel?: string | null
}) {
  const accuracy = commandAccuracyFromSession(run)
  const isFailed = run.status === 'failed'
  const withinMasteryTarget = meetsMasteryAccuracy(accuracy)
  const meetsProgress = meetsProgressAccuracy(accuracy)
  const isNavigating = isStartingNextLevel || isContinuing || isRetrying || isReviewing
  const requiredAttempts = run.mastery_progress?.required ?? 3
  const hasRequiredAttempts = (run.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const canAdvance = run.status === 'completed' && hasRequiredAttempts && meetsProgress
  const shouldContinueAttempt = run.status === 'completed' && !hasRequiredAttempts && meetsProgress
  const shouldRetryForAccuracy = run.status === 'completed' && !meetsProgress
  const headline = isFailed
    ? 'Attempt limit reached'
    : shouldRetryForAccuracy
      ? 'Practice cleared, but accuracy needs a retry'
      : canAdvance
        ? 'Level ready'
        : run.first_attempt_star_eligible && withinMasteryTarget
          ? 'Clean run logged'
          : 'Practice cleared'
  const hitActionLimit = isFailed && run.counts.max_reached
  const message = isFailed
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
          : 'Practice cleared.'
  const Icon = isFailed ? XCircle : Sparkles

  return (
    <Modal
      open={open}
      title={isFailed ? 'Practice failed' : 'Practice complete'}
      className={cn(
        'w-full max-w-2xl overflow-hidden bg-card',
        isFailed
          ? 'border-destructive/30 shadow-[0_28px_110px_rgba(248,113,113,0.16)]'
          : 'border-primary/30 shadow-[0_28px_110px_rgba(0,214,143,0.18)]',
      )}
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="relative overflow-hidden">
        {!isFailed ? <CompletionConfetti /> : null}

        <div className="relative px-5 pb-5 pt-5 text-center">
          <div
            className={cn(
              'mx-auto grid size-12 place-items-center rounded-full border',
              !isFailed && 'completion-sparkle-glow',
              isFailed
                ? 'border-destructive/30 bg-destructive/10 shadow-[0_0_42px_rgba(248,113,113,0.16)]'
                : 'border-primary/30 bg-primary/10',
            )}
          >
            <Icon className={cn('size-6', isFailed ? 'text-destructive' : 'text-primary')} />
          </div>

          <div className="mt-3 flex flex-wrap justify-center gap-2">
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
          </div>

          <h3 className="completion-headline mx-auto mt-3 max-w-xl text-balance text-xl font-extrabold tracking-tight sm:text-2xl">
            {headline}
          </h3>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{message}</p>
          {isFailed && run.variant.looped_variant ? (
            <p className="mx-auto mt-2 max-w-xl text-xs font-medium leading-5 text-warning">
              You have cycled through all authored variants. Consider reviewing the command preview or foundations before this next attempt.
            </p>
          ) : null}

          <div className="mt-4 grid grid-cols-2 gap-2 text-left max-sm:grid-cols-1">
            <CompletionStatTile
              label="Accuracy"
              numerator={accuracy ?? 0}
              suffix="%"
              helper={
                withinMasteryTarget
                  ? 'At mastery target'
                  : meetsProgress
                    ? 'Counts toward progress'
                    : 'Below progress threshold'
              }
              accentColor={TILE_ACCENTS[0]}
              animationDelay={160}
            />
            <CompletionStatTile
              label="Counted actions"
              numerator={run.counts.counted_action_total}
              denominator={run.policy.min_counted_commands}
              helper="Used / mastery target"
              accentColor={TILE_ACCENTS[1]}
              animationDelay={220}
            />
            <CompletionStatTile
              label="Submissions"
              numerator={run.counts.total_attempts}
              helper="All terminal entries"
              accentColor={TILE_ACCENTS[2]}
              animationDelay={280}
            />
            <CompletionStatTile
              label="Free diagnostics"
              numerator={run.counts.non_counted_diagnostic_total}
              helper="Diagnostics excluded from accuracy"
              accentColor={TILE_ACCENTS[3]}
              animationDelay={340}
            />
            <CompletionStatTile
              label="Successful attempts"
              numerator={run.mastery_progress.mastered}
              denominator={run.mastery_progress.required}
              helper="Progress records"
              accentColor={TILE_ACCENTS[4]}
              animationDelay={400}
            />
          </div>

          {previousDifficulties.length > 0 && !isFailed ? (
            <div className="mt-4">
              <div className="mb-2 flex items-center gap-3">
                <div className="h-px flex-1 bg-border/60" />
                <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Previous levels
                </span>
                <div className="h-px flex-1 bg-border/60" />
              </div>
              <div className="grid grid-cols-2 gap-2 max-sm:grid-cols-1">
                {previousDifficulties.map((difficulty) => (
                  <button
                    key={difficulty.id}
                    type="button"
                    disabled={!difficulty.review_available || isNavigating}
                    onClick={() => onReviewDifficulty?.(difficulty)}
                    className={cn(
                      'flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2 text-left transition-all duration-200',
                      difficulty.review_available && !isNavigating
                        ? 'hover:-translate-y-0.5 hover:border-primary/30 hover:bg-primary/5 hover:shadow-md'
                        : 'cursor-not-allowed opacity-50',
                    )}
                  >
                    <div>
                      <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
                      <div className="text-xs text-muted-foreground">
                        {difficulty.review_available ? 'Review available' : 'Locked'}
                      </div>
                    </div>
                    {difficulty.latest_attempt?.accuracy_rate !== null &&
                    difficulty.latest_attempt?.accuracy_rate !== undefined ? (
                      <span
                        className={cn(
                          'font-mono text-sm font-extrabold',
                          meetsMasteryAccuracy(difficulty.latest_attempt.accuracy_rate)
                            ? 'completion-perfect-score text-primary'
                            : meetsProgressAccuracy(difficulty.latest_attempt.accuracy_rate)
                              ? 'text-warning'
                              : 'text-destructive',
                        )}
                      >
                        {difficulty.latest_attempt.accuracy_rate}%
                      </span>
                    ) : null}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div className="mt-4 flex flex-wrap justify-center gap-3">
            {isFailed || shouldRetryForAccuracy ? (
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
            ) : null}
          </div>
        </div>
      </div>
    </Modal>
  )
}

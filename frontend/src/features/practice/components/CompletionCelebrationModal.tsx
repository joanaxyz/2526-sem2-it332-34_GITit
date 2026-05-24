import { ArrowRight, Award, PartyPopper, RefreshCcw, Sparkles, XCircle } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { ScenarioSession } from '@/features/practice/types'
import type { DifficultyAccess } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

const confettiColors = ['#00d68f', '#5aaeff', '#fbbf24', '#f472b6', '#a78bfa', '#f87171']

const confettiPieces = Array.from({ length: 46 }, (_, index) => {
  const side = index % 2 === 0 ? -1 : 1
  const lane = Math.floor(index / 2)
  const x = side * (42 + ((lane * 19) % 230))
  const y = 84 + ((index * 31) % 210)
  return {
    color: confettiColors[index % confettiColors.length],
    delay: `${(index % 9) * 48}ms`,
    duration: `${1850 + (index % 7) * 130}ms`,
    height: `${8 + (index % 3) * 3}px`,
    rotate: `${side * (220 + (index % 8) * 34)}deg`,
    width: `${5 + (index % 4)}px`,
    x: `${x}px`,
    y: `${y}px`,
  }
})

function completionAccuracy(session: ScenarioSession) {
  const targetActions = session.policy.min_counted_commands
  const usedActions = session.counts.counted_action_total
  if (usedActions <= targetActions) return 100
  if (targetActions === 0) return 0
  return Math.round((targetActions / usedActions) * 100)
}

function difficultyLabel(session: ScenarioSession) {
  return session.difficulty.charAt(0).toUpperCase() + session.difficulty.slice(1)
}

export function CompletionCelebrationModal({
  open,
  session,
  onClose,
  onBackToModules,
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
  session: ScenarioSession
  onClose: () => void
  onBackToModules: () => void
  onNextLevel?: () => void
  onContinue?: () => void
  onRetry?: () => void
  onReviewDifficulty?: (difficulty: DifficultyAccess) => void
  previousDifficulties?: DifficultyAccess[]
  isStartingNextLevel?: boolean
  isContinuing?: boolean
  isRetrying?: boolean
  isReviewing?: boolean
  nextDifficultyLabel?: string | null
}) {
  const accuracy = completionAccuracy(session)
  const isFailed = session.status === 'failed'
  const withinMasteryTarget = session.counts.counted_action_total <= session.policy.min_counted_commands
  const isNavigating = isStartingNextLevel || isContinuing || isRetrying || isReviewing
  const requiredAttempts = session.mastery_progress?.required ?? 3
  const hasRequiredAttempts = (session.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const isAccurate = session.counts.counted_action_total <= session.policy.min_counted_commands
  const canAdvance = session.status === 'completed' && hasRequiredAttempts && isAccurate
  const shouldContinueAttempt = session.status === 'completed' && !hasRequiredAttempts && isAccurate
  const shouldRetryForAccuracy = session.status === 'completed' && !isAccurate
  const headline = isFailed
    ? 'Attempt limit reached'
    : shouldRetryForAccuracy
      ? 'Scenario cleared, but accuracy needs a retry'
      : canAdvance
        ? 'Level ready'
        : session.first_attempt_star_eligible
          ? 'Clean run logged'
          : 'Scenario cleared'
  const message = isFailed
    ? 'This attempt ended before the repository reached the target state. Start a fresh variant and try again with a clean workspace.'
    : shouldRetryForAccuracy
      ? 'The target state was reached, but the latest run was not 100% accurate. Retry this level to protect your progress.'
      : canAdvance
        ? 'You completed the required successful attempts at 100% accuracy. The next level is ready.'
        : 'That accurate run counts. Continue to start a fresh attempt for the remaining successful records.'
  const Icon = isFailed ? XCircle : Sparkles

  return (
    <Modal
      open={open}
      title={isFailed ? 'Scenario failed' : 'Scenario complete'}
      className={cn(
        'max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto bg-card',
        isFailed
          ? 'border-destructive/30 shadow-[0_28px_110px_rgba(248,113,113,0.16)]'
          : 'border-primary/30 shadow-[0_28px_110px_rgba(0,214,143,0.18)]',
      )}
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="relative overflow-hidden">
        {!isFailed ? (
          <>
            <div className="completion-party-popper completion-party-popper-left" aria-hidden="true">
              <PartyPopper className="size-11 text-accent" />
            </div>
            <div className="completion-party-popper completion-party-popper-right" aria-hidden="true">
              <PartyPopper className="size-11 -scale-x-100 text-primary" />
            </div>
            <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
              {confettiPieces.map((piece, index) => (
                <span
                  className="completion-confetti"
                  key={`${piece.x}-${piece.y}-${index}`}
                  style={
                    {
                      '--confetti-color': piece.color,
                      '--confetti-delay': piece.delay,
                      '--confetti-duration': piece.duration,
                      '--confetti-height': piece.height,
                      '--confetti-rotate': piece.rotate,
                      '--confetti-width': piece.width,
                      '--confetti-x': piece.x,
                      '--confetti-y': piece.y,
                    } as CSSProperties
                  }
                />
              ))}
            </div>
          </>
        ) : null}

        <div className="relative px-6 pb-6 pt-7 text-center">
          <div
            className={cn(
              'mx-auto grid size-16 place-items-center rounded-full border',
              isFailed
                ? 'border-destructive/30 bg-destructive/10 shadow-[0_0_42px_rgba(248,113,113,0.16)]'
                : 'border-primary/30 bg-primary/10 shadow-[0_0_42px_rgba(0,214,143,0.2)]',
            )}
          >
            <Icon className={cn('size-8', isFailed ? 'text-destructive' : 'text-primary')} />
          </div>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            <Badge variant={isFailed ? 'destructive' : 'default'}>
              {difficultyLabel(session)} {isFailed ? 'failed' : 'complete'}
            </Badge>
            {!isFailed && session.first_attempt_star_eligible ? (
              <Badge variant="warning">
                <Award className="size-3.5" />
                First-attempt star
              </Badge>
            ) : null}
          </div>
          <h3 className="mx-auto mt-4 max-w-xl text-balance text-2xl font-extrabold tracking-tight sm:text-3xl">
            {headline}
          </h3>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground">{message}</p>

          <div className="mt-6 grid grid-cols-2 gap-3 text-left max-sm:grid-cols-1">
            <StatTile
              label="Accuracy"
              value={`${accuracy}%`}
              helper={withinMasteryTarget ? 'At mastery target' : 'Above counted-action target'}
            />
            <StatTile
              label="Counted actions"
              value={`${session.counts.counted_action_total}/${session.policy.min_counted_commands}`}
              helper="Used / mastery target"
            />
            <StatTile label="Submissions" value={`${session.counts.total_attempts}`} helper="All terminal entries" />
            <StatTile
              label="Free diagnostics"
              value={`${session.counts.non_counted_diagnostic_total}`}
              helper="Diagnostics excluded from accuracy"
            />
            <StatTile
              label="Successful attempts"
              value={`${session.mastery_progress.mastered}/${session.mastery_progress.required}`}
              helper="Accurate records"
            />
          </div>

          {previousDifficulties.length > 0 && !isFailed ? (
            <div className="mt-6">
              <div className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Previous levels
              </div>
              <div className="grid grid-cols-2 gap-2 max-sm:grid-cols-1">
                {previousDifficulties.map((difficulty) => (
                  <button
                    key={difficulty.id}
                    type="button"
                    disabled={!difficulty.review_available || isNavigating}
                    onClick={() => onReviewDifficulty?.(difficulty)}
                    className={cn(
                      'flex items-center justify-between rounded-lg border border-border bg-background/50 p-3 text-left transition-colors',
                      difficulty.review_available && !isNavigating
                        ? 'hover:border-primary/30 hover:bg-primary/5'
                        : 'cursor-not-allowed opacity-50',
                    )}
                  >
                    <div>
                      <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
                      <div className="mt-0.5 text-xs text-muted-foreground">
                        {difficulty.review_available ? 'Review available' : 'Locked'}
                      </div>
                    </div>
                    {difficulty.latest_attempt?.accuracy_rate !== null && difficulty.latest_attempt?.accuracy_rate !== undefined ? (
                      <span
                        className={cn(
                          'font-mono text-sm font-extrabold',
                          difficulty.latest_attempt.accuracy_rate >= 100 ? 'text-primary' : 'text-destructive',
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

          <div className="mt-6 flex flex-wrap justify-center gap-3">
            {isFailed || shouldRetryForAccuracy ? (
              <>
                {onRetry ? (
                  <Button type="button" variant="destructive" disabled={isNavigating} onClick={onRetry}>
                    <RefreshCcw data-icon="inline-start" />
                    {isRetrying ? 'Starting retry' : shouldRetryForAccuracy ? 'Retry for accuracy' : 'Retry'}
                  </Button>
                ) : null}
                <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToModules}>
                  Back to Modules
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
                <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToModules}>
                  Back to Modules
                </Button>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </Modal>
  )
}

function StatTile({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <div className="rounded-lg border border-border bg-background/50 p-4">
      <div className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-2xl font-extrabold tracking-tight">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{helper}</div>
    </div>
  )
}

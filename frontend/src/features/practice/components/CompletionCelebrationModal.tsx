import { useEffect, useRef, useState } from 'react'
import { ArrowRight, Award, PartyPopper, RefreshCcw, Sparkles, XCircle } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { PracticeSession } from '@/features/practice/types'
import type { WorkflowLevelAccess } from '@/features/scenarios/types'
import {
  commandAccuracyFromSession,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from '@/features/scenarios/utils/commandAccuracy'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

const TILE_ACCENTS = ['#00d68f', '#5aaeff', '#a78bfa', '#fbbf24', '#f472b6'] as const

const confettiColors = ['#00d68f', '#5aaeff', '#fbbf24', '#f472b6', '#a78bfa', '#f87171']

const confettiPieces = Array.from({ length: 52 }, (_, index) => {
  const side = index % 2 === 0 ? -1 : 1
  const lane = Math.floor(index / 2)
  const x = side * (38 + ((lane * 18) % 220))
  const y = 80 + ((index * 29) % 200)
  return {
    color: confettiColors[index % confettiColors.length],
    delay: `${(index % 10) * 42}ms`,
    duration: `${1700 + (index % 7) * 120}ms`,
    height: `${7 + (index % 4) * 2}px`,
    rotate: `${side * (210 + (index % 8) * 32)}deg`,
    width: `${4 + (index % 4)}px`,
    x: `${x}px`,
    y: `${y}px`,
  }
})

function difficultyLabel(session: PracticeSession) {
  if (!session.difficulty) return 'Drill'
  return session.difficulty.charAt(0).toUpperCase() + session.difficulty.slice(1)
}

function useCountUp(target: number, duration: number, delay = 0): number {
  const [value, setValue] = useState(0)
  const frameRef = useRef<number | null>(null)

  useEffect(() => {
    const timeout = setTimeout(() => {
      const start = performance.now()
      function step(now: number) {
        const elapsed = now - start
        const progress = Math.min(elapsed / duration, 1)
        const eased = 1 - Math.pow(1 - progress, 3)
        setValue(Math.round(eased * target))
        if (progress < 1) {
          frameRef.current = requestAnimationFrame(step)
        }
      }
      frameRef.current = requestAnimationFrame(step)
    }, delay)

    return () => {
      clearTimeout(timeout)
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current)
    }
  }, [target, duration, delay])

  return value
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
  session: PracticeSession
  onClose: () => void
  onBackToModules: () => void
  onNextLevel?: () => void
  onContinue?: () => void
  onRetry?: () => void
  onReviewDifficulty?: (difficulty: WorkflowLevelAccess) => void
  previousDifficulties?: WorkflowLevelAccess[]
  isStartingNextLevel?: boolean
  isContinuing?: boolean
  isRetrying?: boolean
  isReviewing?: boolean
  nextDifficultyLabel?: string | null
}) {
  const accuracy = commandAccuracyFromSession(session)
  const isFailed = session.status === 'failed'
  const withinMasteryTarget = meetsMasteryAccuracy(accuracy)
  const meetsProgress = meetsProgressAccuracy(accuracy)
  const isNavigating = isStartingNextLevel || isContinuing || isRetrying || isReviewing
  const requiredAttempts = session.mastery_progress?.required ?? 3
  const hasRequiredAttempts = (session.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const canAdvance = session.status === 'completed' && hasRequiredAttempts && meetsProgress
  const shouldContinueAttempt = session.status === 'completed' && !hasRequiredAttempts && meetsProgress
  const shouldRetryForAccuracy = session.status === 'completed' && !meetsProgress
  const headline = isFailed
    ? 'Attempt limit reached'
    : shouldRetryForAccuracy
      ? 'Scenario cleared, but accuracy needs a retry'
      : canAdvance
        ? 'Level ready'
        : session.first_attempt_star_eligible && withinMasteryTarget
          ? 'Clean run logged'
          : 'Scenario cleared'
  const hitActionLimit = isFailed && session.counts.max_reached
  const message = isFailed
    ? hitActionLimit
      ? session.failure_reason ??
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
          : 'Scenario cleared.'
  const Icon = isFailed ? XCircle : Sparkles

  return (
    <Modal
      open={open}
      title={isFailed ? 'Scenario failed' : 'Scenario complete'}
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
        {!isFailed ? (
          <>
            <div className="completion-party-popper completion-party-popper-left" aria-hidden="true">
              <PartyPopper className="size-10 text-accent" />
            </div>
            <div className="completion-party-popper completion-party-popper-right" aria-hidden="true">
              <PartyPopper className="size-10 -scale-x-100 text-primary" />
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
              {difficultyLabel(session)} {isFailed ? 'failed' : 'complete'}
            </Badge>
            {!isFailed && session.first_attempt_star_eligible ? (
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
          {isFailed && session.variant.looped_variant ? (
            <p className="mx-auto mt-2 max-w-xl text-xs font-medium leading-5 text-warning">
              You have cycled through all authored variants. Consider reviewing the command preview or foundations before this next attempt.
            </p>
          ) : null}

          <div className="mt-4 grid grid-cols-2 gap-2 text-left max-sm:grid-cols-1">
            <StatTile
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
            <StatTile
              label="Counted actions"
              numerator={session.counts.counted_action_total}
              denominator={session.policy.min_counted_commands}
              helper="Used / mastery target"
              accentColor={TILE_ACCENTS[1]}
              animationDelay={220}
            />
            <StatTile
              label="Submissions"
              numerator={session.counts.total_attempts}
              helper="All terminal entries"
              accentColor={TILE_ACCENTS[2]}
              animationDelay={280}
            />
            <StatTile
              label="Free diagnostics"
              numerator={session.counts.non_counted_diagnostic_total}
              helper="Diagnostics excluded from accuracy"
              accentColor={TILE_ACCENTS[3]}
              animationDelay={340}
            />
            <StatTile
              label="Successful attempts"
              numerator={session.mastery_progress.mastered}
              denominator={session.mastery_progress.required}
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
            ) : session.status === 'completed' && meetsProgress ? (
              <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToModules}>
                Back to Modules
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </Modal>
  )
}

function StatTile({
  label,
  numerator,
  denominator,
  suffix = '',
  helper,
  accentColor,
  animationDelay,
}: {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  accentColor: string
  animationDelay: number
}) {
  const animatedNum = useCountUp(numerator, 900, animationDelay + 50)

  return (
    <div
      className="completion-stat-tile rounded-lg border border-border bg-background/50 p-2.5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
      style={
        {
          animationDelay: `${animationDelay}ms`,
          borderTopColor: accentColor,
          borderTopWidth: '2px',
        } as CSSProperties
      }
    >
      <div className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-muted-foreground">{label}</div>
      <div className="mt-1.5 text-lg font-extrabold tracking-tight">
        {animatedNum}
        {suffix}
        {denominator !== undefined ? `/${denominator}` : ''}
      </div>
      <div className="mt-0.5 text-xs text-muted-foreground">{helper}</div>
    </div>
  )
}

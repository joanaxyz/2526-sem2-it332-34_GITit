import { ArrowRight, Award, PartyPopper, RotateCcw, Sparkles } from 'lucide-react'
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
  return session.counts.counted_action_total <= session.policy.min_counted_commands ? 100 : 0
}

function difficultyLabel(session: ScenarioSession) {
  return session.difficulty.charAt(0).toUpperCase() + session.difficulty.slice(1)
}

export function CompletionCelebrationModal({
  open,
  session,
  onClose,
  onBackToUnits,
  onRetry,
  onNextLevel,
  onReviewDifficulty,
  previousDifficulties = [],
  isRetrying = false,
  isStartingNextLevel = false,
  isReviewing = false,
  nextDifficultyLabel,
}: {
  open: boolean
  session: ScenarioSession
  onClose: () => void
  onBackToUnits: () => void
  onRetry: () => void
  onNextLevel?: () => void
  onReviewDifficulty?: (difficulty: DifficultyAccess) => void
  previousDifficulties?: DifficultyAccess[]
  isRetrying?: boolean
  isStartingNextLevel?: boolean
  isReviewing?: boolean
  nextDifficultyLabel?: string | null
}) {
  const accuracy = completionAccuracy(session)
  const withinMasteryTarget = session.counts.counted_action_total <= session.policy.min_counted_commands
  const headline = session.first_attempt_star_eligible ? 'Clean sweep!' : 'Scenario cleared!'
  const message = session.first_attempt_star_eligible
    ? 'You reached the target state without a miss — crisp, confident Git thinking.'
    : 'You got the repository exactly where it needed to be. The detours count as practice; the finish counts as progress.'
  const isNavigating = isRetrying || isStartingNextLevel || isReviewing

  return (
    <Modal
      open={open}
      title="Completion unlocked"
      className="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto border-primary/30 bg-card shadow-[0_28px_110px_rgba(0,214,143,0.18)]"
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="relative overflow-hidden">
        <div className="completion-party-popper completion-party-popper-left" aria-hidden="true">
          <PartyPopper className="size-11 text-amber-300" />
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

        <div className="relative px-6 pb-6 pt-7 text-center">
          <div className="mx-auto grid size-16 place-items-center rounded-full border border-primary/30 bg-primary/10 shadow-[0_0_42px_rgba(0,214,143,0.2)]">
            <Sparkles className="size-8 text-primary" />
          </div>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            <Badge variant="default">{difficultyLabel(session)} complete</Badge>
            {session.first_attempt_star_eligible ? (
              <Badge variant="warning">
                <Award className="size-3.5" />
                First-attempt star
              </Badge>
            ) : null}
          </div>
          <h3 className="mt-4 text-3xl font-extrabold tracking-tight">{headline}</h3>
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
              label="Free inspections"
              value={`${session.counts.non_counted_diagnostic_total}`}
              helper="Diagnostics excluded from accuracy"
            />
          </div>

          {previousDifficulties.length > 0 ? (
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
                        ? 'hover:bg-primary/5 hover:border-primary/30'
                        : 'opacity-50 cursor-not-allowed'
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
                          difficulty.latest_attempt.accuracy_rate >= 100 ? 'text-primary' : 'text-destructive'
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
            {onNextLevel && nextDifficultyLabel ? (
              <Button type="button" disabled={isNavigating} onClick={onNextLevel}>
                <ArrowRight data-icon="inline-start" />
                {isStartingNextLevel ? 'Opening next level' : `Next: ${nextDifficultyLabel}`}
              </Button>
            ) : null}
            <Button type="button" variant="outline" disabled={isNavigating} onClick={onRetry}>
              <RotateCcw data-icon="inline-start" />
              {isRetrying ? 'Starting retry' : 'Retry level'}
            </Button>
            <Button type="button" variant="secondary" disabled={isNavigating} onClick={onClose}>
              Stay in workspace
            </Button>
            <Button type="button" variant="ghost" disabled={isNavigating} onClick={onBackToUnits}>
              Back to Units
            </Button>
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

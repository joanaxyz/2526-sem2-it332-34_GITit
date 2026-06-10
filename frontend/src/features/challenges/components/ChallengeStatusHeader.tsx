import { ArrowLeft, CircleHelp, GitBranch, RefreshCcw } from 'lucide-react'

import { CommandBudgetHeader } from '@/features/challenges/components/CommandBudgetHeader'
import type { ChallengeRun } from '@/shared/practice/types'
import {
  commandAccuracyFromSession,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from '@/shared/practice/utils/commandAccuracy'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

export function ChallengeStatusHeader({
  run,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onStartOver,
  onOpenTour,
  onContinue,
  onReplay,
}: {
  run: ChallengeRun
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onOpenTour?: () => void
  onContinue?: () => void
  /** Free-play (review) replay: starts a fresh uncounted run on the same level. */
  onReplay?: () => void
}) {
  const exitLabel = run.status === 'started' ? 'Exit' : 'Back'
  const accuracy = commandAccuracyFromSession(run)
  const requiredAttempts = run.mastery_progress?.required ?? 1
  const hasRequiredAttempts = (run.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const meetsProgress = meetsProgressAccuracy(accuracy)
  const isMastered = run.status === 'completed' && hasRequiredAttempts && meetsMasteryAccuracy(accuracy)
  const canRetry =
    !run.review_mode &&
    (run.status === 'failed' || (run.status === 'completed' && !meetsProgress)) &&
    !!onRetry
  const canStartOver = !run.review_mode && run.status === 'started' && !!onStartOver
  const canContinue =
    !canRetry &&
    !run.review_mode &&
    run.status === 'completed' &&
    !isMastered &&
    meetsProgress &&
    !!onContinue
  // Free-play runs replay through a fresh uncounted run rather than retry/start
  // over. "Start over" while playing, "Play again" once the run has ended.
  const canReplay = run.review_mode && !!onReplay
  const replayLabel = run.status === 'started' ? 'Start over' : 'Play again'

  return (
    <header className="relative flex min-h-14 items-center justify-between gap-3 border-b border-border bg-background px-3 py-2">
      <div className="flex min-w-0 items-center gap-3">
        <Button type="button" variant="ghost" size="sm" disabled={isExiting} onClick={onExit}>
          <ArrowLeft data-icon="inline-start" />
          {isExiting ? 'Exiting' : exitLabel}
        </Button>
        <GitBranch className="size-5 shrink-0 text-primary" />
        {run.difficulty ? (
          <Badge variant="outline" className="shrink-0 capitalize">
            {run.difficulty}
          </Badge>
        ) : null}
      </div>
      <div className="flex min-w-0 items-center gap-2">
        <CommandBudgetHeader run={run} />
        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Open workspace guide" onClick={onOpenTour}>
          <CircleHelp className="size-4" />
        </Button>
        {canRetry ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onRetry}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting retry' : run.status === 'completed' ? 'Retry for accuracy' : 'Retry'}
          </Button>
        ) : null}
        {canStartOver ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onStartOver}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting' : 'Start over'}
          </Button>
        ) : null}
        {canContinue ? (
          <Button type="button" variant="outline" size="sm" disabled={isExiting || isRetrying} onClick={onContinue}>
            {isRetrying ? 'Continuing' : 'Continue'}
          </Button>
        ) : null}
        {canReplay ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onReplay}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting' : replayLabel}
          </Button>
        ) : null}
      </div>
    </header>
  )
}

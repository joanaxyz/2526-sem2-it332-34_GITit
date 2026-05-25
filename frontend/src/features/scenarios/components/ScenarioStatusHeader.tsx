import { ArrowLeft, CircleHelp, GitBranch, RefreshCcw } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { CommandBudgetHeader } from '@/features/scenarios/components/CommandBudgetHeader'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

export function ScenarioStatusHeader({
  session,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onStartOver,
  onOpenTour,
  onContinue,
}: {
  session: ScenarioSession
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onOpenTour?: () => void
  onContinue?: () => void
}) {
  const exitLabel = session.status === 'started' ? 'Exit' : 'Back'
  const requiredAttempts = session.mastery_progress?.required ?? 3
  const hasRequiredAttempts = (session.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const isAccurate = session.counts.counted_action_total <= session.policy.min_counted_commands
  const isMastered = session.status === 'completed' && hasRequiredAttempts && isAccurate
  const canRetry =
    !session.review_mode &&
    (session.status === 'failed' || (session.status === 'completed' && !isAccurate)) &&
    !!onRetry
  const canStartOver = !session.review_mode && session.status === 'started' && !!onStartOver
  const canContinue =
    !canRetry &&
    !session.review_mode &&
    session.status === 'completed' &&
    !isMastered &&
    isAccurate &&
    !!onContinue

  return (
    <header className="flex h-12 items-center justify-between gap-3 border-b border-border bg-background px-3">
      <div className="flex min-w-0 items-center gap-3">
        <Button type="button" variant="ghost" size="sm" disabled={isExiting} onClick={onExit}>
          <ArrowLeft data-icon="inline-start" />
          {isExiting ? 'Exiting' : exitLabel}
        </Button>
        <GitBranch className="size-5 text-primary" />
        <span className="truncate font-mono text-xs text-muted-foreground">
          Module {session.module.number} / {session.scenario.focus}
        </span>
      </div>
      <div className="flex min-w-0 items-center gap-2">
        <CommandBudgetHeader session={session} />
        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Open workspace guide" onClick={onOpenTour}>
          <CircleHelp className="size-4" />
        </Button>
        {canRetry ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onRetry}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting retry' : session.status === 'completed' ? 'Retry for accuracy' : 'Retry'}
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
        <Badge variant={session.status === 'completed' ? 'default' : session.status === 'failed' ? 'destructive' : 'blue'}>
          {session.status}
        </Badge>
        <Badge variant="outline" className="hidden sm:inline-flex">
          {session.variant.label}
        </Badge>
      </div>
    </header>
  )
}

import { ArrowLeft, CircleHelp, GitBranch, RefreshCcw } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

export function ScenarioStatusHeader({
  session,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onOpenTour,
}: {
  session: ScenarioSession
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
  onOpenTour?: () => void
}) {
  const exitLabel = session.status === 'started' ? 'Exit' : 'Back'
  const isPerfectCompletion =
    session.status === 'completed' &&
    session.counts.counted_action_total <= session.policy.min_counted_commands
  const canRetry = !session.review_mode && !isPerfectCompletion && onRetry

  return (
    <header className="flex h-12 items-center justify-between gap-3 border-b border-border bg-background px-3">
      <div className="flex min-w-0 items-center gap-3">
        <Button type="button" variant="ghost" size="sm" disabled={isExiting} onClick={onExit}>
          <ArrowLeft data-icon="inline-start" />
          {isExiting ? 'Exiting' : exitLabel}
        </Button>
        <GitBranch className="size-5 text-primary" />
        <span className="truncate font-mono text-xs text-muted-foreground">
          Module {session.unit.number} / {session.scenario.focus}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Open workspace guide" onClick={onOpenTour}>
          <CircleHelp className="size-4" />
        </Button>
        {canRetry ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onRetry}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting retry' : 'Retry'}
          </Button>
        ) : null}
        <Badge variant={session.status === 'completed' ? 'default' : session.status === 'failed' ? 'destructive' : 'blue'}>
          {session.status}
        </Badge>
        <Badge variant="outline">{session.variant.label}</Badge>
      </div>
    </header>
  )
}

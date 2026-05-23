import { ArrowLeft, CircleHelp, GitBranch, RefreshCcw, GaugeCircle } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { Button } from '@/shared/components/Button'

export function ScenarioStatusHeader({
  session,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onOpenTour,
  onContinue,
}: {
  session: ScenarioSession
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
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
      <div className="flex items-center gap-2">
        {/* Compact command counter shown in header (compact height) */}
        <div className="hidden lg:flex items-center">
          {(() => {
            const used = session.counts.counted_action_total
            const max = session.policy.max_counted_commands
            const pct = max ? Math.round((used / max) * 100) : 0
            return (
              <div
                className="mr-2 rounded-md border border-border bg-card px-2 py-1 shadow-sm flex items-center"
                style={{ minWidth: 200, height: 36 }}
              >
                <div className="flex items-center gap-2">
                  <GaugeCircle className="size-4 text-primary" />
                  <span className="text-sm font-semibold">Action</span>
                </div>

                <div className="ml-4 flex flex-col items-end flex-1">
                  <div className="flex items-center gap-2">
                    <div className="font-mono text-sm font-semibold">{used}/{session.policy.min_counted_commands}</div>
                    <Badge variant="default" className="text-xs">Target {session.policy.min_counted_commands}</Badge>
                  </div>
                  <div className="w-full mt-1">
                    <ProgressBar value={pct} />
                  </div>
                </div>
              </div>
            )
          })()}
        </div>
        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Open workspace guide" onClick={onOpenTour}>
          <CircleHelp className="size-4" />
        </Button>
        {canRetry ? (
          <Button type="button" variant="outline" size="sm" disabled={isRetrying} onClick={onRetry}>
            <RefreshCcw data-icon="inline-start" />
            {isRetrying ? 'Starting retry' : 'Retry'}
          </Button>
        ) : null}
        {canContinue ? (
          <Button type="button" variant="outline" size="sm" disabled={isExiting} onClick={onContinue}>
            Continue
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

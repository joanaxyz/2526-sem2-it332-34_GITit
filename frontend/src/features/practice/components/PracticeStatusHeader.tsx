import { ArrowLeft, CircleHelp, GitBranch, RefreshCcw } from 'lucide-react'

import type { PracticeSession } from '@/features/practice/types'
import { CommandBudgetHeader } from '@/features/scenarios/components/CommandBudgetHeader'
import {
  commandAccuracyFromSession,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from '@/features/practice/utils/commandAccuracy'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function PracticeStatusHeader({
  session,
  isExiting = false,
  isRetrying = false,
  onExit,
  onRetry,
  onStartOver,
  onOpenTour,
  onContinue,
}: {
  session: PracticeSession
  isExiting?: boolean
  isRetrying?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onOpenTour?: () => void
  onContinue?: () => void
}) {
  const exitLabel = session.status === 'started' ? 'Exit' : 'Back'
  const accuracy = commandAccuracyFromSession(session)
  const requiredAttempts = session.mastery_progress?.required ?? 1
  const hasRequiredAttempts = (session.mastery_progress?.mastered ?? 0) >= requiredAttempts
  const meetsProgress = meetsProgressAccuracy(accuracy)
  const isMastered = session.status === 'completed' && hasRequiredAttempts && meetsMasteryAccuracy(accuracy)
  const canRetry =
    !session.review_mode &&
    (session.status === 'failed' || (session.status === 'completed' && !meetsProgress)) &&
    !!onRetry
  const canStartOver = !session.review_mode && session.status === 'started' && !!onStartOver
  const canContinue =
    !canRetry &&
    !session.review_mode &&
    session.status === 'completed' &&
    !isMastered &&
    meetsProgress &&
    !!onContinue
  const isCommandDrill = session.practice_kind === 'command_drill'
  const drillProgress = session.mastery_progress?.required
    ? Math.round((session.mastery_progress.mastered / session.mastery_progress.required) * 100)
    : 0
  const commandProblem = isCommandDrill && 'topic' in session.problem ? session.problem : null
  const workflowTitle = !isCommandDrill && 'narrative' in session.problem ? session.problem.title : null
  const tower = session.tower ?? session.module

  return (
    <header className="relative flex min-h-14 items-center justify-between gap-3 border-b border-border bg-background px-3 py-2">
      <div className="flex min-w-0 items-center gap-3">
        <Button type="button" variant="ghost" size="sm" disabled={isExiting} onClick={onExit}>
          <ArrowLeft data-icon="inline-start" />
          {isExiting ? 'Exiting' : exitLabel}
          </Button>
        <GitBranch className="size-5 shrink-0 text-primary" />
        <div className="min-w-0">
          <span className="block truncate font-mono text-xs text-muted-foreground">
            Tower {tower.number} / {isCommandDrill ? commandProblem?.adventure?.title ?? 'Command Adventure' : workflowTitle ?? 'Workflow scenario'}
          </span>
          <span className="mt-0.5 block truncate text-xs text-foreground">
            {isCommandDrill && commandProblem
              ? `${commandProblem.command_level?.label ?? 'Level'} / ${commandProblem.topic.base_command}`
              : session.difficulty
                ? `${session.difficulty} / ${session.counts.counted_action_total} actions used`
                : session.problem.title}
          </span>
        </div>
      </div>
      <div className="flex min-w-0 items-center gap-2">
        {isCommandDrill ? (
          <div className="hidden min-w-[9rem] sm:block">
            <div className="flex justify-between gap-2 font-mono text-[10px] text-muted-foreground">
              <span>Attempts</span>
              <span>{session.mastery_progress.mastered}/{session.mastery_progress.required}</span>
            </div>
            <ProgressBar value={drillProgress} className="mt-1 h-1.5" glow />
          </div>
        ) : (
          <CommandBudgetHeader session={session} />
        )}
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

        <Badge variant="outline" className="hidden sm:inline-flex">
          {session.variant.label}
        </Badge>
      </div>
      {isCommandDrill ? (
        <div className="absolute inset-x-0 bottom-0 h-px bg-secondary">
          <div className="h-full bg-primary transition-all" style={{ width: `${drillProgress}%` }} />
        </div>
      ) : null}
    </header>
  )
}

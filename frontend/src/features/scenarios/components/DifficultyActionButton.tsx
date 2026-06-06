import { ArrowRight, Lock, Play, RefreshCcw, RotateCcw, Star } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { PracticeActionIntent, WorkflowLevelAccess } from '@/features/scenarios/types'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/features/scenarios/utils/commandAccuracy'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

function actionForDifficulty(difficulty: WorkflowLevelAccess): PracticeActionIntent | null {
  if (difficulty.status === 'locked') return null
  if (difficulty.status === 'in_progress') return difficulty.active_session_id ? 'resume' : null
  if (difficulty.status === 'completed') {
    const latestAccuracy = difficulty.latest_attempt?.accuracy_rate ?? null
    if (difficulty.review_available && meetsMasteryAccuracy(latestAccuracy)) return 'review'
    if (meetsProgressAccuracy(latestAccuracy)) return 'continue'
    return 'retry'
  }
  if (difficulty.status === 'failed' || difficulty.status === 'abandoned') return 'retry'
  return 'start'
}

function masteredRecordsFor(difficulty: WorkflowLevelAccess) {
  return {
    mastered: difficulty.successful_attempts.count,
    required: difficulty.successful_attempts.required,
  }
}

export function DifficultyActionButton({
  difficulty,
  disabled = false,
  onAction,
}: {
  difficulty: WorkflowLevelAccess
  disabled?: boolean
  onAction: (difficulty: WorkflowLevelAccess, action: PracticeActionIntent) => void
}) {
  const action = actionForDifficulty(difficulty)
  const buttonLabel =
    difficulty.status === 'locked'
      ? 'Locked'
      : action === 'review'
        ? 'Review'
        : action === 'continue' || action === 'resume'
          ? 'Continue'
        : action === 'retry'
          ? 'Retry'
          : 'Start'
  const Icon =
    difficulty.status === 'locked'
      ? Lock
      : action === 'review'
        ? RotateCcw
        : action === 'continue' || action === 'resume'
          ? ArrowRight
        : action === 'retry'
          ? RefreshCcw
          : Play
  const latestAttempt = difficulty.latest_attempt
  const mastery = latestAttempt?.accuracy_rate ?? null
  const masteredRecords = masteredRecordsFor(difficulty)

  return (
    <div className={cn(
      'flex items-center gap-3 rounded-md border bg-background/30 p-3 transition-opacity',
      difficulty.status === 'locked' ? 'border-border/35 opacity-50' : 'border-border',
    )}>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
          <Button
            type="button"
            size="sm"
            disabled={!action || disabled}
            variant={!action || action === 'review' || action === 'retry' ? 'outline' : 'default'}
            onClick={() => {
              if (action && !disabled) onAction(difficulty, action)
            }}
          >
            <Icon data-icon="inline-start" />
            {buttonLabel}
          </Button>
          {difficulty.completion?.first_attempt_star ? <Star className="size-4 text-primary" /> : null}
        </div>
        <div className="mt-3 flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-muted-foreground">
            {masteredRecords.mastered}/{masteredRecords.required}
          </span>
          <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-border">
            <span
              className="block h-full rounded-full bg-primary"
              style={{ width: `${(masteredRecords.mastered / masteredRecords.required) * 100}%` }}
            />
          </span>
        </div>
      </div>
      <div>
        <MasteryProgress value={mastery} />
      </div>
    </div>
  )
}

function MasteryProgress({ value }: { value: number | null }) {
  const progress = value ?? 0
  const isPerfect = meetsMasteryAccuracy(value)
  const meetsProgress = meetsProgressAccuracy(value)
  const hasValue = value !== null

  const color = !hasValue
    ? 'hsl(var(--muted-foreground))'
    : isPerfect
      ? 'hsl(var(--primary))'
      : meetsProgress
        ? 'hsl(var(--warning))'
        : 'hsl(var(--destructive))'
  const label = !hasValue ? '-' : `${value}%`

  return (
    <div
      aria-label={!hasValue ? 'No accuracy data' : `Accuracy ${value}%`}
      className={cn(
        'relative flex size-[3.25rem] shrink-0 items-center justify-center rounded-full',
        isPerfect && 'shadow-[0_0_12px_rgba(0,214,143,0.35)]'
      )}
      style={
        {
          background: `conic-gradient(${color} ${progress * 3.6}deg, hsl(var(--border)) 0deg)`,
        } as CSSProperties
      }
      title="Accuracy rate"
    >
      <div className="absolute inset-[3px] rounded-full bg-card" />
      <div className="absolute inset-0 z-10 flex items-center justify-center">
        <span
          className={cn(
            'font-mono text-sm font-extrabold leading-none pb-px',
            !hasValue && 'text-muted-foreground',
            isPerfect && 'text-primary',
            hasValue && meetsProgress && !isPerfect && 'text-warning',
            hasValue && !meetsProgress && 'text-destructive'
          )}
        >
          {label}
        </span>
      </div>
    </div>
  )
}

import { Lock, Play, RefreshCcw, RotateCcw, Star } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { DifficultyAccess, DifficultyActionIntent } from '@/features/scenarios/types'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

function actionForDifficulty(difficulty: DifficultyAccess): DifficultyActionIntent | null {
  if (difficulty.status === 'locked') return null
  if (difficulty.status === 'completed') return 'review'
  if (difficulty.status === 'in_progress') return 'continue'
  if (difficulty.status === 'failed' || difficulty.status === 'abandoned') return 'retry'
  return 'start'
}

export function DifficultyActionButton({
  difficulty,
  onAction,
}: {
  difficulty: DifficultyAccess
  onAction: (difficulty: DifficultyAccess, action: DifficultyActionIntent) => void
}) {
  const action = actionForDifficulty(difficulty)
  const buttonLabel = action === 'continue' ? 'Continue' : action === 'review' ? 'Review' : action === 'retry' ? 'Retry' : 'Start'
  const Icon = difficulty.status === 'locked' ? Lock : action === 'review' ? RotateCcw : action === 'retry' ? RefreshCcw : Play
  const latestAttempt = difficulty.latest_attempt
  const mastery = latestAttempt?.accuracy_rate ?? null

  return (
    <div className="relative rounded-md border border-border bg-background/30 p-3">
      <div className="absolute right-3 top-3">
        <MasteryProgress value={mastery} />
      </div>
      <div className="flex flex-col gap-3 pr-14">
        <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
        <div className="flex flex-wrap items-center gap-2">
        <Button
          type="button"
          size="sm"
          disabled={!action}
          variant={action === 'review' || action === 'retry' ? 'outline' : 'default'}
          onClick={() => {
            if (action) onAction(difficulty, action)
          }}
        >
          <Icon data-icon="inline-start" />
          {buttonLabel}
        </Button>
        {difficulty.completion?.first_attempt_star ? <Star className="size-4 text-amber-300" /> : null}
      </div>
      </div>
    </div>
  )
}

function MasteryProgress({ value }: { value: number | null }) {
  const progress = value ?? 0
  const isPerfect = value !== null && value >= 100
  const hasValue = value !== null

  const color = !hasValue
    ? 'hsl(var(--muted-foreground))'
    : isPerfect
      ? 'hsl(var(--primary))'
      : 'hsl(var(--destructive))'
  const label = !hasValue ? '—' : `${value}%`

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
            hasValue && !isPerfect && 'text-destructive'
          )}
        >
          {label}
        </span>
      </div>
    </div>
  )
}

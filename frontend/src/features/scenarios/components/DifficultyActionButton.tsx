import { Lock, Play, RefreshCcw, RotateCcw, Star } from 'lucide-react'

import type { DifficultyAccess, DifficultyActionIntent, DifficultyStatus } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

const statusCopy: Record<DifficultyStatus, { label: string; badge: 'default' | 'outline' | 'warning' | 'destructive' | 'blue' }> = {
  not_started: { label: 'Not Started', badge: 'blue' },
  in_progress: { label: 'In Progress', badge: 'warning' },
  completed: { label: 'Completed', badge: 'default' },
  locked: { label: 'Locked', badge: 'outline' },
  failed: { label: 'Failed', badge: 'destructive' },
  abandoned: { label: 'Abandoned', badge: 'destructive' },
}

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
  const status = statusCopy[difficulty.status]
  const buttonLabel = action === 'continue' ? 'Continue' : action === 'review' ? 'Review' : action === 'retry' ? 'Retry' : 'Start'
  const Icon = difficulty.status === 'locked' ? Lock : action === 'review' ? RotateCcw : action === 'retry' ? RefreshCcw : Play

  return (
    <div className="rounded-md border border-border bg-background/30 p-3">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
        <Badge variant={status.badge}>{status.label}</Badge>
      </div>
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
        {difficulty.completion?.first_attempt_star ? (
          <Badge variant="warning">
            <Star className="size-3" />
            Star
          </Badge>
        ) : null}
      </div>
    </div>
  )
}

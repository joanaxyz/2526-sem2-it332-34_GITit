import { Lock, Play, RefreshCcw, RotateCcw } from 'lucide-react'

import type { ChallengeActionIntent, ChallengeTrialAccess } from '@/features/challenges/types'
import { Button } from '@/shared/components/Button'
import { StarRating } from '@/shared/level/components/StarRating'
import { cn } from '@/shared/utils/cn'

function actionForDifficulty(difficulty: ChallengeTrialAccess): ChallengeActionIntent | null {
  if (difficulty.status === 'locked') return null
  if (difficulty.status === 'in_progress') return 'start'
  if (difficulty.status === 'completed') {
    if (difficulty.replay_available) return 'replay'
    return null
  }
  if (difficulty.status === 'failed' || difficulty.status === 'abandoned') return 'retry'
  return 'start'
}

export function DifficultyActionButton({
  difficulty,
  disabled = false,
  onAction,
}: {
  difficulty: ChallengeTrialAccess
  disabled?: boolean
  onAction: (difficulty: ChallengeTrialAccess, action: ChallengeActionIntent) => void
}) {
  const action = actionForDifficulty(difficulty)
  const buttonLabel =
    difficulty.status === 'locked'
      ? 'Locked'
      : action === 'replay'
        ? 'Replay'
        : action === 'retry'
          ? 'Retry'
          : 'Start'
  const Icon =
    difficulty.status === 'locked'
      ? Lock
      : action === 'replay'
        ? RotateCcw
        : action === 'retry'
          ? RefreshCcw
          : Play
  const completionStars = difficulty.completion?.stars ?? 0

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
            variant={!action || action === 'replay' || action === 'retry' ? 'outline' : 'default'}
            onClick={() => {
              if (action && !disabled) onAction(difficulty, action)
            }}
          >
            <Icon data-icon="inline-start" />
            {buttonLabel}
          </Button>
        </div>
        <StarRating stars={completionStars} size="sm" className="mt-2" label={`${difficulty.difficulty} stars`} />
      </div>
    </div>
  )
}

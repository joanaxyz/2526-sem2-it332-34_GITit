import { Lock, Play, RotateCcw, Star } from 'lucide-react'

import type { DifficultyAccess } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

export function DifficultySelector({
  difficulties,
  onStart,
  onReview,
}: {
  difficulties: DifficultyAccess[]
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
      {difficulties.map((difficulty) => {
        const locked = difficulty.status === 'locked'
        const complete = difficulty.status === 'complete'
        return (
          <div key={difficulty.id} className="rounded-md border border-border bg-background/30 p-3">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
              {complete ? <Badge variant="default">Complete</Badge> : locked ? <Badge variant="outline">Locked</Badge> : <Badge variant="blue">Available</Badge>}
            </div>
            <div className="mt-3 flex flex-col gap-2 text-xs text-muted-foreground">
              <span>CAR threshold: {difficulty.policy.min_counted_commands}</span>
              <span>Limit: {difficulty.policy.max_counted_commands}</span>
            </div>
            <div className="mt-3 flex gap-2">
              {complete && difficulty.review_available ? (
                <Button type="button" size="sm" variant="outline" onClick={() => onReview(difficulty)}>
                  <RotateCcw data-icon="inline-start" />
                  Review
                </Button>
              ) : (
                <Button type="button" size="sm" disabled={locked} onClick={() => onStart(difficulty)}>
                  {locked ? <Lock data-icon="inline-start" /> : <Play data-icon="inline-start" />}
                  Start
                </Button>
              )}
              {difficulty.completion?.first_attempt_star ? (
                <Badge variant="warning">
                  <Star className="size-3" />
                  Star
                </Badge>
              ) : null}
            </div>
          </div>
        )
      })}
    </div>
  )
}

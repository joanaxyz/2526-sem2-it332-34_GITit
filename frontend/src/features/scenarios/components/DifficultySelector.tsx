import { Lock, Play, RotateCcw, Star } from 'lucide-react'

import type { DifficultyAccess } from '@/features/scenarios/types'
import { commitMessageGuidance } from '@/features/scenarios/utils/scenarioGuidance'
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
        const inProgress = difficulty.status === 'in_progress'
        return (
          <div key={difficulty.id} className="rounded-md border border-border bg-background/30 p-3">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-bold capitalize">{difficulty.difficulty}</div>
              {complete ? (
                <Badge variant="default">Complete</Badge>
              ) : locked ? (
                <Badge variant="outline">Locked</Badge>
              ) : inProgress ? (
                <Badge variant="warning">In progress</Badge>
              ) : (
                <Badge variant="blue">Available</Badge>
              )}
            </div>
            <p className="mt-3 text-xs leading-5 text-muted-foreground">{difficulty.task_prompt}</p>
            <div className="mt-3 flex flex-col gap-2 rounded-md border border-border bg-secondary/30 p-2 text-xs text-muted-foreground">
              <span>{commitMessageGuidance(difficulty.task_prompt)}</span>
              <span>Action budget: target {difficulty.policy.min_counted_commands}, limit {difficulty.policy.max_counted_commands} counted actions.</span>
              <span>
                Free inspection: {difficulty.policy.non_counted_patterns.length ? difficulty.policy.non_counted_patterns.join(', ') : 'none listed'}
              </span>
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
                  {inProgress ? 'Continue' : 'Start'}
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

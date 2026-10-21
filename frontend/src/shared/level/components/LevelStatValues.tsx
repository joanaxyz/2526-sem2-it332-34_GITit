import { Star } from 'lucide-react'

import { StarRulesButton } from './StarRules'
import type { LevelTourMode } from '@/shared/level/utils/levelTour'
import { cn } from '@/shared/utils/cn'

/** Values shown in a gameplay workspace's stats strip. */
export function StarTriplet({ count, className, mode = 'tier' }: {
  count: number
  className?: string
  mode?: LevelTourMode
}) {
  return (
    <StarRulesButton label={`Star rules: ${count} of 3 stars`} mode={mode}>
      <span className={cn('gameplay-header-stars', className)} aria-label={`${count} of 3 stars`}>
        {Array.from({ length: 3 }).map((_, index) => (
          <Star key={index} aria-hidden="true" className={index < count ? 'is-lit' : ''} />
        ))}
      </span>
    </StarRulesButton>
  )
}

export function DifficultyChip({ difficulty }: { difficulty: string }) {
  return (
    <span className={cn('lvlctx-chip', `lvlctx-chip--${difficulty.toLowerCase()}`)}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  )
}

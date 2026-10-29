import { Star } from 'lucide-react'

import { StarRulesButton } from './StarRules'
import type { LevelTourMode } from '@/shared/level/utils/levelTour'
import { cn } from '@/shared/utils/cn'
import { normalizeStarScore } from '@/shared/level/utils/starScore'
import type { StarBreakdown } from './StarScoreChecklist'

/** Values shown in a gameplay workspace's stats strip. */
export function StarTriplet({ count, className, mode = 'tier', breakdown, active, savedStars, multiScenario }: {
  count: number
  className?: string
  mode?: LevelTourMode
  breakdown?: StarBreakdown | null
  active?: boolean
  savedStars?: number
  multiScenario?: boolean
}) {
  const earned = normalizeStarScore(count)
  const scoreLabel = `${earned} of 3 stars${active ? ' available on clear' : ''}`
  return (
    <StarRulesButton label={`Star rules: ${scoreLabel}`} mode={mode} breakdown={breakdown} active={active} savedStars={savedStars} multiScenario={multiScenario}>
      <span className={cn('gameplay-header-stars', className)} aria-label={scoreLabel}>
        {Array.from({ length: 3 }).map((_, index) => (
          <Star key={index} aria-hidden="true" className={index < earned ? 'is-lit' : ''} />
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

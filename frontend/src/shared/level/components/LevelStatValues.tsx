import { Star } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import { StarRulesButton } from './StarRules'
import type { LevelTourMode } from '@/shared/level/utils/levelTour'
import { cn } from '@/shared/utils/cn'
import { normalizeStarScore } from '@/shared/level/utils/starScore'
import type { StarBreakdown } from './StarScoreChecklist'

/** Values shown in a gameplay workspace's stats strip. */
export function StarTriplet({ count, className, mode = 'tier', breakdown, active, savedStars, multiScenario, runId }: {
  count: number
  className?: string
  mode?: LevelTourMode
  breakdown?: StarBreakdown | null
  active?: boolean
  savedStars?: number
  multiScenario?: boolean
  runId?: number
}) {
  const earned = normalizeStarScore(count)
  const scoreLabel = `${earned} of 3 stars${active ? ' available on clear' : ''}`
  const previous = useRef({ runId, earned, active })
  const [notice, setNotice] = useState<{ from: number; to: number; reason: string } | null>(null)

  useEffect(() => {
    const before = previous.current
    previous.current = { runId, earned, active }
    if (before.runId !== runId) {
      setNotice(null)
      return
    }
    if (!active || !before.active || earned >= before.earned || !breakdown) return
    const reason = (breakdown.scoring_policy_version ?? 1) >= 2
      ? before.earned > 2 && earned <= 1
        ? `Efficient and generous targets exceeded: ${breakdown.counted_commands} / ${breakdown.command_target} and ${breakdown.generous_target} counted commands.`
        : earned <= 1
          ? `Generous target exceeded: ${breakdown.counted_commands} / ${breakdown.generous_target} counted commands.`
          : `Efficient target exceeded: ${breakdown.counted_commands} / ${breakdown.command_target} counted commands.`
      : breakdown.counted_commands > breakdown.command_target
        ? `Command target exceeded: ${breakdown.counted_commands} / ${breakdown.command_target} counted commands.`
        : `Retry allowance exceeded: ${breakdown.retry_count} retries / 1 allowed.`
    setNotice({ from: before.earned, to: earned, reason })
  }, [active, breakdown, earned, runId])

  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(null), 4500)
    return () => window.clearTimeout(timer)
  }, [notice])

  return (
    <span className="gameplay-star-status">
      <StarRulesButton label={`Star rules: ${scoreLabel}`} mode={mode} breakdown={breakdown} active={active} savedStars={savedStars} multiScenario={multiScenario}>
        <span className={cn('gameplay-header-stars', className)} aria-label={scoreLabel}>
          {Array.from({ length: 3 }).map((_, index) => (
            <Star key={index} aria-hidden="true" className={cn(index < earned && 'is-lit', notice && index >= notice.to && index < notice.from && 'is-lost')} />
          ))}
        </span>
      </StarRulesButton>
      {notice ? createPortal(<div className="gameplay-star-notice" role="status" aria-live="polite">
        <strong>{notice.from} → {notice.to} stars available on clear</strong>
        <span>{notice.reason}</span>
      </div>, document.body) : null}
    </span>
  )
}

export function DifficultyChip({ difficulty }: { difficulty: string }) {
  return (
    <span className={cn('lvlctx-chip', `lvlctx-chip--${difficulty.toLowerCase()}`)}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  )
}

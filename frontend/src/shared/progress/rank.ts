import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/api/queryKeys'
import { homeSummaryApi } from '@/shared/progress/homeSummaryApi'
import type { HomeSummary } from '@/shared/progress/types'

/**
 * Ranked ladder derived from the player's lifetime XP (`HomeSummary.xp`). XP is
 * never spent, so a rank is never lost through the shop. The top threshold stays
 * reachable by a learner who failed every first-run transfer checkpoint.
 */
export type RankTier = {
  /** Ladder position, 1-based (Peasant = 1). */
  rank: number
  /** Roman numeral shown in crests and pills ("IV"). */
  numeral: string
  name: string
  minXp: number
  /** Tier accent and optional RGB token for CSS rgba() vars. */
  color: string
  colorRgb: string
}

export const RANK_TIERS: RankTier[] = [
  { rank: 1, numeral: 'I', name: 'Peasant', minXp: 0, color: 'rgb(var(--theme-spark-rgb))', colorRgb: '125, 211, 252' },
  { rank: 2, numeral: 'II', name: 'Squire', minXp: 500, color: 'hsl(var(--success))', colorRgb: '52, 211, 153' },
  { rank: 3, numeral: 'III', name: 'Knight', minXp: 1500, color: 'hsl(var(--primary))', colorRgb: 'var(--theme-primary-rgb)' },
  { rank: 4, numeral: 'IV', name: 'Baron', minXp: 3000, color: 'rgb(var(--theme-challenge-rgb))', colorRgb: '167, 139, 250' },
  { rank: 5, numeral: 'V', name: 'Duke', minXp: 4500, color: 'rgb(var(--theme-challenge-rgb))', colorRgb: '244, 114, 182' },
  { rank: 6, numeral: 'VI', name: 'King', minXp: 5400, color: 'rgb(var(--theme-spark-rgb))', colorRgb: '251, 191, 36' },
]

export type RankInfo = {
  tier: RankTier
  nextTier: RankTier | null
  xp: number
  /** 0-100 toward the next tier (100 when at the top tier). */
  progressPct: number
}

export function rankForXp(xp: number): RankInfo {
  let tierIndex = 0
  for (let i = RANK_TIERS.length - 1; i >= 0; i -= 1) {
    if (xp >= RANK_TIERS[i].minXp) {
      tierIndex = i
      break
    }
  }
  const tier = RANK_TIERS[tierIndex]
  const nextTier = RANK_TIERS[tierIndex + 1] ?? null
  const progressPct = nextTier
    ? Math.min(100, Math.round(((xp - tier.minXp) / (nextTier.minXp - tier.minXp)) * 100))
    : 100

  return { tier, nextTier, xp, progressPct }
}

export function deriveRank(summary: HomeSummary): RankInfo {
  return rankForXp(summary.xp)
}

/** "2,340 / 3,000 XP" toward the next rank. */
export function rankProgressLabel({ xp, nextTier }: RankInfo): string {
  return nextTier
    ? `${xp.toLocaleString()} / ${nextTier.minXp.toLocaleString()} XP`
    : `${xp.toLocaleString()} XP · Max rank`
}

/**
 * The player's rank on any surface (map panel, workspace headers, profile).
 * Reads the cached home summary; `null` while it has not loaded yet.
 */
export function useRank(): RankInfo | null {
  const home = useQuery({
    queryKey: queryKeys.homeSummary,
    queryFn: homeSummaryApi.summary,
    staleTime: 5 * 60 * 1000,
  })
  return home.data ? deriveRank(home.data) : null
}


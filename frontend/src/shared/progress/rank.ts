import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '@/shared/api/queryKeys'
import { homeSummaryApi } from '@/shared/progress/homeSummaryApi'
import type { HomeSummary } from '@/shared/progress/types'

/**
 * Ranked ladder derived from the player's real, backend-computed Mastery
 * score (`HomeSummary.mastery`, a 0-100 blend of adventure solve depth and
 * challenge clear ratio — the same metric the Stats page's Mastery radar
 * axis shows).
 */
export type RankTier = {
  /** Ladder position, 1-based (Novice = 1). */
  rank: number
  /** Roman numeral shown in crests and pills ("IV"). */
  numeral: string
  name: string
  minScore: number
  /** Tier accent and optional RGB token for CSS rgba() vars. */
  color: string
  colorRgb: string
}

export const RANK_TIERS: RankTier[] = [
  { rank: 1, numeral: 'I', name: 'Novice', minScore: 0, color: 'rgb(var(--theme-spark-rgb))', colorRgb: '125, 211, 252' },
  { rank: 2, numeral: 'II', name: 'Spell Scribe', minScore: 15, color: 'hsl(var(--success))', colorRgb: '52, 211, 153' },
  { rank: 3, numeral: 'III', name: 'Glyph Weaver', minScore: 35, color: 'hsl(var(--primary))', colorRgb: 'var(--theme-primary-rgb)' },
  { rank: 4, numeral: 'IV', name: 'Arcane Adept', minScore: 60, color: 'rgb(var(--theme-challenge-rgb))', colorRgb: '167, 139, 250' },
  { rank: 5, numeral: 'V', name: 'Archon', minScore: 80, color: 'rgb(var(--theme-challenge-rgb))', colorRgb: '244, 114, 182' },
  { rank: 6, numeral: 'VI', name: 'Story Archon', minScore: 95, color: 'rgb(var(--theme-spark-rgb))', colorRgb: '251, 191, 36' },
]

export type RankInfo = {
  tier: RankTier
  nextTier: RankTier | null
  /** Total rank rating earned so far. */
  score: number
  /** Rating progress inside the current tier (e.g. 22/70 toward next). */
  ratingInTier: number
  ratingForNext: number
  /** 0-100 toward the next tier (100 when at the top tier). */
  progressPct: number
}

function rankScore(summary: HomeSummary): number {
  return summary.mastery
}

export function deriveRank(summary: HomeSummary): RankInfo {
  const score = rankScore(summary)
  let tierIndex = 0
  for (let i = RANK_TIERS.length - 1; i >= 0; i -= 1) {
    if (score >= RANK_TIERS[i].minScore) {
      tierIndex = i
      break
    }
  }
  const tier = RANK_TIERS[tierIndex]
  const nextTier = RANK_TIERS[tierIndex + 1] ?? null

  const ratingInTier = score - tier.minScore
  const ratingForNext = nextTier ? nextTier.minScore - tier.minScore : ratingInTier
  const progressPct = nextTier
    ? Math.min(100, Math.round((ratingInTier / ratingForNext) * 100))
    : 100

  return { tier, nextTier, score, ratingInTier, ratingForNext, progressPct }
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


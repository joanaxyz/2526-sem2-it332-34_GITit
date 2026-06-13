import type { HomeSummary } from '@/features/home/types'

/**
 * Medieval ranked ladder derived deterministically from home-summary data.
 *
 * Rank rating = 2 points per completed level + 1 point per first-attempt
 * star. Tiers are fixed thresholds, and the title is flavored with the
 * highest tower storey the player has touched.
 */
export type RankTier = {
  name: string
  minScore: number
  /** Tier accent (hex) and its rgb triplet for CSS rgba() vars. */
  color: string
  colorRgb: string
}

export const RANK_TIERS: RankTier[] = [
  { name: 'Apprentice', minScore: 0, color: '#7DD3FC', colorRgb: '125, 211, 252' },
  { name: 'Squire', minScore: 16, color: '#34D399', colorRgb: '52, 211, 153' },
  { name: 'Knight', minScore: 40, color: '#00F5D4', colorRgb: '0, 245, 212' },
  { name: 'Warden', minScore: 90, color: '#A78BFA', colorRgb: '167, 139, 250' },
  { name: 'Archmage', minScore: 160, color: '#F472B6', colorRgb: '244, 114, 182' },
]

export type RankInfo = {
  tier: RankTier
  nextTier: RankTier | null
  /** Total rank rating earned so far. */
  score: number
  /** Rating progress inside the current tier (e.g. 22/70 toward next). */
  ratingInTier: number
  ratingForNext: number
  /** 0–100 toward the next tier (100 when at the top tier). */
  progressPct: number
  /** Flavored title, e.g. "Knight of the Third Storey". */
  title: string
}

const STOREY_ORDINALS = [
  'First', 'Second', 'Third', 'Fourth', 'Fifth',
  'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth',
]

export function rankScore(summary: HomeSummary): number {
  return summary.counts.completed * 2 + summary.first_attempt_stars
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

  const touchedStoreys = Object.entries(summary.storey_kpis)
    .filter(([, kpis]) => kpis.scr.denominator > 0)
    .map(([storey]) => Number(storey))
    .filter((n) => Number.isFinite(n))
  const highestStorey = touchedStoreys.length > 0 ? Math.max(...touchedStoreys) : 0

  let title = tier.name
  if (!nextTier) {
    title = `${tier.name} of the Tower`
  } else if (highestStorey > 0) {
    const ordinal = STOREY_ORDINALS[Math.min(highestStorey, STOREY_ORDINALS.length) - 1]
    title = `${tier.name} of the ${ordinal} Storey`
  }

  return { tier, nextTier, score, ratingInTier, ratingForNext, progressPct, title }
}

/** Highest tower storey with at least one attempted scenario. */
export function highestStoreyTouched(summary: HomeSummary): number {
  const touched = Object.entries(summary.storey_kpis)
    .filter(([, kpis]) => kpis.scr.denominator > 0)
    .map(([storey]) => Number(storey))
    .filter((n) => Number.isFinite(n))
  return touched.length > 0 ? Math.max(...touched) : 0
}

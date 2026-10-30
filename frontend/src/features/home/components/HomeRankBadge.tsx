import { RANK_BADGE_LOADERS, resolvedRankBadge } from '@/features/home/utils/rankBadges'
import { useLazyImage } from '@/shared/utils/useLazyImage'
import type { RankTier } from '@/shared/progress/rank'

const MIN_RANK = 1
const MAX_RANK = 6

export function RankBadge({ tier, className }: { tier: RankTier; className?: string }) {
  const key = String(Math.max(MIN_RANK, Math.min(tier.rank, MAX_RANK)))
  // Home warms every badge before it opens; the lazy import covers any surface
  // that renders a badge without that gate.
  const resolved = resolvedRankBadge(key)
  const lazy = useLazyImage(resolved ? null : key, RANK_BADGE_LOADERS)
  const badge = resolved ?? lazy
  if (!badge) return null
  return (
    <img
      className={['home-rank-badge', className].filter(Boolean).join(' ')}
      src={badge}
      alt=""
      aria-hidden="true"
    />
  )
}

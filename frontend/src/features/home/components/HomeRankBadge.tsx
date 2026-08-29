import { useLazyImage } from '@/shared/utils/useLazyImage'
import type { RankTier } from '@/shared/progress/rank'

// A player has exactly one rank at a time, so each badge is imported lazily
// (only the needed variant loads) instead of bundling all six upfront.
const RANK_BADGE_LOADERS: Record<string, () => Promise<{ default: string }>> = {
  '1': () => import('@/assets/images/rank1.webp'),
  '2': () => import('@/assets/images/rank2.webp'),
  '3': () => import('@/assets/images/rank3.webp'),
  '4': () => import('@/assets/images/rank4.webp'),
  '5': () => import('@/assets/images/rank5.webp'),
  '6': () => import('@/assets/images/rank6.webp'),
}
const MIN_RANK = 1
const MAX_RANK = 6

export function RankBadge({ tier, className }: { tier: RankTier; className?: string }) {
  const clampedRank = Math.max(MIN_RANK, Math.min(tier.rank, MAX_RANK))
  const badge = useLazyImage(String(clampedRank), RANK_BADGE_LOADERS)
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

import rank1BadgeImage from '@/assets/images/rank1.png'
import rank2BadgeImage from '@/assets/images/rank2.png'
import rank3BadgeImage from '@/assets/images/rank3.png'
import rank4BadgeImage from '@/assets/images/rank4.png'
import rank5BadgeImage from '@/assets/images/rank5.png'
import rank6BadgeImage from '@/assets/images/rank6.png'
import type { RankTier } from '@/shared/progress/rank'

const RANK_BADGE_IMAGES = [
  rank1BadgeImage,
  rank2BadgeImage,
  rank3BadgeImage,
  rank4BadgeImage,
  rank5BadgeImage,
  rank6BadgeImage,
] as const

export function RankBadge({ tier, className }: { tier: RankTier; className?: string }) {
  const badge = RANK_BADGE_IMAGES[Math.max(0, Math.min(tier.rank - 1, RANK_BADGE_IMAGES.length - 1))]
  return (
    <img
      className={['home-rank-badge', className].filter(Boolean).join(' ')}
      src={badge}
      alt=""
      aria-hidden="true"
    />
  )
}

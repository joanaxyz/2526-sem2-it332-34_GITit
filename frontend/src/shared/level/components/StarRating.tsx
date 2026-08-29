import { Star } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

const STAR_VALUES = [1, 2, 3] as const

const SIZE_CLASS = {
  sm: 'size-3.5',
  md: 'size-5',
  lg: 'size-7',
} as const

export function StarRating({
  stars,
  size = 'md',
  className,
  label = 'Stars earned',
}: {
  stars: number
  size?: keyof typeof SIZE_CLASS
  className?: string
  label?: string
}) {
  const safeStars = Number.isFinite(stars) ? stars : 0
  const earned = Math.max(0, Math.min(3, Math.floor(safeStars)))

  return (
    <span
      role="img"
      aria-label={`${label}: ${earned} of 3`}
      className={cn('inline-flex items-center gap-0.5', size === 'lg' && 'gap-1.5', className)}
    >
      {STAR_VALUES.map((value) => (
        <Star
          key={value}
          aria-hidden="true"
          className={cn(
            SIZE_CLASS[size],
            value <= earned ? 'fill-primary text-primary' : 'text-border',
            size === 'lg' && value <= earned && 'drop-shadow-[0_0_6px_rgba(var(--theme-primary-rgb),0.6)]',
          )}
        />
      ))}
    </span>
  )
}

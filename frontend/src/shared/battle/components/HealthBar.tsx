import type { CSSProperties } from 'react'

import { cn } from '@/shared/utils/cn'

/**
 * Compositor-only resource bar: the fill is a `scaleX` transform with a left
 * origin, so draining never triggers layout. Used for monster HP (floating
 * above the actor) and Blue's mana plaque.
 */
export function HealthBar({
  value,
  max,
  variant = 'hp',
  className,
  style,
  'aria-label': ariaLabel,
}: {
  value: number
  max: number
  variant?: 'hp' | 'mana' | 'boss'
  className?: string
  style?: CSSProperties
  'aria-label'?: string
}) {
  const fraction = max > 0 ? Math.max(0, Math.min(1, value / max)) : 0
  const palette =
    variant === 'mana'
      ? 'from-cyan-300 via-primary to-fuchsia-400'
      : variant === 'boss'
        ? 'from-rose-400 via-red-500 to-orange-400'
        : 'from-lime-300 via-emerald-400 to-emerald-500'

  return (
    <div
      role="meter"
      aria-label={ariaLabel ?? (variant === 'mana' ? 'Mana' : 'Health')}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className={cn(
        'relative h-1.5 overflow-hidden rounded-full border border-white/20 bg-black/60',
        'shadow-[0_0_6px_rgba(0,0,0,0.45)]',
        className,
      )}
      style={style}
    >
      <div
        className={cn('h-full w-full origin-left rounded-full bg-gradient-to-r', palette)}
        style={{
          transform: `scaleX(${fraction})`,
          transition: 'transform 350ms cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      />
      {/* Hairline gloss so the bar reads on both bright and dark stage areas. */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-white/30" />
    </div>
  )
}

import type { CSSProperties } from 'react'

import { cn } from '@/shared/utils/cn'

/**
 * Compositor-only resource bar: the fill is a `scaleX` transform with a left
 * origin, so draining never triggers layout. Used for monster HP (floating
 * above the actor), Blue's HP, and any compact resource meters.
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
  variant?: 'hp' | 'mana' | 'boss' | 'battle' | 'battle-active'
  className?: string
  style?: CSSProperties
  'aria-label'?: string
}) {
  const fraction = max > 0 ? Math.max(0, Math.min(1, value / max)) : 0
  const palette =
    variant === 'battle-active'
      ? 'bg-primary'
      : variant === 'battle'
        ? 'bg-success'
      : variant === 'mana'
      ? 'bg-accent'
      : variant === 'boss'
        ? 'bg-destructive'
        : 'bg-primary'

  return (
    <div
      role="meter"
      aria-label={ariaLabel ?? (variant === 'mana' ? 'Mana' : 'Health')}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-valuenow={value}
      className={cn(
        'health-bar relative h-1.5 overflow-hidden rounded-full border border-primary/30 bg-primary/15',
        'shadow-[inset_0_0_6px_rgba(var(--theme-primary-rgb),0.18),0_0_6px_hsl(var(--background)/0.45)]',
        className,
      )}
      style={style}
    >
      <div
        className={cn('health-bar__fill h-full w-full origin-left rounded-full', palette)}
        style={{
          transformOrigin: 'left center',
          transform: `scaleX(${fraction})`,
          transition: 'transform 350ms cubic-bezier(0.22, 1, 0.36, 1)',
        }}
      />
      {/* Hairline gloss so the bar reads on both bright and dark stage areas. */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-foreground/30" />
    </div>
  )
}

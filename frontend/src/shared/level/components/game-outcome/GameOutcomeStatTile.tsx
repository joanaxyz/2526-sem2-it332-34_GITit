import type { CSSProperties, ComponentType, HTMLAttributes } from 'react'
import { Star } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

import { useCountUp } from './useCountUp'

export type GameOutcomeStatTileProps = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  accentColor: string
  animationDelay: number
  /** Shows a small "On target" chip beside the value. */
  targetMet?: boolean
  /** Optional glyph rendered in the accent chip; lucide icons satisfy this. */
  icon?: ComponentType<{ className?: string }>
  /** Neon icon art (battle-outcome assets); wins over `icon` when set. */
  iconSrc?: string
  compact?: boolean
  style?: HTMLAttributes<HTMLDivElement>['style']
}

/**
 * Animated scoreboard cell. Every cell reserves the same rows (header, value,
 * bar, caption) so values and captions line up across the scoreboard; the bar
 * track is drawn only when the stat has a denominator.
 */
export function GameOutcomeStatTile({
  label,
  numerator,
  denominator,
  suffix = '',
  helper,
  accentColor,
  animationDelay,
  targetMet,
  icon: Icon,
  iconSrc,
  style,
  compact = false,
}: GameOutcomeStatTileProps) {
  const animatedNum = useCountUp(numerator, 900, animationDelay + 50)
  const hasBar = denominator !== undefined && denominator > 0
  const fillPercent = hasBar ? Math.min(100, Math.round((numerator / denominator) * 100)) : 0

  return (
    <div
      className="game-outcome-stat-tile"
      style={{ animationDelay: `${animationDelay}ms`, '--stat-accent': accentColor, ...style } as CSSProperties}
    >
      <div className="game-outcome-stat-header">
        {iconSrc ? (
          <img className="game-outcome-stat-icon" src={iconSrc} alt="" aria-hidden="true" />
        ) : Icon ? (
          <span className="game-outcome-stat-chip" aria-hidden="true">
            <Icon className="size-3.5" />
          </span>
        ) : null}
        <span className="game-outcome-stat-label">{label}</span>
      </div>

      <div className="game-outcome-stat-tile-main">
        <div className="game-outcome-stat-number-row">
          <span className="game-outcome-stat-value">
            {animatedNum}{suffix}
          </span>
          {denominator !== undefined ? (
            <span className="game-outcome-stat-denom">/ {denominator}</span>
          ) : null}
          {targetMet ? (
            <span className="game-outcome-stat-target-chip">
              <Star className="size-2.5" fill="currentColor" aria-hidden="true" />
              On target
            </span>
          ) : null}
        </div>

        {!compact ? <div className={cn('game-outcome-stat-bar-track', !hasBar && 'is-empty')} aria-hidden="true">
          {hasBar ? (
            <div className="game-outcome-stat-bar-fill" style={{ transform: `scaleX(${fillPercent / 100})` }} />
          ) : null}
        </div> : null}

        {helper ? <p className="game-outcome-stat-caption">{helper}</p> : null}
      </div>
    </div>
  )
}

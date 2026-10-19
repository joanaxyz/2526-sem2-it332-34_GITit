import type { CSSProperties, ComponentType, HTMLAttributes } from 'react'
import { CheckCircle2 } from 'lucide-react'

import { useCountUp } from './useCountUp'

export type GameOutcomeStatTileProps = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  accentColor: string
  animationDelay: number
  /** Shows a small "Target met" chip in the header row. */
  targetMet?: boolean
  /** Optional glyph rendered in the accent chip; lucide icons satisfy this. */
  icon?: ComponentType<{ className?: string }>
  /** Neon icon art (battle-outcome assets); wins over `icon` when set. */
  iconSrc?: string
  style?: HTMLAttributes<HTMLDivElement>['style']
}

/**
 * Animated stat tile. All three tiles maintain identical height via
 * min-height on `.game-outcome-stat-tile`, and a progress-bar slot is
 * always reserved (empty track when there is no denominator) so numbers
 * and captions stay horizontally aligned across the row.
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
}: GameOutcomeStatTileProps) {
  const animatedNum = useCountUp(numerator, 900, animationDelay + 50)
  const hasBar = denominator !== undefined && denominator > 0
  const fillPercent = hasBar ? Math.min(100, Math.round((numerator / denominator) * 100)) : 0

  return (
    <div
      className="game-outcome-stat-tile"
      style={{ animationDelay: `${animationDelay}ms`, ...style } as CSSProperties}
    >
      {/* Header: icon + label + optional target-met chip */}
      <div className="game-outcome-stat-header">
        {iconSrc ? (
          <img className="game-outcome-stat-icon" src={iconSrc} alt="" aria-hidden="true" />
        ) : Icon ? (
          <span
            className="game-outcome-stat-chip"
            style={{ color: accentColor, background: `color-mix(in srgb, ${accentColor} 18%, transparent)` }}
          >
            <Icon className="size-3.5" />
          </span>
        ) : null}
        <span className="game-outcome-stat-label">{label}</span>
        {targetMet ? (
          <span className="game-outcome-stat-target-chip">
            <CheckCircle2 className="size-2.5" />
            Target
          </span>
        ) : null}
      </div>

      {/* Main content */}
      <div className="game-outcome-stat-tile-main">
        {/* Big number */}
        <div className="game-outcome-stat-number-row">
          <span className="game-outcome-stat-value" style={{ color: accentColor }}>
            {animatedNum}{suffix}
          </span>
          {denominator !== undefined ? (
            <span className="game-outcome-stat-denom">/ {denominator}</span>
          ) : null}
        </div>

        {/* Progress bar slot — always reserves height; empty if no denominator */}
        <div className="game-outcome-stat-bar-track">
          {hasBar ? (
            <div
              className="game-outcome-stat-bar-fill"
              style={{
                transform: `scaleX(${fillPercent / 100})`,
                background: accentColor,
                boxShadow: `0 0 10px color-mix(in srgb, ${accentColor} 70%, transparent)`,
              }}
            />
          ) : null}
        </div>

        {/* Caption */}
        <p className="game-outcome-stat-caption">{helper}</p>
      </div>
    </div>
  )
}

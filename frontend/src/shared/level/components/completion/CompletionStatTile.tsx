import type { CSSProperties, ComponentType } from 'react'

import { useCountUp } from './useCountUp'

export type CompletionStatTileProps = {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  accentColor: string
  animationDelay: number
  /** Optional glyph rendered in the accent chip; lucide icons satisfy this. */
  icon?: ComponentType<{ className?: string }>
}

/**
 * Animated stat tile shared by the challenge and adventure completion modals.
 * The numerator counts up; an optional denominator renders a progress bar so the
 * "X / target" stats read at a glance instead of as plain text.
 */
export function CompletionStatTile({
  label,
  numerator,
  denominator,
  suffix = '',
  helper,
  accentColor,
  animationDelay,
  icon: Icon,
}: CompletionStatTileProps) {
  const animatedNum = useCountUp(numerator, 900, animationDelay + 50)
  const hasBar = denominator !== undefined && denominator > 0
  const fillPercent = hasBar ? Math.min(100, Math.round((numerator / denominator) * 100)) : 0

  return (
    <div
      className="completion-stat-tile group relative overflow-hidden rounded-xl border border-border/50 p-3 transition-all duration-200 hover:-translate-y-0.5"
      style={
        {
          animationDelay: `${animationDelay}ms`,
          background: `linear-gradient(150deg, color-mix(in srgb, ${accentColor} 14%, transparent) 0%, color-mix(in srgb, ${accentColor} 3%, transparent) 55%, transparent 100%)`,
          boxShadow: `inset 0 0 0 1px color-mix(in srgb, ${accentColor} 24%, transparent)`,
        } as CSSProperties
      }
    >
      {/* Soft accent bloom in the corner - pure eye-candy. */}
      <div
        aria-hidden
        className="pointer-events-none absolute -right-5 -top-6 size-16 rounded-full opacity-30 blur-2xl transition-opacity duration-200 group-hover:opacity-60"
        style={{ background: accentColor }}
      />

      <div className="relative flex items-center justify-between gap-2">
        <span className="font-mono text-[0.6rem] uppercase tracking-[0.14em] text-muted-foreground">{label}</span>
        {Icon ? (
          <span
            className="grid size-6 shrink-0 place-items-center rounded-md"
            style={{ color: accentColor, background: `color-mix(in srgb, ${accentColor} 18%, transparent)` }}
          >
            <Icon className="size-3.5" />
          </span>
        ) : null}
      </div>

      <div className="relative mt-2 flex items-baseline gap-1">
        <span className="text-2xl font-extrabold tracking-tight tabular-nums" style={{ color: accentColor }}>
          {animatedNum}
          {suffix}
        </span>
        {denominator !== undefined ? (
          <span className="text-sm font-semibold text-muted-foreground">/ {denominator}</span>
        ) : null}
      </div>

      {hasBar ? (
        <div className="relative mt-2 h-1.5 overflow-hidden rounded-full bg-border/40">
          <div
            className="h-full rounded-full transition-[width] duration-700 ease-out"
            style={{
              width: `${fillPercent}%`,
              background: accentColor,
              boxShadow: `0 0 10px color-mix(in srgb, ${accentColor} 70%, transparent)`,
            }}
          />
        </div>
      ) : null}

      <div className="relative mt-1.5 text-xs leading-snug text-muted-foreground">{helper}</div>
    </div>
  )
}

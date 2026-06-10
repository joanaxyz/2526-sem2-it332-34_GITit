import type { CSSProperties } from 'react'

import { useCountUp } from './useCountUp'

/**
 * Animated stat tile shared by the challenge and adventure completion modals.
 * The numerator counts up; an optional denominator/suffix renders inline.
 */
export function CompletionStatTile({
  label,
  numerator,
  denominator,
  suffix = '',
  helper,
  accentColor,
  animationDelay,
}: {
  label: string
  numerator: number
  denominator?: number
  suffix?: string
  helper: string
  accentColor: string
  animationDelay: number
}) {
  const animatedNum = useCountUp(numerator, 900, animationDelay + 50)

  return (
    <div
      className="completion-stat-tile rounded-lg border border-border/60 bg-card/80 p-2.5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_4px_16px_rgba(0,245,212,0.12)]"
      style={
        {
          animationDelay: `${animationDelay}ms`,
          borderTopColor: accentColor,
          borderTopWidth: '2px',
        } as CSSProperties
      }
    >
      <div className="font-mono text-[0.6rem] uppercase tracking-[0.12em] text-muted-foreground">{label}</div>
      <div className="mt-1.5 text-lg font-extrabold tracking-tight">
        {animatedNum}
        {suffix}
        {denominator !== undefined ? `/${denominator}` : ''}
      </div>
      <div className="mt-0.5 text-xs text-muted-foreground">{helper}</div>
    </div>
  )
}

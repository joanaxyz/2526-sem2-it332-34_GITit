import { Fragment } from 'react'
import type { ReactNode } from 'react'
import { GaugeCircle } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

export type BudgetMeterRow = { label: string; value: ReactNode }

/**
 * Shared shell for the command-budget meters on both level surfaces: a
 * compact `used / max` button with a thin progress underline and a hover/focus
 * tooltip breakdown. It owns only the markup and interaction - every surface
 * difference (labels, colors, tooltip rows, copy) arrives as data, so the
 * challenge and adventure meters stay distinct in wording while sharing one
 * structure. Callers compute the danger state and progress color themselves.
 */
export function BudgetMeter({
  id,
  ariaLabel,
  danger,
  compactLabel,
  used,
  max,
  desktopCount,
  progressPercent,
  progressColorClassName,
  buttonClassName,
  tooltipClassName,
  tooltipTitle,
  tooltipState,
  tooltipStateDanger,
  rows,
  footer,
}: {
  id: string
  ariaLabel: string
  /** Drives the destructive accent on the icon, label, and tooltip state. */
  danger: boolean
  /** Short uppercase label shown only at the widest breakpoint. */
  compactLabel: string
  used: number
  max: number
  /** The `used / max` text shown at >= sm (surfaces phrase it differently). */
  desktopCount: ReactNode
  progressPercent: number
  /** Extra class(es) layered over the base `bg-primary` fill (e.g. a danger or
   *  over-target color). */
  progressColorClassName?: string
  /** Extra class(es) on the button (e.g. a surface-specific max-width). */
  buttonClassName?: string
  /** Extra class(es) on the tooltip (e.g. its width). */
  tooltipClassName?: string
  tooltipTitle: string
  tooltipState: ReactNode
  tooltipStateDanger: boolean
  rows: BudgetMeterRow[]
  footer: ReactNode
}) {
  return (
    <div className="group relative min-w-0 shrink-0">
      <button
        type="button"
        className={cn(
          'relative flex h-8 items-center gap-2 overflow-hidden rounded-md border border-transparent px-2.5 text-left text-xs transition-colors',
          'bg-transparent text-muted-foreground hover:border-border/80 hover:bg-secondary/35 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60',
          danger && 'text-destructive hover:text-destructive',
          buttonClassName,
        )}
        aria-describedby={id}
        aria-label={ariaLabel}
      >
        <GaugeCircle className={cn('hidden size-4 shrink-0 text-primary sm:block', danger && 'text-destructive')} />
        <span className="hidden shrink-0 text-[10px] font-semibold uppercase tracking-normal text-muted-foreground 2xl:inline">
          {compactLabel}
        </span>
        <span className="shrink-0 font-mono font-semibold text-foreground sm:hidden">
          {used}/{max}
        </span>
        <span className="hidden shrink-0 font-mono font-semibold text-foreground sm:inline">{desktopCount}</span>
        <span className="absolute inset-x-2 bottom-0 h-px overflow-hidden rounded-full bg-secondary">
          <span
            className={cn('block h-full rounded-full bg-primary transition-all', progressColorClassName)}
            style={{ width: `${progressPercent}%` }}
          />
        </span>
      </button>
      <div
        id={id}
        className={cn(
          'pointer-events-none absolute right-0 top-full z-50 mt-2 hidden rounded-md border border-border bg-card p-3 text-xs text-card-foreground shadow-xl group-hover:block group-focus-within:block',
          tooltipClassName,
        )}
      >
        <div className="flex items-center justify-between gap-3">
          <span className="font-semibold text-foreground">{tooltipTitle}</span>
          <span className={cn('font-mono font-semibold', tooltipStateDanger ? 'text-destructive' : 'text-primary')}>
            {tooltipState}
          </span>
        </div>
        <dl className="mt-3 grid grid-cols-[1fr_auto] gap-x-4 gap-y-2 text-muted-foreground">
          {rows.map((row) => (
            <Fragment key={row.label}>
              <dt>{row.label}</dt>
              <dd className="font-mono text-foreground">{row.value}</dd>
            </Fragment>
          ))}
        </dl>
        <p className="mt-3 border-t border-border pt-2 text-muted-foreground">{footer}</p>
      </div>
    </div>
  )
}

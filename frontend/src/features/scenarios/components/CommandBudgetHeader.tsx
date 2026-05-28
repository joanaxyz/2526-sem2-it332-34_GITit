import { GaugeCircle } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { cn } from '@/shared/utils/cn'

export function CommandBudgetHeader({ session }: { session: ScenarioSession }) {
  const {
    counted_action_total: used,
    minimum_counted_commands: target,
    maximum_counted_commands: max,
    remaining_counted_commands: remaining,
    max_reached: maxReached,
    non_counted_diagnostic_total: diagnostics,
  } = session.counts
  const failed = session.status === 'failed'
  const progress = max > 0 ? Math.min(100, Math.round((used / max) * 100)) : maxReached ? 100 : 0
  const stateLabel = failed ? 'Failed' : `${remaining} left`

  return (
    <div className="group relative min-w-0 shrink-0">
      <button
        type="button"
        className={cn(
          'relative flex h-8 max-w-[22rem] items-center gap-2 overflow-hidden rounded-md border border-transparent px-2.5 text-left text-xs transition-colors',
          'bg-transparent text-muted-foreground hover:border-border/80 hover:bg-secondary/35 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60',
          failed && 'text-destructive hover:text-destructive',
        )}
        aria-describedby={`command-budget-${session.id}`}
        aria-label={`Command Budget: Actions ${used} of ${max}, target ${target}, ${stateLabel}`}
      >
        <GaugeCircle className={cn('hidden size-4 shrink-0 text-primary sm:block', failed && 'text-destructive')} />
        <span className="hidden shrink-0 text-[10px] font-semibold uppercase tracking-normal text-muted-foreground 2xl:inline">
          Command Budget
        </span>
        <span className="shrink-0 font-mono font-semibold text-foreground sm:hidden">
          {used}/{max}
        </span>
        <span className="hidden shrink-0 font-mono font-semibold text-foreground sm:inline">
          Actions {used} / {max}
        </span>
        <span className="hidden shrink-0 text-muted-foreground xl:inline">Target {target}</span>
        <span className={cn('hidden shrink-0 font-medium xl:inline', failed ? 'text-destructive' : 'text-primary')}>
          {stateLabel}
        </span>
        <span className="absolute inset-x-2 bottom-0 h-px overflow-hidden rounded-full bg-secondary">
          <span
            className={cn('block h-full rounded-full bg-primary transition-all', failed && 'bg-destructive')}
            style={{ width: `${progress}%` }}
          />
        </span>
      </button>
      <div
        id={`command-budget-${session.id}`}
        className="pointer-events-none absolute right-0 top-full z-50 mt-2 hidden w-72 rounded-md border border-border bg-card p-3 text-xs text-card-foreground shadow-xl group-hover:block group-focus-within:block"
      >
        <div className="flex items-center justify-between gap-3">
          <span className="font-semibold text-foreground">Command Budget</span>
          <span className={cn('font-mono font-semibold', failed ? 'text-destructive' : 'text-primary')}>
            {failed ? 'Failed' : stateLabel}
          </span>
        </div>
        <dl className="mt-3 grid grid-cols-[1fr_auto] gap-x-4 gap-y-2 text-muted-foreground">
          <dt>Counted actions used</dt>
          <dd className="font-mono text-foreground">{used}</dd>
          <dt>Target/minimum command count</dt>
          <dd className="font-mono text-foreground">{target}</dd>
          <dt>Maximum/fail limit</dt>
          <dd className="font-mono text-foreground">{max}</dd>
          <dt>Remaining actions</dt>
          <dd className="font-mono text-foreground">{remaining}</dd>
          <dt>Session status</dt>
          <dd className="font-mono text-foreground">{session.status}</dd>
        </dl>
        <p className="mt-3 border-t border-border pt-2 text-muted-foreground">
          Diagnostic commands do not count. You have used {diagnostics} diagnostic command{diagnostics === 1 ? '' : 's'}.
          {' '}You fail when all {max} counted actions are used and the repository has not yet reached the scenario target.
        </p>
      </div>
    </div>
  )
}

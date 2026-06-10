import { GaugeCircle } from 'lucide-react'

import type { AdventureAttempt } from '@/features/command-adventures/types'
import { cn } from '@/shared/utils/cn'

/**
 * Compact counted-command meter for an adventure attempt: how many counted
 * commands have been used against the min target and the max budget, with a
 * hover breakdown. Counterpart to the challenge `CommandBudgetHeader`.
 */
export function AdventureCommandBudget({ attempt }: { attempt: AdventureAttempt }) {
  const { min_counted_commands: min, max_counted_commands: max } = attempt.command_budget
  const used = attempt.counts.counted_command_count
  const hints = attempt.counts.hint_count
  const remaining = Math.max(max - used, 0)
  const progress = max > 0 ? Math.min(100, Math.round((used / max) * 100)) : 0
  const atLimit = used >= max
  const overTarget = used > min

  return (
    <div className="group relative min-w-0 shrink-0">
      <button
        type="button"
        className={cn(
          'relative flex h-8 items-center gap-2 overflow-hidden rounded-md border border-transparent px-2.5 text-left text-xs transition-colors',
          'bg-transparent text-muted-foreground hover:border-border/80 hover:bg-secondary/35 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60',
          atLimit && 'text-destructive hover:text-destructive',
        )}
        aria-describedby={`adventure-budget-${attempt.id}`}
        aria-label={`Commands used ${used} of ${max}, target ${min}, ${remaining} remaining`}
      >
        <GaugeCircle className={cn('hidden size-4 shrink-0 text-primary sm:block', atLimit && 'text-destructive')} />
        <span className="hidden shrink-0 text-[10px] font-semibold uppercase tracking-normal text-muted-foreground 2xl:inline">
          Commands
        </span>
        <span className="shrink-0 font-mono font-semibold text-foreground sm:hidden">
          {used}/{max}
        </span>
        <span className="hidden shrink-0 font-mono font-semibold text-foreground sm:inline">
          {used} / {max}
        </span>
        <span className="absolute inset-x-2 bottom-0 h-px overflow-hidden rounded-full bg-secondary">
          <span
            className={cn(
              'block h-full rounded-full bg-primary transition-all',
              overTarget && 'bg-accent',
              atLimit && 'bg-destructive',
            )}
            style={{ width: `${progress}%` }}
          />
        </span>
      </button>
      <div
        id={`adventure-budget-${attempt.id}`}
        className="pointer-events-none absolute right-0 top-full z-50 mt-2 hidden w-64 rounded-md border border-border bg-card p-3 text-xs text-card-foreground shadow-xl group-hover:block group-focus-within:block"
      >
        <div className="flex items-center justify-between gap-3">
          <span className="font-semibold text-foreground">Command budget</span>
          <span className={cn('font-mono font-semibold', atLimit ? 'text-destructive' : 'text-primary')}>
            {remaining} left
          </span>
        </div>
        <dl className="mt-3 grid grid-cols-[1fr_auto] gap-x-4 gap-y-2 text-muted-foreground">
          <dt>Counted commands used</dt>
          <dd className="font-mono text-foreground">{used}</dd>
          <dt>Target (par)</dt>
          <dd className="font-mono text-foreground">{min}</dd>
          <dt>Maximum / limit</dt>
          <dd className="font-mono text-foreground">{max}</dd>
          <dt>Hints used</dt>
          <dd className="font-mono text-foreground">{hints}</dd>
        </dl>
        <p className="mt-3 border-t border-border pt-2 text-muted-foreground">
          Solve in around {min} command{min === 1 ? '' : 's'} for full efficiency. Diagnostic commands do not count
          toward the {max} you are allowed.
        </p>
      </div>
    </div>
  )
}

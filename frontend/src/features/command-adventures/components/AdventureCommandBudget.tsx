import { BudgetMeter } from '@/shared/level/components/BudgetMeter'
import type { AdventureAttempt } from '@/features/command-adventures/types'

/**
 * Compact counted-command meter for an adventure attempt: how many counted
 * commands have been used against the min target and the max budget, with a
 * hover breakdown. Counterpart to the challenge `CommandBudgetHeader`; both
 * render through the shared `BudgetMeter` shell.
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
    <BudgetMeter
      id={`adventure-budget-${attempt.id}`}
      ariaLabel={`Commands used ${used} of ${max}, target ${min}, ${remaining} remaining`}
      danger={atLimit}
      compactLabel="Commands"
      used={used}
      max={max}
      desktopCount={`${used} / ${max}`}
      progressPercent={progress}
      progressColorClassName={atLimit ? 'bg-destructive' : overTarget ? 'bg-accent' : undefined}
      tooltipClassName="w-64"
      tooltipTitle="Command budget"
      tooltipState={`${remaining} left`}
      tooltipStateDanger={atLimit}
      rows={[
        { label: 'Counted commands used', value: used },
        { label: 'Target (par)', value: min },
        { label: 'Maximum / limit', value: max },
        { label: 'Hints used', value: hints },
      ]}
      footer={
        <>
          Solve in around {min} command{min === 1 ? '' : 's'} for full efficiency. Diagnostic commands do
          not count toward the {max} you are allowed.
        </>
      }
    />
  )
}

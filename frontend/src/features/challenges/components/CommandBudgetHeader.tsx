import { BudgetMeter } from '@/shared/level/components/BudgetMeter'
import type { ChallengeRun } from '@/shared/level/types'

export function CommandBudgetHeader({ run }: { run: ChallengeRun }) {
  const {
    counted_action_total: used,
    minimum_counted_commands: target,
    maximum_counted_commands: max,
    remaining_counted_commands: remaining,
    max_reached: maxReached,
    non_counted_diagnostic_total: diagnostics,
  } = run.counts
  const failed = run.status === 'failed'
  const progress = max > 0 ? Math.min(100, Math.round((used / max) * 100)) : maxReached ? 100 : 0
  const stateLabel = failed ? 'Failed' : `${remaining} left`

  return (
    <BudgetMeter
      id={`command-budget-${run.id}`}
      ariaLabel={`Command Budget: Actions ${used} of ${max}, target ${target}, ${stateLabel}`}
      danger={failed}
      compactLabel="Command Budget"
      used={used}
      max={max}
      desktopCount={`Actions ${used} / ${max}`}
      progressPercent={progress}
      progressColorClassName={failed ? 'bg-destructive' : undefined}
      buttonClassName="max-w-[22rem]"
      tooltipClassName="w-72"
      tooltipTitle="Command Budget"
      tooltipState={stateLabel}
      tooltipStateDanger={failed}
      rows={[
        { label: 'Counted actions used', value: used },
        { label: 'Target/minimum command count', value: target },
        { label: 'Maximum/fail limit', value: max },
        { label: 'Remaining actions', value: remaining },
        { label: 'Session status', value: run.status },
      ]}
      footer={
        <>
          Diagnostic commands do not count. You have used {diagnostics} diagnostic command
          {diagnostics === 1 ? '' : 's'}. You fail when all {max} counted actions are used and the
          repository has not yet reached the scenario target.
        </>
      }
    />
  )
}

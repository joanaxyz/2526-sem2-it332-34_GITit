import { GaugeCircle } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Card } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function CommandCounter({ session }: { session: ScenarioSession }) {
  const used = session.counts.counted_action_total
  const max = session.policy.max_counted_commands
  const pct = max ? Math.round((used / max) * 100) : 0
  return (
    <Card className="p-3 shadow-none">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-semibold">
          <GaugeCircle className="size-5 text-primary" />
          Action commands
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-2">
            <div className="text-xs text-muted-foreground">Target</div>
            <Badge variant="default">{session.policy.min_counted_commands}</Badge>
          </div>
          <div className="mt-1 font-mono text-sm font-semibold">
            {used} used — {session.counts.remaining_counted_commands} left
          </div>
        </div>
      </div>
      <ProgressBar value={pct} className="mt-2" />
      <div className="mt-2 grid grid-cols-1 gap-2 text-xs text-muted-foreground">
        <span
          title={
            session.policy.non_counted_patterns.length
              ? `Inspection commands: ${session.policy.non_counted_patterns.join(', ')}`
              : 'No inspection commands listed'
          }
          className="cursor-help underline decoration-dotted"
        >
          Free inspections: {session.policy.non_counted_patterns.length}
        </span>
      </div>
    </Card>
  )
}

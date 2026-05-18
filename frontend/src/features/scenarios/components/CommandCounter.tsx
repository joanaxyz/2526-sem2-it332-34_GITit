import { GaugeCircle } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Card } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function CommandCounter({ session }: { session: ScenarioSession }) {
  const used = session.counts.counted_action_total
  const max = session.policy.max_counted_commands
  const pct = max ? Math.round((used / max) * 100) : 0
  return (
    <Card className="p-4 shadow-none">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-semibold">
          <GaugeCircle className="size-5 text-primary" />
          Counted commands
        </div>
        <div className="font-mono text-sm">
          {session.counts.remaining_counted_commands} left
        </div>
      </div>
      <ProgressBar value={pct} className="mt-3" />
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
        <span>CAR threshold: {session.policy.min_counted_commands}</span>
        <span>Diagnostics: {session.policy.non_counted_patterns.length}</span>
      </div>
    </Card>
  )
}

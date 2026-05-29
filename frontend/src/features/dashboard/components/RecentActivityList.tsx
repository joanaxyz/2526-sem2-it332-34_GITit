import { useEffect, useState } from 'react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

function useCountUp(target: number, duration = 900): number {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === 0) { setValue(0); return }
    const startTime = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - startTime) / duration, 1)
      setValue(Math.round((1 - Math.pow(1 - p, 3)) * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [target, duration])
  return value
}

type OutcomeStyle = { bg: string; border: string; numberColor: string }

const OUTCOME_STYLES: Record<string, OutcomeStyle> = {
  Started:         { bg: 'rgba(0,245,212,0.07)',   border: 'rgba(0,245,212,0.2)',   numberColor: '#00F5D4' },
  Completed:       { bg: 'rgba(34,197,94,0.07)',   border: 'rgba(34,197,94,0.22)',  numberColor: 'rgb(74,222,128)' },
  Failed:          { bg: 'rgba(239,68,68,0.06)',   border: 'rgba(239,68,68,0.2)',   numberColor: 'rgb(248,113,113)' },
  Abandoned:       { bg: 'rgba(100,116,139,0.07)', border: 'rgba(100,116,139,0.18)',numberColor: 'rgb(148,163,184)' },
  'Review sessions': { bg: 'rgba(59,130,246,0.07)', border: 'rgba(59,130,246,0.2)', numberColor: 'rgb(96,165,250)' },
}

function Outcome({ label, value }: { label: string; value: number }) {
  const count = useCountUp(value)
  const style = OUTCOME_STYLES[label] ?? OUTCOME_STYLES['Abandoned']
  return (
    <div
      className="rounded-md p-3 transition-all duration-200 hover:-translate-y-0.5"
      style={{ background: style.bg, border: `1px solid ${style.border}` }}
    >
      <div className="text-xs text-muted-foreground">{label}</div>
      <div
        className="mt-1 text-2xl font-extrabold"
        style={{ color: style.numberColor }}
      >
        {count}
      </div>
    </div>
  )
}

export function RecentActivityList({ summary }: { summary: DashboardSummary }) {
  return (
    <Card className="dash-card-hover" style={{ borderLeft: '2px solid rgba(0,245,212,0.3)' }}>
      <CardHeader>
        <CardTitle>Session outcomes</CardTitle>
        <CardDescription>Primary and review activity split stays visible.</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 text-sm">
        <Outcome label="Started" value={summary.counts.started} />
        <Outcome label="Completed" value={summary.counts.completed} />
        <Outcome label="Failed" value={summary.counts.failed} />
      </CardContent>
    </Card>
  )
}

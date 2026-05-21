import { Activity, CheckCircle2, Crosshair, GitPullRequest, RotateCcw, ShieldCheck } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent } from '@/shared/components/Card'

const metricMap = [
  ['scr', 'Scenario completion', CheckCircle2],
  ['car', 'Command accuracy', Crosshair],
  ['hlcr', 'Hard completion', ShieldCheck],
  ['rta', 'Retry transfer', GitPullRequest],
  ['sar', 'Abandonment', RotateCcw],
  ['review_scr', 'Review completion', Activity],
] as const

export function ProgressSummaryCards({ summary }: { summary: DashboardSummary }) {
  return (
    <section className="grid grid-cols-3 gap-3 xl:grid-cols-6 max-lg:grid-cols-2">
      {metricMap.map(([key, label, Icon]) => {
        const metric = summary.kpis[key]
        const detail = key === 'car'
          ? `${metric.denominator} completed attempts`
          : `${metric.numerator}/${metric.denominator} attempts`
        return (
          <Card key={key} className="shadow-none">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted-foreground">{label}</p>
                  <p className="mt-2 text-2xl font-extrabold tracking-tight">{metric.value === null ? 'No data' : `${metric.value}%`}</p>
                </div>
                <Icon className="size-5 text-primary" />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                {metric.denominator ? detail : 'Waiting for practice'}
              </p>
            </CardContent>
          </Card>
        )
      })}
    </section>
  )
}

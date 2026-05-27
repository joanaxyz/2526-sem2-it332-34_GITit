import { Gauge, ShieldCheck, GitPullRequest } from 'lucide-react'

import type { DashboardSummary, RateMetric } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'

type ModuleKey = '1' | '2' | '3' | '4'

const MODULE_KEYS: ModuleKey[] = ['1', '2', '3', '4']

export function ModulePerformanceCard({ summary }: { summary: DashboardSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="size-5 text-primary" />
          Module hard + retry performance
        </CardTitle>
        <CardDescription className="flex flex-wrap items-center gap-3">
          <span>Overall Hard completion: {formatPercent(summary.kpis.hlcr.value)}</span>
          <span>Overall Retry transfer: {formatPercent(summary.kpis.rta.value)}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {MODULE_KEYS.map((moduleKey) => {
          const moduleKpis = summary.module_kpis[moduleKey]
          return (
            <div key={moduleKey} className="rounded-md border border-border bg-secondary/40 p-3">
              <div className="mb-3 text-sm font-semibold">Module {moduleKey}</div>
              <div className="grid grid-cols-2 gap-3 max-md:grid-cols-1">
                <MetricMeter label="Hard completion" icon={ShieldCheck} metric={moduleKpis.hlcr} />
                <MetricMeter label="Retry transfer" icon={GitPullRequest} metric={moduleKpis.rta} />
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

function MetricMeter({
  label,
  icon: Icon,
  metric,
}: {
  label: string
  icon: typeof ShieldCheck
  metric: RateMetric
}) {
  const value = metric.value ?? 0
  return (
    <div className="rounded-md border border-border/70 bg-card p-3">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Icon className="size-4 text-primary" />
          <span className="text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground">{label}</span>
        </div>
        <span className="text-sm font-bold">{formatPercent(metric.value)}</span>
      </div>
      <ProgressBar value={value} className="mt-2 h-1.5" />
      <p className="mt-2 text-xs text-muted-foreground">
        {metric.denominator ? `${metric.numerator}/${metric.denominator} attempts` : 'Waiting for practice'}
      </p>
    </div>
  )
}

function formatPercent(value: number | null) {
  return value === null ? 'No data' : `${value}%`
}

import { RotateCcw } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function RetryTrendCard({ summary }: { summary: DashboardSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RotateCcw className="size-5 text-primary" />
          Retry trends
        </CardTitle>
        <CardDescription>Derived from completed, failed, and abandoned session logs.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {summary.retry_trends.length ? (
          summary.retry_trends.map((trend) => (
            <div key={trend.scenario_id} className="rounded-md border border-border bg-secondary/50 p-3">
              <div className="font-semibold">{trend.scenario_title}</div>
              <div className="mt-1 text-xs text-muted-foreground">{trend.label}</div>
            </div>
          ))
        ) : (
          <p className="text-sm text-muted-foreground">No trend available.</p>
        )}
      </CardContent>
    </Card>
  )
}

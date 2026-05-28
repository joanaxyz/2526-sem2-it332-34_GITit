import { RotateCcw } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function RetryTrendCard({ summary }: { summary: DashboardSummary }) {
  return (
    <Card className="dash-card-hover" style={{ borderLeft: '2px solid rgba(0,245,212,0.3)' }}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RotateCcw className="size-5 text-primary" />
          Retry trends
        </CardTitle>
        <CardDescription>Derived from completed, failed, and abandoned session logs.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {summary.retry_trends.length ? (
          summary.retry_trends.map((trend) => {
            const pct = trend.attempts > 0
              ? Math.min(Math.round((trend.retries / trend.attempts) * 100), 100)
              : 0
            return (
              <div
                key={trend.scenario_id}
                className="rounded-md p-3 transition-all duration-200 hover:-translate-y-0.5"
                style={{
                  background: 'rgba(0,180,216,0.06)',
                  border: '1px solid rgba(0,180,216,0.18)',
                  borderTop: '1px solid rgba(0,245,212,0.2)',
                }}
              >
                <div className="font-semibold">{trend.scenario_title}</div>
                <div className="mt-1 text-xs text-muted-foreground">{trend.label}</div>
                {/* Retry ratio bar */}
                <div
                  className="mt-2 h-1 overflow-hidden rounded-full"
                  style={{ background: 'rgba(0,180,216,0.12)' }}
                >
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${pct}%`,
                      background: 'linear-gradient(to right, rgba(0,245,212,0.65), rgba(0,180,216,0.8))',
                      boxShadow: pct > 0 ? '0 0 4px rgba(0,245,212,0.4)' : 'none',
                      transition: 'width 0.7s cubic-bezier(0.16, 1, 0.3, 1)',
                    }}
                  />
                </div>
                <div className="mt-1 text-[10px] text-muted-foreground/50">
                  {trend.retries} retries / {trend.attempts} attempts
                </div>
              </div>
            )
          })
        ) : (
          <p className="text-sm text-muted-foreground">No trend available.</p>
        )}
      </CardContent>
    </Card>
  )
}

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function RecentActivityList({ summary }: { summary: DashboardSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Session outcomes</CardTitle>
        <CardDescription>Primary and review activity split stays visible.</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-3 text-sm">
        <Outcome label="Started" value={summary.counts.started} />
        <Outcome label="Completed" value={summary.counts.completed} />
        <Outcome label="Failed" value={summary.counts.failed} />
        <Outcome label="Abandoned" value={summary.counts.abandoned} />
        <Outcome label="Review sessions" value={summary.counts.review_started} />
      </CardContent>
    </Card>
  )
}

function Outcome({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-secondary/50 p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 text-2xl font-extrabold">{value}</div>
    </div>
  )
}

import type { RateMetric } from '@/features/dashboard/types'
import { Card, CardContent } from '@/shared/components/Card'

export function KpiIndicatorCard({ label, metric }: { label: string; metric: RateMetric }) {
  return (
    <Card className="shadow-none">
      <CardContent className="p-4">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="mt-1 text-2xl font-extrabold">{metric.value === null ? 'No data' : `${metric.value}%`}</div>
      </CardContent>
    </Card>
  )
}

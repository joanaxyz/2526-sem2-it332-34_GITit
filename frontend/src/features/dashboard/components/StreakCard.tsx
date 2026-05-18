import { Flame } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function StreakCard({ summary }: { summary: DashboardSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="size-5 text-primary" />
          Streak
        </CardTitle>
        <CardDescription>Updated on the first completed scenario session per day.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-extrabold">{summary.streak.current}</div>
        <div className="mt-3 flex flex-wrap gap-2">
          <Badge variant="default">Longest {summary.streak.longest}</Badge>
          <Badge variant="outline">{summary.streak.last_completed_on ?? 'No completion yet'}</Badge>
        </div>
      </CardContent>
    </Card>
  )
}

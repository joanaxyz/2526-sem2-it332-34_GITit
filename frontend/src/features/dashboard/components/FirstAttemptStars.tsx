import { Star } from 'lucide-react'

import type { DashboardSummary } from '@/features/dashboard/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function FirstAttemptStars({ summary }: { summary: DashboardSummary }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="size-5 text-primary" />
          First-attempt stars
        </CardTitle>
        <CardDescription>Awarded only when a completed primary session has no misses or invalid commands.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-extrabold">{summary.first_attempt_stars}</div>
      </CardContent>
    </Card>
  )
}

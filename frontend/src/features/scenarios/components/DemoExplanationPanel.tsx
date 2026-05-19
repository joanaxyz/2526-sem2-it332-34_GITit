import type { RepositorySnapshot } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function DemoExplanationPanel({
  explanation,
  snapshot,
}: {
  explanation: string
  snapshot: RepositorySnapshot
}) {
  const workingTreeCount = Object.keys(snapshot.working_tree ?? {}).length
  const stagingCount = Object.keys(snapshot.staging ?? {}).length
  const conflictCount = snapshot.conflicts?.length ?? 0

  return (
    <Card className="h-full shadow-none">
      <CardHeader className="p-3">
        <CardTitle className="text-sm">Demo Explanation Panel</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 p-3 pt-0">
        <p className="text-sm leading-6 text-muted-foreground">{explanation}</p>
        <div className="flex flex-wrap gap-2">
          <Badge variant={workingTreeCount ? 'warning' : 'default'}>{workingTreeCount ? `${workingTreeCount} working` : 'Working tree clean'}</Badge>
          <Badge variant={stagingCount ? 'blue' : 'outline'}>{stagingCount ? `${stagingCount} staged` : 'Nothing staged'}</Badge>
          <Badge variant={conflictCount ? 'destructive' : 'outline'}>{conflictCount ? `${conflictCount} conflict` : 'No conflicts'}</Badge>
        </div>
      </CardContent>
    </Card>
  )
}

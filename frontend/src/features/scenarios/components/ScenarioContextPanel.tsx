import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function ScenarioContextPanel({ session }: { session: ScenarioSession }) {
  return (
    <Card className="shadow-none">
      <CardHeader className="p-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="blue">Unit {session.unit.number}</Badge>
          <Badge variant="default" className="capitalize">{session.difficulty}</Badge>
          {session.review_mode ? <Badge variant="warning">Review Mode</Badge> : null}
          {session.variant.changed_variant ? <Badge variant="warning">Changed variant</Badge> : null}
        </div>
        <CardTitle className="text-base leading-tight">{session.scenario.title}</CardTitle>
        <CardDescription>{session.scenario.focus}</CardDescription>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <p className="text-sm leading-6 text-muted-foreground">{session.scenario.narrative}</p>
        <div className="mt-3 rounded-md border border-border bg-secondary/50 p-3 text-sm leading-6">
          <div className="mb-1 text-xs font-bold uppercase text-muted-foreground">Task</div>
          {session.scenario.task_prompt}
        </div>
      </CardContent>
    </Card>
  )
}

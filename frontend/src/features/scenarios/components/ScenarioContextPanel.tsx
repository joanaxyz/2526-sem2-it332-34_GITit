import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'

export function ScenarioContextPanel({ session }: { session: ScenarioSession }) {
  const taskPrompt = hideCommandAnswers(session.scenario.task_prompt, [session.scenario.focus])

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
          {taskPrompt}
        </div>
      </CardContent>
    </Card>
  )
}

function hideCommandAnswers(prompt: string, commands: string[]) {
  let safePrompt = prompt
  for (const command of commands) {
    if (!command) continue
    safePrompt = safePrompt.replace(new RegExp(escapeRegExp(command), 'gi'), 'the appropriate command')
  }
  return safePrompt
    .replace(/\bgit\s+(?!repository\b)[a-z-]+(?:\s+--?[a-z-]+)*/gi, 'the appropriate command')
    .replace(/\bstage only\b/gi, 'prepare only')
    .replace(/\bstage\b/gi, 'prepare')
    .replace(/\bstaged\b/gi, 'prepared')
    .replace(/\bstaging area\b/gi, 'preparation area')
    .replace(/\bcreate the first commit\b/gi, 'save the first snapshot')
    .replace(/\bcreate a commit\b/gi, 'save a snapshot')
    .replace(/\bcommitted\b/gi, 'saved')
    .replace(/\bcommit\b/gi, 'snapshot')
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

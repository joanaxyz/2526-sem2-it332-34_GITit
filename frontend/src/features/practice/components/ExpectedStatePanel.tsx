import type { ScenarioSession } from '@/features/practice/types'
import { Card, CardTitle } from '@/shared/components/Card'
import { LiveDagPanel } from './LiveDagPanel'

export function ExpectedStatePanel({ session }: { session: ScenarioSession }) {
  if (!session.scaffolding.expected_state || !session.expected_state) {
    return (
      <Card className="p-4 opacity-70 shadow-none">
        <CardTitle className="text-base">Expected state hidden</CardTitle>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">Hard difficulty shows only the live DAG and narrative context.</p>
      </Card>
    )
  }
  return <LiveDagPanel title="Expected-State Diagram" snapshot={session.expected_state} />
}

import { GitPullRequest, ListChecks } from 'lucide-react'

import { DifficultySelector } from '@/features/scenarios/components/DifficultySelector'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function ScenarioCard({
  scenario,
  onStart,
  onReview,
}: {
  scenario: ScenarioSkillFocus
  onStart: (difficulty: DifficultyAccess) => void
  onReview: (difficulty: DifficultyAccess) => void
}) {
  return (
    <Card className="shadow-none">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2">
              <GitPullRequest className="size-5 text-primary" />
              {scenario.title}
            </CardTitle>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{scenario.narrative}</p>
          </div>
          <Badge variant="blue">{scenario.focus}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-3 rounded-md border border-border bg-secondary/30 p-3 text-xs leading-5 text-muted-foreground">
          <div className="mb-2 flex items-center gap-2 font-semibold text-foreground">
            <ListChecks className="size-4 text-primary" />
            How this is graded
          </div>
          <p>
            Reach the final repository state described by the selected level. Any valid command sequence can pass; the
            evaluator checks state, not a hidden command script. Commit-message wording matters only when the task says the
            message must mention a word.
          </p>
        </div>
        <DifficultySelector difficulties={scenario.difficulties} onStart={onStart} onReview={onReview} />
      </CardContent>
    </Card>
  )
}

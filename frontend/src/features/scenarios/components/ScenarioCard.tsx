import { GitPullRequest } from 'lucide-react'

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
        <DifficultySelector difficulties={scenario.difficulties} onStart={onStart} onReview={onReview} />
      </CardContent>
    </Card>
  )
}

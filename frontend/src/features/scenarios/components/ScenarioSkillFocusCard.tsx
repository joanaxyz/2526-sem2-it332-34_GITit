import { GitPullRequest, ListChecks } from 'lucide-react'

import { DifficultyActionButton } from '@/features/scenarios/components/DifficultyActionButton'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function ScenarioSkillFocusCard({
  scenario,
  onDifficultyAction,
}: {
  scenario: ScenarioSkillFocus
  onDifficultyAction: (scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) => void
}) {
  const primaryLabel = scenario.primary_focus_commands.length === 1 ? 'Focus command' : 'Focus commands'
  const focusValue = scenario.primary_focus_commands.length ? scenario.primary_focus_commands.join(', ') : scenario.focus

  return (
    <Card className="shadow-none">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2">
              <GitPullRequest className="size-5 text-primary" />
              Scenario Skill Focus: {scenario.title}
            </CardTitle>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{scenario.summary}</p>
          </div>
          <Badge variant="blue">{scenario.skill_focus_type.replace('_', ' ')}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4 grid gap-2 rounded-md border border-border bg-secondary/30 p-3 text-xs leading-5 text-muted-foreground">
          <div className="flex items-center gap-2 font-semibold text-foreground">
            <ListChecks className="size-4 text-primary" />
            <span className="font-semibold">{scenario.primary_focus_commands.length ? `${primaryLabel}:` : 'Skill focus:'}</span>
            <span className="font-mono">{focusValue}</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
          {scenario.difficulties.map((difficulty) => (
            <DifficultyActionButton
              difficulty={difficulty}
              key={difficulty.id}
              onAction={(selectedDifficulty, action) => onDifficultyAction(scenario, selectedDifficulty, action)}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

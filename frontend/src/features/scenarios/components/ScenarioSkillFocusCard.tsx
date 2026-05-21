import { GitPullRequest, ListChecks } from 'lucide-react'
import { useState } from 'react'

import { DifficultyActionButton } from '@/features/scenarios/components/DifficultyActionButton'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { ExpandToggleButton } from '@/shared/components/ExpandToggleButton'

export function ScenarioSkillFocusCard({
  scenario,
  topicNumber,
  onDifficultyAction,
}: {
  scenario: ScenarioSkillFocus
  topicNumber: number
  onDifficultyAction: (scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) => void
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const primaryLabel = scenario.primary_focus_commands.length === 1 ? 'Focus command' : 'Focus commands'
  const focusValue = scenario.primary_focus_commands.length ? scenario.primary_focus_commands.join(', ') : scenario.focus
  const panelId = `skill-panel-${scenario.id}`

  return (
    <Card className="shadow-none">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-semibold text-primary">Topic {topicNumber}</p>
            <CardTitle className="mt-1 flex items-center gap-2">
              <GitPullRequest className="size-5 shrink-0 text-primary" />
              {scenario.title}
            </CardTitle>
            {isExpanded ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{scenario.summary}</p> : null}
          </div>
          <ExpandToggleButton
            expanded={isExpanded}
            controlsId={panelId}
            label={`Topic ${topicNumber}: ${scenario.title}`}
            onToggle={() => setIsExpanded((current) => !current)}
          />
        </div>
      </CardHeader>
      {isExpanded ? (
        <CardContent id={panelId}>
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
      ) : null}
    </Card>
  )
}

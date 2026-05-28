import { BookOpen, GitPullRequest } from 'lucide-react'
import { useState } from 'react'

import { DifficultyActionButton } from '@/features/scenarios/components/DifficultyActionButton'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { ExpandToggleButton } from '@/shared/components/ExpandToggleButton'

export function ScenarioSkillFocusCard({
  scenario,
  scenarioNumber,
  actionsDisabled = false,
  onDifficultyAction,
  onPreview,
}: {
  scenario: ScenarioSkillFocus
  scenarioNumber: number
  actionsDisabled?: boolean
  onDifficultyAction: (scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) => void
  onPreview: (scenario: ScenarioSkillFocus) => void
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const panelId = `skill-panel-${scenario.id}`
  const isPreviewOnly = scenario.difficulties.length === 0
  const cardLabel = isPreviewOnly ? 'Guided Preview' : `Scenario ${scenarioNumber}`

  return (
    <Card
      className={
        isPreviewOnly
          ? 'shadow-none border-dashed border-primary/30 bg-primary/[0.025]'
          : 'shadow-none'
      }
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-primary">{cardLabel}</p>
            <CardTitle className="mt-1 flex items-center gap-2">
              <GitPullRequest className="size-5 shrink-0 text-primary" />
              {scenario.title}
            </CardTitle>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {isPreviewOnly ? (
                <>
                  Learn the{' '}
                  <span className="tooltip-anchor">
                    <span
                      className="cursor-help"
                      style={{ borderBottom: '1px dashed rgba(0,245,212,0.55)' }}
                    >
                      diagnostic commands
                    </span>
                    <span
                      className="tooltip-popup rounded-md text-xs leading-5 text-muted-foreground"
                      style={{
                        background: 'hsl(var(--card))',
                        border: '1px solid rgba(0,245,212,0.15)',
                        borderLeft: '3px solid rgba(0,245,212,0.55)',
                        boxShadow: '0 4px 16px rgba(0,0,0,0.45)',
                        padding: '0.5rem 0.625rem',
                      }}
                    >
                      Read-only commands that inspect repository state without making any changes.
                    </span>
                  </span>
                  {" you'll use throughout this module, then try them live in a safe demo environment."}
                </>
              ) : isExpanded ? scenario.summary : null}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              className={isPreviewOnly ? 'border-primary/50 text-primary hover:bg-primary/10' : undefined}
              onClick={() => onPreview(scenario)}
            >
              <BookOpen className="size-3.5" />
              Learn
            </Button>
            <ExpandToggleButton
              expanded={isExpanded}
              controlsId={panelId}
              label={`${cardLabel}: ${scenario.title}`}
              onToggle={() => setIsExpanded((current) => !current)}
            />
          </div>
        </div>
      </CardHeader>
      {isExpanded ? (
        <CardContent id={panelId}>
          {/* Command focus intentionally hidden in the card UI */}
          {isPreviewOnly ? null : (
            <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
              {scenario.difficulties.map((difficulty) => (
                <DifficultyActionButton
                  disabled={actionsDisabled}
                  difficulty={difficulty}
                  key={difficulty.id}
                  onAction={(selectedDifficulty, action) => onDifficultyAction(scenario, selectedDifficulty, action)}
                />
              ))}
            </div>
          )}
        </CardContent>
      ) : null}
    </Card>
  )
}

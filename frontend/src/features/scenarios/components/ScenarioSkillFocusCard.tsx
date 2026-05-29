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
  const isPreviewOnly = scenario.difficulties.length === 0
  const cardLabel = isPreviewOnly ? 'Guided Preview' : `Lesson ${scenarioNumber}`
  const panelId = `skill-panel-${scenario.id}`

  return (
    <Card
      className={
        isPreviewOnly
          ? 'scenario-card-hover shadow-none border-dashed'
          : 'scenario-card-hover shadow-none'
      }
      style={isPreviewOnly ? {
        borderColor: 'var(--module-border-rest, rgba(0,212,170,0.3))',
        background: 'color-mix(in srgb, var(--module-color, hsl(var(--primary))) 3%, transparent)',
      } : undefined}
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p
              className="text-xs font-semibold"
              style={{ color: 'var(--module-color, hsl(var(--primary)))' }}
            >
              {cardLabel}
            </p>
            <CardTitle className="mt-1 flex items-center gap-2">
              <GitPullRequest
                className="size-5 shrink-0"
                style={{ color: 'var(--module-color, hsl(var(--primary)))' }}
              />
              {scenario.title}
            </CardTitle>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {isPreviewOnly ? (
                <>
                  Learn the{' '}
                  <span className="tooltip-anchor">
                    <span
                      className="cursor-help"
                      style={{ borderBottom: '1px dashed var(--module-border-hover, rgba(0,212,170,0.55))' }}
                    >
                      diagnostic commands
                    </span>
                    <span
                      className="tooltip-popup rounded-md text-xs leading-5 text-muted-foreground"
                      style={{
                        background: 'hsl(var(--card))',
                        border: '1px solid var(--module-border-rest, rgba(0,212,170,0.15))',
                        borderLeft: '3px solid var(--module-border-hover, rgba(0,212,170,0.55))',
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
              style={{
                borderColor: 'var(--module-border-hover, rgba(0,212,170,0.5))',
                color: 'var(--module-color, hsl(var(--primary)))',
              }}
              onClick={() => onPreview(scenario)}
            >
              <BookOpen className="size-3.5" />
              Learn
            </Button>
            {!isPreviewOnly && (
              <ExpandToggleButton
                expanded={isExpanded}
                controlsId={panelId}
                label={`${cardLabel}: ${scenario.title}`}
                onToggle={() => setIsExpanded((current) => !current)}
              />
            )}
          </div>
        </div>
      </CardHeader>
      {!isPreviewOnly && isExpanded ? (
        <CardContent id={panelId}>
          {/* Command focus intentionally hidden in the card UI */}
          <div className="grid grid-cols-3 gap-2 max-md:grid-cols-1">
            {scenario.difficulties.map((difficulty, index) => {
              const prev = index > 0 ? scenario.difficulties[index - 1] : null
              const prevProgress = prev
                ? (prev.successful_attempts
                    ? { mastered: prev.successful_attempts.count, required: prev.successful_attempts.required }
                    : prev.mastered_records ?? prev.mastery_progress)
                : null
              const gatingLocked = prevProgress !== null && prevProgress.mastered < prevProgress.required
              const effectiveDifficulty = gatingLocked ? { ...difficulty, status: 'locked' as const } : difficulty
              return (
                <DifficultyActionButton
                  disabled={actionsDisabled}
                  difficulty={effectiveDifficulty}
                  key={difficulty.id}
                  onAction={(selectedDifficulty, action) => onDifficultyAction(scenario, selectedDifficulty, action)}
                />
              )
            })}
          </div>
        </CardContent>
      ) : null}
    </Card>
  )
}

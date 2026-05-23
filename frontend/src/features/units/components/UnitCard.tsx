import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

import { ModuleSymbol } from '@/features/units/components/ModuleSymbol'
import { UnitScenarioHub } from '@/features/units/components/UnitScenarioHub'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import type { LearningUnit } from '@/features/units/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { ExpandToggleButton } from '@/shared/components/ExpandToggleButton'
import { ProgressBar } from '@/shared/components/ProgressBar'

function practiceCompletionFromSummary(scenarios: ScenarioSkillFocus[] | undefined) {
  if (!scenarios) return null
  const numerator = scenarios.reduce(
    (total, scenario) =>
      total + scenario.difficulties.reduce((sum, difficulty) => sum + difficulty.mastery_progress.mastered, 0),
    0,
  )
  const denominator = scenarios.reduce(
    (total, scenario) =>
      total + scenario.difficulties.reduce((sum, difficulty) => sum + difficulty.mastery_progress.required, 0),
    0,
  )
  return {
    numerator,
    denominator,
    value: denominator ? Math.round((numerator / denominator) * 100) : 0,
  }
}

export function UnitCard({
  unit,
  isExpanded,
  scenarioSummary,
  scenarioSummaryPending = false,
  onToggle,
}: {
  unit: LearningUnit
  isExpanded: boolean
  scenarioSummary?: ScenarioSkillFocus[]
  scenarioSummaryPending?: boolean
  onToggle: () => void
}) {
  const visibleLessons = unit.is_orientation
    ? unit.lessons.filter((lesson) => !['practice-rules', 'scaffolds-review'].includes(lesson.slug))
    : unit.lessons
  const orientationProgress = Math.round(
    (visibleLessons.filter((lesson) => lesson.is_complete).length / Math.max(visibleLessons.length, 1)) * 100,
  )
  const livePracticeCompletion = practiceCompletionFromSummary(scenarioSummary)
  const practiceProgress = Math.round(livePracticeCompletion?.value ?? unit.practice_completion?.value ?? 0)
  const progressValue = unit.is_orientation ? orientationProgress : practiceProgress
  const overviewLessons = unit.lessons.filter((lesson) => !unit.is_orientation && lesson.scenario_count === 0)
  const panelId = `unit-panel-${unit.id}`

  return (
    <Card className="overflow-hidden shadow-none" data-unit-id={unit.id}>
      <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4 p-5 text-left">
        <ModuleSymbol unit={unit} />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold">{unit.title}</h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{unit.description}</p>
          <div className="mt-3 flex max-w-xl items-center gap-3">
            <ProgressBar value={progressValue} className="flex-1" />
            <span className="font-mono text-xs text-muted-foreground">{progressValue}%</span>
          </div>
        </div>
        <ExpandToggleButton expanded={isExpanded} controlsId={panelId} label={unit.title} onToggle={onToggle} />
      </div>
      {isExpanded ? (
        <div className="border-t border-border bg-background/35 p-5" id={panelId}>
          {unit.is_orientation ? (
            <div className="grid gap-2">
              {visibleLessons.map((lesson) => (
                <div key={lesson.id} className="rounded-md border border-border bg-secondary/40 p-3 transition hover:bg-secondary">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <BookOpen className="size-4 text-primary" />
                        <div className="font-semibold">{lesson.title}</div>
                        <Badge variant={lesson.is_complete ? 'default' : 'outline'}>{lesson.is_complete ? 'Complete' : 'Open'}</Badge>
                      </div>
                      <div className="mt-1 text-sm text-muted-foreground">{lesson.subtitle}</div>
                    </div>
                    <Button asChild size="sm" variant="outline">
                      <Link to={`/lessons/${lesson.id}`}>View lesson</Link>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid gap-5">
              <UnitScenarioHub
                unit={unit}
                scenarioSummary={scenarioSummary}
                scenarioSummaryPending={scenarioSummaryPending}
              />
              {overviewLessons.length ? (
                <div className="rounded-lg border border-border bg-card/60 p-4">
                  <div className="mb-3 flex items-center gap-2 font-bold">
                    <BookOpen className="size-4 text-primary" />
                    Lesson overviews
                  </div>
                  <div className="grid gap-2">
                    {overviewLessons.map((lesson) => (
                      <div key={lesson.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-secondary/30 p-3">
                        <div>
                          <div className="font-semibold">{lesson.title}</div>
                          <div className="mt-1 text-sm text-muted-foreground">{lesson.subtitle}</div>
                        </div>
                        <Button asChild size="sm" variant="outline">
                          <Link to={`/lessons/${lesson.id}`}>View overview</Link>
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
      ) : null}
    </Card>
  )
}

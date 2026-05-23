import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { ModuleScenarioHub } from '@/features/modules/components/ModuleScenarioHub'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import type { LearningModule } from '@/features/modules/types'
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

export function ModuleCard({
  module,
  isExpanded,
  scenarioSummary,
  scenarioSummaryPending = false,
  onToggle,
}: {
  module: LearningModule
  isExpanded: boolean
  scenarioSummary?: ScenarioSkillFocus[]
  scenarioSummaryPending?: boolean
  onToggle: () => void
}) {
  const visibleLessons = module.is_orientation
    ? module.lessons.filter((lesson) => !['practice-rules', 'scaffolds-review'].includes(lesson.slug))
    : module.lessons
  const orientationProgress = Math.round(
    (visibleLessons.filter((lesson) => lesson.is_complete).length / Math.max(visibleLessons.length, 1)) * 100,
  )
  const livePracticeCompletion = practiceCompletionFromSummary(scenarioSummary)
  const practiceProgress = Math.round(livePracticeCompletion?.value ?? module.practice_completion?.value ?? 0)
  const progressValue = module.is_orientation ? orientationProgress : practiceProgress
  const overviewLessons = module.lessons.filter((lesson) => !module.is_orientation && lesson.scenario_count === 0)
  const panelId = `module-panel-${module.id}`

  return (
    <Card className="overflow-hidden shadow-none" data-module-id={module.id}>
      <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4 p-5 text-left">
        <ModuleSymbol module={module} />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold">{module.title}</h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{module.description}</p>
          <div className="mt-3 flex max-w-xl items-center gap-3">
            <ProgressBar value={progressValue} className="flex-1" />
            <span className="font-mono text-xs text-muted-foreground">{progressValue}%</span>
          </div>
        </div>
        <ExpandToggleButton expanded={isExpanded} controlsId={panelId} label={module.title} onToggle={onToggle} />
      </div>
      {isExpanded ? (
        <div className="border-t border-border bg-background/35 p-5" id={panelId}>
          {module.is_orientation ? (
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
              <ModuleScenarioHub
                module={module}
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

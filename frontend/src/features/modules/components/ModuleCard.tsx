import { Link } from 'react-router-dom'

import { OrientationLessonCard } from '@/features/modules/components/OrientationLessonCard'
import { ModuleSymbol } from '@/features/modules/components/ModuleSymbol'
import { ModuleScenarioHub } from '@/features/modules/components/ModuleScenarioHub'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import type { LearningModule } from '@/features/modules/types'
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
    : []
  const orientationProgress = Math.round(
    (visibleLessons.filter((lesson) => lesson.is_complete).length / Math.max(visibleLessons.length, 1)) * 100,
  )
  const livePracticeCompletion = practiceCompletionFromSummary(scenarioSummary)
  const practiceProgress = Math.round(livePracticeCompletion?.value ?? module.practice_completion?.value ?? 0)
  const progressValue = module.is_orientation ? orientationProgress : practiceProgress
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
            <div className="grid gap-3">
              <p className="rounded-md border border-primary/25 bg-primary/5 px-3 py-2 text-sm text-muted-foreground">
                Recommended before scenario practice: complete all {visibleLessons.length} orientation lessons at your
                own pace.
              </p>
              <p className="font-mono text-xs text-muted-foreground">
                {visibleLessons.filter((lesson) => lesson.is_complete).length} / {visibleLessons.length} complete
              </p>
              <div className="grid gap-2">
                {visibleLessons.map((lesson) => (
                  <OrientationLessonCard key={lesson.id} lesson={lesson} />
                ))}
              </div>
            </div>
          ) : (
            <ModuleScenarioHub
              module={module}
              scenarioSummary={scenarioSummary}
              scenarioSummaryPending={scenarioSummaryPending}
            />
          )}
        </div>
      ) : null}
    </Card>
  )
}

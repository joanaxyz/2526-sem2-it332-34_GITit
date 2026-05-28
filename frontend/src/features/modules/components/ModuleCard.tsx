import { useEffect, useState } from 'react'
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

function StatusBadge({ progress }: { progress: number }) {
  if (progress >= 100) {
    return (
      <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold leading-none text-emerald-400">
        Completed
      </span>
    )
  }
  if (progress > 0) {
    return (
      <span className="inline-flex items-center rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 text-[10px] font-semibold leading-none text-primary">
        In Progress
      </span>
    )
  }
  return (
    <span className="inline-flex items-center rounded-full border border-border/60 bg-transparent px-2 py-0.5 text-[10px] font-semibold leading-none text-muted-foreground/70">
      Not Started
    </span>
  )
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
  const [everExpanded, setEverExpanded] = useState(isExpanded)

  useEffect(() => {
    if (isExpanded) setEverExpanded(true)
  }, [isExpanded])

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
    <Card
      className="module-card-hover overflow-hidden shadow-none"
      style={{ borderLeft: '2px solid rgba(0,245,212,0.35)' }}
    >
      <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4 p-5 text-left">
        <ModuleSymbol module={module} />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold">
              <span className="text-aurora-cyan">Module {module.number}:</span>{' '}
              {module.title}
            </h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{module.description}</p>
          <div className="mt-3 flex max-w-xl flex-wrap items-center gap-3">
            <ProgressBar value={progressValue} className="flex-1" glow fillAnimate />
            <span className="font-mono text-xs text-primary/70">{progressValue}%</span>
            <StatusBadge progress={progressValue} />
          </div>
        </div>
        <ExpandToggleButton expanded={isExpanded} controlsId={panelId} label={module.title} onToggle={onToggle} />
      </div>
      {everExpanded && (
        <div
          className="grid"
          style={{
            gridTemplateRows: isExpanded ? '1fr' : '0fr',
            transition: 'grid-template-rows 0.35s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          <div style={{ overflow: 'hidden' }}>
            <div className="border-t border-border/50 bg-secondary/20 p-5" id={panelId}>
              {module.is_orientation ? (
                <div className="grid gap-3">
                  <p className="rounded-md border border-primary/25 bg-primary/5 px-3 py-2 text-sm text-muted-foreground">
                    Recommended before starting the Core Modules: complete all {visibleLessons.length} orientation lessons at your
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
          </div>
        </div>
      )}
    </Card>
  )
}

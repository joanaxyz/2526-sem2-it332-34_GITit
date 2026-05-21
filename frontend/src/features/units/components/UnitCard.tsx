import { BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

import { UnitScenarioHub } from '@/features/units/components/UnitScenarioHub'
import type { LearningUnit } from '@/features/units/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { Skeleton } from '@/shared/components/Skeleton'

export function UnitCard({
  unit,
  isContentVisible,
}: {
  unit: LearningUnit
  isContentVisible: boolean
}) {
  const orientationProgress = Math.round(
    (unit.lessons.filter((lesson) => lesson.is_complete).length / Math.max(unit.lessons.length, 1)) * 100,
  )
  const practiceProgress = Math.round(unit.practice_completion?.value ?? 0)
  const progressValue = unit.is_orientation ? orientationProgress : practiceProgress
  const referenceLessons = unit.lessons.filter((lesson) => lesson.kind !== 'scenario')

  return (
    <Card className="overflow-hidden shadow-none" data-unit-id={unit.id}>
      <div className="grid w-full grid-cols-[3rem_minmax(0,1fr)] items-center gap-4 p-5 text-left">
        <div className="grid size-12 place-items-center rounded-md border border-border bg-secondary text-lg font-extrabold text-primary">
          {unit.number}
        </div>
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
      </div>
      {isContentVisible ? (
        <div className="border-t border-border bg-background/35 p-5">
          {unit.is_orientation ? (
            <div className="grid gap-2">
              {unit.lessons.map((lesson) => (
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
              <UnitScenarioHub unit={unit} />
              {referenceLessons.length ? (
                <div className="rounded-lg border border-border bg-card/60 p-4">
                  <div className="mb-3 flex items-center gap-2 font-bold">
                    <BookOpen className="size-4 text-primary" />
                    Reference lessons
                  </div>
                  <div className="grid gap-2">
                    {referenceLessons.map((lesson) => (
                      <div key={lesson.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-secondary/30 p-3">
                        <div>
                          <div className="font-semibold">{lesson.title}</div>
                          <div className="mt-1 text-sm text-muted-foreground">{lesson.subtitle}</div>
                        </div>
                        <Button asChild size="sm" variant="outline">
                          <Link to={`/lessons/${lesson.id}`}>Open reference</Link>
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>
      ) : (
        <div className="border-t border-border bg-background/25 p-5">
          <div className="grid gap-3">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-14 w-full" />
          </div>
        </div>
      )}
    </Card>
  )
}

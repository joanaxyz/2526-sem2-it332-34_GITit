import { BookOpen, ChevronDown, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { LearningUnit } from '@/features/units/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function UnitCard({
  unit,
  expanded,
  onToggle,
}: {
  unit: LearningUnit
  expanded: boolean
  onToggle: () => void
}) {
  const progress = unit.is_orientation
    ? Math.round((unit.lessons.filter((lesson) => lesson.is_complete).length / Math.max(unit.lessons.length, 1)) * 100)
    : 0

  return (
    <Card className="overflow-hidden shadow-none">
      <button className="grid w-full grid-cols-[3rem_minmax(0,1fr)_auto] items-center gap-4 p-5 text-left" onClick={onToggle} type="button">
        <div className="grid size-12 place-items-center rounded-md border border-border bg-secondary text-lg font-extrabold text-primary">
          {unit.number}
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold">{unit.title}</h2>
            {unit.is_orientation ? <Badge variant="warning">Orientation</Badge> : <Badge variant="blue">{unit.scenario_count} scenarios</Badge>}
          </div>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{unit.description}</p>
          <div className="mt-3 flex max-w-xl items-center gap-3">
            <ProgressBar value={unit.is_orientation ? progress : 0} className="flex-1" />
            <span className="font-mono text-xs text-muted-foreground">{unit.is_orientation ? `${progress}%` : 'Practice'}</span>
          </div>
        </div>
        {expanded ? <ChevronDown className="size-5 text-muted-foreground" /> : <ChevronRight className="size-5 text-muted-foreground" />}
      </button>
      {expanded ? (
        <div className="border-t border-border bg-background/35 p-5">
          <div className="grid gap-2">
            {unit.lessons.map((lesson) => (
              <div key={lesson.id} className="rounded-md border border-border bg-secondary/40 p-3 transition hover:bg-secondary">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <BookOpen className="size-4 text-primary" />
                      <div className="font-semibold">{lesson.title}</div>
                      {lesson.kind === 'orientation' ? (
                        <Badge variant={lesson.is_complete ? 'default' : 'outline'}>{lesson.is_complete ? 'Complete' : 'Open'}</Badge>
                      ) : lesson.scenario_count ? (
                        <Badge variant="blue">{lesson.scenario_count} scenarios</Badge>
                      ) : (
                        <Badge variant="outline">Lesson</Badge>
                      )}
                    </div>
                    <div className="mt-1 text-sm text-muted-foreground">{lesson.subtitle}</div>
                  </div>
                  <Button asChild size="sm" variant={lesson.scenario_count ? 'default' : 'outline'}>
                    <Link to={`/lessons/${lesson.id}`}>View lesson</Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </Card>
  )
}

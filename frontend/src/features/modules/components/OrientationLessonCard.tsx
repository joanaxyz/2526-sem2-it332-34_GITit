import { CheckCircle2, Circle } from 'lucide-react'
import { Link } from 'react-router-dom'

import { displayLessonTitle } from '@/features/modules/orientation/types'
import type { LessonSummary } from '@/features/modules/types'

export function OrientationLessonCard({ lesson }: { lesson: LessonSummary }) {
  return (
    <Link
      className="group flex items-start gap-3 rounded-md border border-border bg-secondary/45 p-3 transition-all hover:bg-secondary hover:shadow-[inset_3px_0_0_rgba(0,245,212,0.5)]"
      to={`/lessons/${lesson.id}`}
    >
      {lesson.is_complete
        ? <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-primary" />
        : <Circle className="mt-0.5 size-5 shrink-0 text-muted-foreground" />
      }
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <div className="text-sm font-semibold">{displayLessonTitle(lesson.title)}</div>
          <span className="-translate-x-1 text-xs text-primary opacity-0 transition-all duration-200 group-hover:translate-x-0 group-hover:opacity-100">
            →
          </span>
        </div>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">{lesson.subtitle}</p>
      </div>
    </Link>
  )
}

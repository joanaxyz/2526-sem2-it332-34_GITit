import { CheckCircle2, Circle } from 'lucide-react'
import { Link } from 'react-router-dom'

import { displayLessonTitle } from '@/features/modules/orientation/types'
import type { LessonSummary } from '@/features/modules/types'

export function OrientationLessonCard({ lesson }: { lesson: LessonSummary }) {
  return (
    <Link className="flex items-start gap-3 rounded-md border border-border bg-secondary/45 p-3 transition hover:bg-secondary" to={`/lessons/${lesson.id}`}>
      {lesson.is_complete ? <CheckCircle2 className="mt-0.5 size-5 text-primary" /> : <Circle className="mt-0.5 size-5 text-muted-foreground" />}
      <div>
        <div className="text-sm font-semibold">{displayLessonTitle(lesson.title)}</div>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">{lesson.subtitle}</p>
      </div>
    </Link>
  )
}

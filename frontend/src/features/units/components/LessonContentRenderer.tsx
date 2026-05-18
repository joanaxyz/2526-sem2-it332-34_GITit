import type { LessonDetail } from '@/features/units/types'

export function LessonContentRenderer({ lesson }: { lesson: LessonDetail }) {
  return (
    <div>
      {lesson.scoped_css ? <style>{lesson.scoped_css}</style> : null}
      <div dangerouslySetInnerHTML={{ __html: lesson.content_html }} />
    </div>
  )
}

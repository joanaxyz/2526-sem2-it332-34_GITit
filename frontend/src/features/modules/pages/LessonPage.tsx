import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { modulesApi } from '@/features/modules/api/modulesApi'
import { LessonContentRenderer } from '@/features/modules/components/LessonContentRenderer'
import { OrientationLessonWorkspace } from '@/features/modules/orientation/OrientationLessonWorkspace'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function LessonPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const { data: lesson, error, isError, isLoading } = useQuery({
    queryKey: queryKeys.lesson(lessonId),
    queryFn: () => modulesApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })
  if (isLoading) {
    return (
      <LoadingState
        description="Opening the lesson content and practice setup."
        label="Loading lesson"
        variant="page"
      />
    )
  }
  if (isError) return <ErrorState title="Could not load lesson" description={error.message} />
  if (!lesson) return <ErrorState title="Could not load lesson" description="The API returned no lesson data." />

  if (lesson.module.is_orientation) {
    return <OrientationLessonWorkspace lesson={lesson} />
  }

  return <LessonContentRenderer lesson={lesson} />
}

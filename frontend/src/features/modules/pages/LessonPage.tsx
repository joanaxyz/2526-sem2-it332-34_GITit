import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { modulesApi } from '@/features/modules/api/modulesApi'
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
  if (isLoading) return <LoadingState label="Loading lesson" />
  if (isError) return <ErrorState title="Could not load lesson" description={error.message} />
  if (!lesson) return <ErrorState title="Could not load lesson" description="The API returned no lesson data." />

  if (lesson.module.is_orientation) {
    return <OrientationLessonWorkspace lesson={lesson} />
  }

  return <ErrorState title="Lesson unavailable" description="This lesson is not available." />
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, BookOpen, CheckCircle2 } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { unitsApi } from '@/features/units/api/unitsApi'
import { LessonContentRenderer } from '@/features/units/components/LessonContentRenderer'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function LessonPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const queryClient = useQueryClient()
  const { data: lesson, error, isError, isLoading } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => unitsApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })
  const completeMutation = useMutation({
    mutationFn: () => unitsApi.completeOrientationLesson(lessonId, 0),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['units'] })
      await queryClient.invalidateQueries({ queryKey: ['lesson', lessonId] })
    },
  })
  if (isLoading) return <LoadingState label="Loading lesson" />
  if (isError) return <ErrorState title="Could not load lesson" description={error.message} />
  if (!lesson) return <ErrorState title="Could not load lesson" description="The API returned no lesson data." />

  const isOrientation = lesson.kind === 'orientation'

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-5">
      <article>
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <Button asChild variant="ghost" size="sm">
            <Link to="/units">
              <ArrowLeft data-icon="inline-start" />
              Back to Modules
            </Link>
          </Button>
          <Badge variant={isOrientation ? 'warning' : lesson.kind === 'scenario' ? 'default' : 'blue'}>
            Module {lesson.unit.number}: {lesson.unit.title}
          </Badge>
        </div>
        <LessonContentRenderer lesson={lesson} />
        {isOrientation ? (
          <Card className="mt-6 flex flex-wrap items-center justify-between gap-4 p-5 shadow-none">
            <div className="flex items-start gap-3">
              <BookOpen className="mt-0.5 size-5 text-primary" />
              <div>
                <h2 className="text-lg font-bold">Foundation note</h2>
                <p className="mt-1 text-sm leading-6 text-muted-foreground">
                  Mark this when the idea feels clear enough to use. You can come back to it any time during practice.
                </p>
              </div>
            </div>
            <Button type="button" disabled={lesson.is_complete || completeMutation.isPending} onClick={() => completeMutation.mutate()}>
              {lesson.is_complete ? 'Marked read' : completeMutation.isPending ? 'Marking read' : 'Mark lesson read'}
            </Button>
          </Card>
        ) : null}
        {lesson.scenario_count ? (
          <section className="mt-6 rounded-lg border border-border bg-card p-5">
            <div className="mb-4">
              <h2 className="text-xl font-bold">Practice starts from the Modules page</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Scenario-bearing modules now show scenarios directly when expanded. This lesson remains as reference material,
                not the main scenario selection path.
              </p>
            </div>
            <Button asChild>
              <Link to="/units">Back to Modules</Link>
            </Button>
          </section>
        ) : null}
      </article>
      <Card className="flex flex-wrap items-center justify-between gap-3 p-5 shadow-none">
        <div className="flex items-center gap-2 font-bold">
          <CheckCircle2 className="size-5 text-primary" />
          Lesson status
        </div>
        <p className="text-sm leading-6 text-muted-foreground">
          {isOrientation ? 'Saved to your foundation progress.' : 'Use this reference only when you want extra context; scenario practice starts from the Modules page.'}
        </p>
      </Card>
    </div>
  )
}

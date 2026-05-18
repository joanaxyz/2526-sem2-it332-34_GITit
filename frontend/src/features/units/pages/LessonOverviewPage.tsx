import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { unitsApi } from '@/features/units/api/unitsApi'
import { LessonContentRenderer } from '@/features/units/components/LessonContentRenderer'
import { ViewScenariosPanel } from '@/features/units/components/ViewScenariosPanel'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { ProgressBar } from '@/shared/components/ProgressBar'

export function LessonOverviewPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const queryClient = useQueryClient()
  const [stepIndex, setStepIndex] = useState(0)
  const [showScenarios, setShowScenarios] = useState(false)
  const { data: lesson, error, isError, isLoading } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => unitsApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })
  const completeMutation = useMutation({
    mutationFn: () => unitsApi.completeOrientationLesson(lessonId, stepIndex),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['units'] })
      await queryClient.invalidateQueries({ queryKey: ['lesson', lessonId] })
    },
  })
  const progress = useMemo(() => {
    if (!lesson?.interaction_steps.length) return 100
    return Math.round(((stepIndex + 1) / lesson.interaction_steps.length) * 100)
  }, [lesson?.interaction_steps.length, stepIndex])

  if (isLoading) return <LoadingState label="Loading lesson" />
  if (isError) return <ErrorState title="Could not load lesson" description={error.message} />
  if (!lesson) return <ErrorState title="Could not load lesson" description="The API returned no lesson data." />

  const isOrientation = lesson.kind === 'orientation'
  const currentStep = lesson.interaction_steps[stepIndex]

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-[minmax(0,1fr)_20rem] gap-5 max-lg:grid-cols-1">
      <article className="rounded-lg border border-border bg-card p-7">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <Button asChild variant="ghost" size="sm">
            <Link to="/units">
              <ArrowLeft data-icon="inline-start" />
              Back to Units
            </Link>
          </Button>
          <Badge variant={isOrientation ? 'warning' : lesson.kind === 'scenario' ? 'default' : 'blue'}>
            Unit {lesson.unit.number}: {lesson.unit.title}
          </Badge>
        </div>
        <LessonContentRenderer lesson={lesson} />
        {isOrientation ? (
          <Card className="mt-6 p-5 shadow-none">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-bold">Concept walkthrough</h2>
                <p className="mt-1 text-sm text-muted-foreground">No terminal input appears in Unit 1 orientation.</p>
              </div>
              <Badge variant={lesson.is_complete ? 'default' : 'blue'}>{lesson.is_complete ? 'Complete' : `${progress}%`}</Badge>
            </div>
            <ProgressBar value={progress} />
            <p className="mt-4 rounded-md border border-border bg-secondary/50 p-4 text-sm leading-6 text-muted-foreground">{currentStep}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button type="button" variant="outline" disabled={stepIndex === 0} onClick={() => setStepIndex((value) => Math.max(0, value - 1))}>
                Previous
              </Button>
              <Button
                type="button"
                onClick={() => {
                  if (stepIndex < lesson.interaction_steps.length - 1) setStepIndex((value) => value + 1)
                  else completeMutation.mutate()
                }}
              >
                {stepIndex < lesson.interaction_steps.length - 1 ? 'Next step' : 'Mark complete'}
              </Button>
            </div>
          </Card>
        ) : null}
        {lesson.kind === 'scenario' ? (
          <>
            <div className="mt-6">
              <Button type="button" onClick={() => setShowScenarios((value) => !value)}>
                View Scenarios
              </Button>
            </div>
            {showScenarios ? <ViewScenariosPanel unitId={lesson.unit.id} /> : null}
          </>
        ) : null}
      </article>
      <aside className="flex flex-col gap-3">
        <Card className="p-5 shadow-none">
          <div className="flex items-center gap-2 font-bold">
            <CheckCircle2 className="size-5 text-primary" />
            Lesson status
          </div>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            {isOrientation ? 'Complete all walkthrough steps to open the Orientation Completion Gate.' : 'Lesson Overview content prepares the scenario skill focus.'}
          </p>
        </Card>
      </aside>
    </div>
  )
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { modulesApi } from '@/features/modules/api/modulesApi'
import { OrientationStepView } from '@/features/modules/orientation/OrientationStepView'
import {
  CRITICAL_LESSON_SLUGS,
  displayLessonTitle,
  LESSON_LAYOUT_BY_SLUG,
  type OrientationLayout,
} from '@/features/modules/orientation/types'
import type { LessonDetail } from '@/features/modules/types'
import { invalidateScenarioProgressQueries } from '@/features/scenarios/utils/scenarioCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

export function OrientationLessonWorkspace({ lesson }: { lesson: LessonDetail }) {
  const queryClient = useQueryClient()
  const steps = lesson.interaction_steps ?? []
  const layout: OrientationLayout = LESSON_LAYOUT_BY_SLUG[lesson.slug] ?? 'storyboard'
  const needsSession = steps.some((step) => step.kind === 'git_command')

  const [stepIndex, setStepIndex] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(() => new Set())
  const [isCompleted, setIsCompleted] = useState(lesson.is_complete)

  const sessionQuery = useQuery({
    queryKey: queryKeys.orientationSession(lesson.id),
    queryFn: () => modulesApi.startOrientationSession(lesson.id),
    enabled: needsSession,
    staleTime: Infinity,
  })
  const modulesQuery = useQuery({
    queryKey: queryKeys.modules,
    queryFn: () => modulesApi.listModules(),
    staleTime: Infinity,
  })

  const completeMutation = useMutation({
    mutationFn: () => modulesApi.completeOrientationLesson(lesson.id, Math.max(steps.length - 1, 0)),
    onSuccess: async () => {
      setIsCompleted(true)
      invalidateScenarioProgressQueries(queryClient)
      await queryClient.invalidateQueries({ queryKey: queryKeys.lesson(lesson.id) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.modules })
    },
  })

  const currentStep = steps[stepIndex]
  const allStepsDone = steps.length > 0 && completedSteps.size >= steps.length
  const sessionLoading = needsSession && (sessionQuery.isLoading || sessionQuery.isFetching)
  const sessionReady = !needsSession || sessionQuery.isSuccess
  const nextLessonId = useMemo(() => {
    const orientationModule = modulesQuery.data?.find((module) => module.is_orientation)
    if (!orientationModule) return null
    const ordered = [...orientationModule.lessons].sort((a, b) => a.sort_order - b.sort_order)
    const currentIndex = ordered.findIndex((item) => item.id === lesson.id)
    if (currentIndex < 0 || currentIndex >= ordered.length - 1) return null
    return ordered[currentIndex + 1]?.id ?? null
  }, [lesson.id, modulesQuery.data])

  useEffect(() => {
    setIsCompleted(lesson.is_complete)
  }, [lesson.id, lesson.is_complete])

  useEffect(() => {
    if (!currentStep?.initial_state || !sessionQuery.data?.id) return
    if (currentStep.kind !== 'git_command') return
    void modulesApi.resetOrientationSession(sessionQuery.data.id, currentStep.id)
  }, [currentStep?.id, currentStep?.initial_state, currentStep?.kind, sessionQuery.data?.id])

  const handleStepComplete = useCallback(() => {
    if (!currentStep) return
    setCompletedSteps((previous) => {
      return new Set([...previous, currentStep.id])
    })
  }, [currentStep])

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link to={`/modules?module=${lesson.module.id}`}>
            <ArrowLeft data-icon="inline-start" />
            Back to Modules
          </Link>
        </Button>
        <div className="flex flex-wrap items-center gap-2">
          {CRITICAL_LESSON_SLUGS.has(lesson.slug) ? (
            <Badge variant="outline">Foundation critical</Badge>
          ) : null}
          <Badge variant="outline">
            Module {lesson.module.number}: {lesson.module.title}
          </Badge>
        </div>
      </div>

      <header className="grid gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">{displayLessonTitle(lesson.title)}</h1>
        <p className="text-muted-foreground">{lesson.subtitle}</p>
        {lesson.content_html ? (
          <div
            className="prose prose-invert max-w-none text-sm text-muted-foreground"
            dangerouslySetInnerHTML={{ __html: lesson.content_html }}
          />
        ) : null}
      </header>

      <div className="flex flex-wrap gap-2">
        {steps.map((step, index) => (
          <button
            key={step.id}
            type="button"
            className={cn(
              'rounded-full px-3 py-1 text-xs font-medium transition',
              index === stepIndex ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground',
              completedSteps.has(step.id) && 'ring-1 ring-primary/50',
            )}
            onClick={() => setStepIndex(index)}
          >
            {completedSteps.has(step.id) ? '✓ ' : ''}
            {step.title}
          </button>
        ))}
      </div>

      <Card className="p-5 shadow-none">
        {layout === 'guide_terminal' ? (
          <div className="mb-5 rounded-lg border border-border bg-secondary/20 p-4">
            <h2 className="text-sm font-bold uppercase tracking-wide text-muted-foreground">Guide</h2>
            <p className="mt-2 text-sm leading-7 text-muted-foreground">
              Install Git on your machine, then practice configuration commands in the terminal. Values you set become
              authorship metadata on every commit.
            </p>
          </div>
        ) : null}
        {currentStep && sessionReady ? (
          <OrientationStepView
            key={currentStep.id}
            step={currentStep}
            layout={layout}
            sessionId={sessionQuery.data?.id ?? null}
            sessionLoading={sessionLoading}
            onStepComplete={handleStepComplete}
            hasNextStep={stepIndex < steps.length - 1}
            onContinueToNext={() => setStepIndex((current) => Math.min(current + 1, steps.length - 1))}
          />
        ) : (
          <p className="text-sm text-muted-foreground">Loading practice session…</p>
        )}
      </Card>

      <Card className="flex flex-wrap items-center justify-between gap-4 p-5 shadow-none">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="mt-0.5 size-5 text-primary" />
          <div>
            <h2 className="text-lg font-bold">Mark as complete</h2>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Finish all steps above, then mark this lesson complete. Orientation is recommended before scenario practice.
            </p>
          </div>
        </div>
        <Button
          type="button"
          disabled={isCompleted || !allStepsDone || completeMutation.isPending}
          onClick={() => completeMutation.mutate()}
        >
          {isCompleted
            ? 'Completed'
            : completeMutation.isPending
              ? 'Saving…'
              : allStepsDone
                ? 'Mark as complete'
                : `Complete steps (${completedSteps.size}/${steps.length})`}
        </Button>
        {isCompleted ? (
          nextLessonId ? (
            <Button asChild variant="outline">
              <Link to={`/lessons/${nextLessonId}`}>Next topic</Link>
            </Button>
          ) : (
            <Button asChild variant="outline">
              <Link to="/modules">Back to module topics</Link>
            </Button>
          )
        ) : null}
      </Card>
    </div>
  )
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, CheckCircle2, ChevronLeft, ChevronRight, Compass, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import { OrientationStepView } from '@/features/story-map/components/orientation/OrientationStepView'
import {
  CRITICAL_LESSON_SLUGS,
  displayLessonTitle,
  LESSON_LAYOUT_BY_SLUG,
  type OrientationLayout,
} from '@/features/story-map/components/orientation/types'
import type { LearningChapter } from '@/features/story-map/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { GamePanel } from '@/shared/components/GamePanel'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

export function OrientationLessonWorkspace({ chapter, onLeaveModule }: {
  chapter: LearningChapter
  /** Ends orientation and returns the player to the story chapters. Reaching
   * the end of Module 0 has to hand the journey back; topics a player skipped
   * must not strand them here. */
  onLeaveModule: () => void
}) {
  const queryClient = useQueryClient()

  const lessonsQuery = useQuery({
    queryKey: queryKeys.orientationLessons(chapter.id),
    queryFn: () => storyMapApi.listOrientationLessons(chapter.id),
    staleTime: 60 * 1000,
  })
  const lessons = useMemo(
    () => [...(lessonsQuery.data ?? [])].sort((a, b) => a.sort_order - b.sort_order),
    [lessonsQuery.data],
  )
  const [activeLessonId, setActiveLessonId] = useState<number | null>(null)

  useEffect(() => {
    setActiveLessonId((current) => {
      if (current && lessons.some((lesson) => lesson.id === current)) return current
      return lessons.find((lesson) => !lesson.is_complete)?.id ?? lessons[0]?.id ?? null
    })
  }, [lessons])

  const lessonDetailQuery = useQuery({
    queryKey: queryKeys.orientationLesson(activeLessonId ?? 0),
    queryFn: () => storyMapApi.getOrientationLesson(activeLessonId!),
    enabled: Boolean(activeLessonId),
    staleTime: 60 * 1000,
  })
  const lesson = lessonDetailQuery.data
  const steps = useMemo(() => lesson?.interaction_steps ?? [], [lesson?.interaction_steps])
  const layout: OrientationLayout = (lesson && LESSON_LAYOUT_BY_SLUG[lesson.slug]) ?? 'storyboard'

  const [stepIndex, setStepIndex] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(() => new Set())

  useEffect(() => {
    setStepIndex(0)
    setCompletedSteps(new Set())
  }, [activeLessonId])

  useEffect(() => {
    if (!lesson?.is_complete) return
    setCompletedSteps(new Set(steps.map((step) => step.id)))
  }, [lesson?.is_complete, lesson?.id, steps])

  const completeMutation = useMutation({
    mutationFn: () => storyMapApi.completeOrientationLesson(lesson!.id, Math.max(steps.length - 1, 0)),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.orientationLesson(lesson!.id) })
      await queryClient.invalidateQueries({ queryKey: queryKeys.orientationLessons(chapter.id) })
    },
  })

  const currentStep = steps[stepIndex]
  const allStepsDone = steps.length > 0 && completedSteps.size >= steps.length
  const activeLessonIndex = lessons.findIndex((item) => item.id === activeLessonId)
  const completedLessonCount = lessons.filter((item) => item.is_complete).length
  const courseProgress = lessons.length ? Math.round((completedLessonCount / lessons.length) * 100) : 0
  const moduleComplete = lessons.length > 0 && completedLessonCount === lessons.length
  const previousLessonId = activeLessonIndex > 0 ? lessons[activeLessonIndex - 1]?.id ?? null : null
  const nextLessonId = activeLessonIndex >= 0 && activeLessonIndex < lessons.length - 1
    ? lessons[activeLessonIndex + 1]?.id ?? null
    : null

  const handleStepComplete = () => {
    if (!currentStep) return
    setCompletedSteps((previous) => new Set([...previous, currentStep.id]))
  }

  const selectLesson = (lessonId: number) => {
    completeMutation.reset()
    setActiveLessonId(lessonId)
  }

  if (lessonsQuery.isLoading) {
    return <LoadingState label="Loading orientation" description="Preparing lessons for this chapter." variant="page" />
  }
  if (lessonsQuery.isError) {
    return <ErrorState title="Could not load orientation lessons" description={lessonsQuery.error.message} />
  }
  if (!lessons.length) {
    return <ErrorState title="No orientation lessons" description="This chapter has no published lessons yet." />
  }

  return (
    <div className="orientation-workspace">
      <GamePanel as="section" className="orientation-panel" aria-labelledby="orientation-title">
        <header className="orientation-overview">
          <div className="orientation-overview-copy">
            <p className="orientation-kicker"><Compass aria-hidden="true" /> Module 0 · Orientation</p>
            <h1 id="orientation-title">{chapter.title}</h1>
            <p>Build the mental model first. The commands will make more sense when you can see the state they change.</p>
          </div>
          <div className="orientation-course-progress" aria-label={`${completedLessonCount} of ${lessons.length} topics complete`}>
            <span><strong>{completedLessonCount}</strong> / {lessons.length} topics</span>
            <div
              className="orientation-progress-track"
              role="progressbar"
              aria-label="Module progress"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={courseProgress}
            >
              <span style={{ width: `${courseProgress}%` }} />
            </div>
          </div>
        </header>

        <nav className="orientation-lesson-nav" aria-label="Module 0 topics">
          <ol>
            {lessons.map((item, index) => {
              const active = item.id === activeLessonId
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={cn('orientation-lesson-tab', active && 'is-active', item.is_complete && 'is-complete')}
                    aria-current={active ? 'page' : undefined}
                    onClick={() => selectLesson(item.id)}
                  >
                    <span className="orientation-lesson-index" aria-hidden="true">
                      {item.is_complete ? <Check /> : String(index + 1).padStart(2, '0')}
                    </span>
                    <span className="orientation-lesson-tab-copy">
                      <strong>{displayLessonTitle(item.title)}</strong>
                      <small>{item.is_complete ? 'Complete' : active ? 'In progress' : 'Not started'}</small>
                    </span>
                  </button>
                </li>
              )
            })}
          </ol>
        </nav>

        {lessonDetailQuery.isError ? (
          <ErrorState title="Could not load this topic" description={lessonDetailQuery.error.message} />
        ) : !lesson || lessonDetailQuery.isLoading ? (
          <div className="orientation-inline-state"><LoadingState label="Loading lesson" variant="inline" /></div>
        ) : (
          <article className="orientation-lesson" aria-labelledby="orientation-lesson-title">
            <header className="orientation-lesson-header">
              <div className="orientation-lesson-meta">
                <span>Topic {activeLessonIndex + 1} of {lessons.length}</span>
                {CRITICAL_LESSON_SLUGS.has(lesson.slug) ? (
                  <Badge variant="outline"><ShieldCheck aria-hidden="true" /> Core mental model</Badge>
                ) : null}
              </div>
              <h2 id="orientation-lesson-title">{displayLessonTitle(lesson.title)}</h2>
              <p className="orientation-lesson-subtitle">{lesson.subtitle}</p>
              {lesson.content_html ? (
                <div
                  className="orientation-lesson-intro"
                  dangerouslySetInnerHTML={{ __html: lesson.content_html }}
                />
              ) : null}
            </header>

            <nav className="orientation-step-nav" aria-label={`${displayLessonTitle(lesson.title)} steps`}>
              <ol>
                {steps.map((step, index) => {
                  const active = index === stepIndex
                  const complete = completedSteps.has(step.id)
                  return (
                    <li key={step.id}>
                      <button
                        type="button"
                        className={cn('orientation-step-tab', active && 'is-active', complete && 'is-complete')}
                        aria-current={active ? 'step' : undefined}
                        aria-label={`Step ${index + 1}: ${step.title}${complete ? ', complete' : ''}`}
                        onClick={() => setStepIndex(index)}
                      >
                        <span aria-hidden="true">{complete ? <Check /> : index + 1}</span>
                        <strong>{step.title}</strong>
                      </button>
                    </li>
                  )
                })}
              </ol>
            </nav>

            {layout === 'guide_terminal' ? (
              <aside className="orientation-guide-note">
                <strong>Use your local terminal</strong>
                <p>Install Git on your machine, then use these commands to verify your setup and authorship details.</p>
              </aside>
            ) : null}

            <div className="orientation-step-stage">
              {currentStep ? (
                <OrientationStepView
                  key={currentStep.id}
                  step={currentStep}
                  layout={layout}
                  completed={completedSteps.has(currentStep.id)}
                  onStepComplete={handleStepComplete}
                  hasNextStep={stepIndex < steps.length - 1}
                  onContinueToNext={() => setStepIndex((current) => Math.min(current + 1, steps.length - 1))}
                />
              ) : null}
            </div>

            <footer className="orientation-completion">
              <div className="orientation-completion-copy">
                <CheckCircle2 aria-hidden="true" />
                <div>
                  <strong>{lesson.is_complete ? 'Topic complete' : allStepsDone ? 'Ready to seal this topic' : 'Complete every interaction'}</strong>
                  <span>{lesson.is_complete ? 'You can revisit any step or continue forward.' : `${completedSteps.size} of ${steps.length} steps complete`}</span>
                </div>
              </div>

              <div className="orientation-completion-actions">
                {previousLessonId ? (
                  <Button type="button" variant="ghost" onClick={() => selectLesson(previousLessonId)}>
                    <ChevronLeft aria-hidden="true" /> Previous topic
                  </Button>
                ) : null}
                {!lesson.is_complete ? (
                  <Button
                    type="button"
                    disabled={!allStepsDone || completeMutation.isPending}
                    aria-busy={completeMutation.isPending}
                    onClick={() => completeMutation.mutate()}
                  >
                    {completeMutation.isPending ? 'Saving…' : 'Complete topic'}
                  </Button>
                ) : nextLessonId ? (
                  <Button type="button" onClick={() => selectLesson(nextLessonId)}>
                    Next topic <ChevronRight aria-hidden="true" />
                  </Button>
                ) : (
                  <>
                    {moduleComplete ? (
                      <span className="orientation-module-complete"><Check aria-hidden="true" /> Module complete</span>
                    ) : null}
                    <Button type="button" onClick={onLeaveModule}>
                      Continue to Module 1 <ChevronRight aria-hidden="true" />
                    </Button>
                  </>
                )}
              </div>
              {completeMutation.isError ? (
                <p className="orientation-save-error" role="alert">Progress was not saved. Please try again.</p>
              ) : null}
            </footer>
          </article>
        )}
      </GamePanel>
    </div>
  )
}

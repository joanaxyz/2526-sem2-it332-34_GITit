import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { ScenarioCard } from '@/features/scenarios/components/ScenarioCard'
import type { DifficultyAccess } from '@/features/scenarios/types'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { unitsApi } from '@/features/units/api/unitsApi'
import { Button } from '@/shared/components/Button'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function ScenarioSelectionPage() {
  const params = useParams()
  const lessonId = Number(params.lessonId)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const lessonQuery = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => unitsApi.getLesson(lessonId),
    enabled: Number.isFinite(lessonId),
  })
  const scenariosQuery = useQuery({
    queryKey: ['lesson-scenarios', lessonId],
    queryFn: () => scenariosApi.listForLesson(lessonId),
    enabled: Number.isFinite(lessonId),
    staleTime: 5 * 60 * 1000,
  })
  const startMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) =>
      scenariosApi.startSession({ difficulty_instance_id: difficulty.id, source_entry_point: 'lesson' }),
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      navigate(`/practice/${session.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => reviewApi.startReviewSession(difficulty.id),
    onSuccess: (session) => navigate(`/review/${session.id}`),
  })

  if (lessonQuery.isLoading || scenariosQuery.isLoading) {
    return <LoadingState label="Loading scenario selection" />
  }
  if (lessonQuery.isError) return <ErrorState title="Could not load lesson" description={lessonQuery.error.message} />
  if (scenariosQuery.isError) return <ErrorState title="Could not load scenarios" description={scenariosQuery.error.message} />
  if (!lessonQuery.data) return <ErrorState title="Could not load scenario selection" description="The API returned no lesson data." />

  const scenarios = scenariosQuery.data ?? []
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <section className="rounded-lg border border-border bg-card p-6">
        <div className="mb-4">
          <Button asChild variant="ghost" size="sm">
            <Link to={`/lessons/${lessonId}`}>
              <ArrowLeft data-icon="inline-start" />
              Read lesson
            </Link>
          </Button>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">{lessonQuery.data.title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Choose a practice topic and start with the level that is open. Medium and Hard unlock as you complete that same topic.
        </p>
      </section>
      {scenarios.length ? (
        <>
          {startMutation.error ? (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
              {startMutation.error.message}
            </div>
          ) : null}
          {reviewMutation.error ? (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
              {reviewMutation.error.message}
            </div>
          ) : null}
          <div className="grid grid-cols-2 gap-4 max-xl:grid-cols-1">
            {scenarios.map((scenario) => (
              <ScenarioCard
                key={scenario.id}
                scenario={scenario}
                onStart={(difficulty) => {
                  if (difficulty.status === 'in_progress' && difficulty.active_session_id) {
                    navigate(`/practice/${difficulty.active_session_id}`)
                    return
                  }
                  startMutation.mutate(difficulty)
                }}
                onReview={(difficulty) => reviewMutation.mutate(difficulty)}
              />
            ))}
          </div>
        </>
      ) : (
        <EmptyState title="No practice set here" description="Use this lesson as a reference, then open a unit with practice topics when you are ready." />
      )}
    </div>
  )
}

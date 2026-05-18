import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { ScenarioCard } from '@/features/scenarios/components/ScenarioCard'
import type { DifficultyAccess } from '@/features/scenarios/types'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type ScenarioListProps =
  | { scope: 'lesson'; lessonId: number; source: 'lesson' }
  | { scope: 'unit'; unitId: number; source: 'unit_card' }

export function ScenarioList(props: ScenarioListProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const queryKey = props.scope === 'lesson' ? ['lesson-scenarios', props.lessonId] : ['unit-scenarios', props.unitId]
  const { data, error, isError, isLoading } = useQuery({
    queryKey,
    queryFn: () => (props.scope === 'lesson' ? scenariosApi.listForLesson(props.lessonId) : scenariosApi.listForUnit(props.unitId)),
    staleTime: 5 * 60 * 1000,
  })
  const startMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) =>
      scenariosApi.startSession({ difficulty_instance_id: difficulty.id, source_entry_point: props.source }),
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      navigate(`/practice/${session.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => reviewApi.startReviewSession(difficulty.id),
    onSuccess: (session) => navigate(`/review/${session.id}`),
  })

  if (isLoading) return <LoadingState label="Loading scenarios" />
  if (isError) return <ErrorState title="Could not load scenarios" description={error.message} />
  if (!data?.length) return <EmptyState title="No scenarios here yet" description="Use this lesson as reference material, then continue with a scenario-bearing lesson." />

  return (
    <div className="flex flex-col gap-3">
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
      {data.map((scenario) => (
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
  )
}

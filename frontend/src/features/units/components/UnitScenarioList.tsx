import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { ScenarioCard } from '@/features/scenarios/components/ScenarioCard'
import type { DifficultyAccess } from '@/features/scenarios/types'
import { EmptyState } from '@/shared/components/EmptyState'
import { LoadingState } from '@/shared/components/LoadingState'

export function UnitScenarioList({ unitId, source }: { unitId: number; source: 'unit_card' | 'lesson_overview' }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['unit-scenarios', unitId],
    queryFn: () => scenariosApi.listForUnit(unitId),
  })
  const startMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) =>
      scenariosApi.startSession({ difficulty_instance_id: difficulty.id, source_entry_point: source }),
    onSuccess: (session) => {
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      navigate(`/practice/${session.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => reviewApi.startReviewSession(difficulty.id),
    onSuccess: (session) => navigate(`/review/${session.id}`),
  })

  if (isLoading) return <LoadingState label="Loading scenarios" />
  if (!data?.length) return <EmptyState title="No scenarios" description="This Unit has reading or orientation content only." />

  return (
    <div className="flex flex-col gap-3">
      {data.map((scenario) => (
        <ScenarioCard
          key={scenario.id}
          scenario={scenario}
          onStart={(difficulty) => startMutation.mutate(difficulty)}
          onReview={(difficulty) => reviewMutation.mutate(difficulty)}
        />
      ))}
    </div>
  )
}

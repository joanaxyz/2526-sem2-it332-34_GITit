import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { ScenarioSkillFocusCard } from '@/features/scenarios/components/ScenarioSkillFocusCard'
import { SkillFocusPreviewModal } from '@/features/scenarios/components/SkillFocusPreviewModal'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { ScenarioListSkeleton } from '@/shared/components/Skeleton'
import { useRef, useState } from 'react'

type ScenarioListProps =
  | { scope: 'lesson'; lessonId: number; source: 'lesson' }
  | {
      scope: 'unit'
      unitId: number
      source: 'unit_card'
      initialScenarios?: ScenarioSkillFocus[]
      deferFetch?: boolean
    }

export function ScenarioList(props: ScenarioListProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const reservedScenarioTabRef = useRef<Window | null>(null)
  const [previewRequest, setPreviewRequest] = useState<{
    scenario: ScenarioSkillFocus
    difficulty: DifficultyAccess
    action: DifficultyActionIntent
  } | null>(null)
  const queryKey = props.scope === 'lesson' ? ['lesson-scenarios', props.lessonId] : ['unit-scenarios', props.unitId]
  const shouldDeferUnitFetch = props.scope === 'unit' && props.deferFetch && !props.initialScenarios
  const { data, error, isError, isLoading } = useQuery({
    queryKey,
    queryFn: () => (props.scope === 'lesson' ? scenariosApi.listForLesson(props.lessonId) : scenariosApi.listForUnit(props.unitId)),
    enabled: !shouldDeferUnitFetch,
    initialData: props.scope === 'unit' ? props.initialScenarios : undefined,
    staleTime: 5 * 60 * 1000,
  })
  const startMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) =>
      scenariosApi.startSession({ difficulty_instance_id: difficulty.id, source_entry_point: props.source }),
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      setPreviewRequest(null)
      openScenarioRoute(`/practice/${session.id}`)
    },
    onError: closeReservedScenarioTab,
  })
  const retryMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => {
      const priorSessionId = difficulty.retry_session_id ?? difficulty.active_session_id
      if (!priorSessionId) throw new Error('Exit the current scenario before retrying.')
      return scenariosApi.retrySession(priorSessionId)
    },
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      setPreviewRequest(null)
      openScenarioRoute(`/practice/${session.id}`)
    },
    onError: closeReservedScenarioTab,
  })
  const reviewMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => reviewApi.startReviewSession(difficulty.id),
    onSuccess: (session) => {
      setPreviewRequest(null)
      openScenarioRoute(`/review/${session.id}`)
    },
    onError: closeReservedScenarioTab,
  })

  function reserveScenarioTab() {
    reservedScenarioTabRef.current = window.open('about:blank', '_blank')
  }

  function closeReservedScenarioTab() {
    const tab = reservedScenarioTabRef.current
    reservedScenarioTabRef.current = null
    if (tab && !tab.closed) tab.close()
  }

  function openScenarioRoute(path: string) {
    const url = new URL(path, window.location.origin).toString()
    const reservedTab = reservedScenarioTabRef.current
    reservedScenarioTabRef.current = null

    if (reservedTab && !reservedTab.closed) {
      reservedTab.opener = null
      reservedTab.location.href = url
      reservedTab.focus()
      return
    }

    const openedTab = window.open(url, '_blank')
    if (openedTab) {
      openedTab.opener = null
      return
    }

    navigate(path)
  }

  if (isLoading) return <ScenarioListSkeleton />
  if (isError) return <ErrorState title="Could not load scenarios" description={error.message} />
  if (!data?.length) return <EmptyState title="No scenarios here yet" description="This module does not have any published scenarios yet." />

  function proceedFromPreview() {
    if (!previewRequest) return
    const { difficulty, action } = previewRequest
    reserveScenarioTab()
    if (action === 'review') {
      reviewMutation.mutate(difficulty)
      return
    }
    if (action === 'retry') {
      retryMutation.mutate(difficulty)
      return
    }
    startMutation.mutate(difficulty)
  }

  const isProceeding = startMutation.isPending || retryMutation.isPending || reviewMutation.isPending

  return (
    <div className="flex flex-col gap-3">
      {startMutation.error ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {startMutation.error.message}
        </div>
      ) : null}
      {retryMutation.error ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {retryMutation.error.message}
        </div>
      ) : null}
      {reviewMutation.error ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {reviewMutation.error.message}
        </div>
      ) : null}
      {data.map((scenario, index) => (
        <ScenarioSkillFocusCard
          key={scenario.id}
          scenario={scenario}
          topicNumber={index + 1}
          onDifficultyAction={(selectedScenario, difficulty, action) =>
            setPreviewRequest({ scenario: selectedScenario, difficulty, action })
          }
        />
      ))}
      {previewRequest ? (
        <SkillFocusPreviewModal
          scenario={previewRequest.scenario}
          difficulty={previewRequest.difficulty}
          action={previewRequest.action}
          isProceeding={isProceeding}
          onClose={() => {
            if (!isProceeding) setPreviewRequest(null)
          }}
          onProceed={proceedFromPreview}
        />
      ) : null}
    </div>
  )
}

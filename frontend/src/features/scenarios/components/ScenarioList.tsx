import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { ScenarioSkillFocusCard } from '@/features/scenarios/components/ScenarioSkillFocusCard'
import { SkillFocusPreviewModal } from '@/features/scenarios/components/SkillFocusPreviewModal'
import type { DifficultyAccess, DifficultyActionIntent, ScenarioSkillFocus } from '@/features/scenarios/types'
import { nextAvailableDifficultyAfter } from '@/features/scenarios/utils/difficulty'
import { invalidateScenarioProgressQueries, syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { ScenarioListSkeleton } from '@/shared/components/Skeleton'
import { useRef, useState } from 'react'

type ScenarioListProps =
  | { scope: 'lesson'; lessonId: number; source: 'lesson' }
  | {
      scope: 'module'
      moduleId: number
      source: 'module_card'
      initialScenarios?: ScenarioSkillFocus[]
      deferFetch?: boolean
    }

export function ScenarioList(props: ScenarioListProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const reservedScenarioTabRef = useRef<Window | null>(null)
  const [previewRequest, setPreviewRequest] = useState<{
    scenario: ScenarioSkillFocus
    difficulty?: DifficultyAccess
    action?: DifficultyActionIntent
    mode: 'manual' | 'gate'
  } | null>(null)
  const queryKey = props.scope === 'lesson' ? queryKeys.lessonScenarios(props.lessonId) : queryKeys.moduleScenarios(props.moduleId)
  const shouldDeferModuleFetch = props.scope === 'module' && props.deferFetch && !props.initialScenarios
  const { data, error, isError, isLoading } = useQuery({
    queryKey,
    queryFn: () => (props.scope === 'lesson' ? scenariosApi.listForLesson(props.lessonId) : scenariosApi.listForModule(props.moduleId)),
    enabled: !shouldDeferModuleFetch,
    initialData: props.scope === 'module' ? props.initialScenarios : undefined,
    staleTime: 5 * 60 * 1000,
  })
  const startMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) =>
      scenariosApi.startSession({ difficulty_instance_id: difficulty.id, source_entry_point: props.source }),
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      invalidateScenarioProgressQueries(queryClient)
      setPreviewRequest(null)
      openScenarioRoute(`/practice/${session.id}`)
    },
    onError: closeReservedScenarioTab,
  })
  const retryMutation = useMutation({
    mutationFn: (difficulty: DifficultyAccess) => {
      const priorSessionId = difficulty.active_session_id ?? difficulty.retry_session_id
      if (!priorSessionId) throw new Error('Exit the current scenario before retrying.')
      return scenariosApi.retrySession(priorSessionId)
    },
    onSuccess: (session) => {
      syncScenarioSessionInCache(queryClient, session)
      invalidateScenarioProgressQueries(queryClient)
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

  function performDifficultyAction(scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) {
    reserveScenarioTab()
    if (action === 'resume') {
      if (!difficulty.active_session_id) throw new Error('No active scenario is available to continue.')
      setPreviewRequest(null)
      openScenarioRoute(`/practice/${difficulty.active_session_id}`)
      return
    }
    if (action === 'continue') {
      const nextDifficulty = nextDifficultyAfter(scenario, difficulty)
      if (nextDifficulty && hasRequiredAccurateAttempts(difficulty)) {
        startMutation.mutate(nextDifficulty)
        return
      }
      if (difficulty.review_available && hasRequiredAccurateAttempts(difficulty)) {
        reviewMutation.mutate(difficulty)
        return
      }
      retryMutation.mutate(difficulty)
      return
    }
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

  function handleDifficultyAction(scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) {
    if (shouldOpenPreviewGate(scenario, difficulty, action)) {
      setPreviewRequest({ scenario, difficulty, action, mode: 'gate' })
      markPreviewSeen(scenario.slug)
      return
    }
    performDifficultyAction(scenario, difficulty, action)
  }

  function openManualPreview(scenario: ScenarioSkillFocus) {
    setPreviewRequest({ scenario, mode: 'manual' })
    markPreviewSeen(scenario.slug)
  }

  function proceedFromPreview() {
    if (!previewRequest) return
    const { scenario, difficulty, action } = previewRequest
    if (!difficulty || !action) {
      setPreviewRequest(null)
      return
    }
    markPreviewSeen(scenario.slug)
    performDifficultyAction(scenario, difficulty, action)
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
          scenarioNumber={playableScenarioNumber(data, index)}
          onDifficultyAction={handleDifficultyAction}
          onPreview={openManualPreview}
        />
      ))}
      {previewRequest ? (
        <SkillFocusPreviewModal
          scenario={previewRequest.scenario}
          difficulty={previewRequest.difficulty}
          action={previewRequest.action}
          isProceeding={isProceeding}
          onClose={() => {
            markPreviewSeen(previewRequest.scenario.slug)
            if (!isProceeding) setPreviewRequest(null)
          }}
          onProceed={previewRequest.mode === 'gate' ? proceedFromPreview : undefined}
        />
      ) : null}
    </div>
  )
}

function hasRequiredAccurateAttempts(difficulty: DifficultyAccess) {
  const latestAccuracy = difficulty.latest_attempt?.accuracy_rate ?? null
  const progress = difficulty.successful_attempts
    ? { mastered: difficulty.successful_attempts.count, required: difficulty.successful_attempts.required }
    : difficulty.mastered_records ?? difficulty.mastery_progress
  return latestAccuracy !== null && latestAccuracy >= 100 && progress.mastered >= progress.required
}

function nextDifficultyAfter(scenario: ScenarioSkillFocus, difficulty: DifficultyAccess) {
  return nextAvailableDifficultyAfter(scenario.difficulties, difficulty.difficulty)
}

function shouldOpenPreviewGate(scenario: ScenarioSkillFocus, difficulty: DifficultyAccess, action: DifficultyActionIntent) {
  return (
    action === 'start'
    && difficulty.difficulty === 'easy'
    && difficulty.status === 'not_started'
    && !hasSeenPreview(scenario.slug)
    && !difficulty.latest_attempt
    && !difficulty.active_session_id
    && !difficulty.retry_session_id
    && !difficulty.completion
  )
}

function previewSeenKey(slug: string) {
  return `git-it-command-preview-seen:${slug}`
}

function playableScenarioNumber(scenarios: ScenarioSkillFocus[], index: number) {
  return scenarios.slice(0, index + 1).filter((scenario) => scenario.difficulties.length > 0).length
}

function hasSeenPreview(slug: string) {
  return window.localStorage.getItem(previewSeenKey(slug)) === 'seen'
}

function markPreviewSeen(slug: string) {
  window.localStorage.setItem(previewSeenKey(slug), 'seen')
}

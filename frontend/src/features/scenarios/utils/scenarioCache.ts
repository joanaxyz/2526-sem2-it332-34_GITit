import type { QueryClient } from '@tanstack/react-query'

import type { ScenarioSession } from '@/features/practice/types'
import type { Difficulty, DifficultyStatus, LatestAttemptStats, ScenarioSkillFocus } from '@/features/scenarios/types'

const scenarioSessionSyncChannel = 'git-it:scenario-session-sync'
const scenarioListQueryKeys = new Set(['lesson-scenarios', 'unit-scenarios'])
const difficultyOrder: Difficulty[] = ['easy', 'medium', 'hard']

type ScenarioSessionSyncMessage = {
  type: 'scenario-session-updated'
  session: ScenarioSession
}

export function syncScenarioSessionInCache(
  queryClient: QueryClient,
  session: ScenarioSession,
  options: { broadcast?: boolean } = {},
) {
  applyScenarioSessionToCache(queryClient, session)
  if (options.broadcast !== false && !session.review_mode) {
    broadcastScenarioSessionSync(session)
  }
}

export function subscribeToScenarioSessionSync(queryClient: QueryClient) {
  if (typeof window === 'undefined') return () => {}

  const handleMessage = (message: unknown) => {
    if (!isScenarioSessionSyncMessage(message)) return
    syncScenarioSessionInCache(queryClient, message.session, { broadcast: false })
    void queryClient.invalidateQueries({ queryKey: ['units'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
  }

  const channel = typeof BroadcastChannel !== 'undefined'
    ? new BroadcastChannel(scenarioSessionSyncChannel)
    : null
  const handleBroadcastMessage = (event: MessageEvent<unknown>) => handleMessage(event.data)
  channel?.addEventListener('message', handleBroadcastMessage)

  const handleStorage = (event: StorageEvent) => {
    if (event.key !== scenarioSessionSyncChannel || !event.newValue) return
    try {
      handleMessage(JSON.parse(event.newValue))
    } catch {
      // Ignore malformed cross-tab messages from older app versions.
    }
  }
  window.addEventListener('storage', handleStorage)

  return () => {
    channel?.removeEventListener('message', handleBroadcastMessage)
    channel?.close()
    window.removeEventListener('storage', handleStorage)
  }
}

function applyScenarioSessionToCache(queryClient: QueryClient, session: ScenarioSession) {
  queryClient.setQueryData(['scenario-session', session.id], session)

  if (session.review_mode) return

  queryClient.setQueriesData<ScenarioSkillFocus[]>(
    {
      predicate: (query) => scenarioListQueryKeys.has(String(query.queryKey[0])),
    },
    (scenarios) => updateScenarioListWithSession(scenarios, session),
  )

  queryClient.setQueriesData<Record<string, ScenarioSkillFocus[]>>(
    {
      predicate: (query) => String(query.queryKey[0]) === 'unit-scenarios-summary',
    },
    (summary) => updateScenarioSummaryWithSession(summary, session),
  )
}

export function updateScenarioListWithSession(
  scenarios: ScenarioSkillFocus[] | undefined,
  session: ScenarioSession,
) {
  if (!scenarios?.length) return scenarios

  let matchedScenario = false
  const unlockedDifficulty = hasRequiredAccurateAttempts(session) ? nextDifficultyAfter(session.difficulty) : null

  const nextScenarios = scenarios.map((scenario) => {
    if (scenario.id !== session.scenario.id) return scenario

    matchedScenario = true
    let changed = false
    const difficulties = scenario.difficulties.map((difficulty) => {
      if (difficulty.difficulty === session.difficulty) {
        // Prefer completion info provided by the server in the session payload
        const hasSessionCompletion = Boolean(session.completion)
        const status = statusFromSession(
          session.status,
          difficulty.status,
          hasSessionCompletion || Boolean(difficulty.completion),
        )
        const latestAttempt = latestAttemptFromSession(session)
        const completedAccurateAttempt = session.status === 'completed' && latestAttempt.accuracy_rate !== null && latestAttempt.accuracy_rate >= 100
        const masteredRecords =
          session.mastery_progress ??
          (completedAccurateAttempt && difficulty.latest_attempt?.id !== session.id
            ? {
                ...difficulty.mastery_progress,
                mastered: Math.min(difficulty.mastery_progress.mastered + 1, difficulty.mastery_progress.required),
              }
            : difficulty.mastery_progress)
        const mastered = masteredRecords.mastered >= masteredRecords.required
        const activeSessionId = session.status === 'started' ? session.id : null
        const retrySessionId =
          session.status === 'started'
            ? null
            : session.status === 'failed' ||
                session.status === 'abandoned' ||
                (session.status === 'completed' && (!mastered || !completedAccurateAttempt))
            ? session.id
            : null
        const completion = session.completion ?? difficulty.completion
        const reviewAvailable = Boolean(completion) && mastered && completedAccurateAttempt

        if (
          difficulty.status === status &&
          difficulty.active_session_id === activeSessionId &&
          difficulty.retry_session_id === retrySessionId &&
          difficulty.review_available === reviewAvailable &&
          difficulty.mastery_progress === masteredRecords &&
          difficulty.completion === completion &&
          difficulty.latest_attempt === latestAttempt
        ) {
          return difficulty
        }

        changed = true
        return {
          ...difficulty,
          status,
          active_session_id: activeSessionId,
          retry_session_id: retrySessionId,
          review_available: reviewAvailable,
          mastery_progress: masteredRecords,
          mastered_records: masteredRecords,
          successful_attempts: {
            count: masteredRecords.mastered,
            required: masteredRecords.required,
          },
          completion,
          latest_attempt: latestAttempt,
        }
      }

      if (difficulty.difficulty === unlockedDifficulty && difficulty.status === 'locked') {
        changed = true
        return { ...difficulty, status: 'not_started' as DifficultyStatus }
      }

      return difficulty
    })

    return changed ? { ...scenario, difficulties } : scenario
  })

  return matchedScenario ? nextScenarios : scenarios
}

export function updateScenarioSummaryWithSession(
  summary: Record<string, ScenarioSkillFocus[]> | undefined,
  session: ScenarioSession,
) {
  if (!summary) return summary
  let changed = false
  const nextSummary = Object.fromEntries(
    Object.entries(summary).map(([unitId, scenarios]) => {
      const nextScenarios = updateScenarioListWithSession(scenarios, session)
      if (nextScenarios !== scenarios) changed = true
      return [unitId, nextScenarios ?? scenarios]
    }),
  )
  return changed ? nextSummary : summary
}

function broadcastScenarioSessionSync(session: ScenarioSession) {
  if (typeof window === 'undefined') return
  const message: ScenarioSessionSyncMessage = {
    type: 'scenario-session-updated',
    session,
  }
  if (typeof BroadcastChannel !== 'undefined') {
    const channel = new BroadcastChannel(scenarioSessionSyncChannel)
    channel.postMessage(message)
    channel.close()
  }
  try {
    window.localStorage.setItem(
      scenarioSessionSyncChannel,
      JSON.stringify({ ...message, sentAt: Date.now() }),
    )
  } catch {
    // Some browsers disable storage; BroadcastChannel is enough when available.
  }
}

function isScenarioSessionSyncMessage(value: unknown): value is ScenarioSessionSyncMessage {
  if (!value || typeof value !== 'object') return false
  const message = value as Partial<ScenarioSessionSyncMessage>
  return message.type === 'scenario-session-updated' && Boolean(message.session)
}

function nextDifficultyAfter(difficulty: Difficulty) {
  const index = difficultyOrder.indexOf(difficulty)
  return index >= 0 ? difficultyOrder[index + 1] ?? null : null
}

function latestAttemptFromSession(session: ScenarioSession): LatestAttemptStats {
  return {
    id: session.id,
    status: session.status,
    accuracy_rate: latestAttemptAccuracy(session),
    command_accurate:
      session.status === 'completed'
        ? session.counts.counted_action_total <= session.policy.min_counted_commands
        : null,
    counted_action_total: session.counts.counted_action_total,
    total_attempts: session.counts.total_attempts,
    completed_at: session.completed_at,
    ended_at: session.completed_at,
  }
}

function latestAttemptAccuracy(session: ScenarioSession) {
  if (session.status === 'started') return null
  if (session.status === 'failed' || session.status === 'abandoned') return 0
  if (session.counts.counted_action_total <= session.policy.min_counted_commands) return 100
  if (session.policy.min_counted_commands === 0) return 0
  return Math.round((session.policy.min_counted_commands / session.counts.counted_action_total) * 100)
}

function hasRequiredAccurateAttempts(session: ScenarioSession) {
  if (session.status !== 'completed') return false
  if (latestAttemptAccuracy(session) !== 100) return false
  return session.mastery_progress.mastered >= session.mastery_progress.required
}

function statusFromSession(
  sessionStatus: ScenarioSession['status'],
  currentStatus: DifficultyStatus,
  hasCompletion: boolean,
): DifficultyStatus {
  if (hasCompletion) return 'completed'
  if (sessionStatus === 'completed') return 'completed'
  if (sessionStatus === 'started') return 'in_progress'
  if (sessionStatus === 'failed') return 'failed'
  if (sessionStatus === 'abandoned') return 'abandoned'
  if (currentStatus === 'completed') return 'completed'
  if (currentStatus === 'locked') return 'locked'
  return 'not_started'
}

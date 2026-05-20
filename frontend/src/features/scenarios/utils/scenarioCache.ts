import type { QueryClient } from '@tanstack/react-query'

import type { ScenarioSession } from '@/features/practice/types'
import type { Difficulty, DifficultyStatus, LatestAttemptStats, ScenarioSkillFocus } from '@/features/scenarios/types'

const scenarioListQueryKeys = new Set(['lesson-scenarios', 'unit-scenarios'])
const difficultyOrder: Difficulty[] = ['easy', 'medium', 'hard']

export function syncScenarioSessionInCache(queryClient: QueryClient, session: ScenarioSession) {
  queryClient.setQueryData(['scenario-session', session.id], session)

  if (session.review_mode) return

  queryClient.setQueriesData<ScenarioSkillFocus[]>(
    {
      predicate: (query) => scenarioListQueryKeys.has(String(query.queryKey[0])),
    },
    (scenarios) => updateScenarioListWithSession(scenarios, session),
  )
}

export function updateScenarioListWithSession(
  scenarios: ScenarioSkillFocus[] | undefined,
  session: ScenarioSession,
) {
  if (!scenarios?.length) return scenarios

  let matchedScenario = false
  const unlockedDifficulty = session.status === 'completed' ? nextDifficultyAfter(session.difficulty) : null

  const nextScenarios = scenarios.map((scenario) => {
    if (scenario.id !== session.scenario.id) return scenario

    matchedScenario = true
    let changed = false
    const difficulties = scenario.difficulties.map((difficulty) => {
      if (difficulty.difficulty === session.difficulty) {
        const status = statusFromSession(session.status, difficulty.status)
        const activeSessionId = session.status === 'started' ? session.id : null
        const retrySessionId =
          session.status === 'failed' || session.status === 'abandoned'
            ? session.id
            : difficulty.retry_session_id
        const completion =
          session.status === 'completed'
            ? {
                first_attempt_star: session.first_attempt_star_eligible,
                counted_action_total: session.counts.counted_action_total,
                completed_at: session.completed_at ?? new Date().toISOString(),
              }
            : difficulty.completion
        const latestAttempt = latestAttemptFromSession(session)

        if (
          difficulty.status === status &&
          difficulty.active_session_id === activeSessionId &&
          difficulty.retry_session_id === retrySessionId &&
          difficulty.review_available === (session.status === 'completed' || difficulty.review_available) &&
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
          review_available: session.status === 'completed' || difficulty.review_available,
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
  if (session.status !== 'completed') return null
  if (session.counts.counted_action_total <= session.policy.min_counted_commands) return 100
  if (session.policy.min_counted_commands === 0) return 0
  return Math.round((session.policy.min_counted_commands / session.counts.counted_action_total) * 100)
}

function statusFromSession(
  sessionStatus: ScenarioSession['status'],
  currentStatus: DifficultyStatus,
): DifficultyStatus {
  if (sessionStatus === 'completed') return 'completed'
  if (sessionStatus === 'started') return 'in_progress'
  if (sessionStatus === 'failed') return 'failed'
  if (sessionStatus === 'abandoned') return 'abandoned'
  if (currentStatus === 'completed') return 'completed'
  if (currentStatus === 'locked') return 'locked'
  return 'not_started'
}

import { useMutation, useQueryClient } from '@tanstack/react-query'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { reviewApi } from '@/features/review/api/reviewApi'
import {
  invalidateScenarioProgressQueries,
  syncScenarioSessionInCache,
  updateScenarioSessionCache,
} from '@/features/scenarios/utils/scenarioCache'
import type { CommandResponse, ScenarioSession } from '@/features/practice/types'
import { queryKeys } from '@/shared/api/queryKeys'

export function useCommandSubmission(sessionId: number, reviewMode: boolean) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (command: string) =>
      reviewMode ? reviewApi.submitCommand(sessionId, command) : practiceApi.submitCommand(sessionId, command),
    onSuccess: (response) => {
      const updatedSession = mergeCommandStepIntoSession(queryClient, response)
      updateScenarioSessionCache(queryClient, updatedSession)

      if (!reviewMode && response.session.status !== 'started') {
        syncScenarioSessionInCache(queryClient, updatedSession)
        invalidateScenarioProgressQueries(queryClient)
      }
    },
  })
}

function mergeCommandStepIntoSession(
  queryClient: ReturnType<typeof useQueryClient>,
  response: CommandResponse,
): ScenarioSession {
  const previous = queryClient.getQueryData<ScenarioSession>(queryKeys.scenarioSession(response.session.id))
  const priorSteps = previous?.steps ?? []
  const step = {
    id: response.step.id,
    command_text: response.step.command_text,
    terminal_output: response.step.terminal_output,
    result_category: response.step.result_category,
    command_classification: response.step.command_classification,
    contextual_feedback: response.step.contextual_feedback,
    created_at: response.step.created_at,
  }

  const hasCompletion = Object.prototype.hasOwnProperty.call(response.session, 'completion')
  const hasNextDifficulty = Object.prototype.hasOwnProperty.call(response.session, 'next_difficulty')
  const session: ScenarioSession = previous
    ? {
        ...previous,
        ...response.session,
        counts: {
          ...previous.counts,
          ...response.session.counts,
        },
        mastery_progress: response.session.mastery_progress ?? previous.mastery_progress,
        mastered_records: response.session.mastered_records ?? previous.mastered_records,
        completion: hasCompletion ? response.session.completion ?? null : previous.completion,
        next_difficulty: hasNextDifficulty ? response.session.next_difficulty ?? null : previous.next_difficulty,
      }
    : (response.session as ScenarioSession)

  return {
    ...session,
    steps: priorSteps.some((item) => item.id === step.id) ? priorSteps : [...priorSteps, step],
  }
}

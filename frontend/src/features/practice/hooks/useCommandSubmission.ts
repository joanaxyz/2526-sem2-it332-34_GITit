import { useMutation, useQueryClient } from '@tanstack/react-query'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { reviewApi } from '@/features/review/api/reviewApi'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import type { CommandResponse, ScenarioSession } from '@/features/practice/types'

export function useCommandSubmission(sessionId: number, reviewMode: boolean) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (command: string) =>
      reviewMode ? reviewApi.submitCommand(sessionId, command) : practiceApi.submitCommand(sessionId, command),
    onSuccess: (response) => {
      syncScenarioSessionInCache(queryClient, mergeCommandStepIntoSession(queryClient, response))
      if (!reviewMode) void queryClient.invalidateQueries({ queryKey: ['modules'] })
    },
  })
}

function mergeCommandStepIntoSession(queryClient: ReturnType<typeof useQueryClient>, response: CommandResponse) {
  const previous = queryClient.getQueryData<ScenarioSession>(['scenario-session', response.session.id])
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

  return {
    ...response.session,
    steps: priorSteps.some((item) => item.id === step.id) ? priorSteps : [...priorSteps, step],
  }
}

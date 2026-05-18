import { useMutation, useQueryClient } from '@tanstack/react-query'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { reviewApi } from '@/features/review/api/reviewApi'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'

export function useCommandSubmission(sessionId: number, reviewMode: boolean) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (command: string) =>
      reviewMode ? reviewApi.submitCommand(sessionId, command) : practiceApi.submitCommand(sessionId, command),
    onSuccess: (response) => syncScenarioSessionInCache(queryClient, response.session),
  })
}

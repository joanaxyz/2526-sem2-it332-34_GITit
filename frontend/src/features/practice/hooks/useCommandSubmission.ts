import { useMutation } from '@tanstack/react-query'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { reviewApi } from '@/features/review/api/reviewApi'

export function useCommandSubmission(sessionId: number, reviewMode: boolean) {
  return useMutation({
    mutationFn: (command: string) =>
      reviewMode ? reviewApi.submitCommand(sessionId, command) : practiceApi.submitCommand(sessionId, command),
  })
}

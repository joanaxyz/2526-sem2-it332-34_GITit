import { apiRequest } from '@/shared/api/httpClient'
import type { CommandResponse, ScenarioSession } from '@/features/practice/types'

export const reviewApi = {
  startReviewSession(difficultyInstanceId: number) {
    return apiRequest<ScenarioSession>('/review/sessions/', {
      method: 'POST',
      body: JSON.stringify({ difficulty_instance_id: difficultyInstanceId, source_entry_point: 'review' }),
    })
  },
  submitCommand(sessionId: number, command: string) {
    return apiRequest<CommandResponse>(`/review/sessions/${sessionId}/commands/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
}

import { apiRequest } from '@/shared/api/httpClient'
import type { CommandResponse, PracticeSession } from '@/features/practice/types'
import type { PracticeStartPayload } from '@/features/scenarios/api/scenariosApi'

export const reviewApi = {
  startReviewSession(payload: PracticeStartPayload) {
    return apiRequest<PracticeSession>('/review/sessions/', {
      method: 'POST',
      body: JSON.stringify({ ...payload, source_entry_point: 'review' }),
    })
  },
  submitCommand(sessionId: number, command: string) {
    return apiRequest<CommandResponse>(`/review/sessions/${sessionId}/commands/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
}

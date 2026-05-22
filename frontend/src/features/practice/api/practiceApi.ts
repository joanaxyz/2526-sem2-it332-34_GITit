import { apiRequest } from '@/shared/api/httpClient'
import type { CommandResponse, InspectionAnswerResponse, ScenarioSession } from '@/features/practice/types'

export const practiceApi = {
  getSession(sessionId: number) {
    return apiRequest<ScenarioSession>(`/scenarios/sessions/${sessionId}/`)
  },
  submitCommand(sessionId: number, command: string) {
    return apiRequest<CommandResponse>(`/scenarios/sessions/${sessionId}/commands/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
  submitInspectionAnswer(sessionId: number, answer: Record<string, unknown>) {
    return apiRequest<InspectionAnswerResponse>(`/scenarios/sessions/${sessionId}/inspection-answer/`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    })
  },
}

import { apiRequest } from '@/shared/api/httpClient'
import type { CommandResponse, PracticeSession } from '@/features/practice/types'

export const practiceApi = {
  getSession(sessionId: number) {
    return apiRequest<PracticeSession>(`/scenarios/sessions/${sessionId}/`)
  },
  submitCommand(sessionId: number, command: string) {
    return apiRequest<CommandResponse>(`/scenarios/sessions/${sessionId}/commands/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
  createFile(sessionId: number, input: { path: string; content: string }) {
    return apiRequest<PracticeSession>(`/scenarios/sessions/${sessionId}/files/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  writeFile(sessionId: number, input: { path: string; content: string }) {
    return apiRequest<PracticeSession>(`/scenarios/sessions/${sessionId}/files/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
}

import { apiRequest } from '@/shared/api/httpClient'
import type { ChallengeCommandResponse, ChallengeRun } from '@/shared/level/types'

export const challengeRunsApi = {
  getRun(runId: number) {
    return apiRequest<ChallengeRun>(`/challenge-runs/${runId}/`)
  },
  submitCommand(runId: number, command: string) {
    return apiRequest<ChallengeCommandResponse>(`/challenge-runs/${runId}/submit-command/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
  createFile(runId: number, input: { path: string; content: string }) {
    return apiRequest<ChallengeRun>(`/challenge-runs/${runId}/files/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  writeFile(runId: number, input: { path: string; content: string }) {
    return apiRequest<ChallengeRun>(`/challenge-runs/${runId}/files/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
}

import { apiRequest } from '@/shared/api/httpClient'
import type {
  AdventureCommandResponse,
  AdventureHintResponse,
  AdventureRun,
} from '@/features/command-adventures/types'

export const commandAdventuresApi = {
  startRun(adventureSlug: string) {
    return apiRequest<AdventureRun>(`/command-adventures/${adventureSlug}/runs/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
  getRun(runId: number) {
    return apiRequest<AdventureRun>(`/adventure-runs/${runId}/`)
  },
  submitCommand(runId: number, command: string) {
    return apiRequest<AdventureCommandResponse>(`/adventure-runs/${runId}/submit-command/`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    })
  },
  createFile(runId: number, input: { path: string; content: string }) {
    return apiRequest<AdventureRun>(`/adventure-runs/${runId}/files/`, {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  writeFile(runId: number, input: { path: string; content: string }) {
    return apiRequest<AdventureRun>(`/adventure-runs/${runId}/files/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
  useHint(runId: number) {
    return apiRequest<AdventureHintResponse>(`/adventure-runs/${runId}/use-hint/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
  finishRun(runId: number) {
    return apiRequest<AdventureRun>(`/adventure-runs/${runId}/finish/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
}

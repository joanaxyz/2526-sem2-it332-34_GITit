import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type CommandIntroduction = ApiSchemas['CommandIntroductionResponse']

export const commandIntroductionsApi = {
  complete(runId: number, token: string) {
    return apiOperationRequest<'command_introduction_complete', ApiSchemas['IntroductionCompleteResponse']>(
      'command_introduction_complete',
      `/adventure-tier-runs/${runId}/introduction/complete/`, { body: { token } })
  },
}

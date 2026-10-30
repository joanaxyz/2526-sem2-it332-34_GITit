import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type CommandIntroduction = ApiSchemas['CommandIntroductionResponse']
export type GuideElsewhere = ApiSchemas['GuideElsewhere']
export type Tip = ApiSchemas['Tip']

export const commandIntroductionsApi = {
  complete(runId: number, token: string) {
    return apiOperationRequest<'command_introduction_complete', ApiSchemas['TeachingResponse']>(
      'command_introduction_complete',
      `/adventure-tier-runs/${runId}/introduction/complete/`, { body: { token } })
  },
}

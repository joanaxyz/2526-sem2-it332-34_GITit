import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { StatsSummary } from '@/features/stats/types'

export type StatsSummaryResult = ApiSchemas['StatsSummaryResponse'] & StatsSummary

export const statsApi = {
  summary() {
    return apiOperationRequest<'progress_stats_retrieve', StatsSummaryResult>('progress_stats_retrieve', '/progress/stats/')
  },
}

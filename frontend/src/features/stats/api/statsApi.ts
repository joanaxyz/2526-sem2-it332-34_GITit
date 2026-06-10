import { apiRequest } from '@/shared/api/httpClient'
import type { StatsSummary } from '@/features/stats/types'

export const statsApi = {
  summary() {
    return apiRequest<StatsSummary>('/progress/stats/')
  },
}

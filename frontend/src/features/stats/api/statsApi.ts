import { apiOperationRequest } from '@/shared/api/httpClient'

export const statsApi = {
  summary() {
    return apiOperationRequest('progress_stats_retrieve', '/progress/stats/')
  },
}

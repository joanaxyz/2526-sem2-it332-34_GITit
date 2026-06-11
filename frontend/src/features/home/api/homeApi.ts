import { apiRequest } from '@/shared/api/httpClient'
import type { HomeSummary } from '@/features/home/types'

export const homeApi = {
  /** Backend endpoint keeps its historical "dashboard" name. */
  summary() {
    return apiRequest<HomeSummary>('/progress/dashboard/')
  },
}

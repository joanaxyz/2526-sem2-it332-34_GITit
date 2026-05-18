import { apiRequest } from '@/shared/api/httpClient'
import type { DashboardSummary } from '@/features/dashboard/types'

export const dashboardApi = {
  summary() {
    return apiRequest<DashboardSummary>('/progress/dashboard/')
  },
}

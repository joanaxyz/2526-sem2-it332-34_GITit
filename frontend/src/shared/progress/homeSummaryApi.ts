import { apiOperationRequest } from '@/shared/api/httpClient'

export const homeSummaryApi = {
  /** Backend endpoint keeps its historical "dashboard" URL, but the frontend names it by domain purpose. */
  summary() {
    return apiOperationRequest('progress_dashboard_retrieve', '/progress/dashboard/')
  },
}

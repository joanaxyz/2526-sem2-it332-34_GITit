import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { HomeSummary } from '@/shared/progress/types'

export type HomeSummaryResult = ApiSchemas['DashboardSummaryResponse'] & HomeSummary

export const homeSummaryApi = {
  /** Backend endpoint keeps its historical "dashboard" URL, but the frontend names it by domain purpose. */
  summary() {
    return apiOperationRequest<'progress_dashboard_retrieve', HomeSummaryResult>('progress_dashboard_retrieve', '/progress/dashboard/')
  },
}

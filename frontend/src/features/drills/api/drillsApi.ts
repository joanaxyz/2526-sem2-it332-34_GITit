import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { DrillPlan, DrillProgress, DrillResume } from '@/features/drills/types'

export const drillsApi = {
  getPlan(levelId: number) {
    return apiOperationRequest<'adventure_levels_drill_retrieve', DrillPlan>(
      'adventure_levels_drill_retrieve',
      `/adventure-levels/${levelId}/drill/`,
    )
  },
  saveRun(levelId: number, body: ApiRequestBody<'adventure_levels_drill_run_update'>) {
    return apiOperationRequest<'adventure_levels_drill_run_update', { resume: DrillResume | null }>(
      'adventure_levels_drill_run_update',
      `/adventure-levels/${levelId}/drill/run/`,
      { body },
    )
  },
  discardRun(levelId: number) {
    return apiOperationRequest<'adventure_levels_drill_run_destroy', { resume: null }>(
      'adventure_levels_drill_run_destroy',
      `/adventure-levels/${levelId}/drill/run/`,
    )
  },
  reportSession(levelId: number, body: ApiRequestBody<'adventure_levels_drill_results_create'>) {
    return apiOperationRequest<
      'adventure_levels_drill_results_create',
      { progress: DrillProgress }
    >('adventure_levels_drill_results_create', `/adventure-levels/${levelId}/drill/results/`, {
      body,
    })
  },
}

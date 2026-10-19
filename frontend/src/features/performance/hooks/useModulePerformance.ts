import { useQuery } from '@tanstack/react-query'

import { performanceApi } from '@/features/performance/api/performanceApi'
import { queryKeys } from '@/shared/api/queryKeys'

/**
 * Overall and per-module practice metrics for Arcane Spire Modules 1–4.
 *
 * Fetched on demand by Home Progress's practice record, so the hub never
 * waits on this request.
 */
export function useModulePerformance() {
  return useQuery({
    queryKey: queryKeys.performanceSummary,
    queryFn: performanceApi.summary,
    staleTime: 60_000,
  })
}

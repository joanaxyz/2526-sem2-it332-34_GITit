import { useQuery } from '@tanstack/react-query'

import { performanceApi } from '@/features/performance/api/performanceApi'
import { queryKeys } from '@/shared/api/queryKeys'

/**
 * Module-level practice metrics for the main story's first four modules.
 *
 * Fetched on demand rather than with the rest of Home: only the Overview's
 * "Run results" view needs it, so the hub never waits on this request.
 */
export function useModulePerformance() {
  return useQuery({
    queryKey: queryKeys.performanceSummary,
    queryFn: performanceApi.summary,
    staleTime: 60_000,
  })
}

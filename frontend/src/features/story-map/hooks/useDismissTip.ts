import { useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { commandIntroductionsApi } from '@/features/story-map/api/commandIntroductionsApi'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { updateTierRunCache } from '@/features/story-map/utils/tierRunCache'
import { queryKeys } from '@/shared/api/queryKeys'

/** Dismisses a tip for good. It leaves the run at once; if saving fails, the
 * next run payload simply offers it again. */
export function useDismissTip(runId: number) {
  const queryClient = useQueryClient()
  return useCallback((key: string) => {
    const current = queryClient.getQueryData<TierRun>(queryKeys.adventureTierRun(runId))
    if (current) {
      updateTierRunCache(queryClient, { ...current, tips: current.tips.filter((tip) => tip.key !== key) })
    }
    void commandIntroductionsApi.dismissTip(key).catch(() => undefined)
  }, [queryClient, runId])
}

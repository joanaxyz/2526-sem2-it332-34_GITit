import { useEffect } from 'react'
import type { NavigateFunction } from 'react-router-dom'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { mapUrlForRun } from '@/features/story-map/components/tierWorkspaceLayout'

/** A run the learner left is kept as abandoned (so it counts as a started
 * session) but has nothing to resume or review, so its URL returns to the map. */
export function useLeaveAbandonedRun(run: TierRun | null | undefined, navigate: NavigateFunction) {
  useEffect(() => {
    if (run?.status === 'abandoned') navigate(mapUrlForRun(run), { replace: true })
  }, [navigate, run])
}

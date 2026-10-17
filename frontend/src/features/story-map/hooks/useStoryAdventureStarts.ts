import { useMutation, useQueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import type { AdventureLevelSummary } from '@/features/story-map/types'
import { syncTierRunInCache } from '@/features/story-map/utils/tierRunCache'

export function useStoryAdventureStarts({
  hasCompanion,
  onCompanionRequired,
  onOpenAdventure,
  onTierRunStarted,
}: {
  hasCompanion: boolean
  onCompanionRequired: () => void
  onOpenAdventure: (level: AdventureLevelSummary) => void
  onTierRunStarted: (runId: number) => void
}) {
  const queryClient = useQueryClient()
  const startTierRunMutation = useMutation({
    mutationFn: ({ tierId, replay }: { tierId: number; replay?: boolean }) =>
      tierRunsApi.startRun(tierId, replay ? { replay: true } : undefined),
    onSuccess: (run) => {
      syncTierRunInCache(queryClient, run)
      onTierRunStarted(run.id)
    },
  })

  function requireCompanion(action: () => void) {
    if (!hasCompanion) {
      onCompanionRequired()
      return
    }
    action()
  }

  return {
    startTierRunMutation,
    openAdventure: (level: AdventureLevelSummary) =>
      requireCompanion(() => onOpenAdventure(level)),
    startTier: (tierId: number, replay: boolean) =>
      requireCompanion(() => startTierRunMutation.mutate({ tierId, replay })),
  }
}

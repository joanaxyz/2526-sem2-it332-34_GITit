import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierRunAssetManifest } from '@/features/story-map/utils/tierBattle'
import { useBattleAssetGate } from '@/shared/battle/hooks/useBattleAssetGate'

/** Hold Tier entry until its deterministic battle roster and companion are decoded. */
export function useTierRunAssets({
  run,
  companionSlug,
  enabled,
}: {
  run: TierRun | null | undefined
  companionSlug: string
  enabled: boolean
}): boolean {
  const entryKey = run ? `tier:${run.id}:${companionSlug}` : null
  return useBattleAssetGate({
    entryKey,
    enabled,
    buildManifest: () => (run ? tierRunAssetManifest(run, companionSlug) : null),
  })
}

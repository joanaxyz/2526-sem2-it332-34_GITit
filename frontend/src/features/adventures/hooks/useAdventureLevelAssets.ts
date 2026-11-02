import type { AdventureRun } from '@/features/adventures/types'
import { adventureLevelAssetManifest } from '@/features/adventures/utils/adventureLevelAssets'
import { useBattleAssetGate } from '@/shared/battle/hooks/useBattleAssetGate'

/**
 * Holds the level entry until its art is decoded.
 *
 * Sprite sheets and the chapter backdrop are CSS `background-image`s, so without
 * this the workspace paints an empty stage and the companion, the foe and the
 * arena fade in over the next several frames.
 *
 * The manifest is captured once, at entry: a wave swap re-seeds the encounter
 * mid-run and re-gating there would drop the learner back onto a loading screen
 * with a live terminal behind it. The incoming wave's art is instead awaited by
 * the encounter choreography, which already hides the foe until its entrance.
 */
export function useAdventureLevelAssets({
  run,
  companionSlug,
  enabled,
}: {
  run: AdventureRun | undefined
  companionSlug: string
  /** False while the equipped companion is still unknown - warming the default
   *  companion's sheets would warm art this level never shows. */
  enabled: boolean
}): boolean {
  const entryKey = run?.current_attempt ? `adventure:${run.id}:${companionSlug}` : null
  return useBattleAssetGate({
    entryKey,
    enabled,
    buildManifest: () => (run ? adventureLevelAssetManifest(run, companionSlug) : null),
  })
}

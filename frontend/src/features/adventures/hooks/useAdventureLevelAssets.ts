import { useEffect, useRef, useState } from 'react'

import type { AdventureRun } from '@/features/adventures/types'
import { adventureLevelAssetManifest } from '@/features/adventures/utils/adventureLevelAssets'
import { battleAssetsWarm, warmBattleAssets } from '@/shared/battle/battleAssets'
import type { BattleAssetManifest } from '@/shared/battle/battleAssets'

/**
 * Past this the wait has cost more than the pop it prevents. The workspace opens
 * with whatever has arrived and the rest keeps decoding in the background.
 */
const LEVEL_ASSET_BUDGET_MS = 8000

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
  const manifestRef = useRef<BattleAssetManifest | null>(null)
  if (!manifestRef.current && enabled && run?.current_attempt) {
    manifestRef.current = adventureLevelAssetManifest(run, companionSlug)
  }
  const manifest = manifestRef.current
  const [warm, setWarm] = useState(() => (manifest ? battleAssetsWarm(manifest) : false))

  useEffect(() => {
    if (!manifest || warm) return undefined
    // A level revisited in the same session is already decoded; opening it
    // behind a loading screen again would be a flicker of its own.
    if (battleAssetsWarm(manifest)) {
      setWarm(true)
      return undefined
    }

    let active = true
    void warmBattleAssets(manifest, { timeoutMs: LEVEL_ASSET_BUDGET_MS }).then(() => {
      if (active) setWarm(true)
    })
    return () => {
      active = false
    }
  }, [manifest, warm])

  // No attempt on stage yet: nothing to paint, so nothing to hold back.
  if (!run?.current_attempt) return true
  return warm
}

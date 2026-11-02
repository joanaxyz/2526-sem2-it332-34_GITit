import { useMemo } from 'react'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierBattleEncounter } from '@/features/story-map/utils/tierBattle'
import { BattleStage } from '@/shared/battle/components/BattleStage'
import { GameplayBattlePanel } from '@/shared/battle/components/GameplayBattlePanel'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'

/** RuneBound encounter stage, sized consistently with the Arcane Spire. */
export function TierBattlePanel({
  run,
  director,
}: {
  run: TierRun
  director: BattleDirector
}) {
  const maxHp = Math.max(1, run.counts.maximum_counted_commands)
  const runId = run.id
  const tierId = run.tier.id
  const adventureLevelId = run.tier.adventure_level_id
  const variantId = run.variant.id
  const storySlug = run.story?.slug
  const storyWorldSlug = run.story?.world_slug
  const encounter = useMemo(
    () => tierBattleEncounter({
      runId,
      tierId,
      adventureLevelId,
      variantId,
      storySlug,
      storyWorldSlug,
      maxHp,
    }),
    [adventureLevelId, maxHp, runId, storySlug, storyWorldSlug, tierId, variantId],
  )
  const { storyWorld, encounterKey, roster } = encounter
  const playerHp = Math.max(0, run.counts.remaining_counted_commands)

  useBattleEncounterSetup({
    director,
    storyWorldSlug: storyWorld.slug,
    encounterKey,
    roster,
    entry: 'run',
    travelOnEncounterChange: false,
    playerHp,
    playerMaxHp: maxHp,
  })

  return (
    <GameplayBattlePanel className="gameplay-battle-slot">
      <BattleStage
        director={director}
        storyWorldSlug={storyWorld.slug}
        className="h-full w-full"
      />
    </GameplayBattlePanel>
  )
}

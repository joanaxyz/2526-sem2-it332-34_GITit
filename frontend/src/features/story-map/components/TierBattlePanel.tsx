import { useMemo } from 'react'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { BattleStage } from '@/shared/battle/components/BattleStage'
import { GameplayBattlePanel } from '@/shared/battle/components/GameplayBattlePanel'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'
import { getStoryWorld } from '@/shared/story-worlds/registry'

/** RuneBound encounter stage, sized consistently with the Arcane Spire. */
export function TierBattlePanel({
  run,
  director,
}: {
  run: TierRun
  director: BattleDirector
}) {
  const storyWorld = getStoryWorld(run.story?.world_slug ?? run.story?.slug)
  const maxHp = Math.max(1, run.counts.maximum_counted_commands)
  const playerHp = Math.max(0, run.counts.remaining_counted_commands)
  const encounterKey = `${run.id}:${run.tier.id}:${run.variant.id}`
  const roster = useMemo(
    () => clientAdventureRoster(0, 1, Object.keys(storyWorld.battle.monsters), {
      seed: `${storyWorld.slug}:${run.tier.adventure_level_id}:${run.variant.id}`,
      storyWorldSlug: storyWorld.slug,
      maxHp,
    }),
    [maxHp, run.tier.adventure_level_id, run.variant.id, storyWorld],
  )

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

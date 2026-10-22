import { useMemo } from 'react'

import { BattleStage } from '@/shared/battle/components/BattleStage'
import { GameplayBattlePanel } from '@/shared/battle/components/GameplayBattlePanel'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useBattleEncounterSetup } from '@/shared/battle/hooks/useBattleEncounterSetup'
import type { WorkspaceRun, WorkspaceScene } from '@/shared/level/workspace/types'
import { workspaceBattleEncounter } from '@/shared/level/workspace/workspaceBattle'

/** RuneBound encounter stage, sized consistently with the Arcane Spire. */
export function WorkspaceBattlePanel({
  run,
  scene,
  director,
}: {
  run: WorkspaceRun
  scene: Pick<WorkspaceScene, 'battle'>
  director: BattleDirector
}) {
  const maxHp = Math.max(1, run.counts.maximum_counted_commands)
  const runId = run.id
  const variantId = run.variant.id
  const { stageKey, levelKey } = scene.battle
  const storySlug = run.story?.slug
  const storyWorldSlug = run.story?.world_slug
  const encounter = useMemo(
    () => workspaceBattleEncounter({
      runId,
      variantId,
      battle: { stageKey, levelKey },
      storySlug,
      storyWorldSlug,
      maxHp,
    }),
    [levelKey, maxHp, runId, stageKey, storySlug, storyWorldSlug, variantId],
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

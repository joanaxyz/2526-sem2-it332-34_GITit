import type { AdventureRun } from '@/features/adventures/types'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster } from '@/shared/battle/types'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

/**
 * Who a wave stages, derived purely from the run.
 *
 * Shared so the battle panel and the level's asset warmer always name the same
 * foe: warming a monster the encounter will not show would leave the real one
 * to load at mount, which is the pop this exists to prevent.
 */
export type AdventureEncounterInput = {
  runId: number
  attemptId: number
  /** Zero-based position in the level's authored wave plan. */
  wave: number
  totalWaves: number
  /** Blue's counted-command budget, which is also the encounter's HP. */
  maxHp: number
  storyWorld: StoryWorldDef
}

export function adventureStoryWorld(run: AdventureRun): StoryWorldDef {
  return getStoryWorld(run.story?.world_slug ?? run.story?.slug)
}

export function adventureEncounterRoster(input: AdventureEncounterInput): BattleMonster[] {
  return clientAdventureRoster(
    input.wave,
    input.totalWaves,
    Object.keys(input.storyWorld.battle.monsters),
    {
      // Wave-independent base seed: clientAdventureRoster rotates by the wave
      // index so consecutive waves always show a new monster.
      seed: `${input.storyWorld.slug}:${input.runId}:${input.attemptId}`,
      storyWorldSlug: input.storyWorld.slug,
      maxHp: input.maxHp,
    },
  )
}

/** The catalog monster ids a wave stages, for asset warming. */
export function adventureEncounterSpecies(input: AdventureEncounterInput): string[] {
  return adventureEncounterRoster(input).map((monster) => monster.species)
}

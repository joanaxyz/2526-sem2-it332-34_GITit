import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { battleAssetManifest, type BattleAssetManifest } from '@/shared/battle/battleAssets'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster } from '@/shared/battle/types'
import { skillForCommand } from '@/shared/level-runtime/commandSkill'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

export type TierBattleEncounter = {
  storyWorld: StoryWorldDef
  roster: BattleMonster[]
  maxHp: number
  encounterKey: string
}

export type TierBattleEncounterInput = {
  runId: number
  tierId: number
  adventureLevelId: number
  variantId: number
  storySlug?: string | null
  storyWorldSlug?: string | null
  maxHp: number
}

/** One deterministic source of truth for both the Tier stage and its preloader. */
export function tierBattleEncounter(input: TierBattleEncounterInput): TierBattleEncounter {
  const storyWorld = getStoryWorld(input.storyWorldSlug ?? input.storySlug)
  const maxHp = Math.max(1, input.maxHp)
  return {
    storyWorld,
    maxHp,
    encounterKey: `${input.runId}:${input.tierId}:${input.variantId}`,
    roster: clientAdventureRoster(0, 1, Object.keys(storyWorld.battle.monsters), {
      seed: `${storyWorld.slug}:${input.adventureLevelId}:${input.variantId}`,
      storyWorldSlug: storyWorld.slug,
      maxHp,
    }),
  }
}

/** Every image the Tier battle can paint before the workspace becomes interactive. */
export function tierRunAssetManifest(run: TierRun, companionSlug: string): BattleAssetManifest {
  const { storyWorld, roster } = tierBattleEncounter({
    runId: run.id,
    tierId: run.tier.id,
    adventureLevelId: run.tier.adventure_level_id,
    variantId: run.variant.id,
    storySlug: run.story?.slug,
    storyWorldSlug: run.story?.world_slug,
    maxHp: run.counts.maximum_counted_commands,
  })
  const skillSlugs = [
    ...(run.tutor ? [skillForCommand(run.tutor.command_form.usage_form)] : []),
    ...run.steps.map((step) => skillForCommand(step.command_text)),
  ]
  return battleAssetManifest({
    storyWorld,
    companionSlug,
    species: roster.map((monster) => monster.species),
    skillSlugs,
  })
}

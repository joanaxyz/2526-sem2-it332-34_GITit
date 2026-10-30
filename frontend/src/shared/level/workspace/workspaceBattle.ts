import { battleAssetManifest, type BattleAssetManifest } from '@/shared/battle/battleAssets'
import { clientAdventureRoster } from '@/shared/battle/deriveBattleEvents'
import type { BattleMonster } from '@/shared/battle/types'
import { skillForCommand } from '@/shared/level-runtime/commandSkill'
import type { WorkspaceRun, WorkspaceScene } from '@/shared/level/workspace/types'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

export type WorkspaceBattleEncounter = {
  storyWorld: StoryWorldDef
  roster: BattleMonster[]
  maxHp: number
  encounterKey: string
}

export type WorkspaceBattleEncounterInput = {
  runId: number
  variantId: number
  battle: WorkspaceScene['battle']
  storySlug?: string | null
  storyWorldSlug?: string | null
  maxHp: number
}

/** One deterministic source of truth for both the battle stage and its preloader. */
export function workspaceBattleEncounter(input: WorkspaceBattleEncounterInput): WorkspaceBattleEncounter {
  const storyWorld = getStoryWorld(input.storyWorldSlug ?? input.storySlug)
  const maxHp = Math.max(1, input.maxHp)
  return {
    storyWorld,
    maxHp,
    encounterKey: `${input.runId}:${input.battle.stageKey}:${input.variantId}`,
    roster: clientAdventureRoster(0, 1, Object.keys(storyWorld.battle.monsters), {
      seed: `${storyWorld.slug}:${input.battle.levelKey}:${input.variantId}`,
      storyWorldSlug: storyWorld.slug,
      maxHp,
    }),
  }
}

/**
 * Every image the battle can paint before the workspace becomes interactive:
 * the roster, the companion, and the skill art of every command already run.
 * `extraCommands` adds commands the run will show next (a command guide's form).
 */
export function workspaceRunAssetManifest(
  run: Pick<WorkspaceRun, 'id' | 'variant' | 'story' | 'counts'> & {
    steps: readonly { command_text: string }[]
  },
  battle: WorkspaceScene['battle'],
  companionSlug: string,
  extraCommands: readonly string[] = [],
): BattleAssetManifest {
  const { storyWorld, roster } = workspaceBattleEncounter({
    runId: run.id,
    variantId: run.variant.id,
    battle,
    storySlug: run.story?.slug,
    storyWorldSlug: run.story?.world_slug,
    maxHp: run.counts.maximum_counted_commands,
  })
  return battleAssetManifest({
    storyWorld,
    companionSlug,
    species: roster.map((monster) => monster.species),
    skillSlugs: [...extraCommands, ...run.steps.map((step) => step.command_text)].map((command) =>
      skillForCommand(command),
    ),
  })
}

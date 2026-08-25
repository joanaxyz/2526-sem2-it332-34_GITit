import type { SpriteDef } from '@/shared/cosmetics/types'
import type { MonsterSkin, StoryWorldDef } from '@/shared/story-worlds/types'

import { arcaneSpireWorld } from './arcane-spire'
import { frostboundCitadelWorld } from './frostbound-citadel'
import { neonBackstreetsWorld } from './neon-backstreets'

/** The default render-ready story world everyone can enter. */
export const DEFAULT_STORY_WORLD_SLUG = 'arcane-spire'

/**
 * Every render-ready story world, keyed by slug. Code-defined - no DB, no fetch.
 * Story API rows choose one via `world_slug`.
 */
export const STORY_WORLDS: Record<string, StoryWorldDef> = {
  [arcaneSpireWorld.slug]: arcaneSpireWorld,
  [frostboundCitadelWorld.slug]: frostboundCitadelWorld,
  [neonBackstreetsWorld.slug]: neonBackstreetsWorld,
}

export function getStoryWorld(slug: string | null | undefined): StoryWorldDef {
  return (slug && STORY_WORLDS[slug]) || STORY_WORLDS[DEFAULT_STORY_WORLD_SLUG]
}

export function listStoryWorlds(): StoryWorldDef[] {
  return Object.values(STORY_WORLDS)
}

/**
 * Resolve a catalog monster id to its skin in the selected story world, falling
 * back to Arcane Spire so a future story can omit redrawn monsters.
 */
export function monsterSkin(storyWorld: StoryWorldDef, species: string): MonsterSkin | null {
  return (
    storyWorld.battle.monsters[species] ??
    STORY_WORLDS[DEFAULT_STORY_WORLD_SLUG].battle.monsters[species] ??
    null
  )
}

export type StoryWorldMonsterEntry = {
  slug: string
  label: string
  skin: MonsterSkin
  portrait?: SpriteDef
}

/** Every monster skin owned by the selected story world, sorted by name. */
export function listStoryWorldMonsters(slug: string | null | undefined): StoryWorldMonsterEntry[] {
  const world = getStoryWorld(slug)
  return Object.entries(world.battle.monsters)
    .map(([monsterSlug, skin]) => ({
      slug: monsterSlug,
      label: skin.label,
      skin,
      portrait: skin.sprites.portrait ?? skin.sprites.idle,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
}

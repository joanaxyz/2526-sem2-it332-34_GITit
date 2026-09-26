import { DEFAULT_STORY_WORLD_SLUG, STORY_WORLDS } from '@/shared/story-worlds/registry'

export type StoryPreview = {
  storyMap: string
  battleBackgrounds: string[]
  monsterPoses: string[]
}

export function storyPreview(slug: string): StoryPreview | undefined {
  const world = STORY_WORLDS[slug]
  if (!world) return undefined

  const fallback = STORY_WORLDS[DEFAULT_STORY_WORLD_SLUG]
  const parallaxBackgrounds = world.battle.parallax
    ? Object.values(world.battle.parallax).map((sprite) => sprite.src)
    : undefined

  const storyMap = world.map?.background.src ?? fallback.map?.background.src
  const battleBackgrounds = world.preview?.battleBackgrounds ?? parallaxBackgrounds ?? fallback.preview?.battleBackgrounds
  const monsterPoses = world.preview?.monsterPoses ?? fallback.preview?.monsterPoses

  if (!storyMap || !battleBackgrounds?.length || !monsterPoses?.length) return undefined

  return {
    storyMap,
    battleBackgrounds,
    monsterPoses,
  }
}

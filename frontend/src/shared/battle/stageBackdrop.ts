import type { BattleStage } from '@/shared/battle/types'
import type { StoryWorldDef } from '@/shared/story-worlds/types'

/**
 * The parallax image one encounter paints behind the duel.
 *
 * A chapter can name its own backdrop through the authored stage; anything else
 * falls back to the story world's default. Shared so the asset warmer and the
 * stage itself can never disagree about which image the level is about to show.
 */
export function stageParallaxUrl(
  storyWorld: StoryWorldDef,
  stage?: BattleStage | null,
): string | null {
  const slug = stage?.parallax?.slug
  if (slug) return storyWorld.battle.parallax?.[slug]?.src ?? storyWorld.battle.backdrop.src
  return storyWorld.battle.backdrop.src
}

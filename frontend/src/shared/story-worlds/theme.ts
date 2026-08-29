import type { CSSProperties } from 'react'

import type { StoryWorldDef } from '@/shared/story-worlds/types'

export function storyWorldStyle(world: StoryWorldDef): CSSProperties {
  return {
    '--theme-primary-rgb': world.tokens.primaryRgb,
    '--theme-secondary-rgb': world.tokens.secondaryRgb,
    '--theme-accent-rgb': world.tokens.accentRgb,
    '--theme-surface-rgb': world.tokens.surfaceRgb,
    '--theme-glow-rgb': world.tokens.glowRgb,
    '--theme-spark-rgb': world.tokens.sparkRgb,
  } as CSSProperties
}

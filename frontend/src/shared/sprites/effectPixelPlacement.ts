import type { SpriteAnimation } from '@/shared/sprites/types'
import type { SpritePixelAnchor } from '@/shared/sprites/pixelBounds'

export type EffectPixelPlacement = {
  anchor: { x: number; y: number }
  bounds: { left: number; top: number; right: number; bottom: number }
}

type EffectPlayback = 'projectile' | 'target'
type EffectAnchor = 'center' | 'feet'

function median(values: number[]): number {
  const ordered = [...values].sort((a, b) => a - b)
  const middle = Math.floor(ordered.length / 2)
  return ordered.length % 2 === 1
    ? ordered[middle]
    : ((ordered[middle - 1] ?? 0) + (ordered[middle] ?? 0)) / 2
}

function clampFraction(value: number): number {
  return Math.min(1, Math.max(0, value))
}

/**
 * Browser-side equivalent of the effect-sheet processor's placement audit.
 * It lets previews align a sheet immediately, even before its measured anchor
 * has been persisted back into the story-world JSON.
 */
export function effectPlacementFromPixelAnchor(
  measured: SpritePixelAnchor | null,
  animation: Pick<SpriteAnimation, 'frameWidth' | 'frameHeight' | 'frameCount'>,
  playback: EffectPlayback,
  anchorMode: EffectAnchor,
  impactStartFrame?: number,
): EffectPixelPlacement | null {
  if (!measured) return null
  const start =
    playback === 'projectile'
      ? Math.max(0, Math.min(animation.frameCount - 1, impactStartFrame ?? animation.frameCount - 5))
      : 0
  const frames = measured.frameBounds.slice(start).filter((bounds) => bounds !== null)
  if (!frames.length) return null

  const centersX = frames.map((bounds) => (bounds.left + bounds.right + 1) / 2)
  const verticals = frames.map((bounds) =>
    anchorMode === 'feet' ? bounds.bottom + 1 : (bounds.top + bounds.bottom + 1) / 2,
  )
  const union = frames.reduce(
    (acc, bounds) => ({
      left: Math.min(acc.left, bounds.left),
      top: Math.min(acc.top, bounds.top),
      right: Math.max(acc.right, bounds.right),
      bottom: Math.max(acc.bottom, bounds.bottom),
    }),
    {
      left: animation.frameWidth,
      top: animation.frameHeight,
      right: -1,
      bottom: -1,
    },
  )
  const pad = 2

  return {
    anchor: {
      x: clampFraction(median(centersX) / animation.frameWidth),
      y: clampFraction(median(verticals) / animation.frameHeight),
    },
    bounds: {
      left: clampFraction((union.left - pad) / animation.frameWidth),
      top: clampFraction((union.top - pad) / animation.frameHeight),
      right: clampFraction((union.right + 1 + pad) / animation.frameWidth),
      bottom: clampFraction((union.bottom + 1 + pad) / animation.frameHeight),
    },
  }
}

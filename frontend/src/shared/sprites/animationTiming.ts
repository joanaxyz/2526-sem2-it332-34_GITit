import type { SpriteAnimation } from '@/shared/sprites/types'

/**
 * Time needed to reach the final frame of a non-looping sprite animation.
 *
 * A caller may provide a cap when its choreography deliberately needs to move
 * on sooner. Omit it for a one-shot that must be allowed to finish.
 */
export function animationDuration(animation: SpriteAnimation, capMs?: number): number {
  const natural = (animation.frameCount / Math.max(1, animation.fps)) * 1000 + 80
  const duration = Math.max(180, natural)
  return capMs === undefined ? duration : Math.min(capMs, duration)
}

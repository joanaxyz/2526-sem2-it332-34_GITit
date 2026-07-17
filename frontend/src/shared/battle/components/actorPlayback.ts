import { animationDuration } from '@/shared/sprites/animationTiming'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

/**
 * Shared imperative sprite playback helpers for battle actors.
 *
 * Companions and monsters both expose an `attack` animation to the battle
 * director: play one non-looping windup/release strip, then fire the gameplay
 * effect only after that strip has completed.
 */
export function playOneShotSprite(
  sprite: SpriteAnimatorHandle | null,
  animation: SpriteAnimation,
  capMs?: number,
): Promise<void> {
  return new Promise((resolve) => {
    if (!sprite) {
      resolve()
      return
    }
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      window.clearTimeout(timeout)
      resolve()
    }
    const timeout = window.setTimeout(finish, animationDuration(animation, capMs))
    sprite.setAnimation(animation, { onComplete: finish })
  })
}

function holdLastFrame(sprite: SpriteAnimatorHandle | null, animation: SpriteAnimation) {
  if (!sprite) return
  sprite.pause()
  sprite.goToFrame(animation.frameCount - 1)
}

export async function playOneShotAndHold(
  sprite: SpriteAnimatorHandle | null,
  animation: SpriteAnimation,
  capMs?: number,
): Promise<void> {
  await playOneShotSprite(sprite, animation, capMs)
  holdLastFrame(sprite, animation)
}

export async function playOneShotAndRestore(
  sprite: SpriteAnimatorHandle | null,
  animation: SpriteAnimation,
  restore: () => void,
  capMs?: number,
): Promise<void> {
  await playOneShotSprite(sprite, animation, capMs)
  restore()
}

export function finishElementAnimation(animation: Animation, ms: number): Promise<void> {
  return Promise.race([
    animation.finished.then(
      () => undefined,
      () => undefined,
    ),
    new Promise<void>((resolve) => {
      window.setTimeout(resolve, ms + 120)
    }),
  ])
}

export function readElementTranslateX(node: HTMLElement): number {
  const inline = node.style.transform
  const match = /translate(?:X)?\(([-\d.]+)px/.exec(inline)
  if (match) return Number(match[1])
  const matrix = window.getComputedStyle(node).transform
  if (matrix && matrix !== 'none') {
    const parts = matrix.match(/matrix\(([^)]+)\)/)
    if (parts) {
      const values = parts[1].split(',').map((value) => Number.parseFloat(value.trim()))
      if (values.length === 6) return values[4]
    }
  }
  return 0
}

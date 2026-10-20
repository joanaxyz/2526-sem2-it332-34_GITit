import { useEffect, useRef } from 'react'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import { warmImages } from '@/shared/sprites/preload'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'

export type MascotPose = 'idle' | 'random' | 'float' | 'fly' | 'take-off' | 'land' | 'walk' | 'run' | 'die'

const mascotAnimations = Object.fromEntries(
  (['idle', 'random', 'float', 'fly', 'take-off', 'land', 'walk', 'run', 'die'] as const).map((pose) => {
    const grid = ['random', 'fly', 'take-off', 'land'].includes(pose) ? 8 : 5
    return [pose, {
      name: `git-it-mascot.${pose}`, src: `/mascot/${pose}.png`,
      frameWidth: 256, frameHeight: 256, columns: grid, rows: grid,
      frameCount: grid * grid, fps: pose === 'take-off' || pose === 'land' ? 48 : 24,
      loop: !['random', 'take-off', 'land', 'die'].includes(pose),
    } satisfies SpriteAnimation]
  }),
) as Record<MascotPose, SpriteAnimation>

export function MascotSprite({ pose, size = 160, flip = false, idleActions = false }: {
  pose: MascotPose; size?: number; flip?: boolean
  /** Opt in to occasional ground-idle actions on the Home surface. */
  idleActions?: boolean
}) {
  const animator = useRef<SpriteAnimatorHandle>(null)

  useEffect(() => {
    if (pose !== 'idle') return
    if (!idleActions) { animator.current?.setAnimation(mascotAnimations.idle); return }

    const media = window.matchMedia?.('(prefers-reduced-motion: reduce)')
    let timer = 0
    let cancelled = false
    void warmImages([mascotAnimations.random.src])

    function schedule() {
      if (cancelled || media?.matches || document.hidden) return
      timer = window.setTimeout(() => {
        if (cancelled || media?.matches || document.hidden) return
        animator.current?.setAnimation(mascotAnimations.random, { onComplete: () => {
          if (cancelled) return
          animator.current?.setAnimation(mascotAnimations.idle)
          schedule()
        } })
      }, 8000 + Math.random() * 10000)
    }
    function reset() {
      window.clearTimeout(timer)
      animator.current?.setAnimation(mascotAnimations.idle)
      schedule()
    }
    schedule()
    media?.addEventListener('change', reset)
    document.addEventListener('visibilitychange', reset)
    return () => {
      cancelled = true
      window.clearTimeout(timer)
      media?.removeEventListener('change', reset)
      document.removeEventListener('visibilitychange', reset)
    }
  }, [pose, idleActions])

  return <SpriteAnimator ref={animator} animation={mascotAnimations[pose]} scale={size / 256}
    flipX={flip} aria-label="Git-It mascot" />
}

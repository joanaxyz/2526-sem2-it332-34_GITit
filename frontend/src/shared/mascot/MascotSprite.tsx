import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'

export type MascotPose = 'idle' | 'float' | 'fly' | 'take-off' | 'land' | 'walk' | 'run' | 'die'

const mascotAnimations = Object.fromEntries(
  (['idle', 'float', 'fly', 'take-off', 'land', 'walk', 'run', 'die'] as const).map((pose) => {
    const grid = ['fly', 'take-off', 'land'].includes(pose) ? 8 : 5
    return [pose, {
      name: `git-it-mascot.${pose}`, src: `/mascot/${pose}.png`,
      frameWidth: 256, frameHeight: 256, columns: grid, rows: grid,
      frameCount: grid * grid, fps: pose === 'take-off' || pose === 'land' ? 48 : 24,
      loop: !['take-off', 'land', 'die'].includes(pose),
    } satisfies SpriteAnimation]
  }),
) as Record<MascotPose, SpriteAnimation>

export function MascotSprite({ pose, size = 160, flip = false }: {
  pose: MascotPose; size?: number; flip?: boolean
}) {
  return <SpriteAnimator animation={mascotAnimations[pose]} scale={size / 256}
    flipX={flip} aria-label="Git-It mascot" />
}

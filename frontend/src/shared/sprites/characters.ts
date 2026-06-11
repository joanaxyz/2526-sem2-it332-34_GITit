import type { SpriteAnimation } from '@/shared/sprites/types'

/**
 * Named character animation configs. Sheets live in /public/character1/.
 * Each sheet is a 5×5 grid of 256×256 frames (1280×1280 total).
 *
 * To add a new move set, add a config here — no component changes needed.
 */
export const CHARACTER1 = {
  idle: {
    name: 'character1.idle',
    src: '/character1/idle.png',
    frameWidth: 256,
    frameHeight: 256,
    columns: 5,
    rows: 5,
    frameCount: 25,
    fps: 10,
    loop: true,
  },
  walk: {
    name: 'character1.walk',
    src: '/character1/walk.png',
    frameWidth: 256,
    frameHeight: 256,
    columns: 5,
    rows: 5,
    frameCount: 25,
    fps: 12,
    loop: true,
  },
} satisfies Record<string, SpriteAnimation>

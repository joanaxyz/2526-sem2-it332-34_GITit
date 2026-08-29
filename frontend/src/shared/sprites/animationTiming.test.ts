import { describe, expect, it } from 'vitest'

import { animationDuration } from '@/shared/sprites/animationTiming'
import type { SpriteAnimation } from '@/shared/sprites/types'

const summon: SpriteAnimation = {
  name: 'blue.summon',
  src: '/summon.png',
  frameWidth: 256,
  frameHeight: 256,
  columns: 8,
  rows: 8,
  frameCount: 64,
  fps: 28,
  loop: false,
}

describe('animationDuration', () => {
  it('allows Blue’s complete 8×8 summon sheet to play when it is not intentionally capped', () => {
    expect(animationDuration(summon)).toBeCloseTo(2365.71, 2)
  })

  it('honours an explicit choreography cap', () => {
    expect(animationDuration(summon, 1400)).toBe(1400)
  })
})

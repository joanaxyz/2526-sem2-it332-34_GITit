import { describe, expect, it } from 'vitest'

import { effectPlacementFromPixelAnchor } from '@/shared/sprites/effectPixelPlacement'
import type { SpritePixelAnchor } from '@/shared/sprites/pixelBounds'

function frame(left: number, top: number, right: number, bottom: number) {
  return {
    left,
    top,
    right,
    bottom,
    width: right - left + 1,
    height: bottom - top + 1,
    alphaPixels: 100,
  }
}

const measured: SpritePixelAnchor = {
  bounds: frame(80, 40, 180, 230),
  frameBounds: [frame(20, 100, 70, 140), frame(92, 180, 164, 228), frame(96, 184, 160, 232)],
  bottomOffset: 23,
  centerOffsetX: -2,
}

describe('effectPlacementFromPixelAnchor', () => {
  it('measures projectile placement from impact frames rather than flight frames', () => {
    const placement = effectPlacementFromPixelAnchor(
      measured,
      { frameWidth: 256, frameHeight: 256, frameCount: 3 },
      'projectile',
      'feet',
      1,
    )

    expect(placement?.anchor.x).toBeCloseTo(0.5, 2)
    expect(placement?.anchor.y).toBeGreaterThan(0.88)
    expect(placement?.bounds.left).toBeGreaterThan(0.3)
  })

  it('uses the visible centre for body-centred target effects', () => {
    const placement = effectPlacementFromPixelAnchor(
      measured,
      { frameWidth: 256, frameHeight: 256, frameCount: 3 },
      'target',
      'center',
    )

    expect(placement?.anchor.x).toBeGreaterThan(0.4)
    expect(placement?.anchor.y).toBeLessThan(0.8)
  })
})

import { describe, expect, it } from 'vitest'

import { measureImagePixelBounds, measureSpritePixelAnchor } from '@/shared/sprites/pixelBounds'

function rgba(width: number, height: number, opaquePixels: Array<[number, number]>): Uint8ClampedArray {
  const data = new Uint8ClampedArray(width * height * 4)
  for (const [x, y] of opaquePixels) {
    data[(y * width + x) * 4 + 3] = 255
  }
  return data
}

describe('pixel bounds', () => {
  it('measures visible image pixels without counting transparent canvas padding', () => {
    const data = rgba(6, 5, [
      [2, 1],
      [3, 1],
      [1, 3],
      [4, 3],
    ])

    expect(measureImagePixelBounds(data, 6, 5)).toMatchObject({
      left: 1,
      top: 1,
      right: 4,
      bottom: 3,
      width: 4,
      height: 3,
      bottomOffset: 1,
      centerOffsetX: 0,
    })
  })

  it('unions sprite frame bounds and derives a foot baseline from alpha pixels', () => {
    const data = rgba(8, 4, [
      [1, 1],
      [2, 2],
      [5, 0],
      [6, 1],
    ])

    const anchor = measureSpritePixelAnchor(data, 8, {
      frameWidth: 4,
      frameHeight: 4,
      columns: 2,
      frameCount: 2,
    })

    expect(anchor).toMatchObject({
      bottomOffset: 1,
      centerOffsetX: 0,
      bounds: {
        left: 1,
        top: 0,
        right: 2,
        bottom: 2,
      },
    })
  })
})

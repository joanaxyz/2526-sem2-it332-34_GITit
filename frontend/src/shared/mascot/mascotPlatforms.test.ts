import { describe, expect, it } from 'vitest'
import { mascotTilt, platformNear, type MascotPlatform } from './mascotPlatforms'

describe('mascot ledge selection and flight tilt', () => {
  const edge = (left: number, right: number, y: number): MascotPlatform => ({ element: document.createElement('section'), left, right, y })
  it('lands on the nearest container edge under the click', () => {
    const platforms = [edge(50, 450, 200), edge(50, 450, 320)]
    expect(platformNear(platforms, 200, 310)).toBe(platforms[1])
    expect(platformNear(platforms, 500, 310)).toBeNull()
    expect(platformNear(platforms, 200, 450)).toBeNull()
  })
  it('tilts toward travel in both directions and limits the bank angle', () => {
    expect(mascotTilt(100, -50)).toBeLessThan(0)
    expect(mascotTilt(-100, -50)).toBeGreaterThan(0)
    expect(mascotTilt(0, 1000)).toBe(30)
    expect(mascotTilt(100, 0)).toBe(0)
  })
})

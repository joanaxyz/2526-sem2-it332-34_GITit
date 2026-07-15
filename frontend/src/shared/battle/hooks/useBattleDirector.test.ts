import { describe, expect, it } from 'vitest'

import { missedSpellFloorTarget } from '@/shared/battle/hooks/useBattleDirector'

function rect(left: number, top: number, width: number, height: number) {
  return {
    left,
    top,
    width,
    height,
    right: left + width,
    bottom: top + height,
  }
}

describe('missedSpellFloorTarget', () => {
  it('lands a miss on the floor closer to the companion than the enemy', () => {
    const layerBox = rect(0, 0, 800, 320)
    const playerBox = rect(80, 130, 90, 120)
    const enemyBox = rect(620, 118, 140, 142)
    const target = missedSpellFloorTarget({
      layerBox,
      playerBox,
      enemyBox,
      floorY: 232,
    })
    const playerFrontX = playerBox.left + playerBox.width * 0.82

    expect(target.y).toBe(232)
    expect(target.x).toBeGreaterThan(playerFrontX)
    expect(target.x - playerFrontX).toBeLessThanOrEqual(150)
    expect(enemyBox.left - target.x).toBeGreaterThanOrEqual(176)
    expect(target.x).toBeLessThan((playerFrontX + enemyBox.left) / 2)
  })

  it('falls back to actor feet while keeping the splash away from a wide enemy', () => {
    const layerBox = rect(0, 0, 640, 300)
    const playerBox = rect(56, 138, 78, 112)
    const enemyBox = rect(480, 104, 300, 164)
    const target = missedSpellFloorTarget({ layerBox, playerBox, enemyBox })

    expect(target.y).toBe(enemyBox.bottom)
    expect(enemyBox.left - target.x).toBeGreaterThanOrEqual(enemyBox.width * 0.72)
    expect(target.x).toBeLessThan((playerBox.left + enemyBox.left) / 2)
  })
})

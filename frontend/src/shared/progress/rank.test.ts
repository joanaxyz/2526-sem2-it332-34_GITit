import { describe, expect, it } from 'vitest'

import { RANK_TIERS, rankForXp, rankProgressLabel } from '@/shared/progress/rank'

describe('rankForXp', () => {
  it.each([
    [0, 'Peasant'],
    [499, 'Peasant'],
    [500, 'Squire'],
    [1500, 'Knight'],
    [3000, 'Baron'],
    [4500, 'Duke'],
    [5400, 'King'],
    [6000, 'King'],
  ])('places %i XP at %s', (xp, name) => {
    expect(rankForXp(xp).tier.name).toBe(name)
  })

  it('measures progress inside the current rank', () => {
    expect(rankForXp(2250).progressPct).toBe(50)
    expect(rankForXp(6000).progressPct).toBe(100)
  })

  it('keeps the top rank reachable with every checkpoint failed and cleared in practice', () => {
    const tiers = 21 * (25 + 35 + 50) + 63 * 3 * 10
    const gates = 4 * (50 + 75 + 100)
    const practiceOnlyCheckpoints = 6 * 50

    expect(tiers + gates + 6 * 150).toBe(6000)
    expect(tiers + gates + practiceOnlyCheckpoints).toBeGreaterThanOrEqual(RANK_TIERS.at(-1)!.minXp)
  })
})

describe('rankProgressLabel', () => {
  it('reads as a total against the next rank', () => {
    expect(rankProgressLabel(rankForXp(2340))).toBe('2,340 / 3,000 XP')
  })

  it('keeps the total at the top rank', () => {
    expect(rankProgressLabel(rankForXp(5600))).toBe('5,600 XP · Max rank')
  })
})

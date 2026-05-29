import { describe, expect, it } from 'vitest'
import { computeBudgetConsumedPct } from './budget'

describe('computeBudgetConsumedPct', () => {
  it('returns 0 when used === min_threshold', () => {
    expect(computeBudgetConsumedPct(3, 3, 12)).toBe(0)
  })

  it('returns 0 when used < min_threshold', () => {
    expect(computeBudgetConsumedPct(2, 3, 12)).toBe(0)
    expect(computeBudgetConsumedPct(0, 2, 8)).toBe(0)
  })

  it('returns ~11.1 at one step past min (3,3,12)', () => {
    expect(computeBudgetConsumedPct(4, 3, 12)).toBeCloseTo(11.11, 1)
  })

  it('returns ~44.4 at 7 used (min=3, max=12) — crosses T1 at 40%', () => {
    expect(computeBudgetConsumedPct(7, 3, 12)).toBeCloseTo(44.44, 1)
  })

  it('returns 0 when used === min_threshold (2,2,8)', () => {
    expect(computeBudgetConsumedPct(2, 2, 8)).toBe(0)
  })

  it('returns 50 at (5,2,8)', () => {
    expect(computeBudgetConsumedPct(5, 2, 8)).toBe(50)
  })

  it('returns ~83.3 at (7,2,8)', () => {
    expect(computeBudgetConsumedPct(7, 2, 8)).toBeCloseTo(83.33, 1)
  })

  it('returns 100 at (8,2,8)', () => {
    expect(computeBudgetConsumedPct(8, 2, 8)).toBe(100)
  })

  it('returns > 100 when used > max_limit (no cap)', () => {
    expect(computeBudgetConsumedPct(9, 2, 8)).toBeGreaterThan(100)
  })

  it('returns 0 when denominator is 0 or negative (guard)', () => {
    expect(computeBudgetConsumedPct(5, 5, 5)).toBe(0)
    expect(computeBudgetConsumedPct(5, 6, 4)).toBe(0)
  })
})

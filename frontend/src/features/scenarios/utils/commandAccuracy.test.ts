import { describe, expect, it } from 'vitest'

import {
  commandAccuracyFromSession,
  commandAccuracyRate,
  meetsMasteryAccuracy,
  meetsProgressAccuracy,
} from './commandAccuracy'

describe('commandAccuracyRate', () => {
  it.each([
    { status: 'started' as const, counted: 0, minimum: 2, expected: null },
    { status: 'failed' as const, counted: 3, minimum: 2, expected: 0 },
    { status: 'abandoned' as const, counted: 1, minimum: 2, expected: 0 },
    { status: 'completed' as const, counted: 2, minimum: 2, expected: 100 },
    { status: 'completed' as const, counted: 3, minimum: 2, expected: 67 },
    { status: 'completed' as const, counted: 4, minimum: 2, expected: 50 },
    { status: 'completed' as const, counted: 5, minimum: 0, expected: 0 },
  ])('returns $expected for $status ($counted/$minimum)', ({ status, counted, minimum, expected }) => {
    expect(
      commandAccuracyRate({
        status,
        counted_action_total: counted,
        minimum_counted_commands: minimum,
      }),
    ).toBe(expected)
  })
})

describe('commandAccuracyFromSession', () => {
  const baseSession = {
    policy: { min_counted_commands: 3 },
    counts: { counted_action_total: 4 },
  }

  it('uses session policy snapshot fields', () => {
    expect(
      commandAccuracyFromSession({
        ...baseSession,
        status: 'completed',
      }),
    ).toBe(75)
  })

  it('returns null for in-progress sessions', () => {
    expect(
      commandAccuracyFromSession({
        ...baseSession,
        status: 'started',
      }),
    ).toBeNull()
  })

  it('returns zero for failed sessions', () => {
    expect(
      commandAccuracyFromSession({
        ...baseSession,
        status: 'failed',
      }),
    ).toBe(0)
  })
})

describe('accuracy thresholds', () => {
  it('treats 70% and above as progress', () => {
    expect(meetsProgressAccuracy(70)).toBe(true)
    expect(meetsProgressAccuracy(75)).toBe(true)
    expect(meetsProgressAccuracy(69)).toBe(false)
    expect(meetsProgressAccuracy(null)).toBe(false)
  })

  it('treats only 100% as mastery', () => {
    expect(meetsMasteryAccuracy(100)).toBe(true)
    expect(meetsMasteryAccuracy(99)).toBe(false)
    expect(meetsMasteryAccuracy(75)).toBe(false)
  })
})

import { describe, expect, it } from 'vitest'

import { kpiEvidence } from './kpiEvidence'

const rate = (numerator: number, denominator: number) => ({
  value: denominator ? (numerator / denominator) * 100 : null,
  numerator,
  denominator,
})

describe('kpiEvidence', () => {
  it.each([
    ['scr', rate(3, 10), '3 of 10 sessions completed'],
    ['car', rate(22, 125), '22 processable / 125 submitted commands'],
    ['hlcr', rate(1, 4), '1 of 4 hard sessions completed'],
    ['arc', rate(1, 10), '1 retry across 10 completed sessions'],
    ['arc', rate(5, 1), '5 retries across 1 completed session'],
    ['rta', rate(2, 3), '2 of 3 eligible retries succeeded'],
    ['retry_success_rate', rate(4, 5), '4 of 5 retry sessions completed'],
  ] as const)('%s %o reads "%s"', (key, value, text) => {
    expect(kpiEvidence(key, value)).toBe(text)
  })

  it.each([
    ['scr', 'No sessions yet'],
    ['car', 'No commands yet'],
    ['arc', 'No completed sessions yet'],
    ['rta', 'No eligible retries yet'],
  ] as const)('names the missing unit for %s', (key, text) => {
    expect(kpiEvidence(key, rate(0, 0))).toBe(text)
  })
})

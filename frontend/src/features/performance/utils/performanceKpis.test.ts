import { describe, expect, it } from 'vitest'

import { formatKpi, kpiEvidence, metricStatus } from './performanceKpis'

const rate = (numerator: number, denominator: number) => ({
  value: denominator ? (numerator / denominator) * 100 : null,
  numerator,
  denominator,
})

describe('kpiEvidence', () => {
  it('keeps zero, missing observations, reversed retry goals, and supplementary context distinct', () => {
    expect(formatKpi('scr', { value: 0, numerator: 0, denominator: 2 })).toBe('0%')
    expect(formatKpi('scr', rate(0, 0))).toBe('—')
    expect(metricStatus('scr', { value: 0, numerator: 0, denominator: 2 })).toBe('miss')
    expect(metricStatus('arc', { value: 0, numerator: 0, denominator: 2 })).toBe('met')
    expect(metricStatus('arc', { value: 2.1, numerator: 21, denominator: 10 })).toBe('miss')
    expect(metricStatus('rta', rate(0, 0))).toBe('none')
    expect(metricStatus('retry_success_rate', rate(4, 5))).toBe('none')
  })
  it.each([
    ['scr', rate(3, 10), '3 of 10 required tiers mastered'],
    ['car', rate(22, 125), '22 score points across 125 assessed tiers'],
    ['hlcr', rate(1, 4), '1 of 4 hard tiers mastered'],
    ['arc', rate(1, 10), '1 unsuccessful attempt across 10 mastered tiers'],
    ['arc', rate(5, 1), '5 unsuccessful attempts across 1 mastered tier'],
    ['rta', rate(2, 3), '2 of 3 transfer checkpoints cleared first time'],
    ['retry_success_rate', rate(4, 5), '4 of 5 recovery retries succeeded'],
  ] as const)('%s %o reads "%s"', (key, value, text) => {
    expect(kpiEvidence(key, value)).toBe(text)
  })

  it.each([
    ['scr', 'No attempted required tiers yet'],
    ['car', 'No validated command assessments yet'],
    ['arc', 'No mastered tiers yet'],
    ['rta', 'No assessed transfer checkpoints yet'],
  ] as const)('names the missing unit for %s', (key, text) => {
    expect(kpiEvidence(key, rate(0, 0))).toBe(text)
  })

  it('counts contributing learners for cohort means, and an empty cohort as missing', () => {
    expect(kpiEvidence('scr', { ...rate(150, 2), unit: 'participants' })).toBe('2 contributing learners · equally weighted')
    expect(kpiEvidence('scr', { ...rate(0, 0), unit: 'participants' })).toBe('No attempted required tiers yet')
  })
})

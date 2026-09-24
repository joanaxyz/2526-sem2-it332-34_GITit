import { describe, expect, it } from 'vitest'

import type { PerformanceModule } from '@/features/performance/types'

import { moduleColumnSeries } from './moduleColumns'

const EMPTY = { value: null, numerator: 0, denominator: 0 }

function module(overrides: Partial<PerformanceModule>): PerformanceModule {
  return {
    number: 3,
    title: 'Conflict Resolution',
    scr: EMPTY,
    hlcr: EMPTY,
    rta: EMPTY,
    retry_success_rate: EMPTY,
    arc: EMPTY,
    ...overrides,
  }
}

describe('moduleColumnSeries', () => {
  it('plots "retries that worked" from the learner retry success rate, not RTA', () => {
    const series = moduleColumnSeries([
      module({
        retry_success_rate: { value: 80, numerator: 4, denominator: 5 },
        rta: { value: 50, numerator: 1, denominator: 2 },
      }),
    ])

    expect(series.hasAnyData).toBe(true)
    expect(series.retriesThatWorked[0]).toMatchObject({
      value: 80,
      display: '80%',
      detail: '4 of 5 retries',
    })
  })

  it('treats a module with only RTA data as having no learner data', () => {
    const series = moduleColumnSeries([module({ rta: { value: 100, numerator: 1, denominator: 1 } })])

    expect(series.hasAnyData).toBe(false)
    expect(series.retriesThatWorked[0]).toMatchObject({ value: null, display: '--' })
  })
})

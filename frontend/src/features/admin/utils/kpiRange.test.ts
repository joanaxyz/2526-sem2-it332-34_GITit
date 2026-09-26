import { describe, expect, it } from 'vitest'

import { kpiRangeLabel } from './kpiRange'

const tz = 'Asia/Manila'

describe('kpiRangeLabel', () => {
  it.each([
    [undefined, 'All time'],
    [{ start_date: null, end_date: null, timezone: tz }, 'All time'],
    [{ start_date: '2026-10-01', end_date: '2026-10-10', timezone: tz }, 'Oct 1, 2026 – Oct 10, 2026'],
    [{ start_date: '2026-10-01', end_date: '2026-10-01', timezone: tz }, 'Oct 1, 2026'],
    [{ start_date: '2026-10-01', end_date: null, timezone: tz }, 'From Oct 1, 2026'],
    [{ start_date: null, end_date: '2026-10-10', timezone: tz }, 'Until Oct 10, 2026'],
  ])('labels %o as %s', (applied, label) => {
    expect(kpiRangeLabel(applied)).toBe(label)
  })
})

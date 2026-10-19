import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { emptyPerformanceFixture } from '@/features/performance/preview/fixtures'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { AdminAnalyticsPage } from './AdminAnalyticsPage'

const mocks = vi.hoisted(() => ({ analytics: vi.fn() }))
vi.mock('@/features/admin/api/adminApi', () => ({ adminApi: { analytics: mocks.analytics } }))
afterEach(cleanup)

describe('Admin analytics shared KPI semantics', () => {
  it('preserves overall targets, zero vs missing data, and aggregate-only CAR', async () => {
    const fixture: ApiSchemas['AdminAnalyticsResponse'] = {
      active_learners_30d: 0, kpi_range: { start_date: null, end_date: null, timezone: 'Asia/Manila' },
      completions: { adventure: 0, challenge: 0, total: 0 },
      runs: { total: 0, passed: 0, adventure: { total: 0, passed: 0, by_status: {} }, challenge: { total: 0, passed: 0, by_status: {} }, by_status: {} },
      per_story: [], objectives: {},
      runebound_performance: {
        ...emptyPerformanceFixture,
        kpis: { ...emptyPerformanceFixture.kpis, scr: { value: 0, numerator: 0, denominator: 1 } },
      },
    }
    mocks.analytics.mockResolvedValue(fixture)
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter><AdminAnalyticsPage /></MemoryRouter>
      </QueryClientProvider>,
    )
    const table = (await screen.findByRole('heading', { name: 'KPI Summary — All Learners' })).closest('section')!
    const rows = within(table).getAllByRole('row')
    expect(rows[1]).toHaveTextContent('≥80%')
    expect(rows[1]).toHaveTextContent('0%')
    expect(rows[2]).toHaveTextContent('≥70%')
    expect(rows[4]).toHaveTextContent('≤2')
    expect(rows[5]).toHaveTextContent('≥65%')
    expect(rows[2].querySelectorAll('td')[3]).toHaveTextContent('--')
    expect(rows[2].querySelectorAll('td')[4]).toHaveTextContent('--')
  })
})

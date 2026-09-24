import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

vi.mock('@/features/admin/api/adminApi', () => ({
  adminApi: {
    analytics: vi.fn(),
    overview: vi.fn(),
  },
}))

import { adminApi } from '@/features/admin/api/adminApi'

import { AdminDashboardPage } from './AdminDashboardPage'

type Rate = ApiSchemas['RateMetric']
type Analytics = ApiSchemas['AdminAnalyticsResponse']

const NONE: Rate = { value: null, numerator: 0, denominator: 0 }

function moduleRow(number: number, overrides: Partial<ApiSchemas['PerformanceModule']> = {}) {
  return {
    number,
    title: `Module ${number}`,
    scr: NONE,
    hlcr: NONE,
    rta: NONE,
    retry_success_rate: NONE,
    arc: NONE,
    ...overrides,
  }
}

function analyticsFixture(overrides: Partial<Analytics['runebound_performance']> = {}): Analytics {
  const breakdown = { total: 20, passed: 18, by_status: { completed: 18, failed: 2 } }
  return {
    // The old SCR card source: every story and run type, 90% passed.
    runs: { ...breakdown, adventure: breakdown, challenge: { total: 0, passed: 0, by_status: {} } },
    completions: { adventure: 0, challenge: 0, total: 0 },
    active_learners_30d: 3,
    per_story: [],
    runebound_performance: {
      kpis: {
        scr: { value: 50, numerator: 2, denominator: 4 },
        car: NONE,
        hlcr: NONE,
        rta: NONE,
        retry_success_rate: NONE,
        arc: NONE,
      },
      completed_sessions: 2,
      modules: [1, 2, 3, 4].map((number) => moduleRow(number)),
      ...overrides,
    },
  } as Analytics
}

function renderPage(data: Analytics) {
  vi.mocked(adminApi.analytics).mockResolvedValue(data)
  vi.mocked(adminApi.overview).mockReturnValue(new Promise(() => {}))
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminDashboardPage />
    </QueryClientProvider>,
  )
}

function kpiCard(abbr: string) {
  const card = screen.getAllByText(abbr).map((node) => node.closest('.dk-kpi-card')).find(Boolean)
  if (!card) throw new Error(`No KPI card for ${abbr}`)
  return card as HTMLElement
}

describe('AdminDashboardPage overall SCR', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('reads overall SCR from the Runebound KPI payload, not all-story run totals', async () => {
    renderPage(analyticsFixture())

    await screen.findByText('KPI Overview')
    const card = kpiCard('SCR')
    expect(card).toHaveTextContent('50%')
    expect(card).toHaveTextContent('2 / 4 sessions')
    expect(card).not.toHaveTextContent('90%')
  })
})

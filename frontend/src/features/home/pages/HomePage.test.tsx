import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { richHomeFixture } from '@/features/home/preview/fixtures'
import { richStatsFixture } from '@/features/stats/preview/fixtures'

import { HomePage } from './HomePage'

const mocks = vi.hoisted(() => ({
  homeSummary: vi.fn(),
  statsSummary: vi.fn(),
  statsActivity: vi.fn(),
}))

vi.mock('@/features/home/api/homeApi', () => ({
  homeApi: { summary: mocks.homeSummary },
}))

vi.mock('@/features/stats/api/statsApi', () => ({
  statsApi: {
    summary: mocks.statsSummary,
    activity: mocks.statsActivity,
  },
}))

vi.mock('@/shared/auth/useAuth', () => ({
  useAuthStore: (selector: (state: { user: { username: string } }) => unknown) =>
    selector({ user: { username: 'Fetch Tester' } }),
}))

vi.mock('@/features/home/components/HomeHubView', () => ({
  HomeHubView: ({ stats }: { stats: typeof richStatsFixture }) => (
    <div data-testid="home-hub" data-window={stats.activity_window}>
      {stats.activity_trend.length} activity buckets
    </div>
  ),
}))

function renderPage(entry = '/home') {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[entry]}>
        <HomePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('HomePage fetching', () => {
  beforeEach(() => {
    mocks.homeSummary.mockResolvedValue(richHomeFixture)
    mocks.statsSummary.mockResolvedValue(richStatsFixture)
    mocks.statsActivity.mockImplementation(async (window: 'week' | 'month' | 'year') => ({
      activity_window: window,
      activity_trend: window === 'year'
        ? richStatsFixture.activity_trend.slice(0, 12)
        : richStatsFixture.activity_trend,
    }))
  })

  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('uses the full summary once for the default month without an activity request', async () => {
    renderPage()

    expect(await screen.findByTestId('home-hub')).toHaveAttribute('data-window', 'month')
    expect(mocks.homeSummary).toHaveBeenCalledTimes(1)
    expect(mocks.statsSummary).toHaveBeenCalledTimes(1)
    expect(mocks.statsSummary).toHaveBeenCalledWith()
    expect(mocks.statsActivity).not.toHaveBeenCalled()
  })

  it('fetches only the narrow activity payload for a non-default range', async () => {
    renderPage('/home?range=year')

    await waitFor(() => {
      expect(screen.getByTestId('home-hub')).toHaveAttribute('data-window', 'year')
    })
    expect(mocks.statsSummary).toHaveBeenCalledTimes(1)
    expect(mocks.statsSummary).toHaveBeenCalledWith()
    expect(mocks.statsActivity).toHaveBeenCalledOnce()
    expect(mocks.statsActivity).toHaveBeenCalledWith('year')
    expect(screen.getByText('12 activity buckets')).toBeInTheDocument()
  })
})

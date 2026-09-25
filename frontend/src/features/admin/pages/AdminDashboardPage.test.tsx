import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
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

function analyticsFixture(
  overrides: Partial<Analytics['runebound_performance']> = {},
  objectives: Analytics['objectives'] = {},
): Analytics {
  const breakdown = { total: 20, passed: 18, by_status: { completed: 18, failed: 2 } }
  return {
    // The old SCR card source: every story and run type, 90% passed.
    runs: { ...breakdown, adventure: breakdown, challenge: { total: 0, passed: 0, by_status: {} } },
    completions: { adventure: 0, challenge: 0, total: 0 },
    active_learners_30d: 3,
    per_story: [],
    objectives,
    kpi_range: { start_date: null, end_date: null, timezone: 'Asia/Manila' },
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
    expect(card).toHaveTextContent('2 of 4 sessions completed')
    expect(card).not.toHaveTextContent('90%')
  })

  it('counts sessions under the header scope, not all-story run totals', async () => {
    renderPage(analyticsFixture())

    await screen.findByText('KPI Overview')
    const stat = screen.getByText('sessions').closest('.dk-stat') as HTMLElement
    expect(stat).toHaveTextContent('4')
    expect(stat).not.toHaveTextContent('20')
  })
})

const OFFICIAL_SOS: Record<number, string[]> = {
  1: [
    'SO 1.1 Initializing Repositories',
    'SO 1.2 Cloning Remote Repositories',
    'SO 1.3 Staging and Committing',
    'SO 1.4 Partial Staging',
    'SO 1.5 Amending Commits',
    'SO 1.6 Unstaging and Discarding Changes',
    'SO 1.7 Independent Local Repository Management',
    'SO 1.8 Efficient Repository-State Reasoning',
  ],
  2: [
    'SO 2.1 Creating and Switching Branches',
    'SO 2.2 Branch Naming Conventions and Housekeeping',
    'SO 2.3 Stashing Work in Progress',
    'SO 2.4 Pushing to a Remote',
    'SO 2.5 Fetching and Pulling from a Remote',
    'SO 2.6 Reconciling Diverged Local and Remote Histories',
    'SO 2.7 Completing Branch Merges',
    'SO 2.8 Squash Merging',
    'SO 2.9 Deleting and Recovering Remote Branches',
    'SO 2.10 Independent Branch and Collaboration Management',
    'SO 2.11 Reduced Trial-and-Error Branching',
  ],
  3: [
    'SO 3.1 Resolving Merge Conflicts Manually',
    'SO 3.2 Resolving Conflicts Using a Merge Tool',
    'SO 3.3 Cherry-Picking Commits',
    'SO 3.4 Independent Conflict Resolution',
    'SO 3.5 Transferable Conflict-Resolution Reasoning',
  ],
  4: [
    'SO 4.1 Recovering from Hard Resets',
    'SO 4.2 Reversing Pushed Commits Safely',
    'SO 4.3 Completing Rebase Recovery Sequences',
    'SO 4.4 Independent Recovery Operations',
    'SO 4.5 Reduced Trial-and-Error Recovery',
  ],
}

async function openModule(number: number) {
  await screen.findByText('KPI Overview')
  const trigger = screen.getByText(`M${number}`).closest('button')!
  if (trigger.getAttribute('aria-expanded') !== 'true') fireEvent.click(trigger)
}

function soRow(id: string) {
  const row = document.querySelector(`[data-so="${id}"]`)
  if (!row) throw new Error(`No row for ${id}`)
  return row as HTMLElement
}

function rowLabels() {
  return Array.from(document.querySelectorAll('[data-so]')).map(
    (row) => `${row.querySelector('.dk-so-id')?.textContent} ${row.querySelector('.dk-so-text')?.textContent}`,
  )
}

describe('AdminDashboardPage specific objectives', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it.each([1, 2, 3, 4])('lists the official SOs for Module %i in order', async (number) => {
    renderPage(analyticsFixture())
    await openModule(number)

    expect(rowLabels()).toEqual(OFFICIAL_SOS[number])
  })

  it('shows per-SO targets that override the card defaults', async () => {
    renderPage(analyticsFixture())
    await openModule(4)

    expect(soRow('SO 4.4')).toHaveTextContent('HLCR')
    expect(soRow('SO 4.4')).toHaveTextContent('≥65%')
    expect(soRow('SO 4.1')).toHaveTextContent('CAR')
    expect(soRow('SO 4.1')).toHaveTextContent('≥70%')
  })

  it('shows both RTA and ARC in SO 3.5, and misses when either misses', async () => {
    renderPage(
      analyticsFixture({
        modules: [
          moduleRow(1),
          moduleRow(2),
          moduleRow(3, {
            rta: { value: 70, numerator: 7, denominator: 10 },
            arc: { value: 2.5, numerator: 5, denominator: 2 },
          }),
          moduleRow(4),
        ],
      }),
    )
    await openModule(3)

    const row = soRow('SO 3.5')
    expect(row).toHaveTextContent('RTA')
    expect(row).toHaveTextContent('70%')
    expect(row).toHaveTextContent('≥65%')
    expect(row).toHaveTextContent('ARC')
    expect(row).toHaveTextContent('2.50')
    expect(row).toHaveTextContent('≤2')
    // RTA met, ARC missed: the objective is missed.
    expect(row).toHaveClass('is-miss')
  })

  it('meets SO 4.5 only when RTA ≥ 65% and ARC ≤ 3 both hold', async () => {
    renderPage(
      analyticsFixture({
        modules: [
          moduleRow(1),
          moduleRow(2),
          moduleRow(3),
          moduleRow(4, {
            rta: { value: 65, numerator: 13, denominator: 20 },
            arc: { value: 2.5, numerator: 5, denominator: 2 },
          }),
        ],
      }),
    )
    await openModule(4)

    const row = soRow('SO 4.5')
    expect(row).toHaveTextContent('≤3')
    expect(row).toHaveClass('is-met')
  })

  it('reads CAR per SO from the objectives map, not the overall CAR', async () => {
    renderPage(
      analyticsFixture(
        { kpis: { ...analyticsFixture().runebound_performance.kpis, car: { value: 99, numerator: 99, denominator: 100 } } },
        {
          'SO 1.1': { value: 80, numerator: 8, denominator: 10 },
          'SO 1.2': { value: 50, numerator: 1, denominator: 2 },
        },
      ),
    )
    await openModule(1)

    expect(soRow('SO 1.1')).toHaveTextContent('80%')
    expect(soRow('SO 1.1')).toHaveClass('is-met')
    expect(soRow('SO 1.2')).toHaveTextContent('50%')
    expect(soRow('SO 1.2')).toHaveClass('is-miss')
    // No data for this SO: shows "—", not the 99% overall CAR.
    expect(soRow('SO 1.3')).toHaveTextContent('—')
    expect(soRow('SO 1.3')).not.toHaveTextContent('99%')
    expect(soRow('SO 1.3')).toHaveClass('is-none')
  })

  it('has no verdict for a two-metric SO while one metric has no data', async () => {
    renderPage(
      analyticsFixture({
        modules: [
          moduleRow(1),
          moduleRow(2),
          moduleRow(3, { arc: { value: 1.5, numerator: 3, denominator: 2 } }),
          moduleRow(4),
        ],
      }),
    )
    await openModule(3)

    expect(soRow('SO 3.5')).toHaveClass('is-none')
  })
})

describe('AdminDashboardPage date range', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  function renderEchoingRange() {
    // The API echoes the range it applied, as the backend does.
    vi.mocked(adminApi.analytics).mockImplementation(async (range) => ({
      ...analyticsFixture(),
      kpi_range: {
        start_date: range?.startDate ?? null,
        end_date: range?.endDate ?? null,
        timezone: 'Asia/Manila',
      },
    }))
    vi.mocked(adminApi.overview).mockReturnValue(new Promise(() => {}))
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <AdminDashboardPage />
      </QueryClientProvider>,
    )
  }

  function rangeGroup() {
    return screen.getByRole('group', { name: 'KPI date range' })
  }

  it('defaults to all time and says so', async () => {
    renderEchoingRange()

    await screen.findByText('KPI Overview')
    expect(adminApi.analytics).toHaveBeenCalledWith({ startDate: null, endDate: null })
    expect(rangeGroup()).toHaveTextContent('Showing All time')
    expect(rangeGroup()).toHaveTextContent('Philippine time (UTC+8)')
    expect(screen.getByRole('button', { name: 'All time' })).toBeDisabled()
  })

  it('refetches for a chosen range, labels it, and resets to all time', async () => {
    renderEchoingRange()
    await screen.findByText('KPI Overview')

    fireEvent.change(screen.getByLabelText('From'), { target: { value: '2026-10-01' } })
    fireEvent.change(screen.getByLabelText('To'), { target: { value: '2026-10-10' } })

    await waitFor(() =>
      expect(adminApi.analytics).toHaveBeenLastCalledWith({
        startDate: '2026-10-01',
        endDate: '2026-10-10',
      }),
    )
    await waitFor(() =>
      expect(rangeGroup()).toHaveTextContent('Showing Oct 1, 2026 – Oct 10, 2026'),
    )

    fireEvent.click(screen.getByRole('button', { name: 'All time' }))

    await waitFor(() => expect(rangeGroup()).toHaveTextContent('Showing All time'))
    expect(adminApi.analytics).toHaveBeenLastCalledWith({ startDate: null, endDate: null })
  })

  it('ignores an end date before the start date', async () => {
    renderEchoingRange()
    await screen.findByText('KPI Overview')

    fireEvent.change(screen.getByLabelText('From'), { target: { value: '2026-10-10' } })
    await waitFor(() =>
      expect(adminApi.analytics).toHaveBeenLastCalledWith({ startDate: '2026-10-10', endDate: null }),
    )
    fireEvent.change(screen.getByLabelText('To'), { target: { value: '2026-10-01' } })

    expect(adminApi.analytics).not.toHaveBeenCalledWith({
      startDate: '2026-10-10',
      endDate: '2026-10-01',
    })
  })
})


describe('AdminDashboardPage supplementary retry success rate', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  const TOOLTIP =
    'Share of retry sessions that eventually ended in completion, any variant, any attempt. ' +
    'Supplementary indicator only; RTA is the evaluation KPI for SO 3.5, SO 4.5 and RQ4.'

  function fixtureWithRetrySuccess() {
    const base = analyticsFixture()
    return analyticsFixture({
      kpis: {
        ...base.runebound_performance.kpis,
        // RTA misses its target; the supplementary card must not look like a verdict.
        rta: { value: 10, numerator: 1, denominator: 10 },
        retry_success_rate: { value: 30, numerator: 3, denominator: 10 },
      },
      modules: [
        moduleRow(1, { retry_success_rate: { value: 80, numerator: 4, denominator: 5 } }),
        moduleRow(2),
        moduleRow(3),
        moduleRow(4),
      ],
    })
  }

  it('is a normal sixth card in the Overall row, with a No target tag instead of a status', async () => {
    renderPage(fixtureWithRetrySuccess())
    await screen.findByText('KPI Overview')

    const grid = document.querySelector('.dk-kpi-grid') as HTMLElement
    const cards = Array.from(grid.querySelectorAll('.dk-kpi-card'))
    expect(cards).toHaveLength(6)
    const card = kpiCard('RSR')
    expect(cards[5]).toBe(card)
    expect(card).toHaveTextContent('Retry Success Rate (supplementary)')
    expect(card).toHaveTextContent('30%')
    expect(card).toHaveTextContent('3 of 10 retry sessions completed')
    expect(card).toHaveTextContent('No target')
    expect(card).toHaveAttribute('title', TOOLTIP)
    expect(card).not.toHaveTextContent('Target:')
    expect(card.className).not.toMatch(/is-met|is-miss/)
    expect(card.querySelector('.dk-kpi-dot')).toBeNull()
    expect(card.querySelector('.dk-kpi-bar')).toBeNull()
    // Same full-contrast value styling as a KPI card with data.
    expect(card.querySelector('.dk-kpi-value')).toHaveClass('has-data')
  })

  it('stays out of "targets met", which counts the five evaluation KPIs', async () => {
    renderPage(fixtureWithRetrySuccess())
    await screen.findByText('KPI Overview')

    const stat = screen.getByText('targets met').closest('.dk-stat') as HTMLElement
    expect(stat).toHaveTextContent('/5')
  })

  it('shows the per-module value inside each module', async () => {
    renderPage(fixtureWithRetrySuccess())
    await openModule(1)

    const row = document.querySelector('.dk-supp-row') as HTMLElement
    expect(row).toHaveTextContent('Retry Success Rate (supplementary)')
    expect(row).toHaveTextContent('No target')
    expect(row).toHaveTextContent('80%')
    expect(row).toHaveTextContent('4 of 5 retry sessions completed')
    expect(row).toHaveAttribute('title', TOOLTIP)
  })
})

describe('AdminDashboardPage denominator labels', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('labels every card with the unit its formula counts', async () => {
    const base = analyticsFixture()
    renderPage(
      analyticsFixture({
        kpis: {
          ...base.runebound_performance.kpis,
          car: { value: 17.6, numerator: 22, denominator: 125 },
          hlcr: { value: 25, numerator: 1, denominator: 4 },
          arc: { value: 0.1, numerator: 1, denominator: 10 },
          rta: { value: 50, numerator: 1, denominator: 2 },
        },
      }),
    )
    await screen.findByText('KPI Overview')

    expect(kpiCard('SCR')).toHaveTextContent('2 of 4 sessions completed')
    expect(kpiCard('CAR')).toHaveTextContent('22 processable / 125 submitted commands')
    expect(kpiCard('HLCR')).toHaveTextContent('1 of 4 hard sessions completed')
    expect(kpiCard('ARC')).toHaveTextContent('1 retry across 10 completed sessions')
    expect(kpiCard('RTA')).toHaveTextContent('1 of 2 eligible retries succeeded')
    expect(kpiCard('CAR')).not.toHaveTextContent('sessions')
  })
})

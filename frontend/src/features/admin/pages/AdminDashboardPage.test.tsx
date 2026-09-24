import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
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

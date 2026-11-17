import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
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
    car: NONE,
    car_first: NONE,
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
        car_first: NONE,
        hlcr: NONE,
        rta: NONE,
        retry_success_rate: NONE,
        arc: NONE,
      },
      completed_sessions: 2,
      samples: { participants: 1, attempted_tiers: 4, in_progress_tiers: 0, mastered_tiers: 0, mastery_missing: 0, car_scored: 0, car_missing: 0, transfer_assigned: 0, transfer_pending: 0, transfer_missing: 0 },
      transfers: [],
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

describe('Learning analytics overview', () => {
  afterEach(() => { cleanup(); vi.clearAllMocks() })

  it.each([
    [2, 1, 'within the allowed maximum'],
    [3, 1, 'exceeds the allowed maximum'],
    [null, 0, 'not enough eligible evidence'],
  ] as const)('interprets ARC %s using its lower-is-better target', async (value, denominator, message) => {
    const base = analyticsFixture()
    renderPage(analyticsFixture({ kpis: { ...base.runebound_performance.kpis, arc: { value, numerator: value ?? 0, denominator } } }))
    await screen.findByText('KPI Overview')
    fireEvent.click(screen.getByRole('button', { name: 'ARC metric details' }))
    const dialog = screen.getByRole('dialog', { name: 'KPI Reference' })
    expect(dialog).toHaveTextContent('Why we measure it')
    expect(dialog).toHaveTextContent(message)
  })

  it('opens the selected metric in the shared reference dialog and closes with Escape', async () => {
    renderPage(analyticsFixture())
    await screen.findByText('KPI Overview')
    fireEvent.click(screen.getByRole('button', { name: 'CAR metric details' }))
    const dialog = screen.getByRole('dialog', { name: 'KPI Reference' })
    expect(within(dialog).getByRole('heading', { name: 'Command Accuracy Rate' })).toBeInTheDocument()
    fireEvent.change(within(dialog).getByLabelText('Metric'), { target: { value: 'scr' } })
    expect(within(dialog).getByRole('heading', { name: 'Scenario Completion Rate' })).toBeInTheDocument()
    expect(dialog).toHaveTextContent('2 of 4 required tiers mastered')
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(document.body.style.overflow).not.toBe('hidden')
    fireEvent.click(screen.getByRole('button', { name: 'CAR metric details' }))
    const reopenedDialog = screen.getByRole('dialog', { name: 'KPI Reference' })
    fireEvent.click(within(reopenedDialog).getByRole('heading', { name: 'Command Accuracy Rate' }))
    expect(reopenedDialog).toBeInTheDocument()
    fireEvent.click(reopenedDialog)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(document.body.style.overflow).not.toBe('hidden')
  })

  it('keeps missing objectives in totals and requires both conditions for attainment', async () => {
    renderPage(analyticsFixture({ modules: [moduleRow(3, {
      scr: { value: 80, numerator: 4, denominator: 5 },
      rta: { value: 70, numerator: 7, denominator: 10 },
      arc: NONE,
    })] }))
    const summary = await screen.findByRole('region', { name: 'Research Objectives Met' })
    expect(summary).toHaveTextContent('1 / 33')
    expect(within(summary).getByRole('progressbar', { name: 'Specific objectives met' })).toHaveAttribute('value', '0')
    expect(within(summary).getByRole('progressbar', { name: 'General objectives met' })).toHaveAttribute('max', '4')
  })

  it('filters objective rows and preserves both module-specific targets', async () => {
    renderPage(analyticsFixture())
    await screen.findByRole('heading', { name: 'Lesson Performance' })
    fireEvent.change(screen.getByLabelText('Module'), { target: { value: '4' } })
    const table = within(screen.getByRole('region', { name: 'Specific objective results' })).getByRole('table')
    expect(within(table).getAllByRole('row')).toHaveLength(6)
    const row = within(table).getByText('Reduced Trial-and-Error Recovery').closest('tr')!
    expect(row).toHaveTextContent('RTA')
    expect(row).toHaveTextContent('≥65%')
    expect(row).toHaveTextContent('ARC')
    expect(row).toHaveTextContent('≤3')
    fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'met' } })
    expect(table).toHaveTextContent('No objectives match these filters.')
  })

  it('does not invent transfer results for Modules 1–2 or participation by module', async () => {
    renderPage(analyticsFixture())
    await screen.findByLabelText('KPI')
    fireEvent.change(screen.getByLabelText('KPI'), { target: { value: 'rta' } })
    const chart = screen.getByRole('group', { name: 'Retry Transfer Accuracy by module' })
    expect(within(chart).getAllByText('Not applicable')).toHaveLength(2)
    expect(within(chart).getAllByText('No evidence')).toHaveLength(2)
    expect(screen.getByRole('region', { name: 'Learners per Module' })).toHaveTextContent('Per-module activity was not returned')
    fireEvent.click(screen.getByText('About trends'))
    expect(screen.getByRole('button', { name: 'Trend' })).toBeDisabled()
  })

  it('uses module participant counts independently of KPI denominators and switches difficulty measures', async () => {
    renderPage(analyticsFixture({ module_activity: [1, 2, 3, 4].map(number => ({
      number, participants: number * 3,
      difficulties: [
        { difficulty: 'easy', attempted_tiers: 12, mastered_tiers: 7, in_progress_tiers: 2 },
        { difficulty: 'medium', attempted_tiers: 6, mastered_tiers: 3, in_progress_tiers: 1 },
        { difficulty: 'hard', attempted_tiers: 2, mastered_tiers: 0, in_progress_tiers: 0 },
      ],
    })) }))
    await screen.findByRole('group', { name: 'Unique learners by module' })
    expect(screen.getByLabelText('Module 1: 3 unique learners')).toBeInTheDocument()
    expect(screen.getByLabelText('Module 4: 12 unique learners')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'How learners are counted' }))
    const explanation = screen.getByRole('dialog', { name: 'How learners are counted' })
    expect(explanation).toHaveTextContent('Each learner is counted once per module')
    fireEvent.click(explanation)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Attempted learner tiers by difficulty' })).toHaveTextContent('Module 1: easy 12, medium 6, hard 2')
    expect(document.querySelector('.la-difficulty-segment.is-easy')).toHaveStyle({ width: '60%' })
    fireEvent.change(screen.getByLabelText('Difficulty measure'), { target: { value: 'mastered_tiers' } })
    expect(screen.getByRole('group', { name: 'Mastered learner tiers by difficulty' })).toHaveTextContent('Module 1: easy 7, medium 3, hard 0')
    expect(document.querySelector('.la-difficulty-segment.is-easy')).toHaveStyle({ width: '35%' })
  })
})

describe('AdminDashboardPage overall SCR', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('reads overall SCR from the Arcane Spire KPI payload, not all-story run totals', async () => {
    renderPage(analyticsFixture())

    await screen.findByText('KPI Overview')
    const card = kpiCard('SCR')
    expect(card).toHaveTextContent('50%')
    expect(card).toHaveTextContent('2 of 4 required tiers mastered')
    expect(card).not.toHaveTextContent('90%')
  })

  it('counts sessions under the header scope, not all-story run totals', async () => {
    renderPage(analyticsFixture())

    await screen.findByText('KPI Overview')
    const stat = screen.getByText('attempted tiers').closest('.dk-stat') as HTMLElement
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
  const trigger = screen.getByRole('button', { name: new RegExp(`^M${number} `) })
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

describe('AdminDashboardPage all-time results', () => {
  afterEach(() => { cleanup(); vi.clearAllMocks() })

  it('requests all-time analytics without a date filter', async () => {
    renderPage(analyticsFixture())
    await screen.findByText('KPI Overview')
    expect(adminApi.analytics).toHaveBeenCalledWith({ startDate: null, endDate: null })
    expect(screen.queryByRole('group', { name: 'KPI date range' })).not.toBeInTheDocument()
    expect(screen.getByText(/Five research metrics/)).toHaveTextContent('All time')
  })
})
describe('AdminDashboardPage supplementary retry success rate', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  const TOOLTIP = 'Successful required repetitions are not recovery retries. Transfer is measured separately.'

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
    expect(card).toHaveTextContent('3 of 10 recovery retries succeeded')
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
    expect(row).toHaveTextContent('4 of 5 recovery retries succeeded')
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
          car_first: { value: 17.6, numerator: 22, denominator: 125 },
          hlcr: { value: 25, numerator: 1, denominator: 4 },
          arc: { value: 0.1, numerator: 1, denominator: 10 },
          rta: { value: 50, numerator: 1, denominator: 2 },
        },
      }),
    )
    await screen.findByText('KPI Overview')

    expect(kpiCard('SCR')).toHaveTextContent('2 of 4 required tiers mastered')
    expect(kpiCard('CAR')).toHaveTextContent('22 score points across 125 scored scenarios')
    expect(kpiCard('HLCR')).toHaveTextContent('1 of 4 hard tiers mastered')
    expect(kpiCard('ARC')).toHaveTextContent('1 unsuccessful attempt across 10 mastered tiers')
    expect(kpiCard('RTA')).toHaveTextContent('1 of 2 transfer checkpoints cleared first time')
    expect(kpiCard('CAR')).not.toHaveTextContent('sessions')
  })
})

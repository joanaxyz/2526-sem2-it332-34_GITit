import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import { emptyHomeFixture, richHomeFixture } from '@/features/home/preview/fixtures'
import type { HomeSummary } from '@/features/home/types'
import type { PerformanceSummary } from '@/features/performance/types'
import { emptyStatsFixture, richStatsFixture } from '@/features/stats/preview/fixtures'
import type { StatsSummary } from '@/features/stats/types'

import { HomeStatsView } from './HomeStatsView'

const mocks = vi.hoisted(() => ({ summary: vi.fn() }))

vi.mock('@/features/performance/api/performanceApi', () => ({
  performanceApi: { summary: mocks.summary },
}))

const performanceFixture: PerformanceSummary = {
  completed_sessions: 14,
  kpis: {
    scr: { value: 40, numerator: 14, denominator: 35 },
    car: { value: 95, numerator: 40, denominator: 42 },
    hlcr: { value: 0, numerator: 0, denominator: 3 },
    rtr: { value: 40, numerator: 2, denominator: 5 },
    arc: { value: 1.43, numerator: 20, denominator: 14 },
  },
  modules: [
    {
      number: 0,
      title: 'Module 0',
      scr: { value: 100, numerator: 2, denominator: 2 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rtr: { value: null, numerator: 0, denominator: 0 },
      arc: { value: null, numerator: 0, denominator: 0 },
    },
    {
      number: 1,
      title: 'Repository Foundations',
      scr: { value: 50, numerator: 1, denominator: 2 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rtr: { value: null, numerator: 0, denominator: 0 },
      arc: { value: 1.5, numerator: 3, denominator: 2 },
    },
    {
      number: 2,
      title: 'Module 2',
      scr: { value: null, numerator: 0, denominator: 0 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rtr: { value: null, numerator: 0, denominator: 0 },
      arc: { value: null, numerator: 0, denominator: 0 },
    },
  ],
}

function renderView(
  view: HomeView = 'progress',
  home: HomeSummary = richHomeFixture,
  stats: StatsSummary = richStatsFixture,
) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <HomeStatsView home={home} stats={stats} view={view} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value)
    Object.values(value).forEach(deepFreeze)
  }
  return value
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('HomeStatsView contract', () => {
  it('renders only the active category', () => {
    renderView('progress')

    // Progress is one plaque of two bands; both belong to the same category.
    expect(screen.getByRole('article', { name: 'Progress' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Where you stand' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Run results' })).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Git skills' })).not.toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Achievement gallery' })).not.toBeInTheDocument()
    // Progress is one column; only Skills splits into two.
    expect(screen.getByRole('region', { name: 'Player overview' })).not.toHaveClass('is-split')
  })

  it('states the finish rate once, in the citadel the record band never repeats', () => {
    renderView('progress')

    const story = screen.getByRole('region', { name: 'Where you stand' }).querySelector('.home-overview-story-block')
    expect(within(story as HTMLElement).getByText('76%')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByText('43 of 57 runs you started')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByLabelText('Runs finished 76%')).toBeInTheDocument()

    // The record band used to open with its own "Levels finished" tile carrying
    // the very same backend rate.
    const record = screen.getByRole('region', { name: 'Run results' })
    expect(within(record).queryByText('Levels finished')).not.toBeInTheDocument()
    expect(Array.from(record.querySelectorAll('.home-overview-kpi-row > div > span:not(.home-overview-mini-sigil)')).map((label) => label.textContent)).toEqual([
      'Hard levels finished',
      'Retries per finish',
      'Commands accepted',
    ])
  })

  it('renders nothing of its own for the Profile category', () => {
    const { container } = renderView('profile')

    expect(container.querySelector('.home-overview-grid')?.children).toHaveLength(0)
  })

  it('plots the activity window and shows the citadel counts under Progress', () => {
    renderView('progress')

    const progress = screen.getByRole('region', { name: 'Where you stand' })
    // The plot describes itself with the same totals the caption under it states.
    const plot = within(progress).getByRole('img', {
      name: 'Last 30 days: 1,084 commands run and 56 levels finished, busiest in Tue, June 9 with 84 commands.',
    })
    expect(plot.querySelectorAll('.recharts-wrapper')).toHaveLength(2)
    expect(progress.querySelector('.home-overview-activity-summary')).toHaveTextContent(
      '1,084 commands and 56 levels finished on 27 of 30 days',
    )

    // The span control states which window is on screen, and only one is.
    const spans = within(progress).getByRole('group', { name: 'Activity span' })
    expect(Array.from(spans.querySelectorAll('button')).map((button) => button.textContent)).toEqual([
      'Week',
      'Month',
      'Year',
    ])
    expect(within(spans).getByRole('button', { name: 'Month' })).toHaveAttribute('aria-pressed', 'true')
    expect(progress.querySelector('.home-overview-activity')).not.toHaveAttribute('data-pending')

    // Hard trials won is gone from the list: it was the same count the record
    // band's "Hard levels finished" tile already reports as its numerator.
    const story = progress.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dt')).map((label) => label.textContent)).toEqual([
      'Levels finished',
      'Flawless finishes',
    ])
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['43', '26'])
  })

  it('pairs command confidence with the achievement gallery under Skills', () => {
    renderView('skills')

    const skills = screen.getByRole('region', { name: 'Git skills' })
    // Bars are the default view: every value is in text without hovering.
    expect(skills.querySelectorAll('.home-overview-command-row')).toHaveLength(18)
    expect(within(skills).getByLabelText('git init: 100%')).toBeInTheDocument()
    expect(within(skills).getByLabelText('git rebase: 0%')).toBeInTheDocument()
    expect(skills.querySelector('.ref-chart-dial')).toBeNull()

    const view = within(skills).getByRole('group', { name: 'Skill profile view' })
    expect(within(view).getByRole('button', { name: 'Bars' })).toHaveAttribute('aria-pressed', 'true')

    // The radar is the same eighteen values as a shape, with the machine names
    // on its rim. It replaces the bars rather than sitting beside them, which is
    // what lets this band share the row with the gallery.
    fireEvent.click(within(view).getByRole('button', { name: 'Radar' }))
    expect(skills.querySelectorAll('.home-overview-command-row')).toHaveLength(0)
    expect(within(skills).getByLabelText('Overall mastery 54%')).toBeInTheDocument()
    expect(within(skills).getByLabelText('2 of 3 proficiency stars')).toBeInTheDocument()
    const radar = within(skills).getByRole('img', { name: /^Mastery across 18 git commands, overall 54%/ })
    expect(Array.from(radar.querySelectorAll('.ref-chart-rim-label')).map((tick) => tick.textContent)).toEqual([
      'init', 'clone', 'log', 'show', 'add', 'commit', 'restore', 'branch', 'switch',
      'merge', 'revert', 'reflog', 'stash', 'cherry-pick', 'fetch', 'pull', 'push', 'rebase',
    ])

    // Achievements were merged into this category rather than kept separate.
    const gallery = screen.getByRole('region', { name: 'Achievement gallery' })
    expect(within(gallery).getByText('/ 19 unlocked')).toBeInTheDocument()
  })

  it('stands the skills band and the gallery side by side', () => {
    renderView('skills')

    const overview = screen.getByRole('region', { name: 'Player overview' })
    expect(overview).toHaveClass('is-split')
    expect(Array.from(overview.children).map((child) => child.getAttribute('aria-label'))).toEqual([
      'Git skills',
      'Achievement gallery',
    ])
  })

  it('shows every achievement a filter matches, and says how many that will be', () => {
    renderView('skills')

    const gallery = screen.getByRole('region', { name: 'Achievement gallery' })
    expect(within(gallery).getByText('325')).toBeInTheDocument()
    expect(within(gallery).getByText('/ 435 pts')).toBeInTheDocument()
    expect(within(gallery).getByLabelText('325 of 435 achievement points earned')).toBeInTheDocument()

    const unlocked = within(gallery).getByRole('button', { name: 'Unlocked 16' })
    const locked = within(gallery).getByRole('button', { name: 'Locked 3' })
    expect(within(gallery).getByRole('button', { name: 'All 19' })).toHaveAttribute('aria-pressed', 'true')
    // The gallery used to stop at eight cards, so "16 unlocked" displayed seven.
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(19)
    expect(gallery.querySelectorAll('.home-overview-achievement-card.is-unlocked')).toHaveLength(16)

    fireEvent.click(unlocked)
    expect(unlocked).toHaveAttribute('aria-pressed', 'true')
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(16)
    expect(gallery.querySelectorAll('.home-overview-achievement-card.is-locked')).toHaveLength(0)

    fireEvent.click(locked)
    expect(locked).toHaveAttribute('aria-pressed', 'true')
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(3)
  })

  it('shows the account record and the fetched module breakdown under Progress', async () => {
    mocks.summary.mockResolvedValue(performanceFixture)
    renderView('progress')

    const results = screen.getByRole('region', { name: 'Run results' })
    expect(Array.from(results.querySelectorAll('.home-overview-kpi-row > div > strong')).map((value) => value.textContent)).toEqual([
      '62%', '1.60', '91%',
    ])

    const modules = within(results).getByRole('region', { name: 'Main story modules 1 to 4' })
    // One small chart per measure, and Module 0 stays outside the reported band.
    const charts = await waitFor(() => {
      const found = Array.from(modules.querySelectorAll('.ref-chart-mini'))
      expect(found).toHaveLength(4)
      return found
    })
    expect(charts.map((chart) => chart.querySelector('figcaption')?.textContent)).toEqual([
      'Levels finished',
      'Hard levels finished',
      'Retries that worked',
      'Retries per finish',
    ])
    expect(
      within(charts[0] as HTMLElement).getByRole('img', {
        name: 'Levels finished per module: Module 1 - Repository Foundations 50%, Module 2 --',
      }),
    ).toBeInTheDocument()
    // Every column is direct-labelled, so no value is reachable only by hovering.
    expect(Array.from(charts[0].querySelectorAll('.ref-chart-column-value')).map((label) => label.textContent)).toEqual([
      '50%',
      '--',
    ])
    expect(Array.from(charts[3].querySelectorAll('.ref-chart-column-value')).map((label) => label.textContent)).toEqual([
      '1.50',
      '--',
    ])
    // The "M1" ticks stay short, so the key underneath expands them.
    expect(Array.from(modules.querySelectorAll('.home-overview-module-key li')).map((entry) => entry.textContent)).toEqual([
      'M1Module 1 - Repository Foundations',
      'M2Module 2',
    ])
  })

  it('keeps the account record readable when the module request fails', async () => {
    mocks.summary.mockRejectedValue(new Error('metrics offline'))
    renderView('progress')

    expect(await screen.findByRole('alert')).toHaveTextContent('Module results are unavailable right now')
    expect(Array.from(document.querySelectorAll('.home-overview-kpi-row > div > strong')).map((value) => value.textContent)).toEqual([
      '62%', '1.60', '91%',
    ])
  })

  it('preserves the empty-account fallbacks in every category', () => {
    const progress = renderView('progress', emptyHomeFixture, emptyStatsFixture)
    // No trend means no plot at all, never fourteen empty days drawn as data.
    expect(screen.queryByRole('img', { name: /^Activity over the last/ })).not.toBeInTheDocument()
    expect(screen.getByText(/Run your first command and this window starts filling in/)).toBeInTheDocument()
    const story = document.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['0', '0'])
    // An account with no runs gets an honest dash, not a 0% citadel.
    expect(within(story as HTMLElement).getByText('--')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByText('No runs yet')).toBeInTheDocument()
    expect(Array.from(document.querySelectorAll('.home-overview-kpi-row > div > strong')).map((value) => value.textContent)).toEqual([
      '--', '--', '--',
    ])
    expect(screen.getByText('Unlocks after 100 commands')).toBeInTheDocument()
    progress.unmount()

    const skills = renderView('skills', emptyHomeFixture, emptyStatsFixture)
    const skillRows = document.querySelectorAll('.home-overview-command-row')
    expect(skillRows).toHaveLength(18)
    expect(Array.from(skillRows).map((row) => row.lastElementChild?.textContent)).toEqual(Array(18).fill('--'))
    // A fresh account's dial is a ring of hollow vertices, not a spike: the
    // inner radius means 0% still draws.
    fireEvent.click(screen.getByRole('button', { name: 'Radar' }))
    expect(screen.getByLabelText('Overall mastery 0%')).toBeInTheDocument()
    expect(document.querySelectorAll('.ref-chart-vertex[data-empty="true"]')).toHaveLength(18)
    expect(screen.getByText('/ 19 unlocked')).toBeInTheDocument()
    skills.unmount()
  })

  it('keeps story precedence and the 100-command accuracy threshold exact', () => {
    const home = structuredClone(richHomeFixture)
    const stats = structuredClone(richStatsFixture)
    stats.headline.levels_completed = 0
    stats.headline.perfect_clears = 30
    stats.headline.commands_run = 99
    stats.headline.accuracy = 95

    const first = renderView('progress', home, stats)
    const story = document.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['43', '30'])
    expect(Array.from(document.querySelectorAll('.home-overview-kpi-row > div > strong')).at(-1)).toHaveTextContent('--')
    first.unmount()

    stats.headline.commands_run = 100
    renderView('progress', home, stats)
    expect(Array.from(document.querySelectorAll('.home-overview-kpi-row > div > strong')).at(-1)).toHaveTextContent('95%')
  })

  it('does not mutate frozen input summaries', () => {
    const home = deepFreeze(structuredClone(richHomeFixture))
    const stats = deepFreeze(structuredClone(richStatsFixture))

    expect(() => renderView('skills', home, stats)).not.toThrow()
  })
})

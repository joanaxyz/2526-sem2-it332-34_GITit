import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

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
  objectives: {},
  samples: { participants: 1, attempted_tiers: 35, in_progress_tiers: 0, mastered_tiers: 14, mastery_missing: 0, car_scored: 0, car_missing: 0, transfer_assigned: 0, transfer_pending: 0, transfer_missing: 0 },
  transfers: [],
  kpis: {
    scr: { value: 40, numerator: 14, denominator: 35 },
    car: { value: 95, numerator: 40, denominator: 42 },
    car_first: { value: 95, numerator: 40, denominator: 42 },
    hlcr: { value: 0, numerator: 0, denominator: 3 },
    rta: { value: null, numerator: 0, denominator: 0 },
    retry_success_rate: { value: 40, numerator: 2, denominator: 5 },
    arc: { value: 1.43, numerator: 20, denominator: 14 },
  },
  modules: [
    {
      car: { value: null, numerator: 0, denominator: 0 },
      car_first: { value: null, numerator: 0, denominator: 0 },
    number: 0,
      title: 'Module 0',
      scr: { value: 100, numerator: 2, denominator: 2 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rta: { value: null, numerator: 0, denominator: 0 },
      retry_success_rate: { value: null, numerator: 0, denominator: 0 },
      arc: { value: null, numerator: 0, denominator: 0 },
    },
    {
      car: { value: 82, numerator: 82, denominator: 1 },
      car_first: { value: 82, numerator: 82, denominator: 1 },
    number: 1,
      title: 'Repository Foundations',
      scr: { value: 50, numerator: 1, denominator: 2 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rta: { value: null, numerator: 0, denominator: 0 },
      retry_success_rate: { value: null, numerator: 0, denominator: 0 },
      arc: { value: 1.5, numerator: 3, denominator: 2 },
    },
    {
      car: { value: null, numerator: 0, denominator: 0 },
      car_first: { value: null, numerator: 0, denominator: 0 },
    number: 2,
      title: 'Module 2',
      scr: { value: null, numerator: 0, denominator: 0 },
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rta: { value: null, numerator: 0, denominator: 0 },
      retry_success_rate: { value: null, numerator: 0, denominator: 0 },
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

beforeEach(() => {
  mocks.summary.mockResolvedValue(performanceFixture)
})

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
    expect(screen.getByRole('region', { name: 'Practice record' })).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Git skills' })).not.toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Achievements' })).not.toBeInTheDocument()
    // Progress is one column; only Skills splits into two.
    expect(screen.getByRole('region', { name: 'Player overview' })).not.toHaveClass('is-split')
  })

  it('keeps the active curriculum finish-rate context separate from module performance', async () => {
    renderView('progress')
    const story = screen.getByRole('region', { name: 'Where you stand' }).querySelector('.home-overview-story-block')
    expect(within(story as HTMLElement).getByText('76%')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByText('43 of 57 runs you started')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByText('Overall finish rate')).toBeInTheDocument()
    const signals = await screen.findByRole('group', { name: 'Module 1 KPIs' })
    expect(within(signals).getByText('Scenario Completion Rate').closest('.objective-metric')!).toHaveTextContent('50%')
    expect(within(signals).getByText('Command Accuracy Rate').closest('.objective-metric')!).toHaveTextContent('82%')
  })

  it('renders nothing of its own for the Profile category', () => {
    const { container } = renderView('profile')

    expect(container.querySelector('.home-overview-grid')?.children).toHaveLength(0)
  })

  it('plots the activity window and shows Arcane Spire tier counts under Progress', () => {
    renderView('progress')

    const progress = screen.getByRole('region', { name: 'Where you stand' })
    // The plot describes itself with the same totals the caption under it states.
    const plot = within(progress).getByRole('img', {
      name: 'Last 30 days: 1,084 Arcane Spire commands run and 56 tiers cleared, busiest in Tue, June 9 with 84 commands.',
    })
    expect(plot.querySelectorAll('.recharts-wrapper')).toHaveLength(2)
    expect(progress.querySelector('.home-overview-activity-summary')).toHaveTextContent(
      '1,084 Arcane Spire commands and 56 tiers cleared on 27 of 30 days',
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
    // band's "Hard runs finished" tile already reports as its numerator.
    const story = progress.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dt')).map((label) => label.textContent)).toEqual([
      'Tiers cleared',
      'Flawless finishes',
    ])
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['43', '26'])
  })

  it('shows the achievement sets on their own, with no skills band beside them', () => {
    renderView('achievements')

    const overview = screen.getByRole('region', { name: 'Player overview' })
    expect(Array.from(overview.children).map((child) => child.getAttribute('aria-label'))).toEqual(['Achievements'])
    expect(document.querySelector('.home-overview-command-row')).toBeNull()

    const gallery = screen.getByRole('region', { name: 'Achievements' })
    expect(within(gallery).getByText('/ 19 unlocked')).toBeInTheDocument()
    expect(within(gallery).getAllByRole('heading', { level: 3 }).map((heading) => heading.textContent)).toEqual([
      'The climb', 'Trials', 'Precision', 'Ranks', 'Practice',
    ])
  })

  it('keeps the art on a locked achievement, marked with a lock', () => {
    renderView('achievements')

    const locked = document.querySelectorAll('.home-overview-achievement-card.is-locked')
    expect(locked).toHaveLength(6)
    locked.forEach((card) => {
      expect(card.querySelector('.home-overview-achievement-medallion img')).not.toBeNull()
      expect(card.querySelector('.home-overview-achievement-lock')).not.toBeNull()
    })
    expect(document.querySelector('.is-unlocked .home-overview-achievement-lock')).toBeNull()
  })

  it('drops an emptied set and explains an empty filter', () => {
    renderView('achievements', emptyHomeFixture, emptyStatsFixture)

    fireEvent.click(screen.getByRole('button', { name: 'Unlocked 0' }))

    expect(document.querySelector('.home-overview-achievement-set')).toBeNull()
    expect(screen.getByText(/Nothing unlocked yet/)).toBeInTheDocument()
  })

  it('shows every achievement a filter matches, and says how many that will be', () => {
    renderView('achievements')

    const gallery = screen.getByRole('region', { name: 'Achievements' })
    expect(within(gallery).getByText('240')).toBeInTheDocument()
    expect(within(gallery).getByText('/ 455 pts')).toBeInTheDocument()
    expect(within(gallery).getByLabelText('240 of 455 achievement points earned')).toBeInTheDocument()

    const unlocked = within(gallery).getByRole('button', { name: 'Unlocked 13' })
    const locked = within(gallery).getByRole('button', { name: 'Locked 6' })
    expect(within(gallery).getByRole('button', { name: 'All 19' })).toHaveAttribute('aria-pressed', 'true')
    // The gallery used to stop at eight cards, so a long unlocked list was cut short.
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(19)
    expect(gallery.querySelectorAll('.home-overview-achievement-card.is-unlocked')).toHaveLength(13)

    fireEvent.click(unlocked)
    expect(unlocked).toHaveAttribute('aria-pressed', 'true')
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(13)
    expect(gallery.querySelectorAll('.home-overview-achievement-card.is-locked')).toHaveLength(0)

    fireEvent.click(locked)
    expect(locked).toHaveAttribute('aria-pressed', 'true')
    expect(gallery.querySelectorAll('.home-overview-achievement-card')).toHaveLength(6)
  })

  it('uses one fetched response for all four modules and their objectives', async () => {
    renderView('progress')
    const signals = await screen.findByRole('group', { name: 'Module 1 KPIs' })
    expect(within(signals).getByText('Scenario Completion Rate').closest('.objective-metric')).toHaveTextContent('50%')
    expect(within(signals).getByText('Average Retry Count').closest('.objective-metric')).toHaveTextContent('1.50')
    expect(screen.getByRole('list', { name: 'Module 1 specific objectives' }).children).toHaveLength(8)
    expect(screen.queryByRole('list', { name: 'Module 4 specific objectives' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: 'Module 4' }))
    expect(screen.getByRole('list', { name: 'Module 4 specific objectives' }).children).toHaveLength(5)
    expect(screen.queryByRole('group', { name: 'Module 1 KPIs' })).not.toBeInTheDocument()
    expect(screen.queryByRole('group', { name: 'Module 0 KPIs' })).not.toBeInTheDocument()
    expect(mocks.summary).toHaveBeenCalledTimes(1)
  })

  it('keeps activity available and recovers the record with Retry', async () => {
    mocks.summary.mockRejectedValueOnce(new Error('metrics offline'))
    renderView('progress')
    expect(await screen.findByRole('alert')).toHaveTextContent('Your practice record is unavailable')
    expect(screen.getByRole('region', { name: 'Where you stand' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    expect(await screen.findByRole('group', { name: 'Module 1 KPIs' })).toBeInTheDocument()
    expect(mocks.summary).toHaveBeenCalledTimes(2)
  })

  it('preserves the empty-account fallbacks in every category', async () => {
    mocks.summary.mockResolvedValue({ ...performanceFixture, objectives: {}, modules: [] })
    const progress = renderView('progress', emptyHomeFixture, emptyStatsFixture)
    // No trend means no plot at all, never fourteen empty days drawn as data.
    expect(screen.queryByRole('img', { name: /^Activity over the last/ })).not.toBeInTheDocument()
    expect(screen.getByText(/Run your first command and this window starts filling in/)).toBeInTheDocument()
    const story = document.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['0', '0'])
    // An account with no runs gets an honest dash, not a 0% run meter.
    expect(within(story as HTMLElement).getByText('--')).toBeInTheDocument()
    expect(within(story as HTMLElement).getByText('No runs yet')).toBeInTheDocument()
    const signals = await screen.findByRole('group', { name: 'Module 1 KPIs' })
    expect(within(signals).getAllByText('Not measured yet')).toHaveLength(4)
    progress.unmount()

    const achievements = renderView('achievements', emptyHomeFixture, emptyStatsFixture)
    expect(screen.getByText('/ 19 unlocked')).toBeInTheDocument()
    achievements.unmount()
  })

  it('keeps tier-completion zero exact and reads command acceptance only from performance', async () => {
    const stats = structuredClone(richStatsFixture)
    stats.headline.levels_completed = 0
    stats.headline.perfect_clears = 30
    stats.headline.commands_run = 1
    stats.headline.accuracy = 10
    renderView('progress', richHomeFixture, stats)
    const story = document.querySelector('.home-overview-story-block')
    expect(Array.from(story!.querySelectorAll('dd')).map((value) => value.textContent)).toEqual(['0', '30'])
    const signals = await screen.findByRole('group', { name: 'Module 1 KPIs' })
    expect(within(signals).getByText('Command Accuracy Rate').closest('.objective-metric')!).toHaveTextContent('82%')
  })

  it('does not mutate frozen input summaries', () => {
    const home = deepFreeze(structuredClone(richHomeFixture))
    const stats = deepFreeze(structuredClone(richStatsFixture))

    expect(() => renderView('achievements', home, stats)).not.toThrow()
  })
})

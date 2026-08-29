import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { forwardRef, useImperativeHandle } from 'react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { LearnedSkill } from '@/features/skills/types'
import { richHomeFixture } from '@/features/home/preview/fixtures'
import { richStatsFixture } from '@/features/stats/preview/fixtures'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'

import { HomeHubView } from './HomeHubView'

const mocks = vi.hoisted(() => ({
  useLearnedSkills: vi.fn(),
  usePlayerLoadout: vi.fn(),
  effectForSkill: vi.fn(),
  effectPlacementForSkill: vi.fn(),
  playEffect: vi.fn(),
  setAnimation: vi.fn(),
}))

vi.mock('@/features/home/components/HomeStatsView', () => ({
  HomeStatsView: ({ companionRequired }: { companionRequired: boolean }) => (
    <div data-testid="home-stats-view" data-companion-required={companionRequired}>
      Overview content
    </div>
  ),
}))

vi.mock('@/features/home/components/HomeLoadoutView', () => ({
  HomeLoadoutView: () => <div data-testid="home-loadout-view">Loadout content</div>,
}))

vi.mock('@/features/skills/hooks/useLearnedSkills', () => ({
  useLearnedSkills: mocks.useLearnedSkills,
}))

vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: mocks.usePlayerLoadout,
}))

vi.mock('@/shared/battle/effects/effectRegistry', () => ({
  effectForSkill: mocks.effectForSkill,
  effectPlacementForSkill: mocks.effectPlacementForSkill,
}))

vi.mock('@/shared/sprites/usePixelBounds', () => ({
  useImagePixelBounds: () => null,
}))

vi.mock('@/shared/sprites/SpriteAnimator', () => ({
  SpriteAnimator: forwardRef(function MockSpriteAnimator(
    props: { 'aria-label'?: string },
    ref,
  ) {
    useImperativeHandle(ref, () => ({
      play: vi.fn(),
      pause: vi.fn(),
      isPlaying: () => true,
      goToFrame: vi.fn(),
      getFrame: () => 0,
      setAnimation: mocks.setAnimation,
      playSegment: vi.fn(),
      setFlipX: vi.fn(),
    }))
    return <div aria-label={props['aria-label']} />
  }),
}))

const learnedSkills: LearnedSkill[] = [
  {
    id: 11,
    slug: 'stage-changes',
    base_command: 'git add',
    title: 'Stage Changes',
    summary: 'Prepare changes for the next commit.',
    chapter_id: 2,
    chapter_number: 2,
    chapter_title: 'The Staging Grounds',
  },
  {
    id: 12,
    slug: 'inspect-history',
    base_command: 'git log',
    title: 'Inspect History',
    summary: 'Read the repository timeline.',
    chapter_id: 3,
    chapter_number: 3,
    chapter_title: 'The Archive',
  },
]

function renderHub(path = '/home') {
  const router = createMemoryRouter(
    [
      {
        path: '/home',
        element: (
          <HomeHubView
            home={richHomeFixture}
            stats={richStatsFixture}
            playerName="Learner"
            gitcoins={null}
          />
        ),
      },
    ],
    { initialEntries: [path] },
  )
  const result = render(<RouterProvider router={router} />)
  return { ...result, router }
}

function homeNavigation() {
  return screen.getByRole('navigation', { name: 'Home sections' })
}

describe('HomeHubView contract', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.useLearnedSkills.mockReturnValue({ data: learnedSkills, isLoading: false })
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: true,
      isLoading: false,
      isError: false,
      error: null,
    })
    mocks.effectForSkill.mockReturnValue(mocks.playEffect)
    mocks.effectPlacementForSkill.mockReturnValue({ playback: 'projectile', anchor: 'feet' })
  })

  afterEach(() => {
    cleanup()
    vi.useRealTimers()
  })

  it('treats an invalid tab as Overview and replaces only the tab parameter', async () => {
    const { router } = renderHub('/home?campaign=alpha&tab=invalid')
    const navigation = homeNavigation()

    expect(within(navigation).getByRole('button', { name: 'Overview' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByTestId('home-stats-view')).toBeInTheDocument()
    expect(document.querySelector('.home-ref-grid')).toHaveAttribute('hidden')

    fireEvent.click(within(navigation).getByRole('button', { name: 'Profile' }))
    expect(router.state.location.search).toBe('?campaign=alpha&tab=profile')
    expect(router.state.historyAction).toBe('REPLACE')
    expect(document.querySelector('.home-ref-grid')).not.toHaveAttribute('hidden')

    fireEvent.click(within(navigation).getByRole('button', { name: 'Overview' }))
    expect(router.state.location.search).toBe('?campaign=alpha')
    expect(router.state.historyAction).toBe('REPLACE')
  })

  it('composes the Loadout tab without unmounting the hidden Profile workspace', () => {
    renderHub('/home?tab=loadout')

    expect(screen.getByTestId('home-loadout-view')).toBeInTheDocument()
    expect(document.querySelector('.home-ref-grid')).toHaveAttribute('hidden')
    expect(mocks.useLearnedSkills).toHaveBeenCalledTimes(1)
    expect(mocks.usePlayerLoadout).toHaveBeenCalledTimes(1)
  })

  it('keeps an empty loadout explicit across Overview and Profile', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    renderHub()

    expect(screen.getByTestId('home-stats-view')).toHaveAttribute('data-companion-required', 'true')
    fireEvent.click(within(homeNavigation()).getByRole('button', { name: 'Profile' }))

    const profile = screen.getByRole('region', { name: 'Player profile overview' })
    expect(within(profile).getAllByText('No companion selected').length).toBeGreaterThan(0)
    const chooseCompanionLinks = within(profile).getAllByRole('link', { name: 'Choose companion' })
    expect(chooseCompanionLinks.length).toBeGreaterThan(0)
    for (const link of chooseCompanionLinks) {
      expect(link).toHaveAttribute('href', '/shop?tab=companions&required=1')
    }
    expect(within(profile).queryByLabelText(/blue idle animation/i)).not.toBeInTheDocument()
  })

  it.each([
    {
      status: 'loading',
      loadout: { isLoading: true, isError: false, error: null },
      heading: 'Loading companion',
      liveRole: 'status' as const,
    },
    {
      status: 'error',
      loadout: { isLoading: false, isError: true, error: new Error('catalog unavailable') },
      heading: 'Companion unavailable',
      liveRole: 'alert' as const,
    },
  ])('keeps an unresolved $status loadout distinct from confirmed empty', ({ loadout, heading, liveRole }) => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      ...loadout,
    })
    renderHub()

    expect(screen.getByTestId('home-stats-view')).toHaveAttribute('data-companion-required', 'false')
    fireEvent.click(within(homeNavigation()).getByRole('button', { name: 'Profile' }))

    const profile = screen.getByRole('region', { name: 'Player profile overview' })
    expect(within(profile).getAllByText(heading)).toHaveLength(2)
    expect(within(profile).getAllByRole(liveRole)).toHaveLength(1)
    expect(within(profile).queryByText('No companion selected')).not.toBeInTheDocument()
    expect(within(profile).queryByRole('link', { name: 'Choose companion' })).not.toBeInTheDocument()
    expect(within(profile).queryByLabelText(/blue idle animation/i)).not.toBeInTheDocument()
  })

  it('keeps cached equipped data ready when a background refresh errors', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.white,
      companionSlug: 'white',
      hasCompanion: true,
      isLoading: false,
      isError: true,
      error: new Error('background refresh failed'),
    })
    renderHub('/home?tab=profile')

    const profile = screen.getByRole('region', { name: 'Player profile overview' })
    expect(within(profile).getByLabelText(/white idle animation/i)).toBeInTheDocument()
    expect(within(profile).queryByText('Companion unavailable')).not.toBeInTheDocument()
    expect(within(profile).queryByRole('link', { name: 'Choose companion' })).not.toBeInTheDocument()
  })

  it('announces a loadout failure while the persisted Rank view is selected', async () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: true,
      isError: false,
      error: null,
    })
    const { router } = renderHub('/home?tab=profile')
    const profile = screen.getByRole('region', { name: 'Player profile overview' })
    fireEvent.click(within(profile).getByRole('tab', { name: 'Rank Ladder' }))

    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: true,
      error: new Error('catalog unavailable'),
    })
    await act(async () => router.navigate('/home?tab=profile&refresh=error', { replace: true }))

    expect(within(profile).getByRole('tab', { name: 'Rank Ladder' })).toHaveAttribute('aria-selected', 'true')
    expect(within(profile).getByRole('alert')).toHaveTextContent('Companion unavailable')
    expect(within(profile).queryByRole('link', { name: 'Choose companion' })).not.toBeInTheDocument()
  })

  it('preserves Profile, rank, and selected-spell state across an outer-tab round trip', () => {
    renderHub('/home?tab=profile')
    const navigation = homeNavigation()
    const profileRegion = screen.getByRole('region', { name: 'Player profile overview' })

    fireEvent.click(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' }))
    fireEvent.click(within(profileRegion).getByRole('button', { name: /attack with inspect history/i }))
    expect(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' })).toHaveAttribute('aria-selected', 'true')
    expect(within(profileRegion).getByRole('button', { name: /attack with inspect history/i })).toHaveClass('is-selected')

    fireEvent.click(within(navigation).getByRole('button', { name: 'Overview' }))
    expect(profileRegion).toHaveAttribute('hidden')
    fireEvent.click(within(navigation).getByRole('button', { name: 'Profile' }))

    expect(profileRegion).not.toHaveAttribute('hidden')
    expect(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' })).toHaveAttribute('aria-selected', 'true')
    expect(within(profileRegion).getByRole('button', { name: /attack with inspect history/i })).toHaveClass('is-selected')
  })

  it('preserves profile value precedence and rank presentation', () => {
    renderHub('/home?tab=profile')
    const profileRegion = screen.getByRole('region', { name: 'Player profile overview' })

    expect(within(profileRegion).getByText('Learner')).toBeInTheDocument()
    expect(within(profileRegion).getAllByText('Arcane Adept').length).toBeGreaterThan(0)
    expect(within(profileRegion).getByText('1,240')).toBeInTheDocument()
    expect(within(profileRegion).getByText('26')).toBeInTheDocument()
    expect(within(profileRegion).getByText('Arcane Adept of the Fifth Chapter')).toBeInTheDocument()

    fireEvent.click(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' }))
    expect(within(profileRegion).getByText('43')).toBeInTheDocument()
    expect(within(profileRegion).getByText('1,187')).toBeInTheDocument()
    expect(within(profileRegion).getByLabelText('40% toward the next rank')).toBeInTheDocument()
  })

  it('renders learned-skill loading, empty, and rich states', () => {
    mocks.useLearnedSkills.mockReturnValue({ data: undefined, isLoading: true })
    const { container, unmount } = renderHub('/home?tab=profile')
    expect(container.querySelectorAll('.home-spellbook-skeleton')).toHaveLength(8)
    unmount()

    mocks.useLearnedSkills.mockReturnValue({ data: [], isLoading: false })
    const empty = renderHub('/home?tab=profile')
    expect(screen.getByText(/inscribe your first spell/i)).toBeInTheDocument()
    empty.unmount()

    mocks.useLearnedSkills.mockReturnValue({ data: learnedSkills, isLoading: false })
    renderHub('/home?tab=profile')
    expect(screen.getByText(/2 learned/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /attack with stage changes/i })).toBeInTheDocument()
  })

  it('selects a skill, plays Attack, and dispatches its placed effect', () => {
    vi.useFakeTimers()
    renderHub('/home?tab=profile')

    const skill = screen.getByRole('button', { name: /attack with stage changes/i })
    fireEvent.click(skill)

    expect(skill).toHaveClass('is-selected')
    expect(mocks.setAnimation).toHaveBeenCalledTimes(1)
    expect(mocks.effectPlacementForSkill).toHaveBeenCalledWith('add', 'blue')
    expect(mocks.effectForSkill).not.toHaveBeenCalled()

    act(() => vi.advanceTimersByTime(120))
    expect(mocks.effectForSkill).toHaveBeenCalledWith('add', 'blue')
    expect(mocks.playEffect).toHaveBeenCalledWith(expect.objectContaining({
      from: { x: 0, y: 0 },
      to: { x: 0, y: 0 },
      impactTo: { x: 0, y: 0 },
    }))
  })

  it('keeps only the latest delayed attack and ignores the older settle callback', () => {
    vi.useFakeTimers()
    renderHub('/home?tab=profile')

    fireEvent.click(screen.getByRole('button', { name: /attack with stage changes/i }))
    const firstSettle = mocks.setAnimation.mock.calls[0][1].onComplete as () => void
    fireEvent.click(screen.getByRole('button', { name: /attack with inspect history/i }))
    const secondSettle = mocks.setAnimation.mock.calls[1][1].onComplete as () => void

    act(firstSettle)
    expect(screen.getByLabelText(/blue attack animation/i)).toBeInTheDocument()
    act(() => vi.advanceTimersByTime(120))
    expect(mocks.effectForSkill).toHaveBeenCalledTimes(1)
    expect(mocks.effectForSkill).toHaveBeenCalledWith('log', 'blue')

    act(secondSettle)
    expect(screen.getByLabelText(/blue idle animation/i)).toBeInTheDocument()
    expect(mocks.setAnimation).toHaveBeenCalledTimes(3)
  })

  it('cancels delayed effect and settle work on unmount', () => {
    vi.useFakeTimers()
    const { unmount } = renderHub('/home?tab=profile')

    fireEvent.click(screen.getByRole('button', { name: /attack with stage changes/i }))
    const settle = mocks.setAnimation.mock.calls[0][1].onComplete as () => void
    unmount()
    act(() => vi.runAllTimers())
    act(settle)

    expect(mocks.effectForSkill).not.toHaveBeenCalled()
    expect(mocks.setAnimation).toHaveBeenCalledTimes(1)
  })

  it('adopts a changed companion without resetting Profile or Rank state', async () => {
    const { router } = renderHub('/home?tab=profile')
    const profileRegion = screen.getByRole('region', { name: 'Player profile overview' })
    fireEvent.click(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' }))

    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.white,
      companionSlug: 'white',
      hasCompanion: true,
      isLoading: false,
      isError: false,
      error: null,
    })
    await act(async () => router.navigate('/home?tab=profile&refresh=1', { replace: true }))

    expect(within(profileRegion).getByRole('tab', { name: 'Rank Ladder' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByLabelText(/white idle animation/i)).toBeInTheDocument()
  })
})

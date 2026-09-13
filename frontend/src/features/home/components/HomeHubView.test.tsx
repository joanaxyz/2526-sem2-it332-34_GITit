import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { forwardRef, useImperativeHandle } from 'react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { LearnedSkill } from '@/features/skills/types'
import { richHomeFixture } from '@/features/home/preview/fixtures'
import { richStatsFixture } from '@/features/stats/preview/fixtures'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { OnboardingContext } from '@/features/onboarding/hooks/onboardingContext'
import type { OnboardingPhase } from '@/shared/preferences/preferences'

import { HomeHubView } from './HomeHubView'

const mocks = vi.hoisted(() => ({
  useLearnedSkills: vi.fn(),
  usePlayerLoadout: vi.fn(),
  effectForSkill: vi.fn(),
  effectPlacementForSkill: vi.fn(),
  playEffect: vi.fn(),
  setAnimation: vi.fn(),
  catalog: vi.fn(),
  equipCompanion: vi.fn(),
  setPhase: vi.fn(),
}))

vi.mock('@/features/home/components/HomeStatsView', () => ({
  HomeStatsView: ({ view }: { view: string }) => (
    <div data-testid="home-stats-view" data-view={view}>
      Category content
    </div>
  ),
}))

vi.mock('@/features/skills/hooks/useLearnedSkills', () => ({
  useLearnedSkills: mocks.useLearnedSkills,
}))

vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: mocks.usePlayerLoadout,
}))

vi.mock('@/shared/player-loadout/playerLoadoutApi', () => ({
  playerLoadoutApi: { equipCompanion: mocks.equipCompanion },
}))

vi.mock('@/shared/shop/api/shopApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/shared/shop/api/shopApi')>()
  return {
    ...actual,
    shopCatalogQueryOptions: () => ({ queryKey: ['shop-catalog'], queryFn: mocks.catalog }),
  }
})

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

function catalog(owned = true, active = true) {
  return {
    active_companion: active ? 'blue' : null,
    purchases_enabled: true,
    items: [{ kind: 'companion' as const, slug: 'blue', label: 'Blue', price: 150, owned, active }],
  }
}

function renderHub(path = '/home', onboardingPhase?: OnboardingPhase) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const router = createMemoryRouter(
    [
      {
        path: '/home',
        element: (
          <HomeHubView home={richHomeFixture} stats={richStatsFixture} playerName="Learner" />
        ),
      },
    ],
    { initialEntries: [path] },
  )
  // No provider means no journey in flight, which is what every existing
  // player sees; a phase opts the render into the guided tutorial instead.
  const tree = <RouterProvider router={router} />
  const result = render(
    <QueryClientProvider client={client}>
      {onboardingPhase ? (
        <OnboardingContext.Provider value={{ phase: onboardingPhase, setPhase: mocks.setPhase }}>
          {tree}
        </OnboardingContext.Provider>
      ) : (
        tree
      )}
    </QueryClientProvider>,
  )
  return { ...result, router }
}

function switcher() {
  return screen.getByRole('button', { name: /showing/i })
}

function openView(label: string) {
  fireEvent.click(switcher())
  fireEvent.click(within(screen.getByRole('listbox')).getByRole('option', { name: new RegExp(label, 'i') }))
}

function profileRegion() {
  return screen.getByRole('region', { name: 'Player profile overview' })
}

/** `hidden` removes the section from the accessibility tree, so state checks use the DOM. */
function profileWorkspace() {
  return document.querySelector('.home-ref-grid')
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
    mocks.catalog.mockResolvedValue(catalog())
    mocks.effectForSkill.mockReturnValue(mocks.playEffect)
    mocks.effectPlacementForSkill.mockReturnValue({ playback: 'projectile', anchor: 'feet' })
  })

  afterEach(() => {
    cleanup()
    vi.useRealTimers()
    window.sessionStorage.clear()
  })

  it('treats an invalid view as Profile and replaces only the view parameter', () => {
    const { router } = renderHub('/home?campaign=alpha&view=invalid')

    expect(switcher()).toHaveTextContent('Profile')
    expect(screen.queryByTestId('home-stats-view')).not.toBeInTheDocument()
    expect(profileWorkspace()).not.toHaveAttribute('hidden')

    openView('Progress')
    expect(router.state.location.search).toBe('?campaign=alpha&view=progress')
    expect(router.state.historyAction).toBe('REPLACE')
    expect(screen.getByTestId('home-stats-view')).toHaveAttribute('data-view', 'progress')
    expect(profileWorkspace()).toHaveAttribute('hidden')

    // Profile is the default, so selecting it drops the parameter entirely.
    openView('Profile')
    expect(router.state.location.search).toBe('?campaign=alpha')
    expect(router.state.historyAction).toBe('REPLACE')
  })

  it('opens on Profile, with Profile first in the dropdown', () => {
    renderHub()

    expect(switcher()).toHaveTextContent('Profile')
    expect(profileWorkspace()).not.toHaveAttribute('hidden')

    fireEvent.click(switcher())
    expect(
      screen.getAllByRole('option').map((option) => option.querySelector('strong')?.textContent),
    ).toEqual(['Profile', 'Progress', 'Skills & achievements'])
  })

  it('hands each data category to the stats view and renders no tab strip', () => {
    renderHub('/home?view=skills')

    expect(screen.getByTestId('home-stats-view')).toHaveAttribute('data-view', 'skills')
    expect(screen.queryByRole('navigation', { name: 'Home sections' })).not.toBeInTheDocument()
  })

  it('lands a bookmarked Run results link on the category that absorbed it', () => {
    renderHub('/home?view=results')

    expect(switcher()).toHaveTextContent('Progress')
    expect(screen.getByTestId('home-stats-view')).toHaveAttribute('data-view', 'progress')
  })

  it('drops the stats view entirely while Profile is showing', () => {
    renderHub('/home?view=profile')

    expect(screen.queryByTestId('home-stats-view')).not.toBeInTheDocument()
    expect(profileWorkspace()).not.toHaveAttribute('hidden')
  })

  it('moves and commits the dropdown selection from the keyboard', () => {
    const { router } = renderHub()

    fireEvent.click(switcher())
    const listbox = screen.getByRole('listbox')
    fireEvent.keyDown(listbox, { key: 'End' })
    fireEvent.keyDown(listbox, { key: 'Enter' })

    expect(router.state.location.search).toBe('?view=skills')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('closes the dropdown on Escape without changing the view', () => {
    const { router } = renderHub()

    fireEvent.click(switcher())
    fireEvent.keyDown(screen.getByRole('listbox'), { key: 'Escape' })

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
    expect(router.state.location.search).toBe('')
    expect(switcher()).toHaveTextContent('Profile')
  })

  it('keeps an empty loadout explicit', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    renderHub()

    // The prerequisite is stated once, by a nudge pinned outside the layout flow.
    const nudge = screen.getByRole('note', { name: 'First step' })
    // The shop no longer has tabs, so the companion link carries only `required`.
    expect(within(nudge).getByRole('link', { name: /open shop/i })).toHaveAttribute(
      'href',
      '/shop?required=1',
    )

    openView('Profile')
    const profile = profileRegion()
    expect(within(profile).getAllByText('No companion selected').length).toBeGreaterThan(0)
    expect(within(profile).getAllByRole('link', { name: 'Choose companion' })).toHaveLength(1)
    expect(within(profile).queryByLabelText(/blue idle animation/i)).not.toBeInTheDocument()
  })

  it('leaves the prerequisite to the tutorial while the guided journey runs', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    renderHub('/home', 'home')

    expect(screen.queryByRole('note', { name: 'First step' })).not.toBeInTheDocument()
  })

  it('turns the nudge on once the journey ends with no companion bought', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    renderHub('/home', 'done')

    expect(screen.getByRole('note', { name: 'First step' })).toBeInTheDocument()
  })

  it('holds a dismissal for the session only, so the next visit asks again', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    renderHub('/home', 'done')

    fireEvent.click(screen.getByRole('button', { name: 'Dismiss first step' }))
    expect(screen.queryByRole('note', { name: 'First step' })).not.toBeInTheDocument()

    // Same session: a remount stays quiet.
    cleanup()
    renderHub('/home', 'done')
    expect(screen.queryByRole('note', { name: 'First step' })).not.toBeInTheDocument()

    // A new session (the next visit) states the prerequisite again.
    cleanup()
    window.sessionStorage.clear()
    renderHub('/home', 'done')
    expect(screen.getByRole('note', { name: 'First step' })).toBeInTheDocument()
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
    renderHub('/home?view=profile')

    expect(screen.queryByRole('note', { name: 'First step' })).not.toBeInTheDocument()
    const profile = profileRegion()
    expect(within(profile).getAllByText(heading)).toHaveLength(2)
    const announcements = within(profile)
      .getAllByRole(liveRole)
      .filter((node) => node.textContent?.includes(heading))
    expect(announcements).toHaveLength(1)
    expect(within(profile).queryByText('No companion selected')).not.toBeInTheDocument()
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
    renderHub('/home?view=profile')

    const profile = profileRegion()
    expect(within(profile).getByLabelText(/white idle animation/i)).toBeInTheDocument()
    expect(within(profile).queryByText('Companion unavailable')).not.toBeInTheDocument()
  })

  it('announces a loadout failure without hiding the rank ladder', async () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: true,
      isError: false,
      error: null,
    })
    const { router } = renderHub('/home?view=profile')
    const profile = profileRegion()
    // The ladder used to sit behind a tab; it is always on screen now, so a
    // companion failure can never be the reason a rank is not visible.
    expect(within(profile).getByText('Arcane Adept')).toBeInTheDocument()

    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: true,
      error: new Error('catalog unavailable'),
    })
    await act(async () => router.navigate('/home?view=profile&refresh=error', { replace: true }))

    expect(within(profile).getByText('Arcane Adept')).toBeInTheDocument()
    expect(within(profile).getAllByRole('alert')[0]).toHaveTextContent('Companion unavailable')
  })

  it('preserves the selected spell across a category round trip, with the ladder always shown', () => {
    renderHub('/home?view=profile')
    const profile = profileRegion()

    fireEvent.click(within(profile).getByRole('button', { name: /attack with inspect history/i }))
    expect(within(profile).getByText('Arcane Adept')).toBeInTheDocument()

    openView('Progress')
    expect(profileWorkspace()).toHaveAttribute('hidden')
    openView('Profile')

    expect(profileWorkspace()).not.toHaveAttribute('hidden')
    expect(within(profile).getByText('Arcane Adept')).toBeInTheDocument()
    expect(within(profile).getByRole('button', { name: /attack with inspect history/i })).toHaveClass('is-selected')
  })

  it('preserves profile value precedence and rank presentation', () => {
    renderHub('/home?view=profile')
    const profile = profileRegion()

    expect(within(profile).getByText('Learner')).toBeInTheDocument()
    expect(within(profile).getByText('Arcane Adept of the Fifth Chapter')).toBeInTheDocument()

    // Each of these is stated once now that both halves render together: the
    // clear counts sit under the crest, the meter sits in it.
    expect(within(profile).getByText('43')).toBeInTheDocument()
    expect(within(profile).getByLabelText('40% toward the next rank')).toBeInTheDocument()
  })

  it('lists the owned roster in Profile and equips the selected companion', async () => {
    mocks.catalog.mockResolvedValue({
      active_companion: 'blue',
      purchases_enabled: true,
      items: [
        { kind: 'companion' as const, slug: 'blue', label: 'Blue', price: 150, owned: true, active: true },
        { kind: 'companion' as const, slug: 'white', label: 'White', price: 150, owned: true, active: false },
      ],
    })
    mocks.equipCompanion.mockResolvedValue({ active_companion: 'white', shop: catalog() })
    renderHub('/home?view=profile')

    const roster = await screen.findByRole('tablist', { name: 'Owned companions' })
    expect(within(roster).getAllByRole('tab')).toHaveLength(2)
    // The equipped companion is preselected, so its action is already satisfied.
    expect(screen.getByRole('button', { name: /blue is equipped/i })).toBeDisabled()

    fireEvent.click(within(roster).getByRole('tab', { name: /white/i }))
    const equip = screen.getByRole('button', { name: 'Equip companion' })
    expect(equip).toBeEnabled()

    await act(async () => {
      fireEvent.click(equip)
    })
    expect(mocks.equipCompanion.mock.calls[0][0]).toBe('white')
  })

  it('sends an empty roster to the shop instead of offering an equip action', async () => {
    mocks.catalog.mockResolvedValue(catalog(false, false))
    renderHub('/home?view=profile')

    const roster = screen.getByRole('region', { name: 'Companion roster' })
    expect(await within(roster).findByRole('link', { name: /choose a companion/i })).toHaveAttribute(
      'href',
      '/shop?required=1',
    )
    expect(within(roster).queryByRole('button', { name: /equip/i })).not.toBeInTheDocument()
  })

  it('renders learned-skill loading, empty, and rich states', () => {
    mocks.useLearnedSkills.mockReturnValue({ data: undefined, isLoading: true })
    const { container, unmount } = renderHub('/home?view=profile')
    expect(container.querySelectorAll('.home-spellbook-skeleton')).toHaveLength(8)
    unmount()

    mocks.useLearnedSkills.mockReturnValue({ data: [], isLoading: false })
    const empty = renderHub('/home?view=profile')
    expect(screen.getByText(/inscribe your first spell/i)).toBeInTheDocument()
    empty.unmount()

    mocks.useLearnedSkills.mockReturnValue({ data: learnedSkills, isLoading: false })
    renderHub('/home?view=profile')
    expect(screen.getByText(/2 learned/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /attack with stage changes/i })).toBeInTheDocument()
  })

  it('selects a skill, plays Attack, and dispatches its placed effect', () => {
    vi.useFakeTimers()
    renderHub('/home?view=profile')

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
    renderHub('/home?view=profile')

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
    const { unmount } = renderHub('/home?view=profile')

    fireEvent.click(screen.getByRole('button', { name: /attack with stage changes/i }))
    const settle = mocks.setAnimation.mock.calls[0][1].onComplete as () => void
    unmount()
    act(() => vi.runAllTimers())
    act(settle)

    expect(mocks.effectForSkill).not.toHaveBeenCalled()
    expect(mocks.setAnimation).toHaveBeenCalledTimes(1)
  })

  it('adopts a changed companion without resetting the profile', async () => {
    const { router } = renderHub('/home?view=profile')
    const profile = profileRegion()

    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.white,
      companionSlug: 'white',
      hasCompanion: true,
      isLoading: false,
      isError: false,
      error: null,
    })
    await act(async () => router.navigate('/home?view=profile&refresh=1', { replace: true }))

    expect(within(profile).getByText('Arcane Adept')).toBeInTheDocument()
    expect(screen.getByLabelText(/white idle animation/i)).toBeInTheDocument()
  })
})

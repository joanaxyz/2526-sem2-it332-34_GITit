import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useEffect } from 'react'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { HomeHubView } from '@/features/home/components/HomeHubView'
import { richHomeFixture } from '@/features/home/preview/fixtures'
import { OnboardingProvider } from '@/features/onboarding/components/OnboardingProvider'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import {
  onboardingStorageKey,
  writeOnboardingPhase,
} from '@/features/onboarding/utils/onboardingState'
import { ShopPage } from '@/features/shop/pages/ShopPage'
import { StoryOnboarding } from '@/features/story-map/components/StoryOnboarding'
import { richStatsFixture } from '@/features/stats/preview/fixtures'
import { playerLoadoutApi } from '@/shared/player-loadout/playerLoadoutApi'
import type { OnboardingPhase } from '@/shared/preferences/preferences'
import { preferencesApi } from '@/shared/preferences/preferencesApi'
import { shopApi, type ShopCatalog } from '@/shared/shop/api/shopApi'
import { walletApi } from '@/shared/wallet/api/walletApi'

vi.mock('@/features/shop/components/CompanionCombatPreview', () => ({
  CompanionPosePreview: () => null,
  CompanionSkillPreview: () => null,
}))
vi.mock('@/features/home/components/HomeStatsView', () => ({
  HomeStatsView: () => (
    <section>
      <p>Learning progress</p>
      <div data-onboarding="overview-progress" />
    </section>
  ),
}))
vi.mock('@/features/home/components/home-hub/HomeProfileWorkspace', async () => {
  const { HomeCompanionRoster } = await import('@/features/home/components/home-hub/HomeCompanionRoster')
  return {
    HomeProfileWorkspace: ({ hidden }: { hidden: boolean }) => (
      <section hidden={hidden}>
        <div data-onboarding="profile-ladder" />
        <div data-onboarding="profile-rank" />
        <HomeCompanionRoster />
        <div data-onboarding="profile-spellbook" />
      </section>
    ),
  }
})

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((promiseResolve) => {
    resolve = promiseResolve
  })
  return { promise, resolve }
}

function catalog(owned = false, active = false): ShopCatalog {
  return {
    active_companion: active ? 'blue' : null,
    purchases_enabled: true,
    items: [{ kind: 'companion', slug: 'blue', label: 'Blue', price: 150, owned, active }],
  }
}

function StoryMap({
  ready = true,
  compact = false,
  hasCompanion = false,
}: {
  ready?: boolean
  compact?: boolean
  hasCompanion?: boolean
}) {
  return <>
    <h1 data-onboarding="stories">Story map</h1>
    {compact ? <>
      <button aria-controls="story-map-tools">Chapter tools</button>
      <button aria-controls="story-map-utilities">Story utilities</button>
    </> : <>
      <button className="chapter-book">Field Guide</button>
      <div className="story-companion-panel">Companion</div>
    </>}
    <button data-onboarding="next-level">Level 1</button>
    <button data-onboarding="challenges" disabled>Challenge Gate</button>
    <StoryOnboarding
      ready={ready}
      compact={compact}
      hasCompanion={hasCompanion}
      orientationAvailable
      onStartOrientation={() => undefined}
      onSkipOrientation={() => undefined}
    />
  </>
}

function PhaseProbe() {
  return <output aria-label="Onboarding phase">{useAppOnboarding()?.phase ?? 'missing'}</output>
}

function OrientationAutoAdvanceProbe() {
  const onboarding = useAppOnboarding()
  useEffect(() => {
    if (onboarding?.phase === 'orientation') onboarding.setPhase('stories')
  }, [onboarding])
  return null
}

const clients: QueryClient[] = []
function renderJourney(userId: number, {
  entry = '/stories/arcane-spire',
  ready = true,
  compact = false,
  hasCompanion = false,
}: {
  entry?: string
  ready?: boolean
  compact?: boolean
  hasCompanion?: boolean
} = {}) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  clients.push(client)
  return render(<QueryClientProvider client={client}>
    <MemoryRouter initialEntries={[entry]}>
      <OnboardingProvider key={userId} userId={userId}>
        <PhaseProbe />
        <div data-onboarding="wallet-balance" />
        <Link to="/shop">Shop tab</Link>
        <Link to="/home">Home tab</Link>
        <Routes>
          <Route path="/stories/:storySlug" element={
            <StoryMap ready={ready} compact={compact} hasCompanion={hasCompanion} />
          } />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="/home" element={
            <HomeHubView home={richHomeFixture} stats={richStatsFixture} playerName="Archivist" />
          } />
        </Routes>
      </OnboardingProvider>
    </MemoryRouter>
  </QueryClientProvider>)
}

async function completeTour(finishLabel: string, nextHeadings: string[]) {
  for (const heading of nextHeadings) {
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
  }
  fireEvent.click(screen.getAllByRole('button', { name: finishLabel }).at(-1)!)
}

let serverPhase: OnboardingPhase
function servePhase(phase: OnboardingPhase) {
  serverPhase = phase
}

beforeEach(() => {
  localStorage.clear()
  servePhase('welcome')
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
    width: 300, height: 160, toJSON: () => ({}),
  })
  vi.spyOn(shopApi, 'catalog').mockResolvedValue(catalog())
  vi.spyOn(walletApi, 'summary').mockResolvedValue({ balance: 150 })
  vi.spyOn(shopApi, 'purchase').mockResolvedValue({ owned: true, shop: catalog(true, true), wallet: { balance: 0 } })
  vi.spyOn(playerLoadoutApi, 'equipCompanion').mockResolvedValue({ active_companion: 'blue', shop: catalog(true, true) })
  vi.spyOn(preferencesApi, 'get').mockImplementation(async () => ({
    motion_mode: 'system', onboarding_phase: serverPhase,
  }))
  vi.spyOn(preferencesApi, 'update').mockImplementation(async (payload) => {
    serverPhase = payload.onboarding_phase ?? serverPhase
    return { motion_mode: 'system', onboarding_phase: serverPhase }
  })
})

afterEach(() => {
  cleanup()
  clients.splice(0).forEach((client) => client.clear())
  vi.restoreAllMocks()
})

describe('first-visit onboarding journey', () => {
  it('guides a new player through the map, required companion setup, and both Home views', async () => {
    const userId = 301
    const view = renderJourney(userId)

    await screen.findByRole('heading', { name: 'Choose how to learn' })
    fireEvent.click(screen.getByRole('button', { name: 'Go to first chapter' }))
    await screen.findByRole('heading', { name: 'This is your learning map' })
    await completeTour('Choose a companion', [
      'Check the chapter guide',
      'Challenges follow practice',
      'Open your next level',
      'Choose a companion before playing',
    ])

    await screen.findByRole('heading', { name: 'Check your GitCoins' })
    await completeTour('Choose a companion', ['Preview a companion', 'Purchase your companion'])
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('purchase')
    expect(screen.queryByRole('button', { name: 'Explore Home' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Purchase' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Explore Home' }))

    await screen.findByRole('heading', { name: 'Switch Home views here' })
    await completeTour('Show Profile', ['Track your progress'])
    await screen.findByRole('heading', { name: 'See the rank ladder' })
    await completeTour('Return to map', [
      'Follow your rank progress',
      'Manage your companions',
      'Review learned commands',
    ])

    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done')
    expect(localStorage.getItem(onboardingStorageKey(userId))).toBe('done')
    expect(shopApi.purchase).toHaveBeenCalledExactlyOnceWith('companion', 'blue')

    view.unmount()
    renderJourney(userId)
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done'))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  }, 20_000)

  it('lets players skip explanations but never the companion requirement', async () => {
    servePhase('stories')
    writeOnboardingPhase(302, 'stories')
    renderJourney(302)

    await screen.findByRole('heading', { name: 'This is your learning map' })
    fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }))
    expect(await screen.findByRole('heading', { name: 'Check your GitCoins' })).toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('shop')

    fireEvent.click(screen.getByRole('button', { name: 'Skip shop tour' }))
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('purchase'))
    expect(screen.queryByRole('button', { name: 'Explore on my own' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('link', { name: 'Home tab' }))
    expect(await screen.findByRole('heading', { name: 'Switch Home views here' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Skip Home tour' }))
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('equip'))
    expect(screen.queryByRole('button', { name: 'Return to map' })).not.toBeInTheDocument()

    fireEvent.click(await screen.findByRole('link', { name: 'Choose a companion' }))
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('purchase'))
    expect(await screen.findByText('Step 2 of 3 · Choose a companion')).toBeInTheDocument()
  })

  it('keeps the required companion step active when a purchase fails', async () => {
    servePhase('purchase')
    writeOnboardingPhase(303, 'purchase')
    vi.mocked(shopApi.purchase).mockRejectedValue(new Error('Purchase failed. Try again.'))
    renderJourney(303, { entry: '/shop' })

    fireEvent.click(await screen.findByRole('button', { name: 'Purchase' }))
    expect(await screen.findByText('Purchase failed. Try again.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Explore Home' })).not.toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('purchase')
  })

  it('takes an already-equipped player through Home without detouring through the Shop', async () => {
    servePhase('stories')
    writeOnboardingPhase(304, 'stories')
    vi.mocked(shopApi.catalog).mockResolvedValue(catalog(true, true))
    renderJourney(304, { hasCompanion: true })

    await screen.findByRole('heading', { name: 'This is your learning map' })
    fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }))
    expect(await screen.findByRole('heading', { name: 'Switch Home views here' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Armory' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Skip Home tour' }))
    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done')
  })

  it('uses the Home walkthrough to equip an owned companion before finishing', async () => {
    servePhase('shop')
    writeOnboardingPhase(305, 'shop')
    vi.mocked(shopApi.catalog).mockResolvedValue(catalog(true, false))
    renderJourney(305, { entry: '/shop' })

    fireEvent.click(await screen.findByRole('button', { name: 'Open Home' }))
    await screen.findByRole('heading', { name: 'Switch Home views here' })
    await completeTour('Show Profile', ['Track your progress'])
    await screen.findByRole('heading', { name: 'See the rank ladder' })
    await completeTour('Set up companion', [
      'Follow your rank progress',
      'Manage your companions',
      'Review learned commands',
    ])

    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('equip')
    fireEvent.click(screen.getByRole('button', { name: 'Equip companion' }))
    expect(await screen.findByRole('button', { name: 'Return to map' })).toBeEnabled()
    expect(playerLoadoutApi.equipCompanion).toHaveBeenCalledOnce()
    expect(vi.mocked(playerLoadoutApi.equipCompanion).mock.calls[0][0]).toBe('blue')
    expect(shopApi.purchase).not.toHaveBeenCalled()
  })

  it.each([
    [306, 0, true],
    [307, 150, false],
  ])('keeps setup unfinished when no companion can be bought (%s)', async (userId, balance, purchasesEnabled) => {
    servePhase('purchase')
    writeOnboardingPhase(userId, 'purchase')
    vi.mocked(walletApi.summary).mockResolvedValue({ balance })
    vi.mocked(shopApi.catalog).mockResolvedValue({ ...catalog(), purchases_enabled: purchasesEnabled })
    renderJourney(userId, { entry: '/shop' })

    fireEvent.click(await screen.findByRole('button', { name: 'Explore Home' }))
    await screen.findByRole('heading', { name: 'Switch Home views here' })
    fireEvent.click(screen.getByRole('button', { name: 'Skip Home tour' }))

    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('equip'))
    expect(localStorage.getItem(onboardingStorageKey(userId))).toBe('equip')
    expect(screen.queryByRole('button', { name: 'Return to map' })).not.toBeInTheDocument()
    expect(shopApi.purchase).not.toHaveBeenCalled()
  })

  it('uses the server phase to replace stale browser progress', async () => {
    writeOnboardingPhase(308, 'shop')
    servePhase('done')
    renderJourney(308)

    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done'))
    await waitFor(() => expect(localStorage.getItem(onboardingStorageKey(308))).toBe('done'))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('does not write a stale cached phase while the server preference is loading', async () => {
    const pendingPreferences = deferred<{ motion_mode: 'system'; onboarding_phase: OnboardingPhase }>()
    writeOnboardingPhase(309, 'welcome')
    vi.mocked(preferencesApi.get).mockReturnValueOnce(pendingPreferences.promise)

    renderJourney(309, { entry: '/shop' })
    expect(preferencesApi.update).not.toHaveBeenCalled()

    pendingPreferences.resolve({ motion_mode: 'system', onboarding_phase: 'done' })
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done'))
    expect(preferencesApi.update).not.toHaveBeenCalled()
    await waitFor(() => expect(localStorage.getItem(onboardingStorageKey(309))).toBe('done'))
  })

  it('does not expose stale orientation state to children before the server responds', async () => {
    const pendingPreferences = deferred<{ motion_mode: 'system'; onboarding_phase: OnboardingPhase }>()
    writeOnboardingPhase(310, 'orientation')
    vi.mocked(preferencesApi.get).mockReturnValueOnce(pendingPreferences.promise)
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    clients.push(client)

    render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={['/stories/arcane-spire']}>
          <OnboardingProvider key={310} userId={310}>
            <PhaseProbe />
            <OrientationAutoAdvanceProbe />
          </OnboardingProvider>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done')
    expect(preferencesApi.update).not.toHaveBeenCalled()

    pendingPreferences.resolve({ motion_mode: 'system', onboarding_phase: 'done' })
    await waitFor(() => expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('done'))
    expect(preferencesApi.update).not.toHaveBeenCalled()
    await waitFor(() => expect(localStorage.getItem(onboardingStorageKey(310))).toBe('done'))
  })

  it('recovers from a failed phase write on the next load', async () => {
    const first = renderJourney(311)
    fireEvent.click(await screen.findByRole('button', { name: 'Go to first chapter' }))
    await screen.findByRole('heading', { name: 'This is your learning map' })
    await waitFor(() => expect(serverPhase).toBe('stories'))
    vi.mocked(preferencesApi.update).mockRejectedValueOnce(new Error('Offline'))
    fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }))
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('shop')
    await waitFor(() => expect(preferencesApi.update).toHaveBeenLastCalledWith({ onboarding_phase: 'shop' }))
    first.unmount()

    renderJourney(311)
    expect(await screen.findByRole('heading', { name: 'This is your learning map' })).toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(311))).toBe('stories')
  })

  it('keeps replay isolated per account when browser storage is blocked', async () => {
    vi.spyOn(localStorage, 'getItem').mockImplementation(() => { throw new Error('Blocked') })
    vi.spyOn(localStorage, 'setItem').mockImplementation(() => { throw new Error('Blocked') })
    const first = renderJourney(312)
    fireEvent.click(await screen.findByRole('button', { name: 'Go to first chapter' }))
    await screen.findByRole('heading', { name: 'This is your learning map' })
    fireEvent.click(screen.getByRole('button', { name: 'Skip tour' }))
    await screen.findByRole('heading', { name: 'Check your GitCoins' })
    first.unmount()

    renderJourney(312, { entry: '/shop' })
    expect(screen.queryByRole('heading', { name: 'Choose how to learn' })).not.toBeInTheDocument()
  })

  it('leaves existing accounts alone', async () => {
    servePhase('done')
    renderJourney(313)

    await waitFor(() => expect(preferencesApi.get).toHaveBeenCalled())
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Getting started' })).not.toBeInTheDocument()
  })

  it('starts Module 0 when a new player asks for the Git primer', async () => {
    renderJourney(314, { ready: false })

    expect(await screen.findByRole('heading', { name: 'Choose how to learn' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Start Git primer' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(314))).toBe('orientation')
  })

  it('waits for the map before showing its walkthrough', () => {
    servePhase('stories')
    writeOnboardingPhase(315, 'stories')
    renderJourney(315, { ready: false })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Getting started' })).not.toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(315))).toBe('stories')
  })

  it('resumes a saved Home walkthrough instead of discarding it', async () => {
    servePhase('home')
    writeOnboardingPhase(316, 'home')
    vi.mocked(shopApi.catalog).mockResolvedValue(catalog(true, true))
    renderJourney(316, { entry: '/home' })

    expect(await screen.findByRole('heading', { name: 'Switch Home views here' })).toBeInTheDocument()
    expect(screen.getByLabelText('Onboarding phase')).toHaveTextContent('home')
    expect(localStorage.getItem(onboardingStorageKey(316))).toBe('home')
  })
})

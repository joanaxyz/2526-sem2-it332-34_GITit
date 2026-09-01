import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ShopPage } from '@/features/shop/pages/ShopPage'
import { HomeHubView } from '@/features/home/components/HomeHubView'
import { richHomeFixture } from '@/features/home/preview/fixtures'
import { richStatsFixture } from '@/features/stats/preview/fixtures'
import { StoryOnboarding } from '@/features/story-map/components/StoryOnboarding'
import { shopApi, type ShopCatalog } from '@/shared/shop/api/shopApi'
import { walletApi } from '@/shared/wallet/api/walletApi'
import { playerLoadoutApi } from '@/shared/player-loadout/playerLoadoutApi'
import { preferencesApi } from '@/shared/preferences/preferencesApi'
import type { OnboardingPhase } from '@/shared/preferences/preferences'
import { OnboardingProvider } from './OnboardingProvider'
import { onboardingStorageKey, writeOnboardingPhase } from './onboardingState'

vi.mock('@/features/shop/components/CompanionCombatPreview', () => ({
  CompanionPosePreview: () => null,
  CompanionSkillPreview: () => null,
}))
// The hub tour anchors on the real markup of each section, so the stand-ins keep
// the onboarding hooks the tour looks for.
vi.mock('@/features/home/components/HomeStatsView', () => ({
  HomeStatsView: () => (
    <section>
      <p>Learning progress</p>
      <div data-onboarding="overview-next" />
      <div data-onboarding="overview-mastery" />
      <div data-onboarding="overview-progress" />
      <div data-onboarding="overview-kpis" />
      <div data-onboarding="overview-achievements" />
    </section>
  ),
}))
vi.mock('@/features/home/components/home-hub/HomeProfileWorkspace', () => ({
  HomeProfileWorkspace: ({ hidden }: { hidden: boolean }) => (
    <section hidden={hidden}>
      <div data-onboarding="profile-switch" />
      <div data-onboarding="profile-rank" />
      <div data-onboarding="profile-currencies" />
      <div data-onboarding="profile-spellbook" />
    </section>
  ),
}))

function catalog(owned = false, active = false): ShopCatalog {
  return {
    active_companion: active ? 'blue' : null,
    purchases_enabled: true,
    items: [{ kind: 'companion', slug: 'blue', label: 'Blue', price: 150, owned, active }],
  }
}

function StoryMap({ ready = true, compact = false }) {
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
    <StoryOnboarding ready={ready} compact={compact} hasCompanion={false} />
    <Link to="/shop?tab=companions">Shop tab</Link>
    <Link to="/home?tab=loadout">Home tab</Link>
  </>
}

const clients: QueryClient[] = []
function renderJourney(userId: number, entry = '/stories/arcane-spire', ready = true, compact = false) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  clients.push(client)
  return render(<QueryClientProvider client={client}>
    <MemoryRouter initialEntries={[entry]}>
      <OnboardingProvider key={userId} userId={userId}>
        <Routes>
          <Route path="/stories/:storySlug" element={<StoryMap ready={ready} compact={compact} />} />
          <Route path="/shop" element={<ShopPage />} />
          <Route path="/home" element={<HomeHubView home={richHomeFixture} stats={richStatsFixture} playerName="Archivist" gitcoins={0} />} />
        </Routes>
      </OnboardingProvider>
    </MemoryRouter>
  </QueryClientProvider>)
}

async function completeTour(label: string, headings: string[]) {
  for (const heading of headings) {
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
  }
  fireEvent.click(screen.getByRole('button', { name: label }))
}

beforeEach(() => {
  localStorage.clear()
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260,
    width: 300, height: 160, toJSON: () => ({}),
  })
  vi.spyOn(shopApi, 'catalog').mockResolvedValue(catalog())
  vi.spyOn(walletApi, 'summary').mockResolvedValue({ balance: 150 })
  vi.spyOn(shopApi, 'purchase').mockResolvedValue({ owned: true, shop: catalog(true, true), wallet: { balance: 0 } })
  vi.spyOn(playerLoadoutApi, 'equipCompanion').mockResolvedValue({ active_companion: 'blue', shop: catalog(true, true) })
  servePhase('stories')
})

// The account's phase lives on the server; only a registration sets it to
// "stories", so the mock stands in for what the API reports for this account.
function servePhase(onboarding_phase: OnboardingPhase) {
  vi.spyOn(preferencesApi, 'get').mockResolvedValue({ motion_mode: 'system', onboarding_phase })
  vi.spyOn(preferencesApi, 'update').mockImplementation(async (payload) => ({
    motion_mode: 'system', onboarding_phase: payload.onboarding_phase ?? onboarding_phase,
  }))
}
afterEach(() => {
  cleanup()
  clients.splice(0).forEach((client) => client.clear())
  vi.restoreAllMocks()
})

describe('first-visit onboarding journey', () => {
  it('navigates Stories → Shop, waits for a real purchase, tours Home, and returns to Stories', async () => {
    const userId = 301
    const { unmount } = renderJourney(userId)
    await screen.findByRole('heading', { name: 'Your Git journey starts here' })
    await completeTour('Visit the Shop', [
      'Read before you practice', 'Practice, then test your skills', 'Open your next level', 'Let’s choose your character',
    ])
    await screen.findByRole('heading', { name: 'Check your GitCoins' })
    await completeTour('Choose my character', ['Choose your character', 'Buy the selected companion'])
    expect(shopApi.purchase).not.toHaveBeenCalled()
    expect(screen.queryByRole('button', { name: 'Visit Home' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '150 GitCoins | Purchase' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Visit Home' }))
    expect(shopApi.purchase).toHaveBeenCalledExactlyOnceWith('companion', 'blue')
    await screen.findByRole('heading', { name: 'Home is your character hub' })
    await completeTour('Show Overview', ['Your owned roster', 'Equip who joins you', 'Worlds you can enter'])
    await screen.findByRole('heading', { name: 'Overview opens on your next step' })
    await completeTour('Show Profile', [
      'Git Skill Mastery', 'Activity and story progress', 'Where your runs stand', 'Achievements to chase',
    ])
    await screen.findByRole('heading', { name: 'Profile and Rank Ladder' })
    for (const heading of ['Your rank and XP', 'GitCoins and perfect clears', 'Spells you have learned']) {
      fireEvent.click(screen.getByRole('button', { name: 'Next' }))
      await screen.findByRole('heading', { name: heading })
    }
    // Both the tutorial and its persistent checklist offer the same next step.
    fireEvent.click(screen.getAllByRole('button', { name: 'Return to Stories' }).at(-1)!)
    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(userId))).toBe('done')
    unmount()
    renderJourney(userId)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Getting started' }))
    expect(await screen.findByRole('dialog')).toBeInTheDocument()
  }, 20_000)

  it('resumes the purchase step after reload and does not advance when buying fails', async () => {
    writeOnboardingPhase(302, 'purchase')
    vi.mocked(shopApi.purchase).mockRejectedValue(new Error('Purchase failed. Try again.'))
    renderJourney(302, '/shop?tab=companions')
    fireEvent.click(await screen.findByRole('button', { name: '150 GitCoins | Purchase' }))
    expect(await screen.findByText('Purchase failed. Try again.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Visit Home' })).not.toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(302))).toBe('purchase')
  })

  it('lets existing owners visit Home without buying again and waits for manual equipment when needed', async () => {
    writeOnboardingPhase(303, 'shop')
    vi.mocked(shopApi.catalog).mockResolvedValue(catalog(true))
    renderJourney(303, '/shop?tab=companions')
    fireEvent.click(await screen.findByRole('button', { name: 'Visit Home' }))
    await screen.findByRole('heading', { name: 'Home is your character hub' })
    await completeTour('Show Overview', ['Your owned roster', 'Equip who joins you', 'Worlds you can enter'])
    await screen.findByRole('heading', { name: 'Overview opens on your next step' })
    await completeTour('Show Profile', [
      'Git Skill Mastery', 'Activity and story progress', 'Where your runs stand', 'Achievements to chase',
    ])
    await screen.findByRole('heading', { name: 'Profile and Rank Ladder' })
    await completeTour('Check my loadout', ['Your rank and XP', 'GitCoins and perfect clears', 'Spells you have learned'])
    expect(screen.queryByRole('button', { name: 'Return to Stories' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Equip companion' }))
    expect(await screen.findByRole('button', { name: 'Return to Stories' })).toBeEnabled()
    expect(playerLoadoutApi.equipCompanion).toHaveBeenCalledOnce()
    expect(vi.mocked(playerLoadoutApi.equipCompanion).mock.calls[0][0]).toBe('blue')
    expect(shopApi.purchase).not.toHaveBeenCalled()
  })

  it.each([
    [304, 0, true], [305, 150, false],
  ])('allows exploring or skipping when the shop cannot sell a character (%s)', async (userId, balance, purchasesEnabled) => {
    writeOnboardingPhase(userId, 'purchase')
    vi.mocked(walletApi.summary).mockResolvedValue({ balance })
    vi.mocked(shopApi.catalog).mockResolvedValue({ ...catalog(), purchases_enabled: purchasesEnabled })
    renderJourney(userId, '/shop?tab=companions')
    expect(await screen.findByRole('button', { name: 'Continue without buying' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Skip setup' }))
    expect(localStorage.getItem(onboardingStorageKey(userId))).toBe('done')
    expect(shopApi.purchase).not.toHaveBeenCalled()
  })

  it('follows normal navigation, and keeps skip/replay isolated per account even without storage', async () => {
    vi.spyOn(localStorage, 'getItem').mockImplementation(() => { throw new Error('Blocked') })
    vi.spyOn(localStorage, 'setItem').mockImplementation(() => { throw new Error('Blocked') })
    const view = renderJourney(306)
    fireEvent.click(screen.getByRole('link', { name: 'Shop tab' }))
    await screen.findByRole('heading', { name: 'Check your GitCoins' })
    fireEvent.keyDown(window, { key: 'Escape' })
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    view.unmount()
    const returning = renderJourney(306)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    returning.unmount()
    renderJourney(307, '/stories/arcane-spire', true, true)
    await screen.findByRole('heading', { name: 'Your Git journey starts here' })
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(await screen.findByText(/Open Chapter tools/)).toBeInTheDocument()
  })

  it('leaves accounts the server never onboarded alone, and still offers a manual replay', async () => {
    servePhase('done')
    renderJourney(309)
    await waitFor(() => expect(preferencesApi.get).toHaveBeenCalled())
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(preferencesApi.update).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Getting started' }))
    expect(await screen.findByRole('heading', { name: 'Your Git journey starts here' })).toBeInTheDocument()
    expect(vi.mocked(preferencesApi.update).mock.calls[0][0]).toEqual({ onboarding_phase: 'stories' })
  })

  it('does not open or mark setup complete before the map is ready', () => {
    renderJourney(308, '/stories/arcane-spire', false)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Getting started' })).toBeDisabled()
    expect(localStorage.getItem(onboardingStorageKey(308))).not.toBe('done')
  })
})

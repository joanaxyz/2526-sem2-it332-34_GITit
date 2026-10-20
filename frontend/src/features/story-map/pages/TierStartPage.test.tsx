import { StrictMode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { TierStartPage } from './TierStartPage'

vi.mock('@/features/story-map/api/tierRunsApi', () => ({
  tierRunsApi: {
    startRun: vi.fn(async () => ({ id: 42 })),
    retryRun: vi.fn(async () => ({ id: 42 })),
  },
}))
vi.mock('@/features/story-map/pages/loadTierRunPage', () => ({ loadTierRunPage: vi.fn(async () => ({})) }))
vi.mock('@/features/story-map/utils/tierBattle', () => ({ tierRunAssetManifest: vi.fn(() => null) }))
vi.mock('@/features/story-map/utils/tierRunCache', () => ({ syncTierRunInCache: vi.fn() }))
vi.mock('@/shared/battle/battleAssets', () => ({ warmBattleAssets: vi.fn(async () => undefined) }))
vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: () => ({ companionSlug: 'fox' }),
}))
vi.mock('@/shared/components/LoadingScreen', () => ({
  LoadingScreen: ({ label }: { label: string }) => <p>{label}</p>,
}))

function renderStart(entry: string) {
  render(
    <StrictMode>
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={[entry]}>
          <Routes>
            <Route path="/adventure-level-tiers/:tierId/runs" element={<TierStartPage mode="start" />} />
            <Route path="/adventure-level-tiers/:tierId/replay" element={<TierStartPage mode="replay" />} />
            <Route path="/adventure-tier-runs/:runId/retry" element={<TierStartPage mode="retry" />} />
            <Route path="/adventure-tier-runs/:runId" element={<p>Workspace</p>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </StrictMode>,
  )
}

describe('TierStartPage', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('starts the run once under StrictMode and enters the workspace', async () => {
    renderStart('/adventure-level-tiers/7/runs')

    expect(screen.getByText('Starting adventure')).toBeInTheDocument()
    expect(await screen.findByText('Workspace')).toBeInTheDocument()
    expect(tierRunsApi.startRun).toHaveBeenCalledOnce()
    expect(tierRunsApi.startRun).toHaveBeenCalledWith(7, { replay: false })
  })

  it('continues a tier from the run just played', async () => {
    renderStart('/adventure-level-tiers/7/runs?prior_run_id=3')

    expect(screen.getByText('Starting next scenario')).toBeInTheDocument()
    expect(await screen.findByText('Workspace')).toBeInTheDocument()
    expect(tierRunsApi.startRun).toHaveBeenCalledWith(7, { prior_run_id: 3 })
  })

  it('starts a replay and retries a run through their own routes', async () => {
    renderStart('/adventure-level-tiers/7/replay')
    expect(await screen.findByText('Workspace')).toBeInTheDocument()
    expect(tierRunsApi.startRun).toHaveBeenCalledWith(7, { replay: true })
    cleanup()

    renderStart('/adventure-tier-runs/5/retry')
    expect(await screen.findByText('Workspace')).toBeInTheDocument()
    expect(tierRunsApi.retryRun).toHaveBeenCalledOnce()
    expect(tierRunsApi.retryRun).toHaveBeenCalledWith(5)
  })
})

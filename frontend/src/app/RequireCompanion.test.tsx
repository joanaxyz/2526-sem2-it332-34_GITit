import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'

import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { RequireCompanion } from './RequireCompanion'

const mocks = vi.hoisted(() => ({
  usePlayerLoadout: vi.fn(),
}))

vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: mocks.usePlayerLoadout,
}))

function Destination() {
  const location = useLocation()
  return <div>{location.pathname}{location.search}</div>
}

describe('RequireCompanion', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('returns direct level attempts to the map so the companion overlay can explain the gate', async () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })

    render(
      <MemoryRouter initialEntries={['/adventure-level-tiers/42/runs']}>
        <Routes>
          <Route
            path="/adventure-level-tiers/:tierId/runs"
            element={<RequireCompanion><div>Level</div></RequireCompanion>}
          />
          <Route path="/stories/:storySlug" element={<Destination />} />
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('/stories/arcane-spire?companion-required=1')).toBeInTheDocument()
    })
  })

  it('renders the level when a companion is equipped', () => {
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: true,
      isLoading: false,
      isError: false,
      error: null,
    })

    render(
      <MemoryRouter>
        <RequireCompanion><div>Level</div></RequireCompanion>
      </MemoryRouter>,
    )

    expect(screen.getByText('Level')).toBeInTheDocument()
  })
})

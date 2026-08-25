import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { useAuthStore } from '@/shared/auth/useAuth'

import { AppTopbar } from './AppNavigation'

vi.mock('@/shared/progress/rank', () => ({
  useRank: () => null,
}))

vi.mock('@/shared/wallet/hooks/useWallet', () => ({
  useWalletSummary: () => ({ data: { balance: 150 }, isPending: false }),
}))

vi.mock('@/shared/player-loadout/usePlayerLoadout', async () => {
  const { COMPANIONS } = await import('@/shared/cosmetics/companions/registry')
  return {
    usePlayerLoadout: () => ({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    }),
  }
})

describe('AppTopbar account state', () => {
  beforeEach(() => {
    useAuthStore.setState({
      accessToken: 'test-token',
      user: {
        id: 1,
        username: 'new-user',
        email: 'new-user@example.test',
        is_staff: false,
      },
    })
  })

  afterEach(() => {
    cleanup()
    useAuthStore.setState({ accessToken: null, user: null })
  })

  it('names the account trigger and uses initials when no companion is equipped', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppTopbar />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    const trigger = screen.getByRole('button', { name: 'Open account menu for new-user' })
    expect(within(trigger).getByText('NE')).toBeInTheDocument()
    expect(trigger.querySelector('.app-profile-avatar img')).toBeNull()

    fireEvent.click(trigger)
    expect(screen.getByRole('button', { name: 'Close account menu for new-user' })).toHaveAttribute(
      'aria-expanded',
      'true',
    )
    expect(screen.getByRole('menuitem', { name: 'Settings' })).toBeInTheDocument()
    queryClient.clear()
  })
})

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

import { AuthSessionChangedError, useAuthStore } from '@/shared/auth/useAuth'
import { authApi } from '@/shared/auth/authApi'

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
    vi.restoreAllMocks()
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
    // A plain labelled button group, not a role="menu"/role="menuitem" widget —
    // this app doesn't implement APG menu keyboarding (arrow keys), so it
    // shouldn't claim menu semantics that promise it.
    expect(screen.getByRole('button', { name: 'Settings' })).toBeInTheDocument()
    queryClient.clear()
  })

  it('moves focus into the panel on open and restores it to the trigger on close', async () => {
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
    trigger.focus()
    fireEvent.click(trigger)

    const settingsItem = await screen.findByRole('button', { name: 'Settings' })
    await waitFor(() => expect(settingsItem).toHaveFocus())

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByRole('button', { name: 'Settings' })).not.toBeInTheDocument()
    await waitFor(() => expect(trigger).toHaveFocus())
    queryClient.clear()
  })

  it('does not sign out a new account when a previous logout finishes late', async () => {
    let rejectLogout!: (error: unknown) => void
    vi.spyOn(authApi, 'logout').mockReturnValue(new Promise((_, reject) => { rejectLogout = reject }))
    const queryClient = new QueryClient()
    render(<QueryClientProvider client={queryClient}><MemoryRouter><AppTopbar /></MemoryRouter></QueryClientProvider>)
    fireEvent.click(screen.getByRole('button', { name: 'Open account menu for new-user' }))
    fireEvent.click(screen.getByRole('button', { name: 'Logout' }))
    await waitFor(() => expect(authApi.logout).toHaveBeenCalledOnce())

    const nextUser = { id: 2, username: 'second', email: 'second@example.com', is_staff: false }
    act(() => { useAuthStore.getState().setSession('second-token', nextUser) })
    await act(async () => { rejectLogout(new AuthSessionChangedError()) })

    expect(useAuthStore.getState()).toMatchObject({ accessToken: 'second-token', user: nextUser })
    expect(screen.getByRole('button', { name: 'Open account menu for second' })).toBeInTheDocument()
    queryClient.clear()
  })
})

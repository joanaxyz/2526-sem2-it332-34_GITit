import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import type { ReactElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { LoadingState } from './LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

function renderLoading(node: ReactElement, catalog?: { active_companion: string | null }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  if (catalog) client.setQueryData(queryKeys.shopCatalog, catalog)
  return render(<QueryClientProvider client={client}>{node}</QueryClientProvider>)
}

describe('LoadingState', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.setState({ user: null })
  })

  it('announces the label before it paints, so a fast load never flashes', async () => {
    const { container } = renderLoading(<LoadingState label="Loading home" variant="page" />)

    // The status and its label are live from the first frame; only the visual
    // frame waits, and the container still holds its box so nothing jumps.
    expect(screen.getByRole('status', { name: 'Loading home' })).toBeInTheDocument()
    expect(container.querySelector('.git-it-loading-state')).not.toHaveClass('is-painted')

    await waitFor(() => expect(container.querySelector('.git-it-loading-state')).toHaveClass('is-painted'))
  })

  it('runs the equipped companion, not the default one', () => {
    const { container } = renderLoading(<LoadingState label="Loading" variant="screen" />, {
      active_companion: 'white',
    })

    expect(container.querySelector('[aria-label="White running"]')).toBeInTheDocument()
  })

  it('greets a player who owns no companion yet, by name', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingState label="Loading" variant="screen" />, { active_companion: null })

    expect(screen.getByText('Welcome, ada')).toBeInTheDocument()
  })

  it('does not greet a player whose catalog has not loaded yet', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingState label="Loading" variant="screen" />)

    // An unread catalog is not the same answer as an empty one: a returning
    // player mid-session restore must not be welcomed like a new one.
    expect(screen.queryByText('Welcome, ada')).not.toBeInTheDocument()
  })

  it('owns up to a wait that has stopped looking like a wait', async () => {
    vi.useFakeTimers()
    try {
      renderLoading(<LoadingState label="Starting adventure" variant="screen" />)
      expect(screen.queryByText(/Still working/)).not.toBeInTheDocument()

      await act(async () => {
        await vi.advanceTimersByTimeAsync(9_000)
      })
      expect(screen.getByText(/Still working/)).toBeInTheDocument()
    } finally {
      vi.useRealTimers()
    }
  })

  it('keeps the greeting off dense variants', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingState label="Loading users" variant="inline" />, { active_companion: null })

    expect(screen.queryByText('Welcome, ada')).not.toBeInTheDocument()
  })
})

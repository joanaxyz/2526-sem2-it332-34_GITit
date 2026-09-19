import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import type { ReactElement } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { LoadingScreen } from './LoadingScreen'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

function renderLoading(node: ReactElement, catalog?: { active_companion: string | null }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  if (catalog) client.setQueryData(queryKeys.shopCatalog, catalog)
  return render(<QueryClientProvider client={client}>{node}</QueryClientProvider>)
}

function screenNode() {
  return document.body.querySelector('.git-it-loading-screen')
}

describe('LoadingScreen', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.setState({ user: null })
  })

  it('paints over the app instead of inside it', () => {
    const { container } = renderLoading(<LoadingScreen label="Loading home" />)

    // The screen portals to the body: a loader that renders where it is called
    // ends up boxed inside whatever column or shell asked for it.
    expect(container).toBeEmptyDOMElement()
    expect(screenNode()?.parentElement).toBe(document.body)
    expect(document.body.style.overflow).toBe('hidden')
  })

  it('releases the scroll lock when the wait ends', () => {
    const { unmount } = renderLoading(<LoadingScreen label="Loading home" />)
    unmount()

    expect(document.body.style.overflow).toBe('')
  })

  it('keeps the page scrollable after two overlapping screens both unmount', () => {
    // One route's screen can still be up as the next one goes in. If each
    // stored and restored the overflow on its own, the loser's stale 'hidden'
    // would outlive both and leave the app permanently unscrollable.
    const outgoing = renderLoading(<LoadingScreen label="Leaving" />)
    const incoming = renderLoading(<LoadingScreen label="Arriving" />)
    expect(document.body.style.overflow).toBe('hidden')

    outgoing.unmount()
    expect(document.body.style.overflow).toBe('hidden')

    incoming.unmount()
    expect(document.body.style.overflow).toBe('')
  })

  it('announces the label before it paints, so a fast load never flashes', async () => {
    renderLoading(<LoadingScreen label="Loading home" />)

    // The status and its label are live from the first frame; only the visual
    // frame waits, and the overlay is opaque throughout so nothing flickers.
    expect(screen.getByRole('status', { name: 'Loading home' })).toBeInTheDocument()
    expect(screenNode()).not.toHaveClass('is-painted')

    await waitFor(() => expect(screenNode()).toHaveClass('is-painted'))
  })

  it('runs the equipped companion, not the default one', () => {
    renderLoading(<LoadingScreen label="Loading" />, { active_companion: 'white' })

    expect(document.body.querySelector('[aria-label="White running"]')).toBeInTheDocument()
  })

  it('greets a player who owns no companion yet, by name', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingScreen label="Loading" />, { active_companion: null })

    expect(screen.getByText('Welcome, ada')).toBeInTheDocument()
  })

  it('does not greet a player whose catalog has not loaded yet', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingScreen label="Loading" />)

    // An unread catalog is not the same answer as an empty one: a returning
    // player mid-session restore must not be welcomed like a new one.
    expect(screen.queryByText('Welcome, ada')).not.toBeInTheDocument()
  })

  it('does not greet when the loader is pinned to somebody else’s companion', () => {
    useAuthStore.setState({ user: { username: 'ada' } as never })
    renderLoading(<LoadingScreen companionSlug="black" label="Loading" />, { active_companion: null })

    expect(screen.queryByText('Welcome, ada')).not.toBeInTheDocument()
  })

  it('owns up to a wait that has stopped looking like a wait', async () => {
    vi.useFakeTimers()
    try {
      renderLoading(<LoadingScreen label="Starting adventure" />)
      expect(screen.queryByText(/Still working/)).not.toBeInTheDocument()

      await act(async () => {
        await vi.advanceTimersByTimeAsync(9_000)
      })
      expect(screen.getByText(/Still working/)).toBeInTheDocument()
    } finally {
      vi.useRealTimers()
    }
  })
})

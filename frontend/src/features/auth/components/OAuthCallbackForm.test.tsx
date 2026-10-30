import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { StrictMode } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { useAuthStore } from '@/shared/auth/useAuth'

import { OAuthButtons } from './OAuthButtons'
import { OAuthCallbackForm } from './OAuthCallbackForm'

const mocks = vi.hoisted(() => ({ exchange: vi.fn() }))

vi.mock('@/shared/auth/authApi', () => ({
  authApi: {
    exchangeOAuthTicket: mocks.exchange,
    oauthStartUrl: (provider: string) => `http://api.test/api/auth/oauth/${provider}/start/`,
  },
}))

const session = {
  access: 'oauth-access',
  user: { id: 7, username: 'octo-cat', email: 'octo@example.com', is_staff: false },
}

function renderCallback(entry: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <StrictMode>
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[entry]}>
          <Routes>
            <Route path="/oauth/callback" element={<OAuthCallbackForm />} />
            <Route path="/stories/arcane-spire" element={<h1>Story map</h1>} />
            <Route path="/admin" element={<h1>Admin</h1>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </StrictMode>,
  )
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  useAuthStore.setState({ accessToken: null, user: null })
})

describe('OAuthCallbackForm', () => {
  it('spends the ticket exactly once and opens Stories', async () => {
    mocks.exchange.mockResolvedValue(session)
    renderCallback('/oauth/callback?ticket=abc123')

    expect(await screen.findByRole('heading', { name: 'Story map' })).toBeInTheDocument()
    expect(mocks.exchange).toHaveBeenCalledTimes(1)
    expect(mocks.exchange).toHaveBeenCalledWith({ ticket: 'abc123' })
    expect(useAuthStore.getState().user?.username).toBe('octo-cat')
  })

  it('sends staff to the admin console', async () => {
    mocks.exchange.mockResolvedValue({ ...session, user: { ...session.user, is_staff: true } })
    renderCallback('/oauth/callback?ticket=abc123')

    expect(await screen.findByRole('heading', { name: 'Admin' })).toBeInTheDocument()
  })

  it('explains a provider error without calling the API', () => {
    renderCallback('/oauth/callback?error=email')

    expect(screen.getByRole('heading', { name: "Sign-in didn't finish" })).toBeInTheDocument()
    expect(screen.getByText(/didn't give us a verified email/)).toBeInTheDocument()
    expect(mocks.exchange).not.toHaveBeenCalled()
  })

  it('shows the API message when the ticket has expired', async () => {
    mocks.exchange.mockRejectedValue(
      new ApiError('This sign-in has expired. Try again.', 400, { detail: 'This sign-in has expired. Try again.' }),
    )
    renderCallback('/oauth/callback?ticket=stale')

    expect(await screen.findByText('This sign-in has expired. Try again.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Back to sign in' })).toHaveAttribute('href', '/login')
  })
})

describe('OAuthButtons', () => {
  it('links each provider to its API start URL', () => {
    render(<OAuthButtons />)

    expect(screen.getByRole('link', { name: 'Continue with GitHub' })).toHaveAttribute(
      'href',
      'http://api.test/api/auth/oauth/github/start/',
    )
    expect(screen.getByRole('link', { name: 'Continue with Google' })).toHaveAttribute(
      'href',
      'http://api.test/api/auth/oauth/google/start/',
    )
  })
})

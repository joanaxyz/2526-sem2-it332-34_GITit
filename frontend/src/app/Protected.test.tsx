import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { Protected } from '@/app/Protected'
import { authApi } from '@/shared/auth/authApi'
import type { User } from '@/shared/auth/types'
import { useAuthStore } from '@/shared/auth/useAuth'
import { queryKeys } from '@/shared/api/queryKeys'

const { refreshSharedAccessToken } = vi.hoisted(() => ({
  refreshSharedAccessToken: vi.fn<() => Promise<string>>(),
}))

vi.mock('@/shared/api/httpClient', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/shared/api/httpClient')>()),
  refreshSharedAccessToken,
}))

const cachedUser: User = {
  id: 1,
  username: 'cached-student',
  email: 'cached@example.com',
  is_staff: false,
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve
    reject = promiseReject
  })
  return { promise, reject, resolve }
}

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  refreshSharedAccessToken.mockReset()
  window.localStorage.clear()
  useAuthStore.setState({ accessToken: null, user: null })
})

function renderProtected(queryClient: QueryClient) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/private']}>
        <Routes>
          <Route
            path="/private"
            element={
              <Protected>
                <div>Protected child</div>
              </Protected>
            }
          />
          <Route path="/login" element={<div>Login destination</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('Protected', () => {
  it('never renders a cached identity while a refreshed token awaits backend confirmation', async () => {
    useAuthStore.setState({ accessToken: null, user: cachedUser })
    refreshSharedAccessToken.mockResolvedValue('refreshed-token')
    const confirmation = deferred<User>()
    vi.spyOn(authApi, 'me').mockReturnValue(confirmation.promise)
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    renderProtected(queryClient)

    await waitFor(() => expect(authApi.me).toHaveBeenCalledTimes(1))
    expect(useAuthStore.getState()).toMatchObject({
      accessToken: 'refreshed-token',
      user: null,
    })
    expect(screen.queryByText('Protected child')).not.toBeInTheDocument()
    expect(screen.getByText('Restoring session')).toBeInTheDocument()

    confirmation.reject(new Error('confirmation failed'))

    await waitFor(() => expect(screen.getByText('Login destination')).toBeInTheDocument())
    expect(screen.queryByText('Protected child')).not.toBeInTheDocument()
    queryClient.clear()
  })

  it('restores the session through the shared refresh gate instead of a second rotation', async () => {
    useAuthStore.setState({ accessToken: null, user: cachedUser })
    refreshSharedAccessToken.mockResolvedValue('refreshed-token')
    vi.spyOn(authApi, 'refresh')
    vi.spyOn(authApi, 'me').mockResolvedValue(cachedUser)
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    renderProtected(queryClient)

    await waitFor(() => expect(screen.getByText('Protected child')).toBeInTheDocument())
    // Rotation is single-use: bootstrapping via its own POST /auth/refresh/
    // would race the 401 retry path and revoke the session it just restored.
    expect(authApi.refresh).not.toHaveBeenCalled()
    expect(refreshSharedAccessToken).toHaveBeenCalledTimes(1)
    queryClient.clear()
  })

  it('waits for re-confirmation instead of bouncing to login when the token is dropped', async () => {
    // A cross-tab rotation drops this tab's token while the cached user stays,
    // and a bootstrap that already succeeded once must not satisfy the re-entry.
    useAuthStore.setState({ accessToken: 'first-token', user: cachedUser })
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    queryClient.setQueryData(queryKeys.authBootstrap, cachedUser)

    const reconfirmation = deferred<User>()
    refreshSharedAccessToken.mockResolvedValue('rotated-token')
    vi.spyOn(authApi, 'me').mockReturnValue(reconfirmation.promise)

    renderProtected(queryClient)
    expect(screen.getByText('Protected child')).toBeInTheDocument()

    act(() => {
      useAuthStore.setState({ accessToken: null })
    })

    await waitFor(() => expect(screen.getByText('Restoring session')).toBeInTheDocument())
    expect(screen.queryByText('Login destination')).not.toBeInTheDocument()

    reconfirmation.resolve(cachedUser)

    await waitFor(() => expect(screen.getByText('Protected child')).toBeInTheDocument())
    expect(screen.queryByText('Login destination')).not.toBeInTheDocument()
    queryClient.clear()
  })
})

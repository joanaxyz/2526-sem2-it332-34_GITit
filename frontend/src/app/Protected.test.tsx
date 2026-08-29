import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { Protected } from '@/app/Protected'
import { authApi } from '@/shared/auth/authApi'
import type { User } from '@/shared/auth/types'
import { useAuthStore } from '@/shared/auth/useAuth'

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
  window.localStorage.clear()
  useAuthStore.setState({ accessToken: null, user: null })
})

describe('Protected', () => {
  it('never renders a cached identity while a refreshed token awaits backend confirmation', async () => {
    useAuthStore.setState({ accessToken: null, user: cachedUser })
    vi.spyOn(authApi, 'refresh').mockResolvedValue({ access: 'refreshed-token' })
    const confirmation = deferred<User>()
    vi.spyOn(authApi, 'me').mockReturnValue(confirmation.promise)
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    render(
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
})

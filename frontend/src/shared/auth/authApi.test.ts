import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { useAuthStore } from '@/shared/auth/useAuth'

import { authApi } from './authApi'

function jsonResponse(status: number, payload: unknown) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('unauthenticated auth requests', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuthStore.getState().clearSession()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('reports wrong credentials without trying a token refresh', async () => {
    const fetchMock = vi.fn<typeof fetch>(() =>
      Promise.resolve(jsonResponse(401, { detail: 'Invalid username/email or password.' })),
    )
    vi.stubGlobal('fetch', fetchMock)

    const error = await authApi.login({ identifier: 'nobody_here', password: 'WrongPass!123' }).catch(
      (caught: unknown) => caught,
    )

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(401)
    expect((error as ApiError).message).toBe('Invalid username/email or password.')
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/login\/$/)
  })
})

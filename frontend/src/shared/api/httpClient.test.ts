import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/features/auth/hooks/useAuth'

import { apiRequest } from './httpClient'

const user = {
  id: 1,
  email: 'student@example.com',
  student_id: 'S0001',
  first_name: 'Student',
  last_name: 'User',
}

function jsonResponse(status: number, payload: unknown) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('apiRequest auth refresh', () => {
  beforeEach(() => {
    localStorage.clear()
    useAuthStore.getState().clearSession()
    useAuthStore.getState().setSession('expired-token', user)
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('shares one refresh request across concurrent 401 responses', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      const headers = init?.headers as Record<string, string> | undefined

      if (url.endsWith('/auth/refresh/')) {
        return Promise.resolve(jsonResponse(200, { access: 'fresh-token' }))
      }

      if (headers?.Authorization === 'Bearer fresh-token') {
        return Promise.resolve(jsonResponse(200, { endpoint: url.split('/').at(-2) }))
      }

      return Promise.resolve(jsonResponse(401, { detail: 'Token expired.' }))
    })
    vi.stubGlobal('fetch', fetchMock)

    const [first, second] = await Promise.all([
      apiRequest<{ endpoint: string }>('/first/'),
      apiRequest<{ endpoint: string }>('/second/'),
    ])

    expect(first).toEqual({ endpoint: 'first' })
    expect(second).toEqual({ endpoint: 'second' })
    expect(useAuthStore.getState().accessToken).toBe('fresh-token')
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh/'))).toHaveLength(1)
  })

  it('retries a stale 401 with the latest access token before refreshing again', async () => {
    let resolveSlowResponse: (response: Response) => void = () => {}
    const slowResponse = new Promise<Response>((resolve) => {
      resolveSlowResponse = resolve
    })
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      const headers = init?.headers as Record<string, string> | undefined

      if (url.endsWith('/auth/refresh/')) {
        return Promise.resolve(jsonResponse(200, { access: 'fresh-token' }))
      }

      if (headers?.Authorization === 'Bearer fresh-token') {
        return Promise.resolve(jsonResponse(200, { endpoint: url.split('/').at(-2) }))
      }

      if (url.endsWith('/slow/')) return slowResponse

      return Promise.resolve(jsonResponse(401, { detail: 'Token expired.' }))
    })
    vi.stubGlobal('fetch', fetchMock)

    const slowRequest = apiRequest<{ endpoint: string }>('/slow/')
    const fastRequest = apiRequest<{ endpoint: string }>('/fast/')

    await expect(fastRequest).resolves.toEqual({ endpoint: 'fast' })
    resolveSlowResponse(jsonResponse(401, { detail: 'Token expired.' }))

    await expect(slowRequest).resolves.toEqual({ endpoint: 'slow' })
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh/'))).toHaveLength(1)
  })

  it('retries refresh once when refresh returns a 401', async () => {
    vi.useFakeTimers()

    let refreshAttempts = 0
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      const headers = init?.headers as Record<string, string> | undefined

      if (url.endsWith('/auth/refresh/')) {
        refreshAttempts += 1
        if (refreshAttempts === 1) {
          return Promise.resolve(jsonResponse(401, { detail: 'Session expired.' }))
        }
        return Promise.resolve(jsonResponse(200, { access: 'fresh-token' }))
      }

      if (headers?.Authorization === 'Bearer fresh-token') {
        return Promise.resolve(jsonResponse(200, { endpoint: url.split('/').at(-2) }))
      }

      return Promise.resolve(jsonResponse(401, { detail: 'Token expired.' }))
    })
    vi.stubGlobal('fetch', fetchMock)

    const request = apiRequest<{ endpoint: string }>('/protected/')

    await vi.runAllTimersAsync()

    await expect(request).resolves.toEqual({ endpoint: 'protected' })
    expect(useAuthStore.getState().accessToken).toBe('fresh-token')
    expect(fetchMock.mock.calls.filter(([url]) => String(url).endsWith('/auth/refresh/'))).toHaveLength(2)
  })
})

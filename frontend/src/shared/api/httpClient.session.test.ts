import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { AuthSessionChangedError, useAuthStore } from '@/shared/auth/useAuth'
import { apiRequest, refreshSharedAccessToken } from './httpClient'

const firstUser = { id: 1, username: 'first', email: 'first@example.com', is_staff: false }
const secondUser = { id: 2, username: 'second', email: 'second@example.com', is_staff: false }

function tokenFor(userId: number) {
  return `header.${btoa(JSON.stringify({ user_id: String(userId) }))}.signature`
}

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => { resolve = done })
  return { promise, resolve }
}

function jsonResponse(status: number, payload: unknown) {
  return new Response(JSON.stringify(payload), { status, headers: { 'Content-Type': 'application/json' } })
}

describe('HTTP authentication session isolation', () => {
  beforeEach(() => { useAuthStore.getState().setSession('first-token', firstUser) })
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    useAuthStore.getState().clearSession()
  })

  it('never replays the previous account purchase using a new account token', async () => {
    const response = deferred<Response>()
    const fetchMock = vi.fn(() => response.promise)
    vi.stubGlobal('fetch', fetchMock)
    const request = apiRequest('/shop/catalog/purchase/', { method: 'POST', body: '{"slug":"blue"}' })
    const rejected = expect(request).rejects.toBeInstanceOf(AuthSessionChangedError)

    useAuthStore.getState().setSession('second-token', secondUser)
    response.resolve(jsonResponse(401, { detail: 'Token expired.' }))

    await rejected
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(useAuthStore.getState()).toMatchObject({ accessToken: 'second-token', user: secondUser })
  })

  it('discards a late successful account response', async () => {
    const response = deferred<Response>()
    vi.stubGlobal('fetch', vi.fn(() => response.promise))
    const request = apiRequest('/wallet/')
    const rejected = expect(request).rejects.toBeInstanceOf(AuthSessionChangedError)

    useAuthStore.getState().setSession('second-token', secondUser)
    response.resolve(jsonResponse(200, { balance: 1000 }))

    await rejected
  })

  it('checks the session again after delayed response body parsing', async () => {
    const body = deferred<unknown>()
    const response = jsonResponse(200, {})
    const parse = vi.spyOn(response, 'json').mockReturnValue(body.promise)
    vi.stubGlobal('fetch', vi.fn(async () => response))
    const request = apiRequest('/wallet/')
    const rejected = expect(request).rejects.toBeInstanceOf(AuthSessionChangedError)
    await vi.waitFor(() => expect(parse).toHaveBeenCalled())

    useAuthStore.getState().setSession('second-token', secondUser)
    body.resolve({ balance: 1000 })

    await rejected
  })

  it('does not resurrect a logged-out session when its refresh finishes', async () => {
    const response = deferred<Response>()
    vi.stubGlobal('fetch', vi.fn(() => response.promise))
    const refresh = refreshSharedAccessToken()
    const rejected = expect(refresh).rejects.toBeInstanceOf(AuthSessionChangedError)

    useAuthStore.getState().clearSession()
    response.resolve(jsonResponse(200, { access: 'late-first-token' }))

    await rejected
    expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })
  })

  it('gives a new session its own refresh flight and ignores the old flight', async () => {
    const oldResponse = deferred<Response>()
    const newResponse = deferred<Response>()
    const fetchMock = vi.fn().mockReturnValueOnce(oldResponse.promise).mockReturnValueOnce(newResponse.promise)
    vi.stubGlobal('fetch', fetchMock)
    const oldRefresh = refreshSharedAccessToken()
    const rejected = expect(oldRefresh).rejects.toBeInstanceOf(AuthSessionChangedError)

    useAuthStore.getState().setSession('second-token', secondUser)
    const newRefresh = refreshSharedAccessToken()
    oldResponse.resolve(jsonResponse(200, { access: 'late-first-token' }))
    await rejected
    expect(useAuthStore.getState().accessToken).toBe('second-token')
    expect(refreshSharedAccessToken()).toBe(newRefresh)
    newResponse.resolve(jsonResponse(200, { access: tokenFor(secondUser.id) }))

    await expect(newRefresh).resolves.toBe(tokenFor(secondUser.id))
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(useAuthStore.getState()).toMatchObject({ accessToken: tokenFor(secondUser.id), user: secondUser })
  })

  it('stops refresh backoff before sending another request after an account switch', async () => {
    vi.useFakeTimers()
    const fetchMock = vi.fn(async () => jsonResponse(401, { detail: 'Expired' }))
    vi.stubGlobal('fetch', fetchMock)
    const refresh = refreshSharedAccessToken()
    const rejected = expect(refresh).rejects.toBeInstanceOf(AuthSessionChangedError)
    await vi.advanceTimersByTimeAsync(0)
    expect(fetchMock).toHaveBeenCalledTimes(1)

    useAuthStore.getState().setSession('second-token', secondUser)
    await vi.advanceTimersByTimeAsync(250)

    await rejected
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(useAuthStore.getState()).toMatchObject({ accessToken: 'second-token', user: secondUser })
  })

  it('retains the session generation through a successful token rotation', async () => {
    const generation = useAuthStore.getState().sessionGeneration
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse(200, { access: tokenFor(firstUser.id) })))

    await expect(refreshSharedAccessToken()).resolves.toBe(tokenFor(firstUser.id))

    expect(useAuthStore.getState()).toMatchObject({
      accessToken: tokenFor(firstUser.id), user: firstUser, sessionGeneration: generation,
    })
  })

  it('rejects another account token from a replaced refresh cookie without replaying a purchase', async () => {
    const fetchMock = vi.fn(async (url: string) => url.endsWith('/auth/refresh/')
      ? jsonResponse(200, { access: tokenFor(secondUser.id) })
      : jsonResponse(401, { detail: 'Expired access token' }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiRequest('/shop/catalog/purchase/', { method: 'POST', body: '{"slug":"blue"}' }))
      .rejects.toBeInstanceOf(AuthSessionChangedError)

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls.filter(([url]) => url.endsWith('/shop/catalog/purchase/'))).toHaveLength(1)
    expect(useAuthStore.getState()).toMatchObject({ accessToken: 'first-token', user: firstUser })
  })

  it.each([
    'invalid-token',
    `header.${btoa(JSON.stringify({}))}.signature`,
    `header.${btoa(JSON.stringify({ user_id: null }))}.signature`,
  ])('rejects malformed or missing refreshed identity %# without replacing the current token', async (access) => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse(200, { access })))

    await expect(refreshSharedAccessToken()).rejects.toBeInstanceOf(AuthSessionChangedError)

    expect(useAuthStore.getState()).toMatchObject({ accessToken: 'first-token', user: firstUser })
  })
})

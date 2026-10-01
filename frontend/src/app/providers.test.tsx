import { MutationObserver, QueryClient, useMutation, useQueryClient } from '@tanstack/react-query'
import { act, cleanup, render, screen, waitFor } from '@testing-library/react'
import { useEffect } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'
import { AUTH_USER_STORAGE_KEY } from '@/shared/auth/authSessionBoundary'
import { AuthSessionChangedError, confirmAuthSession, useAuthStore } from '@/shared/auth/useAuth'
import { AppProviders } from './providers'

vi.mock('@/shared/preferences/PreferencesSync', () => ({ PreferencesSync: () => null }))

const firstUser = { id: 1, username: 'first', email: 'first@example.com', is_staff: false }
const secondUser = { id: 2, username: 'second', email: 'second@example.com', is_staff: false }

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => { resolve = done })
  return { promise, resolve }
}

function QueryClientProbe({ onClient }: { onClient: (client: QueryClient) => void }) {
  const client = useQueryClient()
  onClient(client)
  return <div>Provider ready</div>
}

describe('AppProviders', () => {
  afterEach(() => {
    cleanup()
    useAuthStore.getState().clearSession()
  })

  it('provides a React Query client with conservative defaults', () => {
    let queryClient: QueryClient | undefined

    render(
      <AppProviders>
        <QueryClientProbe onClient={(client) => {
          queryClient = client
        }} />
      </AppProviders>,
    )

    expect(screen.getByText('Provider ready')).toBeInTheDocument()
    expect(queryClient).toBeDefined()
    const client = queryClient as QueryClient
    const queryDefaults = client.getDefaultOptions().queries
    const retry = queryDefaults?.retry

    expect(queryDefaults?.staleTime).toBe(30_000)
    expect(queryDefaults?.refetchOnWindowFocus).toBe(false)
    expect(typeof retry).toBe('function')
    expect(typeof retry === 'function' ? retry(0, new ApiError('Nope', 404, null)) : null).toBe(false)
    expect(typeof retry === 'function' ? retry(0, new Error('Temporary failure')) : null).toBe(true)
    expect(typeof retry === 'function' ? retry(1, new Error('Temporary failure')) : null).toBe(false)
    expect(typeof retry === 'function' ? retry(0, new AuthSessionChangedError()) : null).toBe(false)
  })

  it('isolates cached account data across a cross-tab identity change while preserving token rotations', () => {
    useAuthStore.getState().setSession('first-token', firstUser)
    let currentClient!: QueryClient
    render(<AppProviders><QueryClientProbe onClient={(client) => { currentClient = client }} /></AppProviders>)
    const firstClient = currentClient
    firstClient.setQueryData(queryKeys.homeSummary, { owner: firstUser.id })
    firstClient.setQueryData(queryKeys.preferences, { onboarding_phase: 'welcome' })

    act(() => { useAuthStore.getState().setAccessToken('rotated-first-token') })
    expect(currentClient).toBe(firstClient)
    expect(currentClient.getQueryData(queryKeys.homeSummary)).toEqual({ owner: firstUser.id })

    act(() => {
      localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(secondUser))
      window.dispatchEvent(new StorageEvent('storage', { key: AUTH_USER_STORAGE_KEY }))
      confirmAuthSession('second-token', secondUser)
    })
    expect(currentClient).not.toBe(firstClient)
    expect(currentClient.getQueryData(queryKeys.homeSummary)).toBeUndefined()
    expect(currentClient.getQueryData(queryKeys.preferences)).toBeUndefined()
    expect(firstClient.getQueryCache().getAll()).toHaveLength(0)

    // A callback that already captured its client cannot refill the new one.
    firstClient.setQueryData(queryKeys.homeSummary, { owner: firstUser.id })
    expect(currentClient.getQueryData(queryKeys.homeSummary)).toBeUndefined()
  })

  it('rejects a late mutation success before an old callback can update the new session', async () => {
    useAuthStore.getState().setSession('first-token', firstUser)
    const response = deferred<string>()
    const onSuccess = vi.fn()
    let start!: () => Promise<string>
    function PendingMutation() {
      const mutation = useMutation({ mutationFn: () => response.promise, onSuccess })
      useEffect(() => { start = mutation.mutateAsync }, [mutation.mutateAsync])
      return null
    }
    render(<AppProviders><PendingMutation /></AppProviders>)
    let pending!: Promise<string>
    act(() => { pending = start() })
    const rejected = expect(pending).rejects.toBeInstanceOf(AuthSessionChangedError)
    await waitFor(() => expect(useAuthStore.getState().user?.id).toBe(1))

    act(() => { useAuthStore.getState().setSession('second-token', secondUser) })
    await act(async () => { response.resolve('old-success'); await rejected })

    expect(onSuccess).not.toHaveBeenCalled()
    expect(useAuthStore.getState().user).toEqual(secondUser)
  })

  it('blocks a queued write even when observer options change during an asynchronous onMutate', async () => {
    useAuthStore.getState().setSession('first-token', firstUser)
    let client!: QueryClient
    render(<AppProviders><QueryClientProbe onClient={(value) => { client = value }} /></AppProviders>)
    const release = deferred<void>()
    const onMutate = vi.fn(() => release.promise)
    const firstWrite = vi.fn(async () => 'first')
    const changedWrite = vi.fn(async () => 'changed')
    const observer = new MutationObserver(client, { mutationFn: firstWrite, onMutate })
    const pending = observer.mutate()
    const rejected = expect(pending).rejects.toBeInstanceOf(AuthSessionChangedError)
    await waitFor(() => expect(onMutate).toHaveBeenCalledOnce())
    observer.setOptions({ mutationFn: changedWrite, onMutate })

    act(() => { useAuthStore.getState().setSession('second-token', secondUser) })
    await act(async () => { release.resolve(); await rejected })

    expect(firstWrite).not.toHaveBeenCalled()
    expect(changedWrite).not.toHaveBeenCalled()
    expect(useAuthStore.getState().accessToken).toBe('second-token')
  })
})

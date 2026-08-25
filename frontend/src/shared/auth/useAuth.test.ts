import { afterEach, expect, it, vi } from 'vitest'

import {
  AUTH_SESSION_CHANNEL_NAME,
  AUTH_USER_STORAGE_KEY,
  LEGACY_ACCESS_TOKEN_STORAGE_KEY,
} from './authSessionBoundary'

const canonicalUser = {
  id: 1,
  username: 'student',
  email: 'student@example.com',
  is_staff: false,
}

class TestStorage implements Storage {
  readonly values = new Map<string, string>()
  shouldThrow = false

  get length() {
    return this.values.size
  }

  clear() {
    this.failIfNeeded()
    this.values.clear()
  }

  getItem(key: string) {
    this.failIfNeeded()
    return this.values.get(key) ?? null
  }

  key(index: number) {
    this.failIfNeeded()
    return Array.from(this.values.keys())[index] ?? null
  }

  removeItem(key: string) {
    this.failIfNeeded()
    this.values.delete(key)
  }

  setItem(key: string, value: string) {
    this.failIfNeeded()
    this.values.set(key, String(value))
  }

  private failIfNeeded() {
    if (this.shouldThrow) throw new Error('storage unavailable')
  }
}

class TestBroadcastChannel {
  static instances: TestBroadcastChannel[] = []

  readonly name: string
  readonly posted: unknown[] = []
  shouldThrow = false
  private messageListener: ((event: MessageEvent<unknown>) => void) | undefined

  constructor(name: string) {
    this.name = name
    TestBroadcastChannel.instances.push(this)
  }

  addEventListener(_type: 'message', listener: (event: MessageEvent<unknown>) => void) {
    this.messageListener = listener
  }

  postMessage(message: unknown) {
    if (this.shouldThrow) throw new Error('channel unavailable')
    this.posted.push(message)
  }

  emit(data: unknown) {
    this.messageListener?.({ data } as MessageEvent<unknown>)
  }
}

const originalStorage = window.localStorage
const originalBroadcastChannel = window.BroadcastChannel

afterEach(() => {
  Object.defineProperty(window, 'localStorage', { configurable: true, value: originalStorage })
  Object.defineProperty(window, 'BroadcastChannel', {
    configurable: true,
    value: originalBroadcastChannel,
  })
  TestBroadcastChannel.instances = []
  vi.resetModules()
})

it('owns hydration, event transitions, cross-tab sync, and failure-tolerant actions', async () => {
  const storage = new TestStorage()
  storage.values.set(
    AUTH_USER_STORAGE_KEY,
    JSON.stringify({
      id: 1,
      username: 'student',
      email: 'student@example.com',
      stale: true,
    }),
  )
  storage.values.set(LEGACY_ACCESS_TOKEN_STORAGE_KEY, 'legacy-secret')
  Object.defineProperty(window, 'localStorage', { configurable: true, value: storage })
  Object.defineProperty(window, 'BroadcastChannel', {
    configurable: true,
    value: TestBroadcastChannel,
  })

  const { beginAuthConfirmation, confirmAuthSession, useAuthStore } = await import('./useAuth')
  const channel = TestBroadcastChannel.instances[0]
  expect(channel?.name).toBe(AUTH_SESSION_CHANNEL_NAME)
  expect(useAuthStore.getState().user).toEqual(canonicalUser)
  expect(storage.values.get(AUTH_USER_STORAGE_KEY)).toBe(JSON.stringify(canonicalUser))
  expect(storage.values.has(LEGACY_ACCESS_TOKEN_STORAGE_KEY)).toBe(false)

  useAuthStore.getState().setSession('active', canonicalUser)
  const authenticatedState = useAuthStore.getState()
  channel?.emit({ type: 'session', accessToken: '   ', user: canonicalUser })
  channel?.emit({ type: 'session', accessToken: 'forged', user: { username: 'partial' } })
  expect(useAuthStore.getState()).toMatchObject({
    accessToken: authenticatedState.accessToken,
    user: authenticatedState.user,
  })

  storage.values.set(
    AUTH_USER_STORAGE_KEY,
    JSON.stringify({ id: 1, username: 'student', email: 'student@example.com', stale: true }),
  )
  window.dispatchEvent(new StorageEvent('storage', { key: AUTH_USER_STORAGE_KEY }))
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: canonicalUser })
  expect(storage.values.get(AUTH_USER_STORAGE_KEY)).toBe(JSON.stringify(canonicalUser))

  useAuthStore.getState().setSession('active-again', canonicalUser)
  storage.values.delete(AUTH_USER_STORAGE_KEY)
  window.dispatchEvent(new StorageEvent('storage', { key: AUTH_USER_STORAGE_KEY }))
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })

  useAuthStore.getState().setSession('active-again', canonicalUser)
  storage.values.set(AUTH_USER_STORAGE_KEY, '{bad json')
  window.dispatchEvent(new StorageEvent('storage', { key: AUTH_USER_STORAGE_KEY }))
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })
  expect(storage.values.has(AUTH_USER_STORAGE_KEY)).toBe(false)

  useAuthStore.getState().setSession('active-again', canonicalUser)
  storage.values.set(AUTH_USER_STORAGE_KEY, JSON.stringify({ username: 'partial' }))
  window.dispatchEvent(new StorageEvent('storage', { key: AUTH_USER_STORAGE_KEY }))
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })
  expect(storage.values.has(AUTH_USER_STORAGE_KEY)).toBe(false)

  channel?.emit({
    type: 'session',
    accessToken: 'cross-tab',
    user: { ...canonicalUser, tier: 'stale' },
  })
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'cross-tab', user: null })
  expect(storage.values.has(AUTH_USER_STORAGE_KEY)).toBe(false)

  const postsBeforeSessionConfirmation = channel?.posted.length
  confirmAuthSession('cross-tab', canonicalUser)
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'cross-tab', user: canonicalUser })
  expect(storage.values.get(AUTH_USER_STORAGE_KEY)).toBe(JSON.stringify(canonicalUser))
  expect(storage.values.has(LEGACY_ACCESS_TOKEN_STORAGE_KEY)).toBe(false)
  expect(channel?.posted).toHaveLength(postsBeforeSessionConfirmation ?? 0)

  channel?.emit({ type: 'access-token', accessToken: ' padded-token ' })
  expect(useAuthStore.getState()).toMatchObject({ accessToken: ' padded-token ', user: null })
  expect(storage.values.has(LEGACY_ACCESS_TOKEN_STORAGE_KEY)).toBe(false)

  const postsBeforeTokenConfirmation = channel?.posted.length
  confirmAuthSession(' padded-token ', canonicalUser)
  expect(useAuthStore.getState()).toMatchObject({ accessToken: ' padded-token ', user: canonicalUser })
  expect(channel?.posted).toHaveLength(postsBeforeTokenConfirmation ?? 0)

  const postsBeforeRefreshConfirmation = channel?.posted.length ?? 0
  beginAuthConfirmation('refreshed-token')
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'refreshed-token', user: null })
  expect(channel?.posted).toHaveLength(postsBeforeRefreshConfirmation + 1)
  expect(channel?.posted.at(-1)).toEqual({
    type: 'access-token',
    accessToken: 'refreshed-token',
  })

  confirmAuthSession('refreshed-token', canonicalUser)
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'refreshed-token', user: canonicalUser })
  expect(channel?.posted).toHaveLength(postsBeforeRefreshConfirmation + 1)

  channel?.emit({ type: 'clear-session' })
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })
  expect(storage.values.has(AUTH_USER_STORAGE_KEY)).toBe(false)

  storage.shouldThrow = true
  if (channel) channel.shouldThrow = true
  expect(() => useAuthStore.getState().setSession('offline', canonicalUser)).not.toThrow()
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'offline', user: canonicalUser })
  expect(() => useAuthStore.getState().setAccessToken('rotated-offline')).not.toThrow()
  expect(useAuthStore.getState()).toMatchObject({ accessToken: 'rotated-offline', user: canonicalUser })
  expect(() => useAuthStore.getState().clearSession()).not.toThrow()
  expect(useAuthStore.getState()).toMatchObject({ accessToken: null, user: null })
})

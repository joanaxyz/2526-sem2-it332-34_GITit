import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  AUTH_USER_STORAGE_KEY,
  LEGACY_ACCESS_TOKEN_STORAGE_KEY,
  canonicalizeAuthUser,
  createAuthSessionBoundary,
  decodeAuthSessionMessage,
  type AuthSessionBoundaryEnvironment,
} from './authSessionBoundary'

const user = {
  id: 7,
  username: 'student',
  email: 'student@example.com',
  is_staff: false,
}

const originalStorage = window.localStorage
const originalBroadcastChannel = window.BroadcastChannel

afterEach(() => {
  Object.defineProperty(window, 'localStorage', { configurable: true, value: originalStorage })
  Object.defineProperty(window, 'BroadcastChannel', {
    configurable: true,
    value: originalBroadcastChannel,
  })
})

function createStorage(initial: Record<string, string> = {}) {
  const values = new Map(Object.entries(initial))
  return {
    values,
    storage: {
      getItem: vi.fn((key: string) => values.get(key) ?? null),
      setItem: vi.fn((key: string, value: string) => values.set(key, value)),
      removeItem: vi.fn((key: string) => values.delete(key)),
    },
  }
}

describe('canonicalizeAuthUser', () => {
  it('returns the exact generated user shape and strips unknown fields', () => {
    expect(canonicalizeAuthUser({ ...user, tier: 'stale', nested: {} })).toEqual(user)
  })

  it('migrates legacy users that predate is_staff', () => {
    expect(canonicalizeAuthUser({ id: 7, username: 'student', email: 'student@example.com' })).toEqual(
      user,
    )
  })

  it.each([
    null,
    'student',
    [],
    { username: 'student' },
    { ...user, id: Number.NaN },
    { ...user, id: 7.5 },
    { ...user, id: '7' },
    { ...user, email: null },
    { ...user, is_staff: 'false' },
  ])('rejects invalid user input %#', (value) => {
    expect(canonicalizeAuthUser(value)).toBeNull()
  })
})

describe('decodeAuthSessionMessage', () => {
  it('canonicalizes session users while preserving a valid token verbatim', () => {
    expect(
      decodeAuthSessionMessage({
        type: 'session',
        accessToken: ' token-with-padding ',
        user: { ...user, stale: true },
      }),
    ).toEqual({ type: 'session', accessToken: ' token-with-padding ', user })
  })

  it('accepts access-token and clear-session messages', () => {
    expect(decodeAuthSessionMessage({ type: 'access-token', accessToken: 'fresh' })).toEqual({
      type: 'access-token',
      accessToken: 'fresh',
    })
    expect(decodeAuthSessionMessage({ type: 'clear-session' })).toEqual({ type: 'clear-session' })
  })

  it.each([
    null,
    {},
    { type: 'unknown' },
    { type: 'access-token', accessToken: '' },
    { type: 'access-token', accessToken: '   ' },
    { type: 'session', accessToken: 'fresh', user: { username: 'partial' } },
  ])('rejects malformed channel input %#', (value) => {
    expect(decodeAuthSessionMessage(value)).toBeNull()
  })
})

describe('auth session persistence', () => {
  it('removes malformed and invalid stored users', () => {
    const { storage, values } = createStorage({ [AUTH_USER_STORAGE_KEY]: '{bad json' })
    const boundary = createAuthSessionBoundary({ storage, channel: null, addStorageListener: null })

    expect(boundary.readUser()).toBeNull()
    expect(values.has(AUTH_USER_STORAGE_KEY)).toBe(false)

    values.set(AUTH_USER_STORAGE_KEY, JSON.stringify({ username: 'partial' }))
    expect(boundary.readUser()).toBeNull()
    expect(values.has(AUTH_USER_STORAGE_KEY)).toBe(false)
  })

  it('rewrites legacy and extra fields to the canonical stored shape', () => {
    const { storage, values } = createStorage({
      [AUTH_USER_STORAGE_KEY]: JSON.stringify({
        id: 7,
        username: 'student',
        email: 'student@example.com',
        stale: true,
      }),
      [LEGACY_ACCESS_TOKEN_STORAGE_KEY]: 'legacy-secret',
    })
    const boundary = createAuthSessionBoundary({ storage, channel: null, addStorageListener: null })

    expect(boundary.readUser()).toEqual(user)
    expect(values.get(AUTH_USER_STORAGE_KEY)).toBe(JSON.stringify(user))
    boundary.persistUser(user)
    expect(values.has(LEGACY_ACCESS_TOKEN_STORAGE_KEY)).toBe(false)
  })

  it('validates subscriptions before delivering storage and channel changes', () => {
    const { storage, values } = createStorage({ [AUTH_USER_STORAGE_KEY]: JSON.stringify(user) })
    let storageListener: ((event: StorageEvent) => void) | undefined
    let messageListener: ((event: MessageEvent<unknown>) => void) | undefined
    const onStoredUserChange = vi.fn()
    const onMessage = vi.fn()
    const environment: AuthSessionBoundaryEnvironment = {
      storage,
      channel: {
        postMessage: vi.fn(),
        addEventListener: (_type, listener) => {
          messageListener = listener
        },
      },
      addStorageListener: (listener) => {
        storageListener = listener
      },
    }
    const boundary = createAuthSessionBoundary(environment)
    boundary.subscribe({ onStoredUserChange, onMessage })

    storageListener?.({ key: 'unrelated' } as StorageEvent)
    expect(onStoredUserChange).not.toHaveBeenCalled()

    storageListener?.({ key: AUTH_USER_STORAGE_KEY } as StorageEvent)
    expect(onStoredUserChange).toHaveBeenLastCalledWith(user)

    values.set(AUTH_USER_STORAGE_KEY, JSON.stringify({ username: 'partial' }))
    storageListener?.({ key: AUTH_USER_STORAGE_KEY } as StorageEvent)
    expect(onStoredUserChange).toHaveBeenLastCalledWith(null)

    messageListener?.({ data: { type: 'access-token', accessToken: '   ' } } as MessageEvent)
    expect(onMessage).not.toHaveBeenCalled()
    messageListener?.({ data: { type: 'access-token', accessToken: 'fresh' } } as MessageEvent)
    expect(onMessage).toHaveBeenLastCalledWith({ type: 'access-token', accessToken: 'fresh' })
  })

  it('contains browser API failures', () => {
    const fail = () => {
      throw new Error('browser API unavailable')
    }
    const boundary = createAuthSessionBoundary({
      storage: { getItem: fail, setItem: fail, removeItem: fail },
      channel: { postMessage: fail, addEventListener: fail },
      addStorageListener: fail,
    })

    expect(() => boundary.readUser()).not.toThrow()
    expect(() => boundary.persistUser(user)).not.toThrow()
    expect(() => boundary.removeLegacyAccessToken()).not.toThrow()
    expect(() => boundary.clearPersistedSession()).not.toThrow()
    expect(() => boundary.publish({ type: 'session', accessToken: 'fresh', user })).not.toThrow()
    expect(() => boundary.subscribe({ onStoredUserChange: vi.fn(), onMessage: vi.fn() })).not.toThrow()
  })

  it('contains default browser-environment discovery failures', () => {
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      get: () => {
        throw new Error('storage getter unavailable')
      },
    })
    expect(() => createAuthSessionBoundary()).not.toThrow()

    Object.defineProperty(window, 'localStorage', { configurable: true, value: originalStorage })
    Object.defineProperty(window, 'BroadcastChannel', {
      configurable: true,
      value: class {
        constructor() {
          throw new Error('channel constructor unavailable')
        }
      },
    })
    expect(() => createAuthSessionBoundary()).not.toThrow()
  })
})

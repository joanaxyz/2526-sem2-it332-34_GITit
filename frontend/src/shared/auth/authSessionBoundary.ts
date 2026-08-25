import type { User } from '@/shared/auth/types'

export const AUTH_USER_STORAGE_KEY = 'git-it-user'
export const LEGACY_ACCESS_TOKEN_STORAGE_KEY = 'git-it-access-token'
export const AUTH_SESSION_CHANNEL_NAME = 'git-it-auth-session'

export type AuthSessionMessage =
  | { type: 'session'; accessToken: string; user: User }
  | { type: 'access-token'; accessToken: string }
  | { type: 'clear-session' }

type AuthStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
type AuthChannel = {
  postMessage: (message: unknown) => void
  addEventListener: (
    type: 'message',
    listener: (event: MessageEvent<unknown>) => void,
  ) => void
}

export type AuthSessionBoundaryEnvironment = {
  storage: AuthStorage | null
  channel: AuthChannel | null
  addStorageListener: ((listener: (event: StorageEvent) => void) => void) | null
}

export type AuthSessionBoundary = {
  readUser: () => User | null
  persistUser: (value: unknown) => User | null
  removeLegacyAccessToken: () => void
  clearPersistedSession: () => void
  publish: (message: AuthSessionMessage) => void
  subscribe: (handlers: {
    onStoredUserChange: (user: User | null) => void
    onMessage: (message: AuthSessionMessage) => void
  }) => void
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function hasUsableToken(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

export function canonicalizeAuthUser(value: unknown): User | null {
  if (!isRecord(value)) return null

  const isStaff = value.is_staff === undefined ? false : value.is_staff
  if (
    typeof value.id !== 'number' ||
    !Number.isInteger(value.id) ||
    typeof value.username !== 'string' ||
    typeof value.email !== 'string' ||
    typeof isStaff !== 'boolean'
  ) {
    return null
  }

  return {
    id: value.id,
    username: value.username,
    email: value.email,
    is_staff: isStaff,
  } satisfies User
}

export function decodeAuthSessionMessage(value: unknown): AuthSessionMessage | null {
  if (!isRecord(value) || typeof value.type !== 'string') return null

  if (value.type === 'clear-session') return { type: 'clear-session' }
  if (!hasUsableToken(value.accessToken)) return null

  if (value.type === 'access-token') {
    return { type: 'access-token', accessToken: value.accessToken }
  }

  if (value.type === 'session') {
    const user = canonicalizeAuthUser(value.user)
    return user ? { type: 'session', accessToken: value.accessToken, user } : null
  }

  return null
}

function browserEnvironment(): AuthSessionBoundaryEnvironment {
  let storage: Storage | null = null
  let channel: BroadcastChannel | null = null

  if (typeof window !== 'undefined') {
    try {
      storage = window.localStorage
    } catch {
      storage = null
    }

    try {
      channel = typeof window.BroadcastChannel === 'undefined'
        ? null
        : new window.BroadcastChannel(AUTH_SESSION_CHANNEL_NAME)
    } catch {
      channel = null
    }
  }

  return {
    storage,
    channel,
    addStorageListener:
      typeof window === 'undefined'
        ? null
        : (listener) => window.addEventListener('storage', listener),
  }
}

export function createAuthSessionBoundary(
  environment: AuthSessionBoundaryEnvironment = browserEnvironment(),
): AuthSessionBoundary {
  const { storage, channel, addStorageListener } = environment

  function safely(operation: () => void) {
    try {
      operation()
    } catch {
      // Browser storage and cross-tab synchronization are best-effort caches.
    }
  }

  function removeLegacyAccessToken() {
    if (storage) safely(() => storage.removeItem(LEGACY_ACCESS_TOKEN_STORAGE_KEY))
  }

  function removeUser() {
    if (storage) safely(() => storage.removeItem(AUTH_USER_STORAGE_KEY))
  }

  function persistCanonicalUser(user: User) {
    removeLegacyAccessToken()
    if (storage) safely(() => storage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user)))
  }

  function readUser(): User | null {
    if (!storage) return null

    let raw: string | null = null
    safely(() => {
      raw = storage.getItem(AUTH_USER_STORAGE_KEY)
    })
    if (raw === null) return null

    let parsed: unknown
    try {
      parsed = JSON.parse(raw)
    } catch {
      removeUser()
      return null
    }

    const user = canonicalizeAuthUser(parsed)
    if (!user) {
      removeUser()
      return null
    }

    const canonical = JSON.stringify(user)
    if (canonical !== raw) safely(() => storage.setItem(AUTH_USER_STORAGE_KEY, canonical))
    return user
  }

  return {
    readUser,
    persistUser: (value) => {
      const user = canonicalizeAuthUser(value)
      if (!user) {
        removeUser()
        return null
      }
      persistCanonicalUser(user)
      return user
    },
    removeLegacyAccessToken,
    clearPersistedSession: () => {
      removeLegacyAccessToken()
      removeUser()
    },
    publish: (message) => {
      const validated = decodeAuthSessionMessage(message)
      if (channel && validated) safely(() => channel.postMessage(validated))
    },
    subscribe: ({ onStoredUserChange, onMessage }) => {
      if (addStorageListener) {
        safely(() => {
          addStorageListener((event) => {
            if (
              event.key &&
              event.key !== AUTH_USER_STORAGE_KEY &&
              event.key !== LEGACY_ACCESS_TOKEN_STORAGE_KEY
            ) {
              return
            }
            removeLegacyAccessToken()
            onStoredUserChange(readUser())
          })
        })
      }

      if (channel) {
        safely(() => {
          channel.addEventListener('message', (event) => {
            const message = decodeAuthSessionMessage(event.data)
            if (message) onMessage(message)
          })
        })
      }
    },
  }
}

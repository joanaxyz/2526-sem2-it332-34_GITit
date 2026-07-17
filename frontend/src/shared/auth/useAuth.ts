import { create } from 'zustand'

import type { User } from '@/shared/auth/types'

type AuthState = {
  accessToken: string | null
  user: User | null
  setSession: (accessToken: string, user: User) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

type AuthChannelMessage =
  | { type: 'session'; accessToken: string; user: User }
  | { type: 'access-token'; accessToken: string }
  | { type: 'clear-session' }

const userStorageKey = 'git-it-user'
const legacyAccessTokenStorageKey = 'git-it-access-token'
const authChannelName = 'git-it-auth-session'

function browserStorage() {
  if (typeof window === 'undefined') return null
  try {
    const storage = window.localStorage
    return storage && typeof storage.getItem === 'function' ? storage : null
  } catch {
    return null
  }
}

function getStoredUser() {
  const storage = browserStorage()
  const storedUser = storage?.getItem(userStorageKey)
  if (!storedUser) return null
  try {
    const parsed = JSON.parse(storedUser) as User
    return { ...parsed, is_staff: parsed.is_staff ?? false }
  } catch {
    storage?.removeItem(userStorageKey)
    return null
  }
}

function removeLegacyAccessToken() {
  browserStorage()?.removeItem(legacyAccessTokenStorageKey)
}

function authChannel() {
  if (typeof BroadcastChannel === 'undefined') return null
  try {
    return new BroadcastChannel(authChannelName)
  } catch {
    return null
  }
}

const storedUser = getStoredUser()
const channel = authChannel()

function publishAuthMessage(message: AuthChannelMessage) {
  channel?.postMessage(message)
}

export const useAuthStore = create<AuthState>((set) => {
  removeLegacyAccessToken()

  if (typeof window !== 'undefined') {
    window.addEventListener('storage', (event) => {
      if (event.key && event.key !== userStorageKey && event.key !== legacyAccessTokenStorageKey) return
      removeLegacyAccessToken()
      set({ accessToken: null, user: getStoredUser() })
    })
  }

  if (channel) {
    channel.addEventListener('message', (event: MessageEvent<AuthChannelMessage>) => {
      const message = event.data
      if (!message || typeof message !== 'object' || !('type' in message)) return

      if (message.type === 'session') {
        browserStorage()?.setItem(userStorageKey, JSON.stringify(message.user))
        set({ accessToken: message.accessToken, user: message.user })
        return
      }

      if (message.type === 'access-token') {
        set({ accessToken: message.accessToken })
        return
      }

      if (message.type === 'clear-session') {
        browserStorage()?.removeItem(userStorageKey)
        removeLegacyAccessToken()
        set({ accessToken: null, user: null })
      }
    })
  }

  return {
    accessToken: null,
    user: storedUser,
    setSession: (accessToken, user) => {
      const storage = browserStorage()
      storage?.removeItem(legacyAccessTokenStorageKey)
      storage?.setItem(userStorageKey, JSON.stringify(user))
      set({ accessToken, user })
      publishAuthMessage({ type: 'session', accessToken, user })
    },
    setAccessToken: (accessToken) => {
      removeLegacyAccessToken()
      set({ accessToken })
      publishAuthMessage({ type: 'access-token', accessToken })
    },
    clearSession: () => {
      const storage = browserStorage()
      storage?.removeItem(legacyAccessTokenStorageKey)
      storage?.removeItem(userStorageKey)
      set({ accessToken: null, user: null })
      publishAuthMessage({ type: 'clear-session' })
    },
  }
})

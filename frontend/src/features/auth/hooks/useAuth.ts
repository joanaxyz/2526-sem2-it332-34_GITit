import { create } from 'zustand'

import type { User } from '@/features/auth/types'

type AuthState = {
  accessToken: string | null
  user: User | null
  setSession: (accessToken: string, user: User) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

const accessTokenStorageKey = 'git-it-access-token'
const userStorageKey = 'git-it-user'

function browserStorage() {
  if (typeof window === 'undefined') return null
  const storage = window.localStorage
  return storage && typeof storage.getItem === 'function' ? storage : null
}

export function getStoredAccessToken() {
  return browserStorage()?.getItem(accessTokenStorageKey) ?? null
}

function getStoredUser() {
  const storage = browserStorage()
  const storedUser = storage?.getItem(userStorageKey)
  if (!storedUser) return null
  try {
    return JSON.parse(storedUser) as User
  } catch {
    storage?.removeItem(userStorageKey)
    return null
  }
}

const storedToken = getStoredAccessToken()
const storedUser = getStoredUser()

export const useAuthStore = create<AuthState>((set) => {
  if (typeof window !== 'undefined') {
    window.addEventListener('storage', (event) => {
      if (event.key && event.key !== accessTokenStorageKey && event.key !== userStorageKey) return
      set({ accessToken: getStoredAccessToken(), user: getStoredUser() })
    })
  }

  return {
    accessToken: storedToken,
    user: storedUser,
    setSession: (accessToken, user) => {
      const storage = browserStorage()
      storage?.setItem(accessTokenStorageKey, accessToken)
      storage?.setItem(userStorageKey, JSON.stringify(user))
      set({ accessToken, user })
    },
    setAccessToken: (accessToken) => {
      browserStorage()?.setItem(accessTokenStorageKey, accessToken)
      set({ accessToken })
    },
    clearSession: () => {
      const storage = browserStorage()
      storage?.removeItem(accessTokenStorageKey)
      storage?.removeItem(userStorageKey)
      set({ accessToken: null, user: null })
    },
  }
})

export function useAuth() {
  return useAuthStore()
}

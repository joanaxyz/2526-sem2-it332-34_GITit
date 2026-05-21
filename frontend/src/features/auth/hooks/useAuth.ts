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

export function getStoredAccessToken() {
  return localStorage.getItem(accessTokenStorageKey)
}

function getStoredUser() {
  const storedUser = localStorage.getItem(userStorageKey)
  if (!storedUser) return null
  try {
    return JSON.parse(storedUser) as User
  } catch {
    localStorage.removeItem(userStorageKey)
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
      localStorage.setItem(accessTokenStorageKey, accessToken)
      localStorage.setItem(userStorageKey, JSON.stringify(user))
      set({ accessToken, user })
    },
    setAccessToken: (accessToken) => {
      localStorage.setItem(accessTokenStorageKey, accessToken)
      set({ accessToken })
    },
    clearSession: () => {
      localStorage.removeItem(accessTokenStorageKey)
      localStorage.removeItem(userStorageKey)
      set({ accessToken: null, user: null })
    },
  }
})

export function useAuth() {
  return useAuthStore()
}

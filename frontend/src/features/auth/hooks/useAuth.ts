import { create } from 'zustand'

import type { User } from '@/features/auth/types'

type AuthState = {
  accessToken: string | null
  user: User | null
  setSession: (accessToken: string, user: User) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

const storedToken = localStorage.getItem('git-it-access-token')
const storedUser = localStorage.getItem('git-it-user')

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: storedToken,
  user: storedUser ? (JSON.parse(storedUser) as User) : null,
  setSession: (accessToken, user) => {
    localStorage.setItem('git-it-access-token', accessToken)
    localStorage.setItem('git-it-user', JSON.stringify(user))
    set({ accessToken, user })
  },
  setAccessToken: (accessToken) => {
    localStorage.setItem('git-it-access-token', accessToken)
    set({ accessToken })
  },
  clearSession: () => {
    localStorage.removeItem('git-it-access-token')
    localStorage.removeItem('git-it-user')
    set({ accessToken: null, user: null })
  },
}))

export function useAuth() {
  return useAuthStore()
}

import { create } from 'zustand'

import {
  canonicalizeAuthUser,
  createAuthSessionBoundary,
  type AuthSessionMessage,
} from '@/shared/auth/authSessionBoundary'
import type { User } from '@/shared/auth/types'

type AuthState = {
  accessToken: string | null
  user: User | null
  setSession: (accessToken: string, user: User) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

const browserSession = createAuthSessionBoundary()
const storedUser = browserSession.readUser()

function installSession(accessToken: string, user: User, publish: boolean) {
  const canonicalUser = canonicalizeAuthUser(user)
  if (!canonicalUser) {
    useAuthStore.setState({ accessToken: null, user: null })
    browserSession.clearPersistedSession()
    browserSession.publish({ type: 'clear-session' })
    return
  }

  useAuthStore.setState({ accessToken, user: canonicalUser })
  browserSession.persistUser(canonicalUser)
  if (publish) {
    browserSession.publish({ type: 'session', accessToken, user: canonicalUser })
  }
}

function applyChannelMessage(
  set: (state: Partial<Pick<AuthState, 'accessToken' | 'user'>>) => void,
  message: AuthSessionMessage,
) {
  if (message.type === 'session') {
    set({ accessToken: message.accessToken, user: null })
    return
  }

  if (message.type === 'access-token') {
    set({ accessToken: message.accessToken, user: null })
    browserSession.removeLegacyAccessToken()
    return
  }

  set({ accessToken: null, user: null })
  browserSession.clearPersistedSession()
}

export const useAuthStore = create<AuthState>((set) => {
  browserSession.removeLegacyAccessToken()
  browserSession.subscribe({
    onStoredUserChange: (user) => set({ accessToken: null, user }),
    onMessage: (message) => applyChannelMessage(set, message),
  })

  return {
    accessToken: null,
    user: storedUser,
    setSession: (accessToken, user) => installSession(accessToken, user, true),
    setAccessToken: (accessToken) => {
      set({ accessToken })
      browserSession.removeLegacyAccessToken()
      browserSession.publish({ type: 'access-token', accessToken })
    },
    clearSession: () => {
      set({ accessToken: null, user: null })
      browserSession.clearPersistedSession()
      browserSession.publish({ type: 'clear-session' })
    },
  }
})

export function beginAuthConfirmation(accessToken: string) {
  useAuthStore.setState({ accessToken, user: null })
  browserSession.removeLegacyAccessToken()
  browserSession.publish({ type: 'access-token', accessToken })
}

export function confirmAuthSession(accessToken: string, user: User) {
  installSession(accessToken, user, false)
}

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
  /** Request/cache lifetime; token rotation within an account retains it. */
  sessionGeneration: number
  /** Scope hint retained while /auth/me confirms a rotated token. */
  sessionUserId: number | null
  setSession: (accessToken: string, user: User) => void
  setAccessToken: (accessToken: string) => void
  clearSession: () => void
}

const browserSession = createAuthSessionBoundary()
const storedUser = browserSession.readUser()

export class AuthSessionChangedError extends Error {
  constructor() {
    super('Your sign-in changed. Please try again in your current session.')
    this.name = 'AuthSessionChangedError'
  }
}

export function assertAuthSession(sessionGeneration: number) {
  if (useAuthStore.getState().sessionGeneration !== sessionGeneration) {
    throw new AuthSessionChangedError()
  }
}

function installSession(accessToken: string, user: User, publish: boolean) {
  const canonicalUser = canonicalizeAuthUser(user)
  if (!canonicalUser) {
    useAuthStore.getState().clearSession()
    return
  }

  const current = useAuthStore.getState()
  useAuthStore.setState({
    accessToken,
    user: canonicalUser,
    sessionUserId: canonicalUser.id,
    sessionGeneration: current.sessionGeneration + (publish || current.sessionUserId !== canonicalUser.id ? 1 : 0),
  })
  browserSession.persistUser(canonicalUser)
  if (publish) {
    browserSession.publish({ type: 'session', accessToken, user: canonicalUser })
  }
}

function applyChannelMessage(
  set: (state: Partial<AuthState>) => void,
  message: AuthSessionMessage,
) {
  const current = useAuthStore.getState()
  if (message.type !== 'clear-session') {
    const userId = message.type === 'session' ? message.user.id : message.userId ?? null
    set({
      accessToken: message.accessToken,
      user: null,
      sessionUserId: userId,
      // An identity-free token cannot safely inherit an account's requests.
      sessionGeneration: current.sessionGeneration + (userId === null || userId !== current.sessionUserId ? 1 : 0),
    })
    browserSession.removeLegacyAccessToken()
    return
  }

  set({ accessToken: null, user: null, sessionUserId: null, sessionGeneration: current.sessionGeneration + 1 })
  browserSession.clearPersistedSession()
}

export const useAuthStore = create<AuthState>((set) => {
  browserSession.removeLegacyAccessToken()
  browserSession.subscribe({
    onStoredUserChange: (user) => {
      const current = useAuthStore.getState()
      const userId = user?.id ?? null
      set({
        accessToken: null,
        user,
        sessionUserId: userId,
        sessionGeneration: current.sessionGeneration + (userId === null || userId !== current.sessionUserId ? 1 : 0),
      })
    },
    onMessage: (message) => applyChannelMessage(set, message),
  })

  return {
    accessToken: null,
    user: storedUser,
    sessionGeneration: 0,
    sessionUserId: storedUser?.id ?? null,
    setSession: (accessToken, user) => installSession(accessToken, user, true),
    setAccessToken: (accessToken) => {
      set({ accessToken })
      browserSession.removeLegacyAccessToken()
      publishAccessToken(accessToken)
    },
    clearSession: () => {
      set({ accessToken: null, user: null, sessionUserId: null, sessionGeneration: useAuthStore.getState().sessionGeneration + 1 })
      browserSession.clearPersistedSession()
      browserSession.publish({ type: 'clear-session' })
    },
  }
})

function publishAccessToken(accessToken: string) {
  const userId = useAuthStore.getState().sessionUserId
  browserSession.publish({ type: 'access-token', accessToken, ...(userId === null ? {} : { userId }) })
}

export function beginAuthConfirmation(accessToken: string, sessionGeneration = useAuthStore.getState().sessionGeneration) {
  assertAuthSession(sessionGeneration)
  useAuthStore.setState({ accessToken, user: null })
  browserSession.removeLegacyAccessToken()
  publishAccessToken(accessToken)
}

export function confirmAuthSession(accessToken: string, user: User, sessionGeneration = useAuthStore.getState().sessionGeneration) {
  assertAuthSession(sessionGeneration)
  installSession(accessToken, user, false)
}

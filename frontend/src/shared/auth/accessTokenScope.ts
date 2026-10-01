import { AuthSessionChangedError } from './useAuth'

/**
 * A late Set-Cookie can replace the refresh cookie after an account handoff.
 * SimpleJWT's user_id claim lets us reject that account's refreshed token
 * before replaying a write. This is a scope check, never token authorization.
 */
export function assertAccessTokenScope(accessToken: string, userId: number | null) {
  if (userId === null) return // Cold bootstrap confirms identity through /auth/me.
  let tokenUserId: unknown
  try {
    const encoded = accessToken.split('.')[1]
    const payload: unknown = JSON.parse(atob(encoded.replace(/-/g, '+').replace(/_/g, '/')))
    if (payload && typeof payload === 'object' && 'user_id' in payload) {
      tokenUserId = payload.user_id
    }
  } catch {
    throw new AuthSessionChangedError()
  }
  if (tokenUserId !== userId && tokenUserId !== String(userId)) {
    throw new AuthSessionChangedError()
  }
}

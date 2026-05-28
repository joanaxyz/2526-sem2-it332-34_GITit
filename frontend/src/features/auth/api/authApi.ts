import { apiRequest } from '@/shared/api/httpClient'
import type { AuthResponse, User } from '@/features/auth/types'

export type LoginPayload = {
  identifier: string
  password: string
}

export type RegisterPayload = {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirm: string
}

export type RegisterResponse = {
  user: User
}

type RefreshResponse = {
  access: string
}

export const authApi = {
  register(payload: RegisterPayload) {
    return apiRequest<RegisterResponse>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  async login(payload: LoginPayload) {
    // #region agent log
    fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '4ce873' },
      body: JSON.stringify({
        sessionId: '4ce873',
        location: 'authApi.ts:login',
        message: 'login request start',
        data: {
          identifierType: payload.identifier.includes('@') ? 'email' : 'student_id',
        },
        timestamp: Date.now(),
        hypothesisId: 'D',
      }),
    }).catch(() => {})
    // #endregion
    try {
      const result = await apiRequest<AuthResponse>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      // #region agent log
      fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '4ce873' },
        body: JSON.stringify({
          sessionId: '4ce873',
          location: 'authApi.ts:login',
          message: 'login request success',
          data: { hasAccess: Boolean(result.access), hasUser: Boolean(result.user) },
          timestamp: Date.now(),
          hypothesisId: 'D',
        }),
      }).catch(() => {})
      // #endregion
      return result
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '4ce873' },
        body: JSON.stringify({
          sessionId: '4ce873',
          location: 'authApi.ts:login',
          message: 'login request failed',
          data: {
            errorName: error instanceof Error ? error.name : 'unknown',
            status: (error as { status?: number }).status ?? null,
          },
          timestamp: Date.now(),
          hypothesisId: 'D',
        }),
      }).catch(() => {})
      // #endregion
      throw error
    }
  },
  logout() {
    return apiRequest<null>('/auth/logout/', { method: 'POST' })
  },
  refresh() {
    return apiRequest<RefreshResponse>('/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({}),
      skipAuthRefresh: true,
    })
  },
  me() {
    return apiRequest<User>('/auth/me/')
  },
}

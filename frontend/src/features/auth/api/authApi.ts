import { apiRequest } from '@/shared/api/httpClient'
import type { AuthResponse, User } from '@/features/auth/types'

export type LoginPayload = {
  identifier: string
  password: string
}

export type RegisterPayload = {
  student_id: string
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
  login(payload: LoginPayload) {
    return apiRequest<AuthResponse>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
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

import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { AuthResponse, User } from '@/shared/auth/types'

export type LoginPayload = ApiRequestBody<'auth_login_create'>
export type RegisterPayload = ApiRequestBody<'auth_register_create'>
export type RegisterResponse = Omit<ApiSchemas['AuthUserResponse'], 'user'> & { user: User }
export type RefreshResponse = ApiSchemas['AccessTokenResponse']

export type PasswordResetRequestPayload = ApiRequestBody<'auth_password_reset_request_create'>
export type PasswordResetConfirmPayload = ApiRequestBody<'auth_password_reset_confirm_create'>
export type PasswordChangePayload = ApiRequestBody<'auth_password_change_create'>
export type DetailResponse = ApiSchemas['DetailResponse']

export const authApi = {
  register(payload: RegisterPayload) {
    return apiOperationRequest<'auth_register_create', RegisterResponse>('auth_register_create', '/auth/register/', {
      body: payload,
    })
  },
  async login(payload: LoginPayload) {
    return apiOperationRequest<'auth_login_create', AuthResponse>('auth_login_create', '/auth/login/', {
      body: payload,
    })
  },
  logout() {
    return apiOperationRequest<'auth_logout_create', null>('auth_logout_create', '/auth/logout/', {
      skipAuthRefresh: true,
    })
  },
  refresh() {
    return apiOperationRequest<'auth_refresh_create', RefreshResponse>('auth_refresh_create', '/auth/refresh/', {
      skipAuthRefresh: true,
    })
  },
  me() {
    return apiOperationRequest<'auth_me_retrieve', User>('auth_me_retrieve', '/auth/me/')
  },
  requestPasswordReset(payload: PasswordResetRequestPayload) {
    return apiOperationRequest<'auth_password_reset_request_create', DetailResponse>(
      'auth_password_reset_request_create',
      '/auth/password-reset/request/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  confirmPasswordReset(payload: PasswordResetConfirmPayload) {
    return apiOperationRequest<'auth_password_reset_confirm_create', DetailResponse>(
      'auth_password_reset_confirm_create',
      '/auth/password-reset/confirm/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  changePassword(payload: PasswordChangePayload) {
    return apiOperationRequest<'auth_password_change_create', AuthResponse>(
      'auth_password_change_create',
      '/auth/password-change/',
      { body: payload },
    )
  },
  revokeOtherSessions() {
    return apiOperationRequest<'auth_sessions_revoke_others_create', DetailResponse>(
      'auth_sessions_revoke_others_create',
      '/auth/sessions/revoke-others/',
    )
  },
  revokeAllSessions() {
    return apiOperationRequest<'auth_sessions_revoke_all_create', null>(
      'auth_sessions_revoke_all_create',
      '/auth/sessions/revoke-all/',
    )
  },
}

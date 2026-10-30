import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest, apiUrl } from '@/shared/api/httpClient'

export type LoginPayload = ApiRequestBody<'auth_login_create'>
export type RegisterPayload = ApiRequestBody<'auth_register_create'>

export type PasswordResetRequestPayload = ApiRequestBody<'auth_password_reset_request_create'>
export type PasswordResetConfirmPayload = ApiRequestBody<'auth_password_reset_confirm_create'>
export type PasswordChangePayload = ApiRequestBody<'auth_password_change_create'>
export type EmailVerificationConfirmPayload = ApiRequestBody<'auth_email_verification_confirm_create'>
export type EmailVerificationResendPayload = ApiRequestBody<'auth_email_verification_resend_create'>
export type OAuthTicketExchangePayload = ApiRequestBody<'auth_oauth_exchange_create'>
export type OAuthProvider = 'github' | 'google'

// Register and login run without a session, so their 401 is the API's answer
// (wrong credentials), never an expired access token to refresh.
export const authApi = {
  register(payload: RegisterPayload) {
    return apiOperationRequest('auth_register_create', '/auth/register/', {
      body: payload,
      skipAuthRefresh: true,
    })
  },
  async login(payload: LoginPayload) {
    return apiOperationRequest('auth_login_create', '/auth/login/', {
      body: payload,
      skipAuthRefresh: true,
    })
  },
  logout() {
    return apiOperationRequest('auth_logout_create', '/auth/logout/', {
      skipAuthRefresh: true,
    })
  },
  refresh() {
    return apiOperationRequest('auth_refresh_create', '/auth/refresh/', {
      skipAuthRefresh: true,
    })
  },
  me() {
    return apiOperationRequest('auth_me_retrieve', '/auth/me/')
  },
  requestPasswordReset(payload: PasswordResetRequestPayload) {
    return apiOperationRequest(
      'auth_password_reset_request_create',
      '/auth/password-reset/request/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  confirmPasswordReset(payload: PasswordResetConfirmPayload) {
    return apiOperationRequest(
      'auth_password_reset_confirm_create',
      '/auth/password-reset/confirm/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  confirmEmailVerification(payload: EmailVerificationConfirmPayload) {
    return apiOperationRequest(
      'auth_email_verification_confirm_create',
      '/auth/email-verification/confirm/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  resendEmailVerification(payload: EmailVerificationResendPayload) {
    return apiOperationRequest(
      'auth_email_verification_resend_create',
      '/auth/email-verification/resend/',
      { body: payload, skipAuthRefresh: true },
    )
  },
  /** Where the browser navigates to begin GitHub or Google sign-in. */
  oauthStartUrl(provider: OAuthProvider) {
    return apiUrl(`/auth/oauth/${provider}/start/`)
  },
  exchangeOAuthTicket(payload: OAuthTicketExchangePayload) {
    return apiOperationRequest('auth_oauth_exchange_create', '/auth/oauth/exchange/', {
      body: payload,
      skipAuthRefresh: true,
    })
  },
  changePassword(payload: PasswordChangePayload) {
    return apiOperationRequest('auth_password_change_create', '/auth/password-change/', { body: payload })
  },
  revokeOtherSessions() {
    return apiOperationRequest(
      'auth_sessions_revoke_others_create',
      '/auth/sessions/revoke-others/',
    )
  },
  revokeAllSessions() {
    return apiOperationRequest('auth_sessions_revoke_all_create', '/auth/sessions/revoke-all/')
  },
}

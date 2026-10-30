import { ApiError } from '@/shared/api/apiError'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type EmailVerificationRequired = ApiSchemas['EmailVerificationRequired']

export const VERIFICATION_CODE_LENGTH = 6
/** Matches the backend resend cooldown; a code was always just sent on arrival. */
export const RESEND_COOLDOWN_SECONDS = 60

export function verifyEmailPath(email: string) {
  return `/verify-email?email=${encodeURIComponent(email)}`
}

/** The account email from a sign-in refused only because the sign-up code was never entered. */
export function unverifiedEmailFrom(error: unknown): string | null {
  if (!(error instanceof ApiError) || error.status !== 403) return null
  const payload = error.payload as Partial<EmailVerificationRequired> | null
  if (payload?.code !== 'email_unverified' || typeof payload.email !== 'string') return null
  return payload.email
}

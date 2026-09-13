import { ApiError, type ApiFieldErrors } from '@/shared/api/apiError'

type AuthErrorPresentation = {
  message: string
  retryable: boolean
  retryAfterSeconds?: number
  /** Per-field messages a form can pin to the input that caused them. */
  fieldErrors: ApiFieldErrors
}

const GENERIC_MESSAGE = 'Something went wrong. Try again.'

export function presentAuthError(error: unknown): AuthErrorPresentation {
  if (error instanceof ApiError) {
    const detail = String(error.message || '').toLowerCase()

    if (error.status === 409 && detail.includes('username')) {
      return { message: 'This username is already in use.', retryable: false, fieldErrors: { username: ['This username is already in use.'] } }
    }

    if (error.status === 409 && detail.includes('email')) {
      return { message: 'This email is already in use.', retryable: false, fieldErrors: { email: ['This email is already in use.'] } }
    }

    if (error.status === 401) {
      return { message: 'Incorrect username/email or password', retryable: false, fieldErrors: {} }
    }

    if (error.status === 429) {
      const payload =
        typeof error.payload === 'object' && error.payload !== null ? (error.payload as Record<string, unknown>) : {}
      const retryAfterRaw = payload.retry_after
      const retryAfterSeconds =
        typeof retryAfterRaw === 'number' && Number.isFinite(retryAfterRaw) ? Math.max(0, Math.floor(retryAfterRaw)) : 0
      return {
        message: 'Too many failed attempts. Please wait before trying again.',
        retryable: false,
        retryAfterSeconds,
        fieldErrors: {},
      }
    }

    if (error.status >= 500) {
      return { message: GENERIC_MESSAGE, retryable: true, fieldErrors: {} }
    }

    // A 400 from the password validators says exactly what is wrong with the
    // password; show that text rather than flattening it to a generic failure.
    return { message: error.message || GENERIC_MESSAGE, retryable: false, fieldErrors: error.fieldErrors }
  }

  if (error instanceof TypeError) {
    return { message: GENERIC_MESSAGE, retryable: true, fieldErrors: {} }
  }

  return { message: GENERIC_MESSAGE, retryable: false, fieldErrors: {} }
}

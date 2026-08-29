import { ApiError } from '@/shared/api/apiError'

function firstMessage(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) return value
  if (Array.isArray(value)) {
    for (const item of value) {
      const message = firstMessage(item)
      if (message) return message
    }
  }
  if (value && typeof value === 'object') {
    for (const item of Object.values(value)) {
      const message = firstMessage(item)
      if (message) return message
    }
  }
  return null
}

export function adminErrorMessage(
  error: unknown,
  fallback = 'The change could not be saved.',
) {
  if (error instanceof ApiError) {
    return firstMessage(error.payload) ?? error.message ?? fallback
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}

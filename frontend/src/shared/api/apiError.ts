export type ApiFieldErrors = Record<string, string[]>

export class ApiError extends Error {
  status: number
  payload: unknown
  /**
   * DRF field errors (`{"password": ["This password is too common."]}`) keyed by
   * field name, so a form can attach the message to the input that caused it.
   */
  fieldErrors: ApiFieldErrors

  constructor(message: string, status: number, payload: unknown, fieldErrors: ApiFieldErrors = {}) {
    super(message)
    this.status = status
    this.payload = payload
    this.fieldErrors = fieldErrors
  }
}

const DETAIL_KEYS = ['detail', 'non_field_errors']

function collectMessages(value: unknown): string[] {
  if (typeof value === 'string') {
    const trimmed = value.trim()
    return trimmed ? [trimmed] : []
  }
  if (Array.isArray(value)) return value.flatMap(collectMessages)
  if (value && typeof value === 'object') return Object.values(value).flatMap(collectMessages)
  return []
}

function asRecord(payload: unknown): Record<string, unknown> | null {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return null
  return payload as Record<string, unknown>
}

/**
 * Field-keyed messages from a DRF validation response, minus the non-field keys
 * that belong to the whole request rather than one input.
 */
export function readApiFieldErrors(payload: unknown): ApiFieldErrors {
  const record = asRecord(payload)
  if (!record) return {}

  const fieldErrors: ApiFieldErrors = {}
  for (const [field, value] of Object.entries(record)) {
    if (DETAIL_KEYS.includes(field)) continue
    const messages = collectMessages(value)
    if (messages.length > 0) fieldErrors[field] = messages
  }
  return fieldErrors
}

function humanizeField(field: string): string {
  const words = field.replace(/_/g, ' ').trim()
  return words.charAt(0).toUpperCase() + words.slice(1)
}

/**
 * Turns an error response body into something a user can act on.
 *
 * Django's password validators answer with field errors and no `detail`, so
 * reading only `detail` reduced "This password is too common." to the bare
 * "Bad Request" status text.
 */
export function describeApiError(payload: unknown, fallback: string): string {
  const record = asRecord(payload)
  if (!record) return fallback

  const detail = DETAIL_KEYS.flatMap((key) => collectMessages(record[key]))
  if (detail.length > 0) return detail.join(' ')

  const fieldErrors = readApiFieldErrors(payload)
  const fields = Object.keys(fieldErrors)
  if (fields.length === 0) return fallback
  // One field speaks for itself; several need to say which input they mean.
  if (fields.length === 1) return fieldErrors[fields[0]].join(' ')
  return fields.map((field) => `${humanizeField(field)}: ${fieldErrors[field].join(' ')}`).join(' ')
}

/** Field errors from a thrown request error, empty for anything else. */
export function apiFieldErrors(error: unknown): ApiFieldErrors {
  return error instanceof ApiError ? error.fieldErrors : {}
}

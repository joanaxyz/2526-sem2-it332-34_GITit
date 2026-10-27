import { ApiError } from '@/shared/api/apiError'
import type { TutorReply } from './tutorApi'

export type Recovery = {
  reason: 'offline' | 'rate_limited' | 'timeout' | 'unavailable' | 'guide' | 'validation' | 'session'
  message: string
  canRetry: boolean
  retrySeconds?: number
}

export function retrySeconds(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) && value > 0
    ? Math.min(86400, Math.ceil(value)) : 60
}

export function unavailableRecovery(reason: TutorReply['unavailable_reason'] = 'unavailable', timing?: number): Recovery {
  if (reason === 'rate_limited') return {
    reason, message: 'Git-It needs a short break. Your question is still here.', canRetry: true, retrySeconds: retrySeconds(timing),
  }
  if (reason === 'timeout') return {
    reason, message: 'This is taking longer than expected. Your question is still here.', canRetry: true,
  }
  return { reason: 'unavailable', message: 'I couldn’t get an AI response just now. You can try again or browse FAQS.', canRetry: true }
}

export const OFFLINE_RECOVERY: Recovery = {
  reason: 'offline', message: 'You’re offline. You can keep reading FAQS and send your question when you reconnect.', canRetry: true,
}

export function errorRecovery(error: unknown, workspace: boolean): Recovery {
  if (!(error instanceof ApiError)) return unavailableRecovery()
  const payload = error.payload && typeof error.payload === 'object' ? error.payload as Record<string, unknown> : {}
  if (error.status === 429) return unavailableRecovery('rate_limited', retrySeconds(payload.retry_after_seconds))
  if (error.status >= 500) return unavailableRecovery()
  if (error.status === 401) return {
    reason: 'session', message: 'Your sign-in has expired. Please sign in again to continue.', canRetry: false,
  }
  if (workspace && (error.status === 404 || error.status === 403 || 'context' in payload)) return {
    reason: 'guide', message: 'This command guide is no longer available. Reopen it from the workspace, then try your question again.', canRetry: false,
  }
  if (error.status === 403) return { reason: 'session', message: 'Chat isn’t available for this account.', canRetry: false }
  const message = error.status === 413 || 'message' in payload
    ? 'Please keep your question between 1 and 4,000 characters.'
    : 'history' in payload ? 'This conversation is too long. Start a new chat, then send your question again.'
      : 'I couldn’t send that question. Check your message and try again.'
  return { reason: 'validation', message, canRetry: false }
}

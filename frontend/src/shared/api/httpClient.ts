import { toast } from 'sonner'

import { ApiError, describeApiError, readApiFieldErrors } from './apiError'
import { apiOperations } from './generated/apiTypes'
import type { ApiOperationId, ApiRequestBody, ApiResponseBody } from './generated/apiTypes'
import { assertAuthSession, AuthSessionChangedError, useAuthStore } from '@/shared/auth/useAuth'
import { assertAccessTokenScope } from '@/shared/auth/accessTokenScope'

const API_BASE_URL = resolveApiBaseUrl()

type RequestOptions = RequestInit & { skipAuthRefresh?: boolean }

let refreshFlight: { sessionGeneration: number; promise: Promise<string> } | null = null
const REFRESH_RETRY_DELAY_MS = 250

function resolveApiBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim()

  if (!configured) {
    if (import.meta.env.PROD) {
      throw new Error('VITE_API_BASE_URL must be set for production builds.')
    }

    return defaultApiBaseUrl()
  }

  // Allows same-domain deployments later, for example:
  // VITE_API_BASE_URL=/api
  if (configured.startsWith('/')) {
    return removeTrailingSlash(configured)
  }

  const apiUrl = new URL(configured)

  // Local dev safety: prevents localhost vs 127.0.0.1 cookie mismatch.
  if (!import.meta.env.PROD && typeof window !== 'undefined') {
    const appHost = window.location.hostname
    const localHosts = new Set(['localhost', '127.0.0.1', '::1'])

    if (
      localHosts.has(appHost) &&
      localHosts.has(apiUrl.hostname) &&
      appHost !== apiUrl.hostname
    ) {
      return defaultApiBaseUrl()
    }
  }

  return removeTrailingSlash(apiUrl.toString())
}

function removeTrailingSlash(value: string) {
  return value.endsWith('/') ? value.slice(0, -1) : value
}

function defaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000/api'
  }

  const host = window.location.hostname.includes(':')
    ? `[${window.location.hostname}]`
    : window.location.hostname

  return `${window.location.protocol}//${host}:8000/api`
}
async function parseResponse(response: Response) {
  if (response.status === 204) return null
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) return response.json()
  return response.text()
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  return requestForSession<T>(path, options, useAuthStore.getState().sessionGeneration)
}

async function requestForSession<T>(path: string, options: RequestOptions, sessionGeneration: number): Promise<T> {
  assertAuthSession(sessionGeneration)
  const token = useAuthStore.getState().accessToken
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-Git-It-Client': 'web',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    })
  } catch (error) {
    assertAuthSession(sessionGeneration)
    throw error
  }
  assertAuthSession(sessionGeneration)

  if (response.status === 401 && !options.skipAuthRefresh) {
    const latestToken = useAuthStore.getState().accessToken
    if (token && latestToken && token !== latestToken) {
      return requestForSession<T>(path, { ...options, skipAuthRefresh: true }, sessionGeneration)
    }

    const refreshed = await refreshAccessToken(token, sessionGeneration)
    assertAuthSession(sessionGeneration)
    if (refreshed) {
      return requestForSession<T>(path, { ...options, skipAuthRefresh: true }, sessionGeneration)
    }
  }

  let payload: unknown
  try {
    payload = await parseResponse(response)
  } catch (error) {
    assertAuthSession(sessionGeneration)
    throw error
  }
  // Reading the body is asynchronous too; a handoff can happen after headers.
  assertAuthSession(sessionGeneration)
  if (!response.ok) {
    // Field errors carry the only useful text on a DRF 400 (password rules,
    // for one), so they must reach the caller instead of "Bad Request".
    const message = describeApiError(payload, response.statusText || 'Request failed.')
    throw new ApiError(message, response.status, payload, readApiFieldErrors(payload))
  }
  return payload as T
}

/**
 * Single-flight refresh shared by every caller in the tab.
 *
 * The backend rotates refresh tokens single-use (an atomic row-locked claim on
 * the session record), so a second concurrent POST /auth/refresh/ always loses
 * and comes back 401. Route session bootstrap through this gate as well, or a
 * page load that bootstraps and 401s a request at the same time will kill its
 * own perfectly valid session.
 *
 * Rejects with the underlying ApiError so callers can tell "no session" (401)
 * apart from "refresh could not be reached" (network, 429, 5xx).
 */
export function refreshSharedAccessToken(): Promise<string> {
  const sessionGeneration = useAuthStore.getState().sessionGeneration
  if (!refreshFlight || refreshFlight.sessionGeneration !== sessionGeneration) {
    const pending = requestAccessTokenRefresh(0, sessionGeneration)
    refreshFlight = { sessionGeneration, promise: pending }
    // The catch keeps this bookkeeping chain from surfacing as an unhandled
    // rejection; real callers still await `pending` and see the error.
    pending
      .catch(() => undefined)
      .finally(() => {
        if (refreshFlight?.promise === pending) refreshFlight = null
      })
  }

  return refreshFlight.promise
}

async function refreshAccessToken(tokenAtStart: string | null, sessionGeneration: number): Promise<boolean> {
  try {
    assertAuthSession(sessionGeneration)
    await refreshSharedAccessToken()
    assertAuthSession(sessionGeneration)
    return true
  } catch (error) {
    assertAuthSession(sessionGeneration)
    if (error instanceof AuthSessionChangedError) throw error
    // Another tab may have broadcast a working token while ours was failing.
    const latestToken = useAuthStore.getState().accessToken
    if (latestToken && latestToken !== tokenAtStart) {
      return true
    }
    if (error instanceof ApiError && error.status === 401) {
      useAuthStore.getState().clearSession()
      toast.error('Your session has expired. Please log in again.')
    }
    return false
  }
}

function sleep(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms)
  })
}

async function requestAccessTokenRefresh(attempt: number, sessionGeneration: number): Promise<string> {
  try {
    assertAuthSession(sessionGeneration)
    const payload = await apiRequest<ApiResponseBody<'auth_refresh_create'>>('/auth/refresh/', {
      method: 'POST',
      skipAuthRefresh: true,
    })
    assertAuthSession(sessionGeneration)
    assertAccessTokenScope(payload.access, useAuthStore.getState().sessionUserId)
    useAuthStore.getState().setAccessToken(payload.access)
    return payload.access
  } catch (error) {
    assertAuthSession(sessionGeneration)
    // Refresh token rotation can cause a 401 if another tab refreshed at the same
    // time. Give the browser a moment to apply the rotated refresh cookie, then
    // retry once before giving up.
    if (error instanceof ApiError && error.status === 401 && attempt < 1) {
      await sleep(REFRESH_RETRY_DELAY_MS)
      return requestAccessTokenRefresh(attempt + 1, sessionGeneration)
    }
    throw error
  }
}


type OperationRequestOptions<TOperation extends ApiOperationId> = Omit<RequestOptions, 'body' | 'method'> & {
  body?: ApiRequestBody<TOperation>
  method?: never
}

/**
 * Contract-aware request helper. Runtime URLs can still contain concrete IDs,
 * but request/response types and HTTP method are anchored to the generated
 * OpenAPI operation id so API drift is caught by TypeScript instead of memory.
 */
export async function apiOperationRequest<
  TOperation extends ApiOperationId,
  TResponse = ApiResponseBody<TOperation>,
>(operationId: TOperation, path: string, options: OperationRequestOptions<TOperation> = {}): Promise<TResponse> {
  const operation = apiOperations[operationId]
  const { body, ...rest } = options
  return apiRequest<TResponse>(path, {
    ...rest,
    method: operation.method,
    body: body == null ? undefined : JSON.stringify(body),
  })
}

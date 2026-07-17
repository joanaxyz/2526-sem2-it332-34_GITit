import { ApiError } from './apiError'
import { apiOperations } from './generated/apiTypes'
import type { ApiOperationId, ApiRequestBody, ApiResponseBody } from './generated/apiTypes'
import { useAuthStore } from '@/shared/auth/useAuth'

const API_BASE_URL = resolveApiBaseUrl()

type RequestOptions = RequestInit & { skipAuthRefresh?: boolean }

let refreshPromise: Promise<boolean> | null = null
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
  const token = useAuthStore.getState().accessToken
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-Git-It-Client': 'web',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401 && !options.skipAuthRefresh) {
    const latestToken = useAuthStore.getState().accessToken
    if (token && latestToken && token !== latestToken) {
      return apiRequest<T>(path, { ...options, skipAuthRefresh: true })
    }

    const refreshed = await refreshAccessToken(token)
    if (refreshed) {
      return apiRequest<T>(path, { ...options, skipAuthRefresh: true })
    }
  }

  const payload = await parseResponse(response)
  if (!response.ok) {
    const detail = typeof payload === 'object' && payload && 'detail' in payload ? String(payload.detail) : response.statusText
    throw new ApiError(detail, response.status, payload)
  }
  return payload as T
}

async function refreshAccessToken(tokenAtStart: string | null) {
  if (refreshPromise) return refreshPromise

  refreshPromise = requestAccessTokenRefresh(0, tokenAtStart)
  refreshPromise.finally(() => {
    refreshPromise = null
  })

  return refreshPromise
}

function sleep(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms)
  })
}

async function requestAccessTokenRefresh(attempt = 0, tokenAtStart: string | null): Promise<boolean> {
  try {
    const payload = await apiRequest<{ access: string }>('/auth/refresh/', {
      method: 'POST',
      skipAuthRefresh: true,
    })
    useAuthStore.getState().setAccessToken(payload.access)
    return true
  } catch (error) {
    // Refresh token rotation can cause a 401 if another tab refreshed at the same
    // time. Give the browser a moment to apply the rotated refresh cookie, then
    // retry once before forcing a logout.
    if (error instanceof ApiError && error.status === 401 && attempt < 1) {
      await sleep(REFRESH_RETRY_DELAY_MS)
      return requestAccessTokenRefresh(attempt + 1, tokenAtStart)
    }
    const latestToken = useAuthStore.getState().accessToken
    if (latestToken && latestToken !== tokenAtStart) {
      return true
    }
    if (error instanceof ApiError && error.status === 401) {
      useAuthStore.getState().clearSession()
    }
    return false
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

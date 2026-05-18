import { ApiError } from './apiError'
import { useAuthStore } from '@/features/auth/hooks/useAuth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? defaultApiBaseUrl()

type RequestOptions = RequestInit & { skipAuthRefresh?: boolean }

let refreshPromise: Promise<boolean> | null = null

function defaultApiBaseUrl() {
  if (typeof window === 'undefined') return 'http://127.0.0.1:8000/api'

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
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401 && !options.skipAuthRefresh) {
    const latestToken = useAuthStore.getState().accessToken
    if (token && latestToken && token !== latestToken) {
      return apiRequest<T>(path, { ...options, skipAuthRefresh: true })
    }

    const refreshed = await refreshAccessToken()
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

async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise

  refreshPromise = requestAccessTokenRefresh()
  refreshPromise.finally(() => {
    refreshPromise = null
  })

  return refreshPromise
}

async function requestAccessTokenRefresh() {
  try {
    const payload = await apiRequest<{ access: string }>('/auth/refresh/', {
      method: 'POST',
      skipAuthRefresh: true,
    })
    useAuthStore.getState().setAccessToken(payload.access)
    return true
  } catch {
    useAuthStore.getState().clearSession()
    return false
  }
}

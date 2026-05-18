import { ApiError } from './apiError'
import { useAuthStore } from '@/features/auth/hooks/useAuth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

type RequestOptions = RequestInit & { skipAuthRefresh?: boolean }

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

import { API_BASE_URL, apiRequest } from '@/shared/api/httpClient'
import { ApiError } from '@/shared/api/apiError'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import type { AssetDescriptor, AssetDescriptorResponse, AssetKind } from '@/shared/assets/types'

export const assetsApi = {
  getDescriptors(kind: AssetKind) {
    return apiRequest<AssetDescriptorResponse>(`/assets/descriptors/?kind=${encodeURIComponent(kind)}`)
  },
  /** Official assets merged with the requester's own (private) assets of `kind`. */
  getOwnedDescriptors(kind: AssetKind) {
    return apiRequest<AssetDescriptorResponse>(
      `/assets/descriptors/?kind=${encodeURIComponent(kind)}&mine=1`,
    )
  },
  /** Upload an owned tower piece / artifact. FormData fields: file, kind, label, piece_type?, tags?. */
  upload(form: FormData): Promise<AssetDescriptor> {
    return postFormData('/assets/', form)
  },
  /**
   * Upload an owned monster. FormData fields: label, tier, attack (JSON),
   * metrics (JSON), tags?, and per-action sprite_<action> files with fps_<action>.
   */
  uploadMonster(form: FormData): Promise<AssetDescriptor> {
    return postFormData('/assets/monsters/', form)
  },
}

async function postFormData(path: string, form: FormData): Promise<AssetDescriptor> {
  const token = useAuthStore.getState().accessToken
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  })
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload
        ? String((payload as { detail: unknown }).detail)
        : 'Upload failed.'
    throw new ApiError(detail, response.status, payload)
  }
  return payload as AssetDescriptor
}

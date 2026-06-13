import { apiRequest } from '@/shared/api/httpClient'
import type { AssetDescriptorResponse, AssetKind } from '@/shared/assets/types'

export const assetsApi = {
  getDescriptors(kind: AssetKind) {
    return apiRequest<AssetDescriptorResponse>(`/assets/descriptors/?kind=${encodeURIComponent(kind)}`)
  },
}


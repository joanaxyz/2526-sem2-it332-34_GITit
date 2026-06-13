import { apiRequest } from '@/shared/api/httpClient'
import type { ContentDefinition } from '@/features/authoring/types'
import type { TowerDesign } from '@/features/towers/types'
import type { AssetKind } from '@/shared/assets/types'

export type GalleryAsset = {
  id: number
  kind: AssetKind
  slug: string
  label: string
  visibility: string
  price: number
}

export const galleryApi = {
  assets() {
    return apiRequest<{ results: GalleryAsset[] }>('/gallery/assets/')
  },
  content() {
    return apiRequest<{ results: ContentDefinition[] }>('/gallery/content/')
  },
  towerDesigns() {
    return apiRequest<{ results: TowerDesign[] }>('/gallery/tower-designs/')
  },
}

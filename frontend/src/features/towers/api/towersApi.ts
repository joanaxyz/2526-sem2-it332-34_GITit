import { apiRequest } from '@/shared/api/httpClient'
import type { TowerDesign, TowerDesignList, TowerDesignOverview } from '@/features/towers/types'

export const towersApi = {
  mine() {
    return apiRequest<TowerDesignList>('/tower-designs/mine/')
  },
  create(input: { slug: string; title: string; summary?: string }) {
    return apiRequest<TowerDesign>('/tower-designs/', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  setActive(id: number) {
    return apiRequest<TowerDesign>(`/tower-designs/${id}/set-active/`, { method: 'POST' })
  },
  overview() {
    return apiRequest<TowerDesignOverview>('/my-tower/overview/')
  },
  layout(id: number) {
    return apiRequest<TowerDesignOverview>(`/tower-designs/${id}/layout/`)
  },
}

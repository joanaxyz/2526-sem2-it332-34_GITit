import { apiRequest } from '@/shared/api/httpClient'
import type { StoreyContentOverview } from '@/features/challenges/types'
import type { StoreyBook } from '@/features/tower-map/book/bookTypes'
import type { LearningStorey } from '@/features/tower-map/types'

export const towerMapApi = {
  listStoreys() {
    return apiRequest<LearningStorey[]>('/storeys/')
  },
  getStoreyOverview(storeyId: number) {
    return apiRequest<StoreyContentOverview>(`/storeys/${storeyId}/overview/`)
  },
  getStoreyBook(storeyId: number) {
    return apiRequest<StoreyBook>(`/storeys/${storeyId}/book/`)
  },
}

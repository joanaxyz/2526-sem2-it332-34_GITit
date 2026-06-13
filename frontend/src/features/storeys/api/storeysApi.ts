import { apiRequest } from '@/shared/api/httpClient'
import type { StoreyContentOverview } from '@/features/challenges/types'
import type { StoreyBook } from '@/features/storeys/book/bookTypes'
import type { LearningStorey } from '@/features/storeys/types'

export const storeysApi = {
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

import { apiRequest } from '@/shared/api/httpClient'
import type { StoreyBook } from '@/features/storeys/book/bookTypes'
import type { LearningStorey } from '@/features/storeys/types'

export const storeysApi = {
  listStoreys() {
    return apiRequest<LearningStorey[]>('/storeys/')
  },
  getStoreyBook(storeyId: number) {
    return apiRequest<StoreyBook>(`/storeys/${storeyId}/book/`)
  },
}

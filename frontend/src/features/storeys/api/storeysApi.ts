import { apiRequest } from '@/shared/api/httpClient'
import type { FoundationTopic, LearningStorey } from '@/features/storeys/types'

export const storeysApi = {
  listFoundations() {
    return apiRequest<FoundationTopic[]>('/concept-pages/')
  },
  listStoreys() {
    return apiRequest<LearningStorey[]>('/storeys/')
  },
}

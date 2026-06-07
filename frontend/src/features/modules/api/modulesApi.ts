import { apiRequest } from '@/shared/api/httpClient'
import type { FoundationTopic, LearningStorey } from '@/features/modules/types'

export const storeysApi = {
  listFoundations() {
    return apiRequest<FoundationTopic[]>('/learning/foundations/')
  },
  listStoreys() {
    return apiRequest<LearningStorey[]>('/learning/storeys/')
  },
  listModules() {
    return apiRequest<LearningStorey[]>('/learning/storeys/')
  },
}

export const modulesApi = storeysApi

import { apiRequest } from '@/shared/api/httpClient'
import type { FoundationTopic, LearningTower } from '@/features/modules/types'

export const towersApi = {
  listFoundations() {
    return apiRequest<FoundationTopic[]>('/learning/foundations/')
  },
  listTowers() {
    return apiRequest<LearningTower[]>('/learning/towers/')
  },
  listModules() {
    return apiRequest<LearningTower[]>('/learning/towers/')
  },
}

export const modulesApi = towersApi

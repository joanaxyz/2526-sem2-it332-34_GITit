import { apiRequest } from '@/shared/api/httpClient'
import type { FoundationTopic, LearningModule } from '@/features/modules/types'

export const modulesApi = {
  listFoundations() {
    return apiRequest<FoundationTopic[]>('/learning/foundations/')
  },
  listModules() {
    return apiRequest<LearningModule[]>('/learning/modules/')
  },
}

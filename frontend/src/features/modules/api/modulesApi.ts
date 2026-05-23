import { apiRequest } from '@/shared/api/httpClient'
import type { LearningModule, LessonDetail, OrientationStatus } from '@/features/modules/types'

export const modulesApi = {
  listModules() {
    return apiRequest<LearningModule[]>('/learning/modules/')
  },
  getLesson(lessonId: number) {
    return apiRequest<LessonDetail>(`/learning/lessons/${lessonId}/`)
  },
  orientationStatus() {
    return apiRequest<OrientationStatus>('/learning/orientation/status/')
  },
  completeOrientationLesson(lessonId: number, highestStepSeen: number) {
    return apiRequest(`/learning/orientation/${lessonId}/complete/`, {
      method: 'POST',
      body: JSON.stringify({ highest_step_seen: highestStepSeen }),
    })
  },
}

import { apiRequest } from '@/shared/api/httpClient'
import type { LearningUnit, LessonDetail, OrientationStatus } from '@/features/units/types'

export const unitsApi = {
  listUnits() {
    return apiRequest<LearningUnit[]>('/learning/units/')
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

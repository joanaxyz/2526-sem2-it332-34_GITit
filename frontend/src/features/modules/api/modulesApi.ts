import { apiRequest } from '@/shared/api/httpClient'
import type { LearningModule, LessonDetail, OrientationStatus } from '@/features/modules/types'
import type { OrientationCommandResult, OrientationLessonSession } from '@/features/modules/orientation/types'

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
  startOrientationSession(lessonId: number) {
    return apiRequest<OrientationLessonSession>(`/learning/orientation/${lessonId}/sessions/`, {
      method: 'POST',
    })
  },
  getOrientationSession(sessionId: number) {
    return apiRequest<OrientationLessonSession>(`/learning/orientation/sessions/${sessionId}/`)
  },
  submitOrientationCommand(sessionId: number, command: string, stepId: string) {
    return apiRequest<OrientationCommandResult>(`/learning/orientation/sessions/${sessionId}/commands/`, {
      method: 'POST',
      body: JSON.stringify({ command, step_id: stepId }),
    })
  },
  resetOrientationSession(sessionId: number, stepId: string) {
    return apiRequest<OrientationLessonSession>(`/learning/orientation/sessions/${sessionId}/reset/`, {
      method: 'POST',
      body: JSON.stringify({ step_id: stepId }),
    })
  },
}

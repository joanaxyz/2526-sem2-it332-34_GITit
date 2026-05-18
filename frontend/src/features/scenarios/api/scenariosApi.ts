import { apiRequest } from '@/shared/api/httpClient'
import type { ScenarioSession } from '@/features/practice/types'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'

export const scenariosApi = {
  listForLesson(lessonId: number) {
    return apiRequest<ScenarioSkillFocus[]>(`/scenarios/lessons/${lessonId}/`)
  },
  listForUnit(unitId: number) {
    return apiRequest<ScenarioSkillFocus[]>(`/scenarios/units/${unitId}/`)
  },
  startSession(payload: { difficulty_instance_id: number; source_entry_point: 'lesson' | 'unit_card' }) {
    return apiRequest<ScenarioSession>('/scenarios/sessions/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  retrySession(sessionId: number) {
    return apiRequest<ScenarioSession>(`/scenarios/sessions/${sessionId}/retry/`, { method: 'POST' })
  },
  abandonSession(sessionId: number) {
    return apiRequest<ScenarioSession>(`/scenarios/sessions/${sessionId}/abandon/`, { method: 'POST' })
  },
}

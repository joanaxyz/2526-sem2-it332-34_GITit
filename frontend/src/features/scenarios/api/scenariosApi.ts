import { apiRequest } from '@/shared/api/httpClient'
import type { ScenarioSession } from '@/features/practice/types'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'

type DemoCommandResponse = {
  repository_state: unknown
  terminal_output: string
  was_processable: boolean
}

export const scenariosApi = {
  listForModule(moduleId: number) {
    return apiRequest<ScenarioSkillFocus[]>(`/scenarios/modules/${moduleId}/`)
  },
  listForModules(moduleIds: number[]) {
    const params = new URLSearchParams({ module_ids: moduleIds.join(',') })
    return apiRequest<Record<string, ScenarioSkillFocus[]>>(`/scenarios/modules/summary/?${params.toString()}`)
  },
  getSkillFocus(skillFocusSlug: string, options?: { commandIndex?: number }) {
    const params = new URLSearchParams()
    if (options?.commandIndex !== undefined) {
      params.set('command_index', String(options.commandIndex))
    }
    const query = params.toString()
    return apiRequest<ScenarioSkillFocus>(`/scenarios/skill-focus/${skillFocusSlug}/${query ? `?${query}` : ''}`)
  },
  submitDemoCommand(skillFocusSlug: string, payload: { command: string; repository_state?: unknown }) {
    return apiRequest<DemoCommandResponse>(`/scenarios/skill-focus/${skillFocusSlug}/demo/commands/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  startSession(payload: { difficulty_instance_id: number; source_entry_point: 'module_card' | 'retry' | 'review'; prior_session_id?: number | null }) {
    return apiRequest<ScenarioSession>('/scenarios/sessions/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  retrySession(sessionId: number) {
    return apiRequest<ScenarioSession>(`/scenarios/sessions/${sessionId}/retry/`, {
      method: 'POST',
      body: JSON.stringify({ source_entry_point: 'retry' }),
    })
  },
  abandonSession(sessionId: number) {
    return apiRequest<ScenarioSession>(`/scenarios/sessions/${sessionId}/abandon/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
}

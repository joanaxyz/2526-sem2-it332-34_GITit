import { apiRequest } from '@/shared/api/httpClient'
import type {
  CommandDrillAdventureSummary,
  CommandTopicSummary,
  CommandUsagePreview,
  TowerContentPage,
  TowerContentSection,
  PracticeKind,
  WorkflowScenarioSummary,
} from '@/features/scenarios/types'
import type { PracticeSession } from '@/features/practice/types'

export type PracticeStartPayload =
  | {
      problem_type: 'command_drill'
      command_drill_id: number
      source_entry_point: 'tower_page' | 'module_page' | 'retry' | 'review'
      prior_session_id?: number | null
    }
  | {
      problem_type: 'workflow_scenario'
      workflow_level_id: number
      source_entry_point: 'tower_page' | 'module_page' | 'retry' | 'review'
      prior_session_id?: number | null
    }

type TowerContentResult<TSection extends TowerContentSection> =
  TSection extends 'command_adventures'
    ? TowerContentPage<CommandDrillAdventureSummary>
    : TSection extends 'command_topics'
    ? TowerContentPage<CommandTopicSummary>
    : TowerContentPage<WorkflowScenarioSummary>

export function startPayloadForPractice(
  practiceKind: PracticeKind,
  id: number,
  sourceEntryPoint: 'tower_page' | 'module_page' | 'retry' | 'review' = 'tower_page',
  priorSessionId?: number | null,
): PracticeStartPayload {
  if (practiceKind === 'command_drill') {
    return {
      problem_type: 'command_drill',
      command_drill_id: id,
      source_entry_point: sourceEntryPoint,
      prior_session_id: priorSessionId ?? null,
    }
  }
  return {
    problem_type: 'workflow_scenario',
    workflow_level_id: id,
    source_entry_point: sourceEntryPoint,
    prior_session_id: priorSessionId ?? null,
  }
}

export const scenariosApi = {
  towerContent<TSection extends TowerContentSection>(
    towerId: number,
    section: TSection,
    options?: { cursor?: number | null; limit?: number },
  ) {
    const params = new URLSearchParams({ section })
    if (options?.cursor) params.set('cursor', String(options.cursor))
    if (options?.limit) params.set('limit', String(options.limit))
    return apiRequest<TowerContentResult<TSection>>(
      `/scenarios/towers/${towerId}/content/?${params.toString()}`,
    )
  },
  moduleContent<TSection extends TowerContentSection>(
    moduleId: number,
    section: TSection,
    options?: { cursor?: number | null; limit?: number },
  ) {
    const params = new URLSearchParams({ section })
    if (options?.cursor) params.set('cursor', String(options.cursor))
    if (options?.limit) params.set('limit', String(options.limit))
    return apiRequest<TowerContentResult<TSection>>(
      `/scenarios/towers/${moduleId}/content/?${params.toString()}`,
    )
  },
  commandUsagePreview(usageId: number) {
    return apiRequest<CommandUsagePreview>(`/scenarios/command-usages/${usageId}/preview/`)
  },
  startSession(payload: PracticeStartPayload) {
    return apiRequest<PracticeSession>('/scenarios/sessions/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  retrySession(sessionId: number) {
    return apiRequest<PracticeSession>(`/scenarios/sessions/${sessionId}/retry/`, {
      method: 'POST',
      body: JSON.stringify({ source_entry_point: 'retry' }),
    })
  },
  abandonSession(sessionId: number) {
    return apiRequest<PracticeSession>(`/scenarios/sessions/${sessionId}/abandon/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
}

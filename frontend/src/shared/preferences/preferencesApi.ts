import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import { onboardingPhases, type PlayerAccountPreferences } from '@/shared/preferences/preferences'

type PreferencesResponse = ApiSchemas['PlayerPreferences']
type PreferencesUpdate = ApiRequestBody<'player_preferences_partial_update'>

function normalizePreferences(data: PreferencesResponse): PlayerAccountPreferences {
  const phase = data.onboarding_phase
  return {
    motion_mode: data.motion_mode ?? 'system',
    onboarding_phase: phase && onboardingPhases.includes(phase) ? phase : 'done',
  }
}

export const preferencesApi = {
  async get(): Promise<PlayerAccountPreferences> {
    const data = await apiOperationRequest<'player_preferences_retrieve', PreferencesResponse>(
      'player_preferences_retrieve',
      '/player/preferences/',
    )
    return normalizePreferences(data)
  },
  async update(payload: PreferencesUpdate): Promise<PlayerAccountPreferences> {
    const data = await apiOperationRequest<'player_preferences_partial_update', PreferencesResponse>(
      'player_preferences_partial_update',
      '/player/preferences/',
      { body: payload },
    )
    return normalizePreferences(data)
  },
}

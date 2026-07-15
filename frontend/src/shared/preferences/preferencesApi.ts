import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { PlayerPreferences } from '@/shared/preferences/preferences'

type PreferencesResponse = ApiSchemas['PlayerPreferences']
type PreferencesUpdate = ApiRequestBody<'player_preferences_partial_update'>

function normalizePreferences(data: PreferencesResponse): PlayerPreferences {
  return {
    motion_mode: data.motion_mode ?? 'system',
  }
}

export const preferencesApi = {
  async get(): Promise<PlayerPreferences> {
    const data = await apiOperationRequest<'player_preferences_retrieve', PreferencesResponse>(
      'player_preferences_retrieve',
      '/player/preferences/',
    )
    return normalizePreferences(data)
  },
  async update(payload: PreferencesUpdate): Promise<PlayerPreferences> {
    const data = await apiOperationRequest<'player_preferences_partial_update', PreferencesResponse>(
      'player_preferences_partial_update',
      '/player/preferences/',
      { body: payload },
    )
    return normalizePreferences(data)
  },
}

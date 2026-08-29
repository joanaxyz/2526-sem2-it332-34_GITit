import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type CompanionLoadoutResult = ApiSchemas['ShopEquipResponse']
type CompanionLoadoutPayload = ApiRequestBody<'player_loadout_companion_create'>

export const playerLoadoutApi = {
  equipCompanion(slug: string) {
    const body: CompanionLoadoutPayload = { kind: 'companion', slug }
    return apiOperationRequest<'player_loadout_companion_create', CompanionLoadoutResult>(
      'player_loadout_companion_create',
      '/player/loadout/companion/',
      { body },
    )
  },
}

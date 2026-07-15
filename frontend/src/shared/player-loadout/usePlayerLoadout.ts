import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

import { apiRequest } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import { DEFAULT_COMPANION_SLUG, getCompanion } from '@/shared/cosmetics/companions/registry'
import type { CompanionDef } from '@/shared/cosmetics/types'

/**
 * The player's equipped companion.
 * Stories provide the world visuals; loadout only controls companion art.
 */
export type PlayerLoadout = {
  companion: CompanionDef
  companionSlug: string
  /** True once the player owns and has equipped a companion. No companion is
   * free anymore, so a brand-new player has none - `companion`/`companionSlug`
   * still fall back to Blue for rendering, but nothing has actually been
   * bought yet. Gates (e.g. RequireCompanion) must check this, not companionSlug. */
  hasCompanion: boolean
  isLoading: boolean
  isError: boolean
  error: Error | null
}

type ShopCatalogResponse = {
  active_companion: string | null
}

export function usePlayerLoadout(): PlayerLoadout {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: queryKeys.shopCatalog,
    queryFn: () => apiRequest<ShopCatalogResponse>('/shop/catalog/'),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  const companionSlug = data?.active_companion ?? DEFAULT_COMPANION_SLUG
  const hasCompanion = Boolean(data?.active_companion)
  return useMemo(
    () => ({
      companion: getCompanion(companionSlug),
      companionSlug,
      hasCompanion,
      isLoading,
      isError,
      error: error instanceof Error ? error : null,
    }),
    [companionSlug, hasCompanion, isLoading, isError, error],
  )
}

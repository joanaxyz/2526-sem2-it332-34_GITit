import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

import { DEFAULT_COMPANION_SLUG } from '@/shared/cosmetics/companions/registry'
import { shopCatalogQueryOptions } from '@/shared/shop/api/shopApi'

export type EquippedCompanion = {
  /** Always renderable: falls back to the default companion. */
  slug: string
  /**
   * True only once the catalog is known AND nothing is equipped. An unread
   * catalog is not the same answer as an empty one, and a surface that greets
   * a brand-new player must not greet a returning one mid-restore.
   */
  isUnequipped: boolean
}

/**
 * The equipped companion, read from cache only.
 *
 * Loading states have to show the player's own companion without being the
 * reason it gets fetched: a loader can mount before sign-in resolves, or
 * several can mount at once, and none of them should fire a catalog request.
 * `enabled: false` subscribes to the cached entry without ever running the
 * query, so a loader shows the default until the catalog is known and swaps to
 * the real companion the moment some other screen has loaded it.
 *
 * It lives apart from `usePlayerLoadout` on purpose: that hook is mocked
 * wholesale by tests of the surfaces it gates, and the shared loading state
 * must not break when it is.
 */
export function useEquippedCompanion(): EquippedCompanion {
  const { data } = useQuery({ ...shopCatalogQueryOptions(), enabled: false })
  return useMemo(
    () => ({
      slug: data?.active_companion ?? DEFAULT_COMPANION_SLUG,
      isUnequipped: Boolean(data) && !data?.active_companion,
    }),
    [data],
  )
}

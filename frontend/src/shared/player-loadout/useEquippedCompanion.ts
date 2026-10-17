import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

import { DEFAULT_COMPANION_SLUG } from '@/shared/cosmetics/companions/registry'
import { useAuthStore } from '@/shared/auth/useAuth'
import { shopCatalogQueryOptions } from '@/shared/shop/api/shopApi'

export type EquippedCompanion = {
  /** Null until the catalog is known, so callers never paint Blue as a
   * temporary stand-in for another equipped companion. */
  slug: string | null
  /**
   * True only once the catalog is known AND nothing is equipped. An unread
   * catalog is not the same answer as an empty one, and a surface that greets
   * a brand-new player must not greet a returning one mid-restore.
   */
  isUnequipped: boolean
}

/**
 * The equipped companion used by shared chrome such as the loading screen.
 *
 * A loader can mount before sign-in resolves, so the catalog request stays
 * disabled until an authenticated session exists. Once it does, React Query
 * deduplicates this request with any screen that also needs the catalog. Until
 * that shared result arrives, `slug` remains null instead of briefly showing
 * the default Blue companion and then swapping to the equipped one.
 *
 * It lives apart from `usePlayerLoadout` on purpose: that hook is mocked
 * wholesale by tests of the surfaces it gates, and the shared loading state
 * must not break when it is.
 */
export function useEquippedCompanion(): EquippedCompanion {
  const accessToken = useAuthStore((state) => state.accessToken)
  const { data } = useQuery({ ...shopCatalogQueryOptions(), enabled: Boolean(accessToken) })
  return useMemo(
    () => ({
      slug: data ? data.active_companion ?? DEFAULT_COMPANION_SLUG : null,
      isUnequipped: Boolean(data) && !data?.active_companion,
    }),
    [data],
  )
}

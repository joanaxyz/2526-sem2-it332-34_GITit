import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { towerDesignsApi } from '@/features/tower-designs/api/towerDesignsApi'
import type { TowerDesign } from '@/features/tower-designs/types'
import { queryKeys } from '@/shared/api/queryKeys'

/**
 * One personal tower per user, plus an optional private fork of the official
 * tower. `mine()` returns BOTH, so we must select by `origin` — never by index —
 * or the fork masquerades as the personal tower and `/my-tower/overview/` (which
 * needs the active personal design) 404s. The personal create is idempotent
 * server-side, so the cap reads as a fact of the world, not a validation error.
 */
export function useTowerDesignEditor() {
  const queryClient = useQueryClient()
  const minesQuery = useQuery({
    queryKey: queryKeys.towerDesigns,
    queryFn: towerDesignsApi.mine,
    staleTime: 60 * 1000,
  })

  const results = minesQuery.data?.results ?? []
  const design: TowerDesign | null = results.find((d) => d.origin === 'personal') ?? null
  const fork: TowerDesign | null = results.find((d) => d.origin === 'official_fork') ?? null
  const hasDesign = design !== null

  const createMutation = useMutation({
    mutationFn: () => {
      const stamp = Date.now().toString(36)
      return towerDesignsApi.create({ slug: `your-tower-${stamp}`, title: 'Your Tower' })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
    },
  })

  const officialForkMutation = useMutation({
    mutationFn: () => towerDesignsApi.officialFork(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.towerDesigns })
    },
  })

  return {
    isLoading: minesQuery.isLoading,
    isError: minesQuery.isError,
    design,
    fork,
    hasDesign,
    canCreate: !hasDesign && !createMutation.isPending,
    isCreating: createMutation.isPending,
    isForking: officialForkMutation.isPending,
    /** Creates the single design and resolves to it (caller routes into the editor). */
    raiseSpire: () => createMutation.mutateAsync(),
    /** Get-or-create the private official fork; resolves to its overview. */
    openOfficialFork: () => officialForkMutation.mutateAsync(),
  }
}

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

import { assetsApi } from '@/shared/assets/assetsApi'
import { queryKeys } from '@/shared/api/queryKeys'
import type { MonsterAssetDescriptor } from '@/shared/assets/types'

/** Official + the user's own + purchased monsters, for the roster pickers. */
export function useOwnedMonsters() {
  const query = useQuery({
    queryKey: queryKeys.assetDescriptorsOwned('monster'),
    queryFn: () => assetsApi.getOwnedDescriptors('monster'),
    staleTime: 5 * 60 * 1000,
  })

  const monsters = useMemo<MonsterAssetDescriptor[]>(() => {
    return Object.values(query.data?.results ?? {})
      .filter((d): d is MonsterAssetDescriptor => d.kind === 'monster')
      .sort((a, b) => a.label.localeCompare(b.label))
  }, [query.data])

  return { monsters, isLoading: query.isLoading }
}

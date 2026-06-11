import type { QueryClient } from '@tanstack/react-query'

import type { AdventureRun } from '@/features/command-adventures/types'
import { queryKeys } from '@/shared/api/queryKeys'

export function syncAdventureRunInCache(queryClient: QueryClient, run: AdventureRun) {
  queryClient.setQueryData(queryKeys.adventureRun(run.id), run)
}

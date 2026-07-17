import type { QueryClient } from '@tanstack/react-query'

import type { AdventureRun } from '@/features/adventures/types'
import { queryKeyRoots, queryKeys } from '@/shared/api/queryKeys'

export function syncAdventureRunInCache(queryClient: QueryClient, run: AdventureRun) {
  queryClient.setQueryData(queryKeys.adventureRun(run.id), run)
  invalidateAdventureProgressQueries(queryClient)
}

export function invalidateAdventureProgressQueries(queryClient: QueryClient) {
  void queryClient.invalidateQueries({ queryKey: queryKeys.chapters })
  void queryClient.invalidateQueries({ queryKey: queryKeys.homeSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeys.statsSummary })
  void queryClient.invalidateQueries({ queryKey: queryKeyRoots.chapterOverview })
  void queryClient.invalidateQueries({ queryKey: queryKeys.learnedSkills })
  void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
}

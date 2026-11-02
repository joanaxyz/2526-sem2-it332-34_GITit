import type { MutableRefObject } from 'react'
import { useMutation, type QueryClient } from '@tanstack/react-query'
import type { NavigateFunction } from 'react-router-dom'

import { adventuresApi } from '@/features/adventures/api/adventuresApi'
import { useStartAdventureRun } from '@/features/adventures/hooks/useAdventureRun'
import type { AdventureRun } from '@/features/adventures/types'
import { mapUrlForAdventure } from '@/features/adventures/utils/adventureNavigation'
import {
  invalidateAdventureProgressQueries,
  syncAdventureRunInCache,
} from '@/features/adventures/utils/adventureRunCache'
import { queryKeys } from '@/shared/api/queryKeys'

type StartAdventureRunMutation = ReturnType<typeof useStartAdventureRun>

export function useAdventureSessionMutations({
  runId,
  run,
  onRestart,
  navigate,
  queryClient,
  retryRun,
  startNextLevel,
  latestRunRef,
  bypassNavigationRunId,
  setExitNavigationRunId,
  setExitConfirmOpen,
  setStartOverConfirmOpen,
}: {
  runId: number
  run: AdventureRun | undefined
  onRestart?: () => void
  navigate: NavigateFunction
  queryClient: QueryClient
  retryRun: StartAdventureRunMutation
  startNextLevel: StartAdventureRunMutation
  latestRunRef: MutableRefObject<AdventureRun | null>
  bypassNavigationRunId: MutableRefObject<number | null>
  setExitNavigationRunId: (runId: number | null) => void
  setExitConfirmOpen: (open: boolean) => void
  setStartOverConfirmOpen: (open: boolean) => void
}) {
  const exitMutation = useMutation({
    onMutate: () => {
      const latestRun = latestRunRef.current ?? run
      bypassNavigationRunId.current = latestRun?.id ?? runId
      setExitNavigationRunId(latestRun?.id ?? runId)
      setExitConfirmOpen(false)
    },
    mutationFn: async () => {
      const latestRun = latestRunRef.current ?? run
      if (!latestRun) throw new Error('No adventure run is available to exit.')
      if (latestRun.status === 'started') await adventuresApi.discardRun(latestRun.id)
      return latestRun
    },
    onSuccess: (exitedRun) => {
      navigate(mapUrlForAdventure(exitedRun), { replace: true })
      window.setTimeout(() => {
        if (exitedRun.status === 'started') {
          queryClient.removeQueries({ queryKey: queryKeys.adventureRun(exitedRun.id) })
        } else {
          syncAdventureRunInCache(queryClient, exitedRun)
        }
        invalidateAdventureProgressQueries(queryClient)
      }, 0)
    },
    onError: () => {
      bypassNavigationRunId.current = null
      setExitNavigationRunId(null)
    },
  })

  const openAdventureRun = (mutation: StartAdventureRunMutation, levelId: number) => {
    mutation.mutate(
      { levelId },
      {
        onSuccess: (nextRun) => {
          const previousRun = run
          syncAdventureRunInCache(queryClient, nextRun)
          setExitConfirmOpen(false)
          setStartOverConfirmOpen(false)
          if (previousRun?.status === 'started') {
            bypassNavigationRunId.current = previousRun.id
            setExitNavigationRunId(previousRun.id)
          } else {
            bypassNavigationRunId.current = null
            setExitNavigationRunId(null)
          }
          navigate(`/adventure-runs/${nextRun.id}`, { replace: true })
          if (previousRun?.id && previousRun.id !== nextRun.id) {
            window.setTimeout(() => {
              queryClient.removeQueries({ queryKey: queryKeys.adventureRun(previousRun.id) })
            }, 0)
          }
        },
      },
    )
  }

  const restart =
    onRestart ??
    (() => {
      const levelId = run?.selected_level?.id
      if (!levelId || retryRun.isPending) return
      openAdventureRun(retryRun, levelId)
    })
  const backToMap = () => {
    if (run) navigate(mapUrlForAdventure(run))
  }
  const openNextLevel = run?.next_level
    ? () => {
        if (startNextLevel.isPending) return
        openAdventureRun(startNextLevel, run.next_level!.id)
      }
    : undefined

  return {
    exitMutation,
    restart,
    backToMap,
    openNextLevel,
    isRestarting: retryRun.isPending,
    isOpeningNextLevel: startNextLevel.isPending,
  }
}

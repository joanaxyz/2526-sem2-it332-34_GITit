import type { Dispatch, MutableRefObject, SetStateAction } from 'react'
import type { NavigateFunction } from 'react-router-dom'
import { useMutation, type QueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import {
  invalidateTierProgressQueries,
  syncTierRunInCache,
  updateTierRunCache,
} from '@/features/story-map/utils/tierRunCache'
import {
  mapUrlForRun,
  tierRetryUrl,
  tierStartUrl,
} from '@/features/story-map/components/tierWorkspaceLayout'
import { queryKeys } from '@/shared/api/queryKeys'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'

export function useTierWorkspaceMutations({
  run,
  runId,
  navigate,
  queryClient,
  latestRunRef,
  bypassNavigationRunId,
  setExitNavigationRunId,
  setExitConfirmOpen,
}: {
  run: TierRun | null
  runId: number
  navigate: NavigateFunction
  queryClient: QueryClient
  latestRunRef: MutableRefObject<TierRun | null>
  bypassNavigationRunId: MutableRefObject<number | null>
  setExitNavigationRunId: Dispatch<SetStateAction<number | null>>
  setExitConfirmOpen: Dispatch<SetStateAction<boolean>>
}) {
  const exitMutation = useMutation({
    onMutate: () => {
      const latestRun = latestRunRef.current ?? run
      bypassNavigationRunId.current = latestRun?.id ?? runId
      setExitNavigationRunId(latestRun?.id ?? runId)
      setExitConfirmOpen(false)
    },
    mutationFn: async () => {
      if (!run) throw new Error('No adventure tier run is available to exit.')
      if (run.status === 'started') await tierRunsApi.discardRun(run.id)
      return run
    },
    onSuccess: (exitedRun) => {
      navigate(mapUrlForRun(exitedRun), { replace: true })
      window.setTimeout(() => {
        if (exitedRun.status === 'started') {
          queryClient.removeQueries({ queryKey: queryKeys.adventureTierRun(exitedRun.id) })
        } else {
          syncTierRunInCache(queryClient, exitedRun)
        }
        invalidateTierProgressQueries(queryClient)
      }, 0)
    },
    onError: () => {
      bypassNavigationRunId.current = null
      setExitNavigationRunId(null)
    },
  })

  // Every new attempt opens through a start route, which holds the loading
  // screen until the run exists and its artwork has decoded. Leaving a run in
  // progress that way must not trip the discard-on-leave blocker: the start
  // request discards the old run itself.
  function openStartRoute(url: string, { replacesRun = false } = {}) {
    const leavingRun = latestRunRef.current ?? run
    if (leavingRun?.status === 'started') bypassNavigationRunId.current = leavingRun.id
    navigate(url)
    if (replacesRun && leavingRun) {
      window.setTimeout(() => {
        queryClient.removeQueries({ queryKey: queryKeys.adventureTierRun(leavingRun.id) })
      }, 0)
    }
  }

  const startNextLevel = (tierId: number) => openStartRoute(tierStartUrl(tierId))

  // Continues the SAME tier after a wave clear that left waves to play: the
  // server starts the learner's next uncleared wave. prior_run_id links the
  // runs so a replay chain stays a replay.
  const continueTier = () => {
    if (run) openStartRoute(tierStartUrl(run.tier.id, { priorRunId: run.id }))
  }

  const retry = () => {
    if (run) openStartRoute(tierRetryUrl(run.id), { replacesRun: true })
  }

  const replay = () => {
    if (run) openStartRoute(tierStartUrl(run.tier.id, { replay: true }), { replacesRun: true })
  }

  const createFileMutation = useMutation({
    mutationFn: (input: WorkspaceFileInput) => {
      if (!run) throw new Error('No adventure tier run is available to update.')
      return tierRunsApi.createFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateTierRunCache(queryClient, updatedRun)
    },
  })

  const writeFileMutation = useMutation({
    mutationFn: (input: WorkspaceFileInput) => {
      if (!run) throw new Error('No adventure tier run is available to update.')
      return tierRunsApi.writeFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateTierRunCache(queryClient, updatedRun)
    },
  })

  const renameFileMutation = useMutation({
    mutationFn: (input: WorkspaceFileRenameInput) => {
      if (!run) throw new Error('No adventure tier run is available to update.')
      return tierRunsApi.renameFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateTierRunCache(queryClient, updatedRun)
    },
  })

  const deleteFileMutation = useMutation({
    mutationFn: (path: string) => {
      if (!run) throw new Error('No adventure tier run is available to update.')
      return tierRunsApi.deleteFile(run.id, path)
    },
    onSuccess: (updatedRun) => {
      updateTierRunCache(queryClient, updatedRun)
    },
  })

  const playAgain = () => (run?.replay ? replay() : retry())

  return {
    exitMutation,
    startNextLevel,
    continueTier,
    retry,
    replay,
    playAgain,
    createFileMutation,
    writeFileMutation,
    renameFileMutation,
    deleteFileMutation,
  }
}

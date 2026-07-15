import type { Dispatch, MutableRefObject, SetStateAction } from 'react'
import type { NavigateFunction } from 'react-router-dom'
import { useMutation, type QueryClient } from '@tanstack/react-query'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { challengeRunsApi } from '@/features/challenges/api/challengeRunsApi'
import type { ChallengeRun } from '@/features/challenges/types'
import {
  invalidateLevelProgressQueries,
  syncChallengeRunInCache,
  updateChallengeRunCache,
} from '@/features/challenges/utils/challengeRunCache'
import { mapUrlForRun } from '@/features/challenges/components/challengeWorkspaceLayout'
import { queryKeys } from '@/shared/api/queryKeys'

export function useChallengeWorkspaceMutations({
  run,
  runId,
  navigate,
  queryClient,
  latestRunRef,
  bypassNavigationRunId,
  setExitNavigationRunId,
  setExitConfirmOpen,
  setStartOverConfirmOpen,
  setDismissedCompletionRunId,
}: {
  run: ChallengeRun | null
  runId: number
  navigate: NavigateFunction
  queryClient: QueryClient
  latestRunRef: MutableRefObject<ChallengeRun | null>
  bypassNavigationRunId: MutableRefObject<number | null>
  setExitNavigationRunId: Dispatch<SetStateAction<number | null>>
  setExitConfirmOpen: Dispatch<SetStateAction<boolean>>
  setStartOverConfirmOpen: Dispatch<SetStateAction<boolean>>
  setDismissedCompletionRunId: Dispatch<SetStateAction<number | null>>
}) {
  const exitMutation = useMutation({
    onMutate: () => {
      const latestRun = latestRunRef.current ?? run
      bypassNavigationRunId.current = latestRun?.id ?? runId
      setExitNavigationRunId(latestRun?.id ?? runId)
      setExitConfirmOpen(false)
    },
    mutationFn: async () => {
      if (!run) throw new Error('No challenge run is available to exit.')
      if (run.status === 'started') await challengesApi.discardChallengeRun(run.id)
      return run
    },
    onSuccess: (exitedRun) => {
      navigate(mapUrlForRun(exitedRun), { replace: true })
      window.setTimeout(() => {
        if (exitedRun.status === 'started') {
          queryClient.removeQueries({ queryKey: queryKeys.challengeRun(exitedRun.id) })
        } else {
          syncChallengeRunInCache(queryClient, exitedRun)
        }
        invalidateLevelProgressQueries(queryClient)
      }, 0)
    },
    onError: () => {
      bypassNavigationRunId.current = null
      setExitNavigationRunId(null)
    },
  })

  // Starts a fresh run on any trial - the "Next level" CTA and the completion
  // modal's navigator both route through here, so jumping to a lower trial works
  // exactly like advancing to the next one.
  const startLevelMutation = useMutation({
    mutationFn: (trialId: number) => challengesApi.startChallengeRun(trialId),
    onSuccess: (next) => {
      syncChallengeRunInCache(queryClient, next)
      invalidateLevelProgressQueries(queryClient)
      if (run?.status === 'completed') setDismissedCompletionRunId(run.id)
      navigate(`/challenge-runs/${next.id}`)
    },
  })

  // Replaying a free-play run starts a fresh uncounted run on the same trial -
  // never the retry endpoint, which rejects non-replay runs. This keeps "Play
  // again" working for already-completed trials without touching progress.
  const replayMutation = useMutation({
    mutationFn: (trialId: number) => challengesApi.startChallengeRun(trialId, { replay: true }),
    onSuccess: (next) => {
      moveToReplacementRun({
        previousRun: run,
        nextRun: next,
        navigate,
        queryClient,
        bypassNavigationRunId,
        setExitNavigationRunId,
        setExitConfirmOpen,
        setStartOverConfirmOpen,
        setDismissedCompletionRunId,
      })
    },
  })

  const retryMutation = useMutation({
    mutationFn: () => {
      if (!run) throw new Error('No challenge run is available to retry.')
      return challengesApi.retryChallengeRun(run.id)
    },
    onSuccess: (next) => {
      moveToReplacementRun({
        previousRun: run,
        nextRun: next,
        navigate,
        queryClient,
        bypassNavigationRunId,
        setExitNavigationRunId,
        setExitConfirmOpen,
        setStartOverConfirmOpen,
        setDismissedCompletionRunId,
      })
    },
  })

  const createFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.createFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })

  const writeFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.writeFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })

  const renameFileMutation = useMutation({
    mutationFn: (input: { path: string; newPath: string }) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.renameFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })

  const deleteFileMutation = useMutation({
    mutationFn: (path: string) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.deleteFile(run.id, path)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })

  const startFreshAttempt = () => retryMutation.mutate()
  const playAgain = () => {
    if (run?.replay) {
      replayMutation.mutate(run.challenge.level_id)
    } else {
      retryMutation.mutate()
    }
  }

  return {
    exitMutation,
    startLevelMutation,
    replayMutation,
    retryMutation,
    createFileMutation,
    writeFileMutation,
    renameFileMutation,
    deleteFileMutation,
    startFreshAttempt,
    playAgain,
  }
}

function moveToReplacementRun({
  previousRun,
  nextRun,
  navigate,
  queryClient,
  bypassNavigationRunId,
  setExitNavigationRunId,
  setExitConfirmOpen,
  setStartOverConfirmOpen,
  setDismissedCompletionRunId,
}: {
  previousRun: ChallengeRun | null
  nextRun: ChallengeRun
  navigate: NavigateFunction
  queryClient: QueryClient
  bypassNavigationRunId: MutableRefObject<number | null>
  setExitNavigationRunId: Dispatch<SetStateAction<number | null>>
  setExitConfirmOpen: Dispatch<SetStateAction<boolean>>
  setStartOverConfirmOpen: Dispatch<SetStateAction<boolean>>
  setDismissedCompletionRunId: Dispatch<SetStateAction<number | null>>
}) {
  syncChallengeRunInCache(queryClient, nextRun)
  invalidateLevelProgressQueries(queryClient)
  setDismissedCompletionRunId(null)
  setExitConfirmOpen(false)
  setStartOverConfirmOpen(false)
  if (previousRun?.status === 'started') {
    bypassNavigationRunId.current = previousRun.id
    setExitNavigationRunId(previousRun.id)
  } else {
    bypassNavigationRunId.current = null
    setExitNavigationRunId(null)
  }
  navigate(`/challenge-runs/${nextRun.id}`)
  if (previousRun?.id && previousRun.id !== nextRun.id) {
    window.setTimeout(() => {
      queryClient.removeQueries({ queryKey: queryKeys.challengeRun(previousRun.id) })
    }, 0)
  }
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo } from 'react'

import { adventuresApi } from '@/features/adventures/api/adventuresApi'
import type { AdventureRun } from '@/features/adventures/types'
import { terminalLinesFromSteps } from '@/shared/level/terminalSteps'
import { queryKeys } from '@/shared/api/queryKeys'
import {
  invalidateAdventureProgressQueries,
  syncAdventureRunInCache,
} from '@/features/adventures/utils/adventureRunCache'

const pendingAdventureStarts = new Map<number, Promise<AdventureRun>>()

export function startAdventureRun(levelId: number) {
  const pendingStart = pendingAdventureStarts.get(levelId)
  if (pendingStart) return pendingStart

  const start = adventuresApi.startRun(levelId)
  pendingAdventureStarts.set(levelId, start)
  const clearPendingStart = () => {
    if (pendingAdventureStarts.get(levelId) === start) {
      pendingAdventureStarts.delete(levelId)
    }
  }
  void start.then(clearPendingStart, clearPendingStart)
  return start
}

export function useAdventureRun(runId: number | null) {
  const queryClient = useQueryClient()
  const key = runId ? queryKeys.adventureRun(runId) : ['adventure-run', 'none']

  const query = useQuery({
    queryKey: key,
    queryFn: () => adventuresApi.getRun(runId as number),
    enabled: runId != null,
  })

  function writeRun(run: AdventureRun) {
    syncAdventureRunInCache(queryClient, run)
  }

  // The terminal derives its lines from the live attempt's cached step history,
  // so an optimistic placeholder appears instantly and the history survives a
  // refresh. Switching problems resets the terminal for free (new empty steps).
  const run = query.data ?? null
  const lines = useMemo(
    () => terminalLinesFromSteps(run?.current_attempt?.steps ?? []),
    [run],
  )

  const discardRun = useMutation({
    mutationFn: () => adventuresApi.discardRun(runId as number),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: key })
      invalidateAdventureProgressQueries(queryClient)
    },
  })

  const createFile = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      const attempt = queryClient.getQueryData<AdventureRun>(key)?.current_attempt
      if (!attempt) throw new Error('No adventure attempt is available to update.')
      return adventuresApi.createFile(runId as number, input)
    },
    onSuccess: writeRun,
  })

  const writeFile = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      const attempt = queryClient.getQueryData<AdventureRun>(key)?.current_attempt
      if (!attempt) throw new Error('No adventure attempt is available to update.')
      return adventuresApi.writeFile(runId as number, input)
    },
    onSuccess: writeRun,
  })

  const renameFile = useMutation({
    mutationFn: (input: { path: string; newPath: string }) => {
      const attempt = queryClient.getQueryData<AdventureRun>(key)?.current_attempt
      if (!attempt) throw new Error('No adventure attempt is available to update.')
      return adventuresApi.renameFile(runId as number, input)
    },
    onSuccess: writeRun,
  })

  const deleteFile = useMutation({
    mutationFn: (path: string) => {
      const attempt = queryClient.getQueryData<AdventureRun>(key)?.current_attempt
      if (!attempt) throw new Error('No adventure attempt is available to update.')
      return adventuresApi.deleteFile(runId as number, path)
    },
    onSuccess: writeRun,
  })

  return { query, lines, discardRun, createFile, writeFile, renameFile, deleteFile, writeRun }
}

export function useStartAdventureRun() {
  return useMutation({
    mutationFn: ({ levelId }: { levelId: number }) => startAdventureRun(levelId),
  })
}

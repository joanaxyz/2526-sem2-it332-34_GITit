import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo } from 'react'

import { commandAdventuresApi } from '@/features/command-adventures/api/commandAdventuresApi'
import type { AdventureRun } from '@/features/command-adventures/types'
import { terminalLinesFromSteps } from '@/shared/practice/terminalSteps'
import { queryKeys } from '@/shared/api/queryKeys'

export function useAdventureRun(runId: number | null) {
  const queryClient = useQueryClient()
  const key = runId ? queryKeys.adventureRun(runId) : ['adventure-run', 'none']

  const query = useQuery({
    queryKey: key,
    queryFn: () => commandAdventuresApi.getRun(runId as number),
    enabled: runId != null,
  })

  function writeRun(run: AdventureRun) {
    queryClient.setQueryData(queryKeys.adventureRun(run.id), run)
  }

  // The terminal derives its lines from the live attempt's cached step history,
  // so an optimistic placeholder appears instantly and the history survives a
  // refresh. Switching problems resets the terminal for free (new empty steps).
  const run = query.data ?? null
  const lines = useMemo(
    () => terminalLinesFromSteps(run?.current_attempt?.steps ?? []),
    [run],
  )

  const useHint = useMutation({
    mutationFn: () => commandAdventuresApi.useHint(runId as number),
    onSuccess: (response) => writeRun(response.run),
  })

  const finishRun = useMutation({
    mutationFn: () => commandAdventuresApi.finishRun(runId as number),
    onSuccess: writeRun,
  })

  const createFile = useMutation({
    mutationFn: (input: { path: string; content: string }) =>
      commandAdventuresApi.createFile(runId as number, input),
    onSuccess: writeRun,
  })

  const writeFile = useMutation({
    mutationFn: (input: { path: string; content: string }) =>
      commandAdventuresApi.writeFile(runId as number, input),
    onSuccess: writeRun,
  })

  return { query, lines, useHint, finishRun, createFile, writeFile, writeRun }
}

export function useStartAdventureRun() {
  return useMutation({
    mutationFn: (adventureSlug: string) => commandAdventuresApi.startRun(adventureSlug),
  })
}

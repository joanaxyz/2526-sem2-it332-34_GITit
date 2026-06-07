import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { commandAdventuresApi } from '@/features/command-adventures/api/commandAdventuresApi'
import type { AdventureRun } from '@/features/command-adventures/types'
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

  const submitCommand = useMutation({
    mutationFn: (command: string) => commandAdventuresApi.submitCommand(runId as number, command),
    onSuccess: (response) => writeRun(response.run),
  })

  const useHint = useMutation({
    mutationFn: () => commandAdventuresApi.useHint(runId as number),
    onSuccess: (response) => writeRun(response.run),
  })

  const finishRun = useMutation({
    mutationFn: () => commandAdventuresApi.finishRun(runId as number),
    onSuccess: writeRun,
  })

  return { query, submitCommand, useHint, finishRun, writeRun }
}

export function useStartAdventureRun() {
  return useMutation({
    mutationFn: (adventureSlug: string) => commandAdventuresApi.startRun(adventureSlug),
  })
}

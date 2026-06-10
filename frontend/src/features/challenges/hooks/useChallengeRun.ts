import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo } from 'react'

import { challengeRunsApi } from '@/features/challenges/api/challengeRunsApi'
import {
  clearChallengeRunBootstrap,
  readChallengeRunBootstrap,
} from '@/features/challenges/utils/challengeRunBootstrap'
import type { ChallengeRun, TerminalLine } from '@/shared/practice/types'
import { isEphemeralStep, terminalLinesFromSteps } from '@/shared/practice/terminalSteps'
import { queryKeys } from '@/shared/api/queryKeys'

const bootLines: TerminalLine[] = []

export function useChallengeRun(runId: number) {
  const queryClient = useQueryClient()
  const bootstrapRun = Number.isFinite(runId) ? readChallengeRunBootstrap(runId) : undefined
  const cachedRun = Number.isFinite(runId)
    ? queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))
    : undefined
  const initialRun = cachedRun ?? bootstrapRun

  const query = useQuery({
    queryKey: queryKeys.challengeRun(runId),
    queryFn: async () => {
      const run = await challengeRunsApi.getRun(runId)
      clearChallengeRunBootstrap(runId)
      return run
    },
    enabled: Number.isFinite(runId),
    initialData: initialRun,
    staleTime: 30_000,
  })

  const run = query.data ?? null
  const lines = useMemo(() => (run ? terminalLinesFromSteps(run.steps ?? []) : bootLines), [run])
  const feedback = run?.steps?.filter((step) => !isEphemeralStep(step)).at(-1)?.contextual_feedback ?? ''

  return {
    query,
    run,
    lines,
    feedback,
  }
}

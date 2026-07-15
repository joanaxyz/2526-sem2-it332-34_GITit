import { useEffect } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { syncChallengeRunInCache } from '@/features/challenges/utils/challengeRunCache'
import type { ChallengeRun } from '@/features/challenges/types'
import { ApiError } from '@/shared/api/apiError'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type ChallengeStartMode = 'start' | 'replay' | 'retry'

const loadingCopy: Record<ChallengeStartMode, { label: string; description: string }> = {
  start: {
    label: 'Starting challenge',
    description: 'Preparing the repository, terminal, and challenge workspace.',
  },
  replay: {
    label: 'Starting replay',
    description: 'Preparing an uncounted replay of this challenge.',
  },
  retry: {
    label: 'Retrying challenge',
    description: 'Resetting the repository and preparing a fresh attempt.',
  },
}

export function ChallengeStartPage({ mode = 'start' }: { mode?: ChallengeStartMode }) {
  const { trialId, runId } = useParams<{ trialId?: string; runId?: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const targetId = Number(mode === 'retry' ? runId : trialId)

  const start = useMutation({
    mutationFn: async (): Promise<ChallengeRun> => {
      if (!Number.isFinite(targetId)) {
        throw new Error(mode === 'retry' ? 'Missing challenge run.' : 'Missing challenge trial.')
      }
      if (mode === 'retry') return challengesApi.retryChallengeRun(targetId)
      return challengesApi.startChallengeRun(targetId, { replay: mode === 'replay' })
    },
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`, { replace: true })
    },
  })

  useEffect(() => {
    if (start.isIdle) {
      start.mutate()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (start.isError) {
    // See AdventureStartPage: the RequireCompanion route guard should already
    // have caught this, but a stale shop cache can let one request
    // through. Only redirect for that specific lock reason.
    if (
      start.error instanceof ApiError &&
      start.error.status === 423 &&
      start.error.message.toLowerCase().includes('companion')
    ) {
      return <Navigate replace to="/shop?tab=companions&required=1" />
    }
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare challenge" description={start.error.message} />
      </div>
    )
  }

  const copy = loadingCopy[mode]
  return <LoadingState description={copy.description} label={copy.label} variant="screen" />
}

import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { syncChallengeRunInCache } from '@/features/challenges/utils/challengeRunCache'
import type { ChallengeRun } from '@/shared/practice/types'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type ChallengeStartMode = 'start' | 'review' | 'retry'

const loadingCopy: Record<ChallengeStartMode, { label: string; description: string }> = {
  start: {
    label: 'Starting challenge',
    description: 'Preparing the repository, terminal, and challenge workspace.',
  },
  review: {
    label: 'Starting replay',
    description: 'Preparing an uncounted replay of this challenge.',
  },
  retry: {
    label: 'Retrying challenge',
    description: 'Resetting the repository and preparing a fresh attempt.',
  },
}

export function ChallengeStartPage({ mode = 'start' }: { mode?: ChallengeStartMode }) {
  const { questId, runId } = useParams<{ questId?: string; runId?: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const targetId = Number(mode === 'retry' ? runId : questId)

  const start = useMutation({
    mutationFn: async (): Promise<ChallengeRun> => {
      if (!Number.isFinite(targetId)) {
        throw new Error(mode === 'retry' ? 'Missing challenge run.' : 'Missing challenge quest.')
      }
      if (mode === 'retry') return challengesApi.retryChallengeRun(targetId)
      return challengesApi.startChallengeRun(targetId, { review: mode === 'review' })
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
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare challenge" description={start.error.message} />
      </div>
    )
  }

  const copy = loadingCopy[mode]
  return <LoadingState description={copy.description} label={copy.label} variant="screen" />
}

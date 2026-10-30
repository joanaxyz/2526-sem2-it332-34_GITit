import { useEffect, useRef } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { loadTierRunPage } from '@/features/story-map/pages/loadTierRunPage'
import { tierRunAssetManifest } from '@/features/story-map/utils/tierBattle'
import { syncTierRunInCache } from '@/features/story-map/utils/tierRunCache'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { warmBattleAssets } from '@/shared/battle/battleAssets'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

type TierStartMode = 'start' | 'replay' | 'retry'

const loadingCopy: Record<TierStartMode | 'continue', { label: string; description: string }> = {
  start: {
    label: 'Starting adventure',
    description: 'Preparing the repository, terminal, and adventure workspace.',
  },
  continue: {
    label: 'Starting next scenario',
    description: 'Preparing a fresh variant of this adventure.',
  },
  replay: {
    label: 'Starting replay',
    description: 'Preparing an uncounted replay of this adventure.',
  },
  retry: {
    label: 'Retrying adventure',
    description: 'Resetting the repository and preparing a fresh attempt.',
  },
}

/** Mirrors ChallengeStartPage.tsx for the adventure-tier run lifecycle. */
export function TierStartPage({ mode = 'start' }: { mode?: TierStartMode }) {
  const { tierId, runId } = useParams<{ tierId?: string; runId?: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { companionSlug } = usePlayerLoadout()
  const targetId = Number(mode === 'retry' ? runId : tierId)
  // Continuing after a partial clear passes the run just played, so
  // TierVariantSelectionService rotates away from its variant.
  const [searchParams] = useSearchParams()
  const transfer = searchParams.get('transfer') === '1'
  const priorRunValue = Number(searchParams.get('prior_run_id') ?? Number.NaN)
  const priorRunId = mode === 'start' && Number.isInteger(priorRunValue) && priorRunValue > 0
    ? priorRunValue
    : null

  const start = useMutation({
    mutationFn: async (): Promise<TierRun> => {
      if (!Number.isFinite(targetId)) {
        throw new Error(mode === 'retry' ? 'Missing adventure tier run.' : 'Missing adventure tier.')
      }
      if (mode === 'retry') return tierRunsApi.retryRun(targetId)
      if (transfer) return tierRunsApi.startRun(targetId, { transfer: true })
      if (priorRunId !== null) return tierRunsApi.startRun(targetId, { prior_run_id: priorRunId })
      return tierRunsApi.startRun(targetId, { replay: mode === 'replay' })
    },
    onSuccess: async (run) => {
      syncTierRunInCache(queryClient, run)
      await Promise.allSettled([
        loadTierRunPage(),
        warmBattleAssets(tierRunAssetManifest(run, companionSlug)),
      ])
      navigate(`/adventure-tier-runs/${run.id}`, { replace: true })
    },
  })

  // A second start discards the first run server-side, so StrictMode's
  // remount must not fire the request again.
  const requested = useRef(false)
  useEffect(() => {
    if (requested.current) return
    requested.current = true
    void loadTierRunPage().catch(() => undefined)
    start.mutate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (start.isError) {
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare adventure" description={start.error.message} />
      </div>
    )
  }

  const copy = transfer
    ? { label: 'Starting transfer checkpoint', description: 'Your first attempt on this unfamiliar scenario is recorded.' }
    : loadingCopy[priorRunId === null ? mode : 'continue']
  return <LoadingScreen description={copy.description} label={copy.label} />
}

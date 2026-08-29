import { useEffect } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { useStartAdventureRun } from '@/features/adventures/hooks/useAdventureRun'
import { syncAdventureRunInCache } from '@/features/adventures/utils/adventureRunCache'
import { ApiError } from '@/shared/api/apiError'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

/**
 * Entry page for chapter adventure-level runs.
 *
 * The story map should only navigate here. This page owns the start mutation,
 * caches the created run, then replaces itself with the real run workspace.
 * That keeps the loading screen inside the level flow instead of the map.
 */
export function AdventureStartPage() {
  const { levelId: levelIdParam } = useParams<{ levelId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const start = useStartAdventureRun()
  const { companionSlug } = usePlayerLoadout()
  const rawLevelId = Number(levelIdParam)
  const levelId = Number.isInteger(rawLevelId) && rawLevelId > 0 ? rawLevelId : null

  useEffect(() => {
    if (levelId && start.isIdle) {
      start.mutate({ levelId }, {
        onSuccess: (run) => {
          syncAdventureRunInCache(queryClient, run)
          navigate(`/adventure-runs/${run.id}`, { replace: true })
        },
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [levelId])

  if (!levelId) {
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare adventure" description="Missing adventure level." />
      </div>
    )
  }

  if (start.isError) {
    // No companion owned yet - the RequireCompanion route guard should
    // already have caught this, but a stale shop cache can let the
    // request through once. Only redirect for that specific lock reason;
    // other 423s (chapter/adventure progression, locked story) are
    // real errors this page should still surface.
    if (
      start.error instanceof ApiError &&
      start.error.status === 423 &&
      start.error.message.toLowerCase().includes('companion')
    ) {
      return <Navigate replace to="/shop?tab=companions&required=1" />
    }
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare adventure" description={start.error.message} />
      </div>
    )
  }

  return (
    <LoadingState
      companionSlug={companionSlug}
      description="Preparing the repository, terminal, and command challenge."
      label="Starting adventure"
      variant="screen"
    />
  )
}

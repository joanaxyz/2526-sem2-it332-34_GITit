import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { useStartAdventureRun } from '@/features/command-adventures/hooks/useAdventureRun'
import { syncAdventureRunInCache } from '@/features/command-adventures/utils/adventureRunCache'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

/**
 * Entry page for Command Adventure runs.
 *
 * The tower should only navigate here. This page owns the start mutation,
 * caches the created run, then replaces itself with the real run workspace.
 * That keeps the loading screen inside the level flow instead of the tower.
 */
export function AdventureStartPage() {
  const { adventureSlug } = useParams<{ adventureSlug: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const start = useStartAdventureRun()

  useEffect(() => {
    if (adventureSlug && start.isIdle) {
      start.mutate(adventureSlug, {
        onSuccess: (run) => {
          syncAdventureRunInCache(queryClient, run)
          navigate(`/adventure-runs/${run.id}`, { replace: true })
        },
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [adventureSlug])

  if (!adventureSlug) {
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare adventure" description="Missing adventure." />
      </div>
    )
  }

  if (start.isError) {
    return (
      <div className="grid min-h-screen place-items-center bg-background p-6">
        <ErrorState title="Could not prepare adventure" description={start.error.message} />
      </div>
    )
  }

  return (
    <LoadingState
      description="Preparing the repository, terminal, and command challenge."
      label="Starting adventure"
      variant="screen"
    />
  )
}
